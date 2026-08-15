#!/usr/bin/env python3
"""Prove a production InfusionCalc build starts in a truly offline browser."""

from __future__ import annotations

import argparse
import functools
import http.client
import http.server
import json
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


class SmokeTestError(RuntimeError):
    """Raised when the real-browser offline contract is not satisfied."""


class RecordingHandler(http.server.SimpleHTTPRequestHandler):
    """Serve the build and retain concise request diagnostics."""

    request_log: list[str] = []

    def log_message(self, format: str, *args: object) -> None:
        self.request_log.append(format % args)


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
        candidate.bind(("127.0.0.1", 0))
        return int(candidate.getsockname()[1])


def json_request(
    base_url: str,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    timeout: float = 10,
) -> dict[str, Any]:
    data = None
    headers: dict[str, str] = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    request = urllib.request.Request(
        f"{base_url}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise SmokeTestError(
            f"WebDriver {method} {path} failed with {error.code}: {body}",
        ) from error
    except OSError as error:
        raise SmokeTestError(
            f"WebDriver {method} {path} failed: {error}",
        ) from error

    value = json.loads(body) if body else {"value": None}
    if not isinstance(value, dict):
        raise SmokeTestError(f"Unexpected WebDriver response for {path}: {value!r}")
    if isinstance(value.get("value"), dict) and value["value"].get("error"):
        raise SmokeTestError(f"WebDriver error for {path}: {value['value']}")
    return value


