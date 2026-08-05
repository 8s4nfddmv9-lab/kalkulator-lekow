#!/usr/bin/env python3
"""Exercise canonical, static and not-found routes in a real browser."""

from __future__ import annotations

import argparse
import functools
import http.client
import http.server
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from urllib.parse import urlsplit

from smoke_test_offline_pwa import (
    SmokeTestError,
    execute,
    free_port,
    json_request,
    navigate,
    prepare_strict_offline_network,
    wait_for_webdriver,
)

CANONICAL_ROUTES = {
    "/about/": (
        "InfusionCalc — technical infusion calculator",
        "Technical infusion calculations, without a setup screen.",
    ),
    "/privacy/": (
        "Prywatność — InfusionCalc",
        "Obliczenia lokalne i ograniczona analityka.",
    ),
    "/changelog/": (
        "Changelog — InfusionCalc",
        "Co zmienia się w InfusionCalc.",
    ),
}
NOT_FOUND_ROUTE = "/route-that-must-not-become-the-calculator/"
NOT_FOUND_TITLE = "Nie znaleziono strony — InfusionCalc"


class GitHubPagesLikeHandler(http.server.SimpleHTTPRequestHandler):
    """Serve directories with slash redirects and root 404.html for misses."""

    request_log: list[str] = []

    def log_message(self, format: str, *args: object) -> None:
        self.request_log.append(format % args)

    def _serve_not_found(self, *, include_body: bool) -> None:
        body = (Path(self.directory) / "404.html").read_bytes()
        self.send_response(404, "Not Found")
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def _path_exists(self) -> bool:
        request_path = urlsplit(self.path).path
        translated = Path(self.translate_path(request_path))
        return translated.exists()

    def do_GET(self) -> None:  # noqa: N802 - inherited HTTP method name
        if self._path_exists():
            super().do_GET()
            return
        self._serve_not_found(include_body=True)

    def do_HEAD(self) -> None:  # noqa: N802 - inherited HTTP method name
        if self._path_exists():
            super().do_HEAD()
            return
        self._serve_not_found(include_body=False)


def _http_request(port: int, path: str) -> tuple[int, dict[str, str], bytes]:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read()
        headers = {key.lower(): value for key, value in response.getheaders()}
        return response.status, headers, body
    finally:
        connection.close()


def _assert_server_contract(port: int) -> None:
    for path, (title, _) in CANONICAL_ROUTES.items():
        status, _, body = _http_request(port, path)
        if status != 200 or f"<title>{title}</title>".encode() not in body:
            raise SmokeTestError(
                f"Canonical route {path} is not a direct static 200 response.",
            )

    for path in ("/about", "/privacy", "/changelog"):
        status, headers, _ = _http_request(port, path)
        expected = f"{path}/"
        if status not in {301, 302, 307, 308}:
            raise SmokeTestError(
                f"{path} must redirect to its trailing-slash canonical; got {status}.",
            )
        if headers.get("location") != expected:
            raise SmokeTestError(
                f"{path} redirect must target {expected}; got {headers.get('location')}.",
            )

    status, _, body = _http_request(port, NOT_FOUND_ROUTE)
    if status != 404:
        raise SmokeTestError(
            f"Unknown route must return HTTP 404; got {status}.",
        )
    if b'data-page="not-found"' not in body:
        raise SmokeTestError("The custom 404 body was not served for an unknown route.")


def _page_state(base_url: str, session_id: str) -> dict[str, object]:
    value = execute(
        base_url,
        session_id,
        """
        return {
          title: document.title,
          h1: document.querySelector('h1')?.textContent?.trim() || null,
          page: document.body?.dataset?.page || null,
          flutterView: Boolean(document.querySelector('flutter-view')),
          ready: document.documentElement?.dataset.offlineReady === 'true',
          controller: Boolean(navigator.serviceWorker?.controller),
          href: window.location.href,
        };
        """,
    )
    return value if isinstance(value, dict) else {}


def _wait_for_page(
    base_url: str,
    session_id: str,
    *,
    label: str,
    title: str,
    h1: str,
    page: str | None = None,
    flutter_view: bool = False,
    href_suffix: str | None = None,
    require_offline_ready: bool = False,
    timeout: float = 45,
) -> dict[str, object]:
    deadline = time.monotonic() + timeout
    last: dict[str, object] = {}
    while time.monotonic() < deadline:
        try:
            last = _page_state(base_url, session_id)
        except SmokeTestError:
            time.sleep(0.25)
            continue

        matches = (
            last.get("title") == title
            and last.get("h1") == h1
            and last.get("flutterView") is flutter_view
            and (page is None or last.get("page") == page)
            and (
                href_suffix is None
                or str(last.get("href") or "").endswith(href_suffix)
            )
            and (
                not require_offline_ready
                or (
                    last.get("ready") is True
                    and last.get("controller") is True
                )
            )
        )
        if matches:
            return last
        time.sleep(0.25)

    raise SmokeTestError(f"{label} did not reach the expected state: {last}")


