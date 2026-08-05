#!/usr/bin/env python3
"""Validate the deployed InfusionCalc Pages site after one production release."""

from __future__ import annotations

import argparse
import json
import ssl
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin

SITE_URL = "https://infusioncalc.eu/"
ROBOTS_URL = f"{SITE_URL}robots.txt"
SITEMAP_URL = f"{SITE_URL}sitemap.xml"
SOCIAL_IMAGE_URL = f"{SITE_URL}social/infusioncalc-preview.png"
BUILD_INFO_URL = f"{SITE_URL}pwa-build-info.json"
NOT_FOUND_TITLE = "Nie znaleziono strony — InfusionCalc"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"

CANONICAL_PAGES = {
    SITE_URL: "InfusionCalc — techniczny kalkulator infuzji",
    f"{SITE_URL}about/": "InfusionCalc — technical infusion calculator",
    f"{SITE_URL}privacy/": "Prywatność — InfusionCalc",
    f"{SITE_URL}changelog/": "Changelog — InfusionCalc",
}


class ProductionSiteError(RuntimeError):
    """Raised when the deployed public site violates its release contract."""


@dataclass(frozen=True)
class HttpSnapshot:
    status: int
    final_url: str
    headers: dict[str, str]
    body: bytes


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        request: urllib.request.Request,
        file_pointer: object,
        code: int,
        message: str,
        headers: object,
        new_url: str,
    ) -> None:
        return None


class _HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._inside_title = False
        self._title_parts: list[str] = []
        self.titles: list[str] = []
        self.canonicals: list[str] = []
        self.meta_robots: list[str] = []
        self.body_page: str | None = None

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = {name.lower(): value for name, value in attrs}
        normalized = tag.lower()
        if normalized == "title":
            self._inside_title = True
            self._title_parts = []
        elif normalized == "link":
            rel = (values.get("rel") or "").lower().split()
            href = values.get("href")
            if "canonical" in rel and href:
                self.canonicals.append(href)
        elif normalized == "meta":
            if (values.get("name") or "").lower() == "robots":
                content = values.get("content")
                if content is not None:
                    self.meta_robots.append(content)
        elif normalized == "body":
            self.body_page = values.get("data-page")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title" and self._inside_title:
            self._inside_title = False
            self.titles.append("".join(self._title_parts).strip())

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            self._title_parts.append(data)


def _request(url: str, *, follow_redirects: bool = True) -> HttpSnapshot:
    handlers: list[urllib.request.BaseHandler] = [
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
    ]
    if not follow_redirects:
        handlers.append(_NoRedirect())

    opener = urllib.request.build_opener(*handlers)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "InfusionCalc-production-validator/0.1.4",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    try:
        with opener.open(request, timeout=20) as response:
            body = response.read()
            return HttpSnapshot(
                status=response.status,
                final_url=response.geturl(),
                headers={
                    key.lower(): value for key, value in response.headers.items()
                },
                body=body,
            )
    except urllib.error.HTTPError as error:
        return HttpSnapshot(
            status=error.code,
            final_url=error.geturl(),
            headers={
                key.lower(): value for key, value in error.headers.items()
            },
            body=error.read(),
        )


def _parse_html(snapshot: HttpSnapshot, *, label: str) -> tuple[str, _HeadParser]:
    content_type = snapshot.headers.get("content-type", "")
    if "text/html" not in content_type.lower():
        raise ProductionSiteError(
            f"{label} must be served as HTML; Content-Type={content_type!r}.",
        )
    source = snapshot.body.decode("utf-8", errors="strict")
    parser = _HeadParser()
    parser.feed(source)
    parser.close()
    return source, parser