def wait_for_webdriver(base_url: str, process: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise SmokeTestError("ChromeDriver exited before becoming ready.")
        try:
            status = json_request(base_url, "GET", "/status", timeout=1)
            if status.get("value", {}).get("ready") is True:
                return
        except (SmokeTestError, json.JSONDecodeError):
            pass
        time.sleep(0.2)
    raise SmokeTestError("ChromeDriver did not become ready.")


def execute(
    base_url: str,
    session_id: str,
    script: str,
) -> Any:
    response = json_request(
        base_url,
        "POST",
        f"/session/{session_id}/execute/sync",
        {"script": script, "args": []},
    )
    return response.get("value")


def cdp_command(
    base_url: str,
    session_id: str,
    command: str,
    params: dict[str, Any] | None = None,
) -> Any:
    response = json_request(
        base_url,
        "POST",
        f"/session/{session_id}/goog/cdp/execute",
        {"cmd": command, "params": params or {}},
    )
    return response.get("value")


def navigate(base_url: str, session_id: str, url: str) -> None:
    json_request(
        base_url,
        "POST",
        f"/session/{session_id}/url",
        {"url": url},
        timeout=15,
    )


def prepare_strict_offline_network(base_url: str, session_id: str) -> None:
    """Remove normal HTTP cache, preserve CacheStorage, then cut the network."""

    cdp_command(base_url, session_id, "Network.enable")
    cdp_command(base_url, session_id, "Network.clearBrowserCache")
    cdp_command(
        base_url,
        session_id,
        "Network.setCacheDisabled",
        {"cacheDisabled": True},
    )
    cdp_command(
        base_url,
        session_id,
        "Network.emulateNetworkConditions",
        {
            "offline": True,
            "latency": 0,
            "downloadThroughput": 0,
            "uploadThroughput": 0,
            "connectionType": "none",
        },
    )


def browser_state(base_url: str, session_id: str) -> dict[str, Any]:
    value = execute(
        base_url,
        session_id,
        """
        return {
          ready: document.documentElement?.dataset.offlineReady === 'true',
          build: document.documentElement?.dataset.offlineBuild || null,
          bootVisible: Boolean(document.getElementById('boot-status')),
          bootFailure: document.documentElement?.dataset.bootFailure || null,
          controller: Boolean(navigator.serviceWorker?.controller),
          flutterView: Boolean(document.querySelector('flutter-view')),
          href: window.location.href,
          title: document.title,
        };
        """,
    )
    return value if isinstance(value, dict) else {}


def browser_resource_urls(base_url: str, session_id: str) -> list[str]:
    value = execute(
        base_url,
        session_id,
        """
        return performance.getEntriesByType('resource')
          .map((entry) => entry.name)
          .filter((name) => typeof name === 'string');
        """,
    )
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise SmokeTestError(f"Unexpected browser resource list: {value!r}")
    return value


def assert_self_contained_startup(
    base_url: str,
    session_id: str,
    *,
    application_origin: str,
) -> None:
    """Reject startup resources outside the app origin, except optional Umami."""

    application_netloc = urlparse(application_origin).netloc
    allowed_external_origins = {"https://cloud.umami.is"}
    forbidden: list[str] = []

    for resource_url in browser_resource_urls(base_url, session_id):
        parsed = urlparse(resource_url)
        if parsed.scheme in {"data", "blob"}:
            continue
        resource_origin = f"{parsed.scheme}://{parsed.netloc}"
        if parsed.netloc == application_netloc:
            continue
        if resource_origin in allowed_external_origins:
            continue
        forbidden.append(resource_url)

    if forbidden:
        raise SmokeTestError(
            "Flutter startup used external runtime resources that are unavailable "
            f"offline: {sorted(set(forbidden))}",
        )


def browser_diagnostics(base_url: str, session_id: str) -> dict[str, Any]:
    value = execute(
        base_url,
        session_id,
        """
        return Promise.all([
          navigator.serviceWorker?.getRegistration?.(),
          window.caches?.keys?.() || Promise.resolve([]),
        ]).then(([registration, cacheKeys]) => ({
          page: {
            ready: document.documentElement?.dataset.offlineReady || null,
            build: document.documentElement?.dataset.offlineBuild || null,
            bootVisible: Boolean(document.getElementById('boot-status')),
            bootFailure: document.documentElement?.dataset.bootFailure || null,
            controller: Boolean(navigator.serviceWorker?.controller),
            href: window.location.href,
            title: document.title,
          },
          worker: registration ? {
            installing: registration.installing?.state || null,
            waiting: registration.waiting?.state || null,
            active: registration.active?.state || null,
            scope: registration.scope,
          } : null,
          resources: performance.getEntriesByType('resource')
            .map((entry) => entry.name),
          cacheKeys,
        }));
        """,
    )
    return value if isinstance(value, dict) else {}


def wait_for_ready_page(
    base_url: str,
    session_id: str,
    *,
    label: str,
    require_controller: bool,
    timeout: float = 90,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last_state: dict[str, Any] = {}
    while time.monotonic() < deadline:
        try:
            last_state = browser_state(base_url, session_id)
        except SmokeTestError:
            time.sleep(0.25)
            continue

        if (
            last_state.get("ready") is True
            and last_state.get("bootVisible") is False
            and last_state.get("flutterView") is True
            and last_state.get("title")
            == "InfusionCalc — kalkulator infuzji, stężenia, przepływu i dawki"
            and (not require_controller or last_state.get("controller") is True)
        ):
            return last_state
        time.sleep(0.5)

    diagnostics = browser_diagnostics(base_url, session_id)
    raise SmokeTestError(
        f"{label} did not become ready. Last state: {last_state}; "
        f"diagnostics: {diagnostics}",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir", nargs="?", default="build/web", type=Path)
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    if not (build_dir / "index.html").is_file():
        raise SystemExit(f"Finalized web build is missing: {build_dir}")

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
            "The offline smoke test requires Chrome/Chromium and ChromeDriver.",
        )

    RecordingHandler.request_log = []
    handler = functools.partial(RecordingHandler, directory=str(build_dir))
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
            wait_for_webdriver(driver_base, driver)
            session_response = json_request(
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
                                    "--window-size=800,1000",
                                    f"--user-data-dir={profile_directory}",
                                ],
                            },
                        },
                    },
                },
                timeout=30,
            )
            session_value = session_response.get("value", {})
            session_id = session_value.get("sessionId")
            if not isinstance(session_id, str) or not session_id:
                raise SmokeTestError(
                    f"ChromeDriver did not return a session ID: {session_response}",
                )

            navigate(driver_base, session_id, origin)
            first_online = wait_for_ready_page(
                driver_base,
                session_id,
                label="First online launch",
                require_controller=True,
            )
            assert_self_contained_startup(
                driver_base,
                session_id,
                application_origin=origin,
            )

            # The complete worker must claim the first page directly. Reopen the
            # same origin without visiting about:blank; otherwise a waiting
            # worker bug would be hidden exactly as it was in the iOS regression.
            navigate(driver_base, session_id, origin)
            controlled_online = wait_for_ready_page(
                driver_base,
                session_id,
                label="Controlled online relaunch",
                require_controller=True,
            )
            assert_self_contained_startup(
                driver_base,
                session_id,
                application_origin=origin,
            )

            # Remove the ordinary browser HTTP cache. Only the versioned service
            # worker CacheStorage is allowed to make the next launch succeed.
            prepare_strict_offline_network(driver_base, session_id)

            server.shutdown()
            server.server_close()
            server_thread.join(timeout=5)
            try:
                connection = http.client.HTTPConnection(
                    "127.0.0.1",
                    server.server_port,
                    timeout=1,
                )
                connection.request("GET", "/")
                connection.getresponse()
            except OSError:
                pass
            else:
                raise SmokeTestError(
                    "The local origin is still reachable; offline mode was not tested.",
                )

            navigate(driver_base, session_id, "about:blank")
            navigate(driver_base, session_id, origin)
            offline = wait_for_ready_page(
                driver_base,
                session_id,
                label="Strict offline launch without HTTP cache",
                require_controller=True,
            )

            if not (
                first_online.get("build")
                == controlled_online.get("build")
                == offline.get("build")
            ):
                raise SmokeTestError(
                    "Online and offline launches used different application builds: "
                    f"{first_online}, {controlled_online}, {offline}",
                )

            print(
                "Self-contained offline PWA smoke test passed for build "
                f"{offline.get('build')} using {Path(chrome).name}; "
                "normal HTTP cache was cleared and disabled.",
            )
        except Exception as error:
            diagnostics: dict[str, Any] = {}
            if session_id is not None:
                try:
                    diagnostics = browser_diagnostics(driver_base, session_id)
                except Exception:
                    diagnostics = {}
            request_tail = RecordingHandler.request_log[-80:]
            raise SystemExit(
                f"{error}\nBrowser diagnostics: {diagnostics}\n"
                f"Origin request log: {request_tail}",
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
