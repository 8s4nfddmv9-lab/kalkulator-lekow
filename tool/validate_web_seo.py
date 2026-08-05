#!/usr/bin/env python3
"""Validate the public SEO contract of the InfusionCalc web build."""

from __future__ import annotations

import argparse
import json
import struct
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

SITE_URL = "https://infusioncalc.eu/"
SITEMAP_URL = f"{SITE_URL}sitemap.xml"
SOCIAL_IMAGE_URL = f"{SITE_URL}social/infusioncalc-preview.png"
SOCIAL_IMAGE_PATH = Path("social/infusioncalc-preview.png")
EXPECTED_ROBOTS = "index,follow,max-image-preview:large"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
REQUIRED_INTERNAL_LINKS = frozenset({"/", "/about/", "/privacy/", "/changelog/"})

ROOT_TITLE = "InfusionCalc — techniczny kalkulator infuzji"
ROOT_DESCRIPTION = (
    "Dwukierunkowy kalkulator stężenia, przepływu i dawki we wlewie, "
    "działający także offline. Bez zaleceń dawkowania."
)


@dataclass(frozen=True)
class StaticPageSpec:
    path: Path
    canonical: str
    title: str
    description: str
    language: str
    locale: str
    schema_type: str
    entity_key: str


STATIC_PAGES = (
    StaticPageSpec(
        path=Path("about/index.html"),
        canonical=f"{SITE_URL}about/",
        title="InfusionCalc — technical infusion calculator",
        description=(
            "A free bidirectional infusion calculator for concentration, flow rate "
            "and dose calculations. Runs in the browser and works offline as a PWA."
        ),
        language="en",
        locale="en_US",
        schema_type="AboutPage",
        entity_key="mainEntity",
    ),
    StaticPageSpec(
        path=Path("privacy/index.html"),
        canonical=f"{SITE_URL}privacy/",
        title="Prywatność — InfusionCalc",
        description=(
            "Jak InfusionCalc przetwarza dane lokalnie, korzysta z minimalnej "
            "analityki Umami i przygotowuje pełny tryb offline PWA."
        ),
        language="pl",
        locale="pl_PL",
        schema_type="WebPage",
        entity_key="about",
    ),
    StaticPageSpec(
        path=Path("changelog/index.html"),
        canonical=f"{SITE_URL}changelog/",
        title="Changelog — InfusionCalc",
        description=(
            "Historia wydań InfusionCalc: zmiany funkcji, stabilności, działania "
            "offline, prywatności i widoczności wyszukiwarkowej."
        ),
        language="pl",
        locale="pl_PL",
        schema_type="WebPage",
        entity_key="about",
    ),
)

EXPECTED_SITEMAP_LOCATIONS = frozenset(
    {SITE_URL, *(page.canonical for page in STATIC_PAGES)},
)


class WebSeoError(RuntimeError):
    """Raised when the production web artifact violates its SEO contract."""


class _SeoHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.h1_documents: list[str] = []
        self._inside_title = False
        self._inside_h1 = False
        self._h1_parts: list[str] = []
        self._inside_json_ld = False
        self._json_ld_parts: list[str] = []
        self.json_ld_documents: list[str] = []
        self.meta: dict[str, list[str]] = {}
        self.links: dict[str, list[str]] = {}
        self.anchor_hrefs: list[str] = []
        self.html_lang: str | None = None

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = {name.lower(): value for name, value in attrs}
        normalized_tag = tag.lower()

        if normalized_tag == "html":
            self.html_lang = values.get("lang")
        elif normalized_tag == "title":
            self._inside_title = True
        elif normalized_tag == "h1":
            if self._inside_h1:
                raise WebSeoError("Nested h1 elements are invalid.")
            self._inside_h1 = True
            self._h1_parts = []
        elif normalized_tag == "meta":
            key = values.get("name") or values.get("property")
            content = values.get("content")
            if key and content is not None:
                self.meta.setdefault(key.lower(), []).append(content)
        elif normalized_tag == "link":
            rel = values.get("rel")
            href = values.get("href")
            if rel and href:
                for token in rel.lower().split():
                    self.links.setdefault(token, []).append(href)
        elif normalized_tag == "a":
            href = values.get("href")
            if href:
                self.anchor_hrefs.append(href)
        elif (
            normalized_tag == "script"
            and (values.get("type") or "").lower() == "application/ld+json"
        ):
            if self._inside_json_ld:
                raise WebSeoError("Nested JSON-LD script elements are invalid.")
            self._inside_json_ld = True
            self._json_ld_parts = []

    def handle_endtag(self, tag: str) -> None:
        normalized_tag = tag.lower()
        if normalized_tag == "title":
            self._inside_title = False
        elif normalized_tag == "h1" and self._inside_h1:
            self._inside_h1 = False
            self.h1_documents.append("".join(self._h1_parts).strip())
            self._h1_parts = []
        elif normalized_tag == "script" and self._inside_json_ld:
            self._inside_json_ld = False
            self.json_ld_documents.append("".join(self._json_ld_parts).strip())
            self._json_ld_parts = []

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            self.title_parts.append(data)
        if self._inside_h1:
            self._h1_parts.append(data)
        if self._inside_json_ld:
            self._json_ld_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


