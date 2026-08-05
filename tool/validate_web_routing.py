#!/usr/bin/env python3
"""Validate canonical routing and hard-404 behavior of the InfusionCalc build."""

from __future__ import annotations

import argparse
import xml.etree.ElementTree as ElementTree
from html.parser import HTMLParser
from pathlib import Path

NOT_FOUND_TITLE = "Nie znaleziono strony — InfusionCalc"
NOT_FOUND_DESCRIPTION = (
    "Nie znaleziono żądanej strony InfusionCalc. Wróć do kalkulatora "
    "albo przejdź do informacji o aplikacji."
)
NOT_FOUND_ROBOTS = "noindex,follow"
CANONICAL_PATHS = frozenset({"/", "/about/", "/privacy/", "/changelog/"})
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"


class WebRoutingError(RuntimeError):
    """Raised when the public routing contract is inconsistent."""


class _RoutingHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._inside_title = False
        self._inside_h1 = False
        self._title_parts: list[str] = []
        self._h1_parts: list[str] = []
        self.titles: list[str] = []
        self.h1_documents: list[str] = []
        self.meta: dict[str, list[str]] = {}
        self.links: dict[str, list[str]] = {}
        self.anchor_hrefs: set[str] = set()
        self.html_lang: str | None = None
        self.body_page: str | None = None
        self.json_ld_count = 0

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = {key.lower(): value for key, value in attrs}
        normalized = tag.lower()

        if normalized == "html":
            self.html_lang = values.get("lang")
        elif normalized == "body":
            self.body_page = values.get("data-page")
        elif normalized == "title":
            self._inside_title = True
            self._title_parts = []
        elif normalized == "h1":
            self._inside_h1 = True
            self._h1_parts = []
        elif normalized == "meta":
            key = values.get("name") or values.get("property")
            content = values.get("content")
            if key and content is not None:
                self.meta.setdefault(key.lower(), []).append(content)
        elif normalized == "link":
            rel = values.get("rel")
            href = values.get("href")
            if rel and href:
                for token in rel.lower().split():
                    self.links.setdefault(token, []).append(href)
        elif normalized == "a":
            href = values.get("href")
            if href:
                self.anchor_hrefs.add(href)
        elif (
            normalized == "script"
            and (values.get("type") or "").lower() == "application/ld+json"
        ):
            self.json_ld_count += 1

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        if normalized == "title" and self._inside_title:
            self._inside_title = False
            self.titles.append("".join(self._title_parts).strip())
        elif normalized == "h1" and self._inside_h1:
            self._inside_h1 = False
            self.h1_documents.append("".join(self._h1_parts).strip())

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            self._title_parts.append(data)
        if self._inside_h1:
            self._h1_parts.append(data)


def _parse_html(path: Path) -> tuple[str, _RoutingHtmlParser]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        raise WebRoutingError(f"Cannot read {path}: {error}") from error

    parser = _RoutingHtmlParser()
    try:
        parser.feed(source)
        parser.close()
    except Exception as error:
        raise WebRoutingError(f"Cannot parse {path}: {error}") from error
    return source, parser


def _require_single(
    values: dict[str, list[str]],
    key: str,
    expected: str,
    *,
    label: str,
) -> None:
    actual = values.get(key.lower(), [])
    if actual != [expected]:
        raise WebRoutingError(
            f"{label} must occur exactly once with value {expected!r}; "
            f"found {actual!r}.",
        )


