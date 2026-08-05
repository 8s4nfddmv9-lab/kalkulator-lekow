#!/usr/bin/env python3
"""Audit the deployed InfusionCalc routes, metadata and HTTP status contract."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ElementTree
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Mapping

DEFAULT_BASE_URL = "https://infusioncalc.eu/"
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
USER_AGENT = "InfusionCalc-production-audit/0.1.4-beta.1"


@dataclass(frozen=True)
class PublicRoute:
    path: str
    title: str
    canonical: str
    language: str


PUBLIC_ROUTES = (
    PublicRoute(
        path="/",
        title="InfusionCalc — kalkulator infuzji, stężenia, przepływu i dawki",
        canonical="https://infusioncalc.eu/",
        language="pl",
    ),
    PublicRoute(
        path="/about/",
        title="InfusionCalc — technical infusion calculator",
        canonical="https://infusioncalc.eu/about/",
        language="en",
    ),
    PublicRoute(
        path="/privacy/",
        title="Prywatność — InfusionCalc",
        canonical="https://infusioncalc.eu/privacy/",
        language="pl",
    ),
    PublicRoute(
        path="/changelog/",
        title="Changelog — InfusionCalc",
        canonical="https://infusioncalc.eu/changelog/",
        language="pl",
    ),
)

EXPECTED_SITEMAP_LOCATIONS = frozenset(route.canonical for route in PUBLIC_ROUTES)
SLASH_REDIRECTS = (
    ("/about", "/about/"),
    ("/privacy", "/privacy/"),
    ("/changelog", "/changelog/"),
)
MISSING_ROUTE = "/__infusioncalc_missing_route_beta_1__/"
MISSING_TITLE = "Nie znaleziono strony — InfusionCalc"


class AuditError(RuntimeError):
    """Raised when the public deployment violates its route contract."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(  # type: ignore[override]
        self,
        req: urllib.request.Request,
        fp: object,
        code: int,
        msg: str,
        headers: Mapping[str, str],
        newurl: str,
    ) -> None:
        return None


@dataclass(frozen=True)
class HttpResult:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes


class _MetadataParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._inside_title = False
        self._title_parts: list[str] = []
        self.html_lang: str | None = None
        self.body_page: str | None = None
        self.meta: dict[str, list[str]] = {}
        self.links: dict[str, list[str]] = {}
        self.anchor_hrefs: set[str] = set()

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = {name.lower(): value for name, value in attrs}
        normalized = tag.lower()
        if normalized == "html":
            self.html_lang = values.get("lang")
        elif normalized == "body":
            self.body_page = values.get("data-page")
        elif normalized == "title":
            self._inside_title = True
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

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._inside_title = False

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            self._title_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self._title_parts).strip()


def _decode_html(result: HttpResult) -> tuple[str, _MetadataParser]:
    try:
        source = result.body.decode("utf-8")
    except UnicodeDecodeError as error:
        raise AuditError(f"Response is not valid UTF-8: {result.url}: {error}") from error
    parser = _MetadataParser()
    parser.feed(source)
    parser.close()
    return source, parser


def _opener(*, follow_redirects: bool) -> urllib.request.OpenerDirector:
    if follow_redirects:
        return urllib.request.build_opener()
    return urllib.request.build_opener(_NoRedirect())


def _request(
    url: str,
    *,
    follow_redirects: bool = False,
    timeout: float = 20,
) -> HttpResult:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with _opener(follow_redirects=follow_redirects).open(
            request,
            timeout=timeout,
        ) as response:
            status = int(response.status)
            headers = {key.lower(): value for key, value in response.headers.items()}
            body = response.read()
            final_url = response.geturl()
    except urllib.error.HTTPError as error:
        status = int(error.code)
        headers = {key.lower(): value for key, value in error.headers.items()}
        body = error.read()
        final_url = error.geturl()
    except OSError as error:
        raise AuditError(f"Cannot fetch {url}: {error}") from error
    return HttpResult(final_url, status, headers, body)


def _join(base_url: str, path: str) -> str:
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def _require_content_type(result: HttpResult, expected: str) -> None:
    actual = result.headers.get("content-type", "")
    if expected not in actual.lower():
        raise AuditError(
            f"{result.url} must use a {expected} content type; found {actual!r}.",
        )