def _parse_html(path: Path) -> tuple[str, _SeoHtmlParser]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        raise WebSeoError(f"Cannot read {path}: {error}") from error

    parser = _SeoHtmlParser()
    try:
        parser.feed(source)
        parser.close()
    except WebSeoError:
        raise
    except Exception as error:
        raise WebSeoError(f"Cannot parse {path}: {error}") from error
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
        raise WebSeoError(
            f"{label} must occur exactly once with value {expected!r}; "
            f"found {actual!r}.",
        )


def _load_single_json_ld(documents: list[str], *, page_label: str) -> dict[str, Any]:
    if len(documents) != 1:
        raise WebSeoError(
            f"{page_label} must contain exactly one JSON-LD document; "
            f"found {len(documents)}.",
        )
    try:
        payload = json.loads(documents[0])
    except json.JSONDecodeError as error:
        raise WebSeoError(f"Invalid JSON-LD in {page_label}: {error}") from error
    if not isinstance(payload, dict):
        raise WebSeoError(f"JSON-LD root in {page_label} must be an object.")
    if payload.get("@context") != "https://schema.org":
        raise WebSeoError(f"JSON-LD in {page_label} must use https://schema.org.")
    return payload


def _validate_social_metadata(
    parser: _SeoHtmlParser,
    *,
    title: str,
    description: str,
    canonical: str,
    locale: str,
) -> None:
    required_open_graph = {
        "og:type": "website",
        "og:site_name": "InfusionCalc",
        "og:locale": locale,
        "og:title": title,
        "og:description": description,
        "og:url": canonical,
        "og:image": SOCIAL_IMAGE_URL,
        "og:image:type": "image/png",
        "og:image:width": "1200",
        "og:image:height": "630",
        "og:image:alt": title,
    }
    for key, expected in required_open_graph.items():
        _require_single(
            parser.meta,
            key,
            expected,
            label=f"Open Graph {key}",
        )

    required_twitter = {
        "twitter:card": "summary_large_image",
        "twitter:title": title,
        "twitter:description": description,
        "twitter:image": SOCIAL_IMAGE_URL,
        "twitter:image:alt": title,
    }
    for key, expected in required_twitter.items():
        _require_single(
            parser.meta,
            key,
            expected,
            label=f"Twitter card {key}",
        )


def _validate_common_page(
    source: str,
    parser: _SeoHtmlParser,
    *,
    page_label: str,
    title: str,
    description: str,
    canonical: str,
    language: str,
    locale: str,
) -> None:
    if parser.html_lang != language:
        raise WebSeoError(
            f"{page_label} must declare lang={language!r}; "
            f"found {parser.html_lang!r}.",
        )
    if parser.title != title:
        raise WebSeoError(
            f"{page_label} title must be {title!r}; found {parser.title!r}.",
        )

    _require_single(parser.meta, "description", description, label="Meta description")
    _require_single(parser.meta, "robots", EXPECTED_ROBOTS, label="Robots meta tag")
    _require_single(parser.links, "canonical", canonical, label="Canonical link")
    _validate_social_metadata(
        parser,
        title=title,
        description=description,
        canonical=canonical,
        locale=locale,
    )

    lowered = source.lower()
    if "noindex" in lowered or "nofollow" in lowered:
        raise WebSeoError(f"{page_label} must not contain noindex or nofollow.")


