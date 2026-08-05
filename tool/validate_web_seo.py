#!/usr/bin/env python3
"""Validate the public SEO contract of the InfusionCalc web build."""

from __future__ import annotations

import argparse
import json
import struct
import xml.etree.ElementTree as ElementTree
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

CANONICAL_URL = "https://infusioncalc.eu/"
SITEMAP_URL = "https://infusioncalc.eu/sitemap.xml"
SOCIAL_IMAGE_URL = (
    "https://infusioncalc.eu/social/infusioncalc-preview.png"
)
SOCIAL_IMAGE_PATH = Path("social/infusioncalc-preview.png")
EXPECTED_TITLE = "InfusionCalc — techniczny kalkulator infuzji"
EXPECTED_DESCRIPTION = (
    "Dwukierunkowy kalkulator stężenia, przepływu i dawki we wlewie, "
    "działający także offline. Bez zaleceń dawkowania."
)
EXPECTED_ROBOTS = "index,follow,max-image-preview:large"
EXPECTED_SITEMAP_LOCATIONS = frozenset({CANONICAL_URL})
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"


class WebSeoError(RuntimeError):
    """Raised when the production web artifact violates its SEO contract."""


class _SeoHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self._inside_title = False
        self._inside_json_ld = False
        self._json_ld_parts: list[str] = []
        self.json_ld_documents: list[str] = []
        self.meta: dict[str, list[str]] = {}
        self.links: dict[str, list[str]] = {}
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
        elif normalized_tag == "script" and self._inside_json_ld:
            self._inside_json_ld = False
            self.json_ld_documents.append("".join(self._json_ld_parts).strip())
            self._json_ld_parts = []

    def handle_data(self, data: str) -> None:
        if self._inside_title:
            self.title_parts.append(data)
        if self._inside_json_ld:
            self._json_ld_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


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


def _as_type_set(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return set(value)
    return set()


def _validate_json_ld(documents: list[str]) -> None:
    if len(documents) != 1:
        raise WebSeoError(
            "The application page must contain exactly one JSON-LD document.",
        )

    try:
        payload = json.loads(documents[0])
    except json.JSONDecodeError as error:
        raise WebSeoError(f"Invalid JSON-LD: {error}") from error

    if not isinstance(payload, dict):
        raise WebSeoError("The JSON-LD root must be an object.")
    if payload.get("@context") != "https://schema.org":
        raise WebSeoError("JSON-LD must use the https://schema.org context.")

    application_types = _as_type_set(payload.get("@type"))
    if not application_types.intersection({"WebApplication", "SoftwareApplication"}):
        raise WebSeoError(
            "JSON-LD must describe a WebApplication or SoftwareApplication.",
        )

    expected_values = {
        "name": "InfusionCalc",
        "url": CANONICAL_URL,
        "description": EXPECTED_DESCRIPTION,
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Any",
        "inLanguage": "pl",
        "license": (
            "https://github.com/8s4nfddmv9-lab/"
            "kalkulator-lekow/blob/main/LICENSE"
        ),
        "sameAs": (
            "https://github.com/8s4nfddmv9-lab/kalkulator-lekow"
        ),
    }
    for key, expected in expected_values.items():
        if payload.get(key) != expected:
            raise WebSeoError(
                f"JSON-LD field {key!r} must be {expected!r}; "
                f"found {payload.get(key)!r}.",
            )

    if payload.get("isAccessibleForFree") is not True:
        raise WebSeoError("JSON-LD must state that InfusionCalc is free.")

    offers = payload.get("offers")
    if not isinstance(offers, dict):
        raise WebSeoError("JSON-LD must contain a free Offer object.")
    if offers.get("@type") != "Offer" or offers.get("price") != "0":
        raise WebSeoError("JSON-LD Offer must have type Offer and price 0.")
    if offers.get("priceCurrency") != "EUR":
        raise WebSeoError("JSON-LD free Offer must use EUR as its currency.")

    feature_list = payload.get("featureList")
    if (
        not isinstance(feature_list, list)
        or len(feature_list) < 4
        or not all(isinstance(item, str) and item.strip() for item in feature_list)
    ):
        raise WebSeoError(
            "JSON-LD featureList must contain at least four non-empty strings.",
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


def _validate_index(index_path: Path) -> None:
    try:
        source = index_path.read_text(encoding="utf-8")
    except OSError as error:
        raise WebSeoError(f"Cannot read {index_path}: {error}") from error

    parser = _SeoHtmlParser()
    try:
        parser.feed(source)
        parser.close()
    except WebSeoError:
        raise
    except Exception as error:
        raise WebSeoError(f"Cannot parse {index_path}: {error}") from error

    if parser.html_lang != "pl":
        raise WebSeoError("The application HTML must declare lang=\"pl\".")
    if parser.title != EXPECTED_TITLE:
        raise WebSeoError(
            f"Page title must be {EXPECTED_TITLE!r}; found {parser.title!r}.",
        )

    _require_single(
        parser.meta,
        "description",
        EXPECTED_DESCRIPTION,
        label="Meta description",
    )
    _require_single(
        parser.meta,
        "robots",
        EXPECTED_ROBOTS,
        label="Robots meta tag",
    )
    _require_single(
        parser.links,
        "canonical",
        CANONICAL_URL,
        label="Canonical link",
    )

    required_open_graph = {
        "og:type": "website",
        "og:site_name": "InfusionCalc",
        "og:locale": "pl_PL",
        "og:title": EXPECTED_TITLE,
        "og:description": EXPECTED_DESCRIPTION,
        "og:url": CANONICAL_URL,
        "og:image": SOCIAL_IMAGE_URL,
        "og:image:type": "image/png",
        "og:image:width": "1200",
        "og:image:height": "630",
        "og:image:alt": EXPECTED_TITLE,
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
        "twitter:title": EXPECTED_TITLE,
        "twitter:description": EXPECTED_DESCRIPTION,
        "twitter:image": SOCIAL_IMAGE_URL,
        "twitter:image:alt": EXPECTED_TITLE,
    }
    for key, expected in required_twitter.items():
        _require_single(
            parser.meta,
            key,
            expected,
            label=f"Twitter card {key}",
        )

    lowered = source.lower()
    if "noindex" in lowered or "nofollow" in lowered:
        raise WebSeoError(
            "Indexable application HTML must not contain noindex or nofollow.",
        )

    _validate_json_ld(parser.json_ld_documents)


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
            "sitemap.xml locations do not match the current canonical pages. "
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


def validate_web_seo(build_dir: Path) -> None:
    """Validate all indexable assets in one finalized web build."""

    build_dir = build_dir.resolve()
    if not build_dir.is_dir():
        raise WebSeoError(f"Web build directory does not exist: {build_dir}")

    required = {
        "index.html": build_dir / "index.html",
        "robots.txt": build_dir / "robots.txt",
        "sitemap.xml": build_dir / "sitemap.xml",
        "social preview": build_dir / SOCIAL_IMAGE_PATH,
    }
    missing = [label for label, path in required.items() if not path.is_file()]
    if missing:
        raise WebSeoError(
            "Missing public SEO build files: " + ", ".join(sorted(missing)),
        )

    _validate_index(required["index.html"])
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
        "Validated InfusionCalc SEO contract: canonical metadata, "
        "social preview, robots.txt, sitemap.xml and JSON-LD.",
    )


if __name__ == "__main__":
    main()