def _validate_build(expected_build: str) -> None:
    snapshot = _request(BUILD_INFO_URL)
    if snapshot.status != 200:
        raise ProductionSiteError(
            f"pwa-build-info.json returned HTTP {snapshot.status}.",
        )
    try:
        payload = json.loads(snapshot.body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProductionSiteError(
            f"Invalid pwa-build-info.json: {error}",
        ) from error
    if not isinstance(payload, dict) or payload.get("build_id") != expected_build:
        raise ProductionSiteError(
            "The custom domain is not serving the expected deployment yet: "
            f"expected {expected_build!r}, found "
            f"{payload.get('build_id') if isinstance(payload, dict) else payload!r}.",
        )


def _validate_canonical_pages() -> None:
    for url, expected_title in CANONICAL_PAGES.items():
        snapshot = _request(url)
        if snapshot.status != 200 or snapshot.final_url != url:
            raise ProductionSiteError(
                f"{url} must be a direct HTTP 200; got "
                f"{snapshot.status} at {snapshot.final_url}.",
            )
        source, parser = _parse_html(snapshot, label=url)
        if parser.titles != [expected_title]:
            raise ProductionSiteError(
                f"{url} has an unexpected title: {parser.titles!r}.",
            )
        if parser.canonicals != [url]:
            raise ProductionSiteError(
                f"{url} canonical must be itself; found {parser.canonicals!r}.",
            )
        if "noindex" in source.lower():
            raise ProductionSiteError(f"{url} unexpectedly contains noindex.")
        if url != SITE_URL and (
            "flutter_bootstrap.js" in source or "main.dart.js" in source
        ):
            raise ProductionSiteError(
                f"Static page {url} unexpectedly loads the Flutter runtime.",
            )


def _validate_trailing_slashes() -> None:
    for path in ("about", "privacy", "changelog"):
        source_url = f"{SITE_URL}{path}"
        expected_url = f"{source_url}/"
        snapshot = _request(source_url, follow_redirects=False)
        if snapshot.status not in {301, 302, 307, 308}:
            raise ProductionSiteError(
                f"{source_url} must redirect to its slash canonical; "
                f"got HTTP {snapshot.status}.",
            )
        location = snapshot.headers.get("location")
        if not location or urljoin(source_url, location) != expected_url:
            raise ProductionSiteError(
                f"{source_url} redirect target is {location!r}, "
                f"expected {expected_url}.",
            )


def _validate_robots_and_sitemap() -> None:
    robots = _request(ROBOTS_URL)
    if robots.status != 200:
        raise ProductionSiteError(f"robots.txt returned HTTP {robots.status}.")
    expected_robots = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITEMAP_URL}\n"
    )
    if robots.body.decode("utf-8") != expected_robots:
        raise ProductionSiteError("Production robots.txt does not match the contract.")

    sitemap = _request(SITEMAP_URL)
    if sitemap.status != 200:
        raise ProductionSiteError(f"sitemap.xml returned HTTP {sitemap.status}.")
    try:
        root = ElementTree.fromstring(sitemap.body)
    except ElementTree.ParseError as error:
        raise ProductionSiteError(f"Invalid production sitemap.xml: {error}") from error
    locations = {
        (element.text or "").strip()
        for element in root.findall(
            f"{{{SITEMAP_NAMESPACE}}}url/"
            f"{{{SITEMAP_NAMESPACE}}}loc",
        )
    }
    expected_locations = set(CANONICAL_PAGES)
    if locations != expected_locations:
        raise ProductionSiteError(
            "Production sitemap locations are inconsistent: "
            f"expected {sorted(expected_locations)!r}, "
            f"found {sorted(locations)!r}.",
        )


def _validate_social_image() -> None:
    snapshot = _request(SOCIAL_IMAGE_URL)
    if snapshot.status != 200:
        raise ProductionSiteError(
            f"Social preview returned HTTP {snapshot.status}.",
        )
    if not snapshot.body.startswith(PNG_SIGNATURE):
        raise ProductionSiteError("Production social preview is not a PNG.")
    if "image/png" not in snapshot.headers.get("content-type", "").lower():
        raise ProductionSiteError(
            "Production social preview has an invalid Content-Type.",
        )


def _validate_hard_404(expected_build: str) -> None:
    url = f"{SITE_URL}__missing_{expected_build[:12]}/"
    snapshot = _request(url)
    if snapshot.status != 404:
        raise ProductionSiteError(
            f"Unknown production URL must return HTTP 404; got {snapshot.status}.",
        )
    source, parser = _parse_html(snapshot, label="custom 404")
    if parser.titles != [NOT_FOUND_TITLE]:
        raise ProductionSiteError(
            f"Custom 404 title is incorrect: {parser.titles!r}.",
        )
    if parser.meta_robots != ["noindex,follow"]:
        raise ProductionSiteError(
            f"Custom 404 robots metadata is incorrect: {parser.meta_robots!r}.",
        )
    if parser.canonicals:
        raise ProductionSiteError("Custom 404 must not declare a canonical URL.")
    if parser.body_page != "not-found" or 'data-page="not-found"' not in source:
        raise ProductionSiteError("The deployed custom 404 marker is missing.")


def _validate_https_redirect() -> None:
    snapshot = _request("http://infusioncalc.eu/")
    if snapshot.status != 200 or snapshot.final_url != SITE_URL:
        raise ProductionSiteError(
            "HTTP must resolve to the canonical HTTPS root; "
            f"got {snapshot.status} at {snapshot.final_url}.",
        )


def _validate_once(expected_build: str) -> None:
    _validate_build(expected_build)
    _validate_canonical_pages()
    _validate_trailing_slashes()
    _validate_robots_and_sitemap()
    _validate_social_image()
    _validate_hard_404(expected_build)
    _validate_https_redirect()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-build", required=True)
    parser.add_argument("--attempts", type=int, default=30)
    parser.add_argument("--delay", type=float, default=10.0)
    args = parser.parse_args()

    if args.attempts < 1 or args.delay < 0:
        raise SystemExit("attempts must be positive and delay cannot be negative.")

    last_error: Exception | None = None
    for attempt in range(1, args.attempts + 1):
        try:
            _validate_once(args.expected_build)
        except (
            ProductionSiteError,
            OSError,
            UnicodeDecodeError,
            urllib.error.URLError,
        ) as error:
            last_error = error
            if attempt == args.attempts:
                break
            print(
                f"Production validation attempt {attempt}/{args.attempts} "
                f"did not pass yet: {error}",
            )
            time.sleep(args.delay)
        else:
            print(
                "Validated deployed InfusionCalc: expected build, canonical pages, "
                "slash redirects, robots, sitemap, social image, HTTPS and hard 404.",
            )
            return

    raise SystemExit(
        f"Production site validation failed after {args.attempts} attempts: "
        f"{last_error}",
    )


if __name__ == "__main__":
    main()