def _validate_application_json_ld(documents: list[str]) -> None:
    payload = _load_single_json_ld(documents, page_label="application page")
    if payload.get("@type") not in {"WebApplication", "SoftwareApplication"}:
        raise WebSeoError(
            "Application JSON-LD must describe a WebApplication or SoftwareApplication.",
        )

    expected_values = {
        "name": "InfusionCalc",
        "url": SITE_URL,
        "description": ROOT_DESCRIPTION,
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Any",
        "inLanguage": "pl",
        "license": (
            "https://github.com/8s4nfddmv9-lab/"
            "kalkulator-lekow/blob/main/LICENSE"
        ),
        "sameAs": "https://github.com/8s4nfddmv9-lab/kalkulator-lekow",
    }
    for key, expected in expected_values.items():
        if payload.get(key) != expected:
            raise WebSeoError(
                f"Application JSON-LD field {key!r} must be {expected!r}; "
                f"found {payload.get(key)!r}.",
            )

    if payload.get("isAccessibleForFree") is not True:
        raise WebSeoError("Application JSON-LD must state that InfusionCalc is free.")

    offers = payload.get("offers")
    if not isinstance(offers, dict):
        raise WebSeoError("Application JSON-LD must contain a free Offer object.")
    if offers.get("@type") != "Offer" or offers.get("price") != "0":
        raise WebSeoError("Application JSON-LD Offer must have type Offer and price 0.")
    if offers.get("priceCurrency") != "EUR":
        raise WebSeoError("Application JSON-LD free Offer must use EUR.")

    feature_list = payload.get("featureList")
    if (
        not isinstance(feature_list, list)
        or len(feature_list) < 4
        or not all(isinstance(item, str) and item.strip() for item in feature_list)
    ):
        raise WebSeoError(
            "Application JSON-LD featureList must contain at least four strings.",
        )

    forbidden_fields = {
        "medicalSpecialty",
        "recognizingAuthority",
        "clinicalPharmacology",
    }
    unexpected = sorted(forbidden_fields.intersection(payload))
    if unexpected:
        raise WebSeoError(
            "Technical product metadata must not add unsupported clinical fields: "
            f"{unexpected}.",
        )


def _validate_static_json_ld(
    documents: list[str],
    *,
    spec: StaticPageSpec,
) -> None:
    payload = _load_single_json_ld(documents, page_label=spec.path.as_posix())
    expected_values = {
        "@type": spec.schema_type,
        "name": spec.title,
        "url": spec.canonical,
        "description": spec.description,
        "inLanguage": spec.language,
    }
    for key, expected in expected_values.items():
        if payload.get(key) != expected:
            raise WebSeoError(
                f"{spec.path} JSON-LD field {key!r} must be {expected!r}; "
                f"found {payload.get(key)!r}.",
            )

    is_part_of = payload.get("isPartOf")
    if not isinstance(is_part_of, dict):
        raise WebSeoError(f"{spec.path} JSON-LD must contain isPartOf.")
    if is_part_of != {
        "@type": "WebSite",
        "name": "InfusionCalc",
        "url": SITE_URL,
    }:
        raise WebSeoError(f"{spec.path} JSON-LD has an invalid isPartOf object.")

    entity = payload.get(spec.entity_key)
    if not isinstance(entity, dict):
        raise WebSeoError(
            f"{spec.path} JSON-LD must contain {spec.entity_key!r}.",
        )
    if entity.get("@type") != "WebApplication":
        raise WebSeoError(
            f"{spec.path} JSON-LD entity must describe a WebApplication.",
        )
    if entity.get("name") != "InfusionCalc" or entity.get("url") != SITE_URL:
        raise WebSeoError(f"{spec.path} JSON-LD entity must identify InfusionCalc.")


def _validate_index(index_path: Path) -> None:
    source, parser = _parse_html(index_path)
    _validate_common_page(
        source,
        parser,
        page_label="application page",
        title=ROOT_TITLE,
        description=ROOT_DESCRIPTION,
        canonical=SITE_URL,
        language="pl",
        locale="pl_PL",
    )
    _validate_application_json_ld(parser.json_ld_documents)


def _validate_static_page(build_dir: Path, spec: StaticPageSpec) -> None:
    source, parser = _parse_html(build_dir / spec.path)
    _validate_common_page(
        source,
        parser,
        page_label=spec.path.as_posix(),
        title=spec.title,
        description=spec.description,
        canonical=spec.canonical,
        language=spec.language,
        locale=spec.locale,
    )

    if len(parser.h1_documents) != 1 or not parser.h1_documents[0]:
        raise WebSeoError(
            f"{spec.path} must contain exactly one non-empty h1; "
            f"found {parser.h1_documents!r}.",
        )

    lowered = source.lower()
    forbidden_runtime = ("flutter_bootstrap.js", "main.dart.js", "flutter-view")
    found_runtime = [item for item in forbidden_runtime if item in lowered]
    if found_runtime:
        raise WebSeoError(
            f"{spec.path} must remain readable without Flutter runtime: "
            f"{found_runtime}.",
        )

    internal_links = {
        href
        for href in parser.anchor_hrefs
        if href.startswith("/") and not href.startswith("//")
    }
    missing_links = sorted(REQUIRED_INTERNAL_LINKS - internal_links)
    if missing_links:
        raise WebSeoError(
            f"{spec.path} is missing internal navigation links: {missing_links}.",
        )

    _require_single(
        parser.links,
        "stylesheet",
        "/site.css",
        label=f"{spec.path} stylesheet",
    )
    _validate_static_json_ld(parser.json_ld_documents, spec=spec)