def _audit_public_page(base_url: str, route: PublicRoute) -> dict[str, object]:
    requested_url = _join(base_url, route.path)
    result = _request(requested_url, follow_redirects=False)
    if result.status != 200:
        raise AuditError(f"{requested_url} must return 200; found {result.status}.")
    _require_content_type(result, "text/html")

    source, parser = _decode_html(result)
    if parser.title != route.title:
        raise AuditError(
            f"{route.path} title must be {route.title!r}; found {parser.title!r}.",
        )
    if route.path == "/":
        expected_h1 = f'<h1 class="seo-heading">{route.title}</h1>'
        if expected_h1 not in source:
            raise AuditError("The deployed calculator page is missing its semantic h1.")
    if parser.html_lang != route.language:
        raise AuditError(
            f"{route.path} lang must be {route.language!r}; "
            f"found {parser.html_lang!r}.",
        )
    canonical = parser.links.get("canonical", [])
    if canonical != [route.canonical]:
        raise AuditError(
            f"{route.path} canonical must be {route.canonical!r}; found {canonical!r}.",
        )
    robots = parser.meta.get("robots", [])
    if len(robots) != 1 or "noindex" in robots[0].lower():
        raise AuditError(f"{route.path} must be indexable; found robots={robots!r}.")
    x_robots = result.headers.get("x-robots-tag", "")
    if "noindex" in x_robots.lower():
        raise AuditError(f"{route.path} is blocked by X-Robots-Tag: {x_robots!r}.")
    if route.path != "/" and "flutter_bootstrap.js" in source:
        raise AuditError(f"{route.path} must not depend on the Flutter runtime.")

    return {
        "path": route.path,
        "status": result.status,
        "title": parser.title,
        "canonical": canonical[0],
        "language": parser.html_lang,
        "content_type": result.headers.get("content-type"),
    }


def _audit_slash_redirect(base_url: str, source: str, target: str) -> dict[str, object]:
    requested_url = _join(base_url, source)
    result = _request(requested_url, follow_redirects=False)
    if result.status not in {301, 302, 307, 308}:
        raise AuditError(
            f"{source} must redirect to its trailing-slash URL; "
            f"found status {result.status}.",
        )
    location = result.headers.get("location")
    if not location:
        raise AuditError(f"{source} redirect is missing a Location header.")
    resolved_location = urllib.parse.urljoin(requested_url, location)
    expected = _join(base_url, target)
    if resolved_location != expected:
        raise AuditError(
            f"{source} must redirect to {expected!r}; found {resolved_location!r}.",
        )
    return {
        "path": source,
        "status": result.status,
        "location": resolved_location,
    }


def _audit_not_found(base_url: str) -> dict[str, object]:
    requested_url = _join(base_url, MISSING_ROUTE)
    result = _request(requested_url, follow_redirects=False)
    if result.status != 404:
        raise AuditError(
            f"Unknown routes must return a real 404; {requested_url} returned "
            f"{result.status}.",
        )
    _require_content_type(result, "text/html")
    _, parser = _decode_html(result)
    if parser.title != MISSING_TITLE:
        raise AuditError(
            f"The 404 page title must be {MISSING_TITLE!r}; found {parser.title!r}.",
        )
    robots = parser.meta.get("robots", [])
    if robots != ["noindex,follow"]:
        raise AuditError(f"The 404 page must use noindex,follow; found {robots!r}.")
    if parser.links.get("canonical"):
        raise AuditError("The 404 page must not declare a canonical URL.")
    if parser.body_page != "not-found":
        raise AuditError("The 404 page must expose data-page=\"not-found\".")
    required_links = {"/", "/about/", "/privacy/", "/changelog/"}
    if not required_links.issubset(parser.anchor_hrefs):
        raise AuditError(
            "The 404 page must link to every public destination; "
            f"found {sorted(parser.anchor_hrefs)!r}.",
        )
    return {
        "path": MISSING_ROUTE,
        "status": result.status,
        "title": parser.title,
        "robots": robots[0],
    }