def _wait_for_calculator_ready(
    base_url: str,
    session_id: str,
    *,
    timeout: float = 90,
) -> dict[str, object]:
    deadline = time.monotonic() + timeout
    last: dict[str, object] = {}
    while time.monotonic() < deadline:
        try:
            last = _page_state(base_url, session_id)
        except SmokeTestError:
            time.sleep(0.25)
            continue
        if (
            last.get("ready") is True
            and last.get("controller") is True
            and last.get("flutterView") is True
        ):
            return last
        time.sleep(0.5)
    raise SmokeTestError(f"Calculator did not prepare the offline bundle: {last}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir", nargs="?", type=Path, default=Path("build/web"))
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    for required in ("index.html", "404.html", "pwa_service_worker.js"):
        if not (build_dir / required).is_file():
            raise SystemExit(f"Finalized web build is missing {required}: {build_dir}")

    chrome = next(
        (
            path
            for name in (
                "google-chrome",
                "google-chrome-stable",
                "chromium",
                "chromium-browser",
            )
            if (path := shutil.which(name))
        ),
        None,
    )
    chromedriver = shutil.which("chromedriver")
    if chrome is None or chromedriver is None:
        raise SystemExit(
            "The route smoke test requires Chrome/Chromium and ChromeDriver.",
        )

    GitHubPagesLikeHandler.request_log = []
    handler = functools.partial(
        GitHubPagesLikeHandler,
        directory=str(build_dir),
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    origin = f"http://127.0.0.1:{server.server_port}/"

    driver_port = free_port()
    driver_base = f"http://127.0.0.1:{driver_port}"

    with tempfile.TemporaryDirectory() as profile_directory:
        driver = subprocess.Popen(
            [chromedriver, f"--port={driver_port}", "--allowed-ips="],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        session_id: str | None = None
        try:
            _assert_server_contract(server.server_port)
            wait_for_webdriver(driver_base, driver)
            response = json_request(
                driver_base,
                "POST",
                "/session",
                {
                    "capabilities": {
                        "alwaysMatch": {
                            "browserName": "chrome",
                            "pageLoadStrategy": "none",
                            "goog:chromeOptions": {
                                "binary": chrome,
                                "args": [
                                    "--headless=new",
                                    "--no-sandbox",
                                    "--disable-dev-shm-usage",
                                    "--enable-unsafe-swiftshader",
                                    "--no-first-run",
                                    "--no-default-browser-check",
                                    "--window-size=1000,1000",
                                    f"--user-data-dir={profile_directory}",
                                ],
                            },
                        },
                    },
                },
                timeout=30,
            )
            value = response.get("value", {})
            session_id = value.get("sessionId") if isinstance(value, dict) else None
            if not isinstance(session_id, str) or not session_id:
                raise SmokeTestError(
                    f"ChromeDriver did not return a session ID: {response}",
                )

            navigate(driver_base, session_id, origin)
            _wait_for_calculator_ready(driver_base, session_id)

            for path, (title, h1) in CANONICAL_ROUTES.items():
                navigate(driver_base, session_id, f"{origin.rstrip('/')}{path}")
                _wait_for_page(
                    driver_base,
                    session_id,
                    label=f"Online {path}",
                    title=title,
                    h1=h1,
                    href_suffix=path,
                )

            navigate(
                driver_base,
                session_id,
                f"{origin.rstrip('/')}{NOT_FOUND_ROUTE}",
            )
            _wait_for_page(
                driver_base,
                session_id,
                label="Online hard 404",
                title=NOT_FOUND_TITLE,
                h1="Nie znaleziono strony.",
                page="not-found",
                href_suffix=NOT_FOUND_ROUTE,
            )

            navigate(driver_base, session_id, origin)
            _wait_for_calculator_ready(driver_base, session_id)
            prepare_strict_offline_network(driver_base, session_id)

            server.shutdown()
            server.server_close()
            server_thread.join(timeout=5)

            for path, (title, h1) in CANONICAL_ROUTES.items():
                navigate(driver_base, session_id, f"{origin.rstrip('/')}{path}")
                _wait_for_page(
                    driver_base,
                    session_id,
                    label=f"Offline {path}",
                    title=title,
                    h1=h1,
                    href_suffix=path,
                )

            navigate(driver_base, session_id, f"{origin.rstrip('/')}/about")
            _wait_for_page(
                driver_base,
                session_id,
                label="Offline trailing-slash redirect",
                title=CANONICAL_ROUTES["/about/"][0],
                h1=CANONICAL_ROUTES["/about/"][1],
                href_suffix="/about/",
            )

            navigate(
                driver_base,
                session_id,
                f"{origin.rstrip('/')}{NOT_FOUND_ROUTE}",
            )
            _wait_for_page(
                driver_base,
                session_id,
                label="Offline hard 404",
                title=NOT_FOUND_TITLE,
                h1="Nie znaleziono strony.",
                page="not-found",
                href_suffix=NOT_FOUND_ROUTE,
            )

            print(
                "Public-route smoke test passed: canonical pages, slash redirects "
                "and custom 404 remain distinct online and offline.",
            )
        except Exception as error:
            request_tail = GitHubPagesLikeHandler.request_log[-80:]
            raise SystemExit(
                f"{error}\nOrigin request log: {request_tail}",
            ) from error
        finally:
            if session_id is not None:
                try:
                    json_request(
                        driver_base,
                        "DELETE",
                        f"/session/{session_id}",
                        timeout=5,
                    )
                except Exception:
                    pass
            driver.terminate()
            try:
                driver.wait(timeout=5)
            except subprocess.TimeoutExpired:
                driver.kill()
            if server_thread.is_alive():
                server.shutdown()
                server.server_close()
                server_thread.join(timeout=5)


if __name__ == "__main__":
    main()