def _validate_robots(path: Path) -> None:
    try:
        lines = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except OSError as error:
        raise WebSeoError(f"Cannot read {path}: {error}") from error

    expected = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {SITEMAP_URL}",
    ]
    if lines != expected:
        raise WebSeoError(
            f"robots.txt must contain exactly {expected!r}; found {lines!r}.",
        )


def _validate_sitemap(path: Path) -> None:
    try:
        root = ElementTree.parse(path).getroot()
    except (OSError, ElementTree.ParseError) as error:
        raise WebSeoError(f"Invalid sitemap.xml: {error}") from error

    expected_root = f"{{{SITEMAP_NAMESPACE}}}urlset"
    if root.tag != expected_root:
        raise WebSeoError(
            f"sitemap.xml root must be {expected_root!r}; found {root.tag!r}.",
        )

    locations = {
        (element.text or "").strip()
        for element in root.findall(
            f"{{{SITEMAP_NAMESPACE}}}url/"
            f"{{{SITEMAP_NAMESPACE}}}loc",
        )
    }
    if "" in locations:
        raise WebSeoError("sitemap.xml contains an empty <loc> value.")
    if locations != EXPECTED_SITEMAP_LOCATIONS:
        raise WebSeoError(
            "sitemap.xml locations do not match the canonical pages. "
            f"Expected {sorted(EXPECTED_SITEMAP_LOCATIONS)!r}; "
            f"found {sorted(locations)!r}.",
        )


def _validate_social_image(path: Path) -> None:
    try:
        header = path.read_bytes()[:24]
    except OSError as error:
        raise WebSeoError(f"Cannot read social preview image: {error}") from error

    if len(header) < 24 or header[:8] != PNG_SIGNATURE:
        raise WebSeoError("Social preview must be a valid PNG file.")
    if header[12:16] != b"IHDR":
        raise WebSeoError("Social preview PNG is missing the IHDR chunk.")

    width, height = struct.unpack(">II", header[16:24])
    if (width, height) != (1200, 630):
        raise WebSeoError(
            "Social preview must be 1200×630 pixels; "
            f"found {width}×{height}.",
        )


def _validate_unique_page_metadata(build_dir: Path) -> None:
    documents = [(Path("index.html"), ROOT_TITLE, ROOT_DESCRIPTION)]
    documents.extend((page.path, page.title, page.description) for page in STATIC_PAGES)

    titles = [title for _, title, _ in documents]
    descriptions = [description for _, _, description in documents]
    if len(titles) != len(set(titles)):
        raise WebSeoError("Every indexable page must have a unique title.")
    if len(descriptions) != len(set(descriptions)):
        raise WebSeoError("Every indexable page must have a unique description.")

    css_path = build_dir / "site.css"
    try:
        css = css_path.read_text(encoding="utf-8")
    except OSError as error:
        raise WebSeoError(f"Cannot read shared static-page CSS: {error}") from error
    if len(css.strip()) < 500:
        raise WebSeoError("Shared static-page CSS is unexpectedly small or empty.")


def validate_web_seo(build_dir: Path) -> None:
    """Validate all indexable assets in one finalized web build."""

    build_dir = build_dir.resolve()
    if not build_dir.is_dir():
        raise WebSeoError(f"Web build directory does not exist: {build_dir}")

    required = {
        "index.html": build_dir / "index.html",
        "robots.txt": build_dir / "robots.txt",
        "sitemap.xml": build_dir / "sitemap.xml",
        "site.css": build_dir / "site.css",
        "social preview": build_dir / SOCIAL_IMAGE_PATH,
        **{
            page.path.as_posix(): build_dir / page.path
            for page in STATIC_PAGES
        },
    }
    missing = [label for label, path in required.items() if not path.is_file()]
    if missing:
        raise WebSeoError(
            "Missing public SEO build files: " + ", ".join(sorted(missing)),
        )

    _validate_index(required["index.html"])
    for spec in STATIC_PAGES:
        _validate_static_page(build_dir, spec)
    _validate_unique_page_metadata(build_dir)
    _validate_robots(required["robots.txt"])
    _validate_sitemap(required["sitemap.xml"])
    _validate_social_image(required["social preview"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir", nargs="?", default="build/web", type=Path)
    args = parser.parse_args()

    try:
        validate_web_seo(args.build_dir)
    except WebSeoError as error:
        raise SystemExit(str(error)) from error

    print(
        "Validated InfusionCalc SEO contract: application page, three static "
        "information pages, canonical metadata, internal navigation, social "
        "preview, robots.txt, sitemap.xml and JSON-LD.",
    )


if __name__ == "__main__":
    main()
