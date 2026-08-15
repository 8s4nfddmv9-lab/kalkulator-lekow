#!/usr/bin/env python3
"""Exercise the public route contract against a local GitHub Pages analogue."""

from __future__ import annotations

import argparse
import functools
import http.server
import threading
from pathlib import Path

from audit_production_routes import audit


def _validate_runtime_language_contract(web_dir: Path) -> None:
    source = (web_dir / "index.html").read_text(encoding="utf-8")
    required_fragments = (
        "const preferenceKeys = [",
        "'infusioncalc.presentation.v1.language'",
        "flutter.infusioncalc.presentation.v1.language",
        "value = JSON.parse(value)",
        "window.infusionCalcSetLanguage",
        "document.documentElement.lang = language",
        "Starting InfusionCalc…",
        "InfusionCalc could not be started.",
        "This installation does not have a complete offline version.",
        "bootStatus.dataset.failure = 'true'",
    )
    missing = [fragment for fragment in required_fragments if fragment not in source]
    if missing:
        raise SystemExit(
            "Root page is missing its persisted PL/EN boot contract: "
            f"{missing!r}",
        )


class GitHubPagesLikeHandler(http.server.SimpleHTTPRequestHandler):
    """Serve directory indexes and the repository's custom 404 document."""

    def log_message(self, format: str, *args: object) -> None:
        return

    def send_error(
        self,
        code: int,
        message: str | None = None,
        explain: str | None = None,
    ) -> None:
        if code != 404:
            super().send_error(code, message, explain)
            return

        root = Path(self.directory or ".")
        not_found = root / "404.html"
        if not not_found.is_file():
            super().send_error(code, message, explain)
            return

        body = not_found.read_bytes()
        self.send_response(404, "Not Found")
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("web_dir", nargs="?", default="web", type=Path)
    args = parser.parse_args()

    web_dir = args.web_dir.resolve()
    if not (web_dir / "index.html").is_file():
        raise SystemExit(f"Public web directory is missing index.html: {web_dir}")
    if not (web_dir / "404.html").is_file():
        raise SystemExit(f"Public web directory is missing 404.html: {web_dir}")
    _validate_runtime_language_contract(web_dir)

    handler = functools.partial(GitHubPagesLikeHandler, directory=str(web_dir))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        base_url = f"http://127.0.0.1:{server.server_port}/"
        report = audit(base_url)
        if len(report.get("public_pages", [])) != 4:
            raise SystemExit("Local route audit did not validate four public pages.")
        if report.get("not_found", {}).get("status") != 404:
            raise SystemExit("Local route audit did not preserve a real 404 status.")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    print(
        "Local GitHub Pages route contract passed: canonical pages, trailing "
        "slashes, robots, sitemap and custom noindex 404.",
    )


if __name__ == "__main__":
    main()