def _audit_robots(base_url: str) -> dict[str, object]:
    result = _request(_join(base_url, "/robots.txt"), follow_redirects=False)
    if result.status != 200:
        raise AuditError(f"robots.txt must return 200; found {result.status}.")
    _require_content_type(result, "text/plain")
    lines = [line.strip() for line in result.body.decode("utf-8").splitlines() if line.strip()]
    expected = [
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://infusioncalc.eu/sitemap.xml",
    ]
    if lines != expected:
        raise AuditError(f"robots.txt must contain {expected!r}; found {lines!r}.")
    return {"path": "/robots.txt", "status": result.status, "lines": lines}


def _audit_sitemap(base_url: str) -> dict[str, object]:
    result = _request(_join(base_url, "/sitemap.xml"), follow_redirects=False)
    if result.status != 200:
        raise AuditError(f"sitemap.xml must return 200; found {result.status}.")
    _require_content_type(result, "xml")
    try:
        root = ElementTree.fromstring(result.body)
    except ElementTree.ParseError as error:
        raise AuditError(f"Invalid production sitemap.xml: {error}") from error
    locations = {
        (element.text or "").strip()
        for element in root.findall(
            f"{{{SITEMAP_NAMESPACE}}}url/{{{SITEMAP_NAMESPACE}}}loc",
        )
    }
    if locations != EXPECTED_SITEMAP_LOCATIONS:
        raise AuditError(
            "Production sitemap locations do not match public canonical pages. "
            f"Expected {sorted(EXPECTED_SITEMAP_LOCATIONS)!r}; "
            f"found {sorted(locations)!r}.",
        )
    return {
        "path": "/sitemap.xml",
        "status": result.status,
        "locations": sorted(locations),
    }


def _audit_http_to_https(base_url: str) -> dict[str, object] | None:
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme != "https" or parsed.hostname not in {"infusioncalc.eu", "www.infusioncalc.eu"}:
        return None
    insecure_url = urllib.parse.urlunparse(
        ("http", parsed.netloc, "/", "", "", ""),
    )
    result = _request(insecure_url, follow_redirects=False)
    if result.status not in {301, 302, 307, 308}:
        raise AuditError(
            f"HTTP must redirect to HTTPS; {insecure_url} returned {result.status}.",
        )
    location = result.headers.get("location", "")
    resolved = urllib.parse.urljoin(insecure_url, location)
    if not resolved.startswith("https://"):
        raise AuditError(f"HTTP redirect must target HTTPS; found {resolved!r}.")
    return {"url": insecure_url, "status": result.status, "location": resolved}


def audit(base_url: str) -> dict[str, object]:
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise AuditError(f"Invalid base URL: {base_url!r}")

    pages = [_audit_public_page(base_url, route) for route in PUBLIC_ROUTES]
    redirects = [
        _audit_slash_redirect(base_url, source, target)
        for source, target in SLASH_REDIRECTS
    ]
    return {
        "base_url": base_url,
        "public_pages": pages,
        "slash_redirects": redirects,
        "not_found": _audit_not_found(base_url),
        "robots": _audit_robots(base_url),
        "sitemap": _audit_sitemap(base_url),
        "http_to_https": _audit_http_to_https(base_url),
        "contract": {
            "public_routes": [asdict(route) for route in PUBLIC_ROUTES],
            "missing_route": MISSING_ROUTE,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--attempts", type=int, default=6)
    parser.add_argument("--retry-delay", type=float, default=10.0)
    args = parser.parse_args()

    if args.attempts < 1:
        raise SystemExit("--attempts must be at least 1.")

    last_error: AuditError | None = None
    report: dict[str, object] | None = None
    for attempt in range(1, args.attempts + 1):
        try:
            report = audit(args.base_url)
            break
        except AuditError as error:
            last_error = error
            if attempt == args.attempts:
                break
            print(
                f"Production audit attempt {attempt}/{args.attempts} failed: {error}. "
                f"Retrying in {args.retry_delay:g}s.",
            )
            time.sleep(args.retry_delay)

    if report is None:
        raise SystemExit(str(last_error or "Production route audit failed."))

    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")

    print(
        "Validated deployed InfusionCalc routes: four indexable pages, trailing-"
        "slash redirects, real noindex 404, robots.txt, sitemap.xml and HTTPS.",
    )
    print(serialized)


if __name__ == "__main__":
    main()