def _validate_not_found(build_dir: Path) -> None:
    path = build_dir / "404.html"
    if not path.is_file():
        raise WebRoutingError("The published root must contain 404.html.")

    source, parser = _parse_html(path)
    if parser.html_lang != "pl":
        raise WebRoutingError('404.html must declare lang="pl".')
    if parser.titles != [NOT_FOUND_TITLE]:
        raise WebRoutingError(
            f"404.html must contain exactly one title {NOT_FOUND_TITLE!r}; "
            f"found {parser.titles!r}.",
        )
    if parser.h1_documents != ["Nie znaleziono strony."]:
        raise WebRoutingError(
            "404.html must contain exactly one explicit not-found h1.",
        )
    if parser.body_page != "not-found":
        raise WebRoutingError(
            '404.html body must expose data-page="not-found" for browser tests.',
        )

    _require_single(
        parser.meta,
        "description",
        NOT_FOUND_DESCRIPTION,
        label="404 meta description",
    )
    _require_single(
        parser.meta,
        "robots",
        NOT_FOUND_ROBOTS,
        label="404 robots metadata",
    )

    if parser.links.get("canonical"):
        raise WebRoutingError("404.html must not declare a canonical URL.")
    if parser.json_ld_count:
        raise WebRoutingError("404.html must not publish structured data.")

    missing_links = sorted(CANONICAL_PATHS - parser.anchor_hrefs)
    if missing_links:
        raise WebRoutingError(
            f"404.html is missing canonical recovery links: {missing_links}.",
        )

    forbidden_runtime = (
        "flutter_bootstrap.js",
        "main.dart.js",
        "pwa_service_worker.js",
    )
    for fragment in forbidden_runtime:
        if fragment in source:
            raise WebRoutingError(
                f"404.html must remain static and must not load {fragment}.",
            )


def _validate_sitemap_excludes_not_found(build_dir: Path) -> None:
    path = build_dir / "sitemap.xml"
    try:
        root = ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError) as error:
        raise WebRoutingError(f"Invalid sitemap.xml: {error}") from error

    locations = {
        (element.text or "").strip()
        for element in root.findall(
            f"{{{SITEMAP_NAMESPACE}}}url/"
            f"{{{SITEMAP_NAMESPACE}}}loc",
        )
    }
    if any(location.endswith("/404.html") for location in locations):
        raise WebRoutingError("404.html must not appear in sitemap.xml.")


def _validate_service_worker(build_dir: Path) -> None:
    path = build_dir / "pwa_service_worker.js"
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        raise WebRoutingError(f"Cannot read {path}: {error}") from error

    required_fragments = (
        "const NOT_FOUND_DOCUMENT = './404.html';",
        "const CANONICAL_DOCUMENTS = new Map([",
        "const CANONICAL_REDIRECTS = new Map([",
        "function canonicalRedirectFor(url)",
        "return CANONICAL_DOCUMENTS.get(relativePath) || null;",
        "Response.redirect(redirectUrl.href, 308)",
        "async function cachedNotFoundResponse(cache)",
        "headers.set('Cache-Control', 'no-store');",
        "status: 404",
        "statusText: 'Not Found'",
        "const notFound = await cachedNotFoundResponse(cache);",
    )
    for fragment in required_fragments:
        if fragment not in source:
            raise WebRoutingError(
                f"Service worker is missing routing behavior: {fragment}",
            )

    forbidden_generic_fallbacks = (
        "relativePath.endsWith('/')",
        "return `./${relativePath}index.html`",
        "const cachedIndex = await cache.match(INDEX_DOCUMENT",
    )
    for fragment in forbidden_generic_fallbacks:
        if fragment in source:
            raise WebRoutingError(
                "Service worker must not turn arbitrary paths into the "
                f"application shell: {fragment}",
            )

    redirect_pairs = {
        "['index.html', '']",
        "['about', 'about/']",
        "['about/index.html', 'about/']",
        "['privacy', 'privacy/']",
        "['privacy/index.html', 'privacy/']",
        "['changelog', 'changelog/']",
        "['changelog/index.html', 'changelog/']",
    }
    missing_pairs = sorted(
        pair for pair in redirect_pairs if pair not in source
    )
    if missing_pairs:
        raise WebRoutingError(
            f"Service worker is missing canonical redirects: {missing_pairs}.",
        )


def validate_web_routing(build_dir: Path) -> None:
    """Validate hard 404, canonical paths and offline navigation behavior."""

    build_dir = build_dir.resolve()
    if not build_dir.is_dir():
        raise WebRoutingError(f"Web build directory does not exist: {build_dir}")

    _validate_not_found(build_dir)
    _validate_sitemap_excludes_not_found(build_dir)
    _validate_service_worker(build_dir)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir", nargs="?", type=Path, default=Path("build/web"))
    args = parser.parse_args()

    try:
        validate_web_routing(args.build_dir)
    except WebRoutingError as error:
        raise SystemExit(str(error)) from error

    print(
        "Validated InfusionCalc routing contract: canonical trailing slashes, "
        "static 404.html and a non-SPA offline not-found response.",
    )


if __name__ == "__main__":
    main()
