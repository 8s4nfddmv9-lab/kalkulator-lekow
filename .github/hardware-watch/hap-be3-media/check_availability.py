#!/usr/bin/env python3
"""Conservative availability checker for retail product pages.

The checker prefers Product/Offer JSON-LD and falls back to store-specific
status phrases. Ambiguous or conflicting signals are reported as UNKNOWN and
never generate an availability alert.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import sys
import time
import unicodedata
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

AVAILABLE = "available"
UNAVAILABLE = "unavailable"
PREORDER = "preorder"
UNKNOWN = "unknown"

MAX_RESPONSE_BYTES = 4 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 25
USER_AGENT = (
    "HomeZone-HardwareWatch/1.0 "
    "(+https://github.com/8s4nfddmv9-lab/kalkulator-lekow; one request per store per day)"
)


@dataclass(frozen=True)
class Store:
    name: str
    country: str
    region: str
    url: str
    positive_patterns: tuple[str, ...]
    negative_patterns: tuple[str, ...]
    preorder_patterns: tuple[str, ...]


@dataclass
class Result:
    store: str
    country: str
    region: str
    url: str
    status: str
    reason: str
    checked_at: str
    http_status: int | None = None
    price: str | None = None
    currency: str | None = None
    error: str | None = None


class VisibleTextParser(HTMLParser):
    """Extract visible-ish text while skipping scripts, styles, and SVG."""

    SKIP_TAGS = {"script", "style", "noscript", "svg", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self._parts.append(data)

    def text(self) -> str:
        return normalize_whitespace(" ".join(self._parts))


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


def normalize_identifier(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value)).casefold()
    return re.sub(r"[^a-z0-9]+", "", text)


def extract_visible_text(html: str) -> str:
    parser = VisibleTextParser()
    parser.feed(html)
    parser.close()
    return parser.text()


def iter_json_ld(html: str) -> Iterable[Any]:
    pattern = re.compile(
        r"<script\b[^>]*\btype\s*=\s*['\"]application/ld\+json['\"][^>]*>(.*?)</script\s*>",
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(html):
        payload = unescape(match.group(1)).strip()
        if not payload:
            continue
        try:
            yield json.loads(payload)
        except json.JSONDecodeError:
            cleaned = payload.removeprefix("<!--").removesuffix("-->").strip().rstrip(";")
            try:
                yield json.loads(cleaned)
            except json.JSONDecodeError:
                continue


def walk_json(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def has_schema_type(node: dict[str, Any], expected: str) -> bool:
    raw = node.get("@type")
    values = raw if isinstance(raw, list) else [raw]
    return any(str(value).casefold() == expected.casefold() for value in values if value)


def product_matches(node: dict[str, Any], product: dict[str, Any]) -> bool:
    expected_ids = {
        normalize_identifier(product.get("mpn", "")),
        normalize_identifier(product.get("ean", "")),
    }
    expected_ids.discard("")

    observed_ids = {
        normalize_identifier(node.get(key, ""))
        for key in ("mpn", "sku", "productID", "gtin", "gtin13")
    }
    observed_ids.discard("")
    if expected_ids & observed_ids:
        return True

    normalized_name = normalize_identifier(node.get("name", ""))
    terms = [normalize_identifier(term) for term in product.get("name_terms", [])]
    return bool(normalized_name and terms and all(term in normalized_name for term in terms))


def extract_offer_nodes(product_node: dict[str, Any]) -> list[dict[str, Any]]:
    raw = product_node.get("offers")
    if raw is None:
        return []
    if isinstance(raw, dict):
        if has_schema_type(raw, "AggregateOffer"):
            nested = raw.get("offers")
            if isinstance(nested, dict):
                return [nested]
            if isinstance(nested, list):
                return [item for item in nested if isinstance(item, dict)]
        return [raw]
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    return []


def schema_availability_to_status(value: Any) -> str | None:
    if not value:
        return None
    token = str(value).rstrip("/").rsplit("/", 1)[-1].casefold()
    if token in {"instock", "limitedavailability", "onlineonly"}:
        return AVAILABLE
    if token in {"preorder", "presale", "backorder"}:
        return PREORDER
    if token in {"outofstock", "soldout", "discontinued"}:
        return UNAVAILABLE
    return None


def offer_price(offer: dict[str, Any]) -> tuple[str | None, str | None]:
    price = offer.get("price")
    if price is None:
        price = offer.get("lowPrice")
    currency = offer.get("priceCurrency")
    return (str(price) if price is not None else None, str(currency) if currency else None)


def structured_signal(html: str, product: dict[str, Any]) -> tuple[str | None, str, str | None, str | None]:
    matching_products: list[dict[str, Any]] = []
    all_offer_nodes: list[dict[str, Any]] = []

    for document in iter_json_ld(html):
        for node in walk_json(document):
            if has_schema_type(node, "Product") and product_matches(node, product):
                matching_products.append(node)
            if has_schema_type(node, "Offer") or has_schema_type(node, "AggregateOffer"):
                all_offer_nodes.append(node)

    offers: list[dict[str, Any]] = []
    for product_node in matching_products:
        offers.extend(extract_offer_nodes(product_node))

    if not offers and matching_products and len(all_offer_nodes) == 1:
        offers = all_offer_nodes

    signals: list[tuple[str, str | None, str | None]] = []
    for offer in offers:
        status = schema_availability_to_status(offer.get("availability"))
        if status:
            price, currency = offer_price(offer)
            signals.append((status, price, currency))

    if not signals:
        return None, "no matching Product/Offer availability in JSON-LD", None, None

    statuses = {status for status, _, _ in signals}
    if AVAILABLE in statuses and (UNAVAILABLE in statuses or PREORDER in statuses):
        return UNKNOWN, "conflicting availability values in JSON-LD", None, None

    if AVAILABLE in statuses:
        available_prices = [(price, currency) for status, price, currency in signals if status == AVAILABLE]
        price, currency = next(((p, c) for p, c in available_prices if p), (None, None))
        return AVAILABLE, "JSON-LD Offer availability=InStock/LimitedAvailability", price, currency
    if PREORDER in statuses:
        return PREORDER, "JSON-LD Offer availability=PreOrder/BackOrder", None, None
    return UNAVAILABLE, "JSON-LD Offer availability=OutOfStock/Discontinued", None, None


def first_matching_pattern(patterns: Iterable[str], text: str) -> str | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return normalize_whitespace(match.group(0))[:180]
    return None


def text_signal(text: str, store: Store) -> tuple[str | None, str]:
    positive = first_matching_pattern(store.positive_patterns, text)
    negative = first_matching_pattern(store.negative_patterns, text)
    preorder = first_matching_pattern(store.preorder_patterns, text)

    if positive and negative:
        return UNKNOWN, f"conflicting visible text: positive={positive!r}, negative={negative!r}"
    if positive and preorder:
        return UNKNOWN, f"conflicting visible text: positive={positive!r}, preorder={preorder!r}"
    if negative:
        return UNAVAILABLE, f"visible status: {negative}"
    if preorder:
        return PREORDER, f"visible status: {preorder}"
    if positive:
        return AVAILABLE, f"visible status: {positive}"
    return None, "no configured availability phrase found"


def combine_signals(
    structured: tuple[str | None, str, str | None, str | None],
    textual: tuple[str | None, str],
) -> tuple[str, str, str | None, str | None]:
    structured_status, structured_reason, price, currency = structured
    text_status, text_reason = textual

    if structured_status == UNKNOWN or text_status == UNKNOWN:
        return UNKNOWN, f"ambiguous page: {structured_reason}; {text_reason}", None, None
    if structured_status and text_status and structured_status != text_status:
        if {structured_status, text_status} <= {UNAVAILABLE, PREORDER}:
            return PREORDER if PREORDER in {structured_status, text_status} else UNAVAILABLE, (
                f"non-stock signals: {structured_reason}; {text_reason}"
            ), None, None
        return UNKNOWN, f"conflicting signals: {structured_reason}; {text_reason}", None, None
    if structured_status:
        return structured_status, structured_reason, price, currency
    if text_status:
        return text_status, text_reason, None, None
    return UNKNOWN, f"no reliable signal: {structured_reason}; {text_reason}", None, None


def classify_html(html: str, store: Store, product: dict[str, Any]) -> tuple[str, str, str | None, str | None]:
    text = extract_visible_text(html)
    return combine_signals(structured_signal(html, product), text_signal(text, store))


def decode_response(raw: bytes, content_type: str | None) -> str:
    charset = None
    if content_type:
        match = re.search(r"charset=([^;\s]+)", content_type, re.IGNORECASE)
        if match:
            charset = match.group(1).strip('"\'')
    for encoding in (charset, "utf-8", "windows-1250", "iso-8859-1"):
        if not encoding:
            continue
        try:
            return raw.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("utf-8", errors="replace")


def fetch_html(url: str, timeout: int) -> tuple[str, int]:
    request = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.5",
            "Accept-Language": "pl,en;q=0.9,de;q=0.7,cs;q=0.6",
            "Cache-Control": "no-cache",
        },
    )
    context = ssl.create_default_context()
    with urlopen(request, timeout=timeout, context=context) as response:
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError(f"response exceeds {MAX_RESPONSE_BYTES} bytes")
        return decode_response(raw, response.headers.get("Content-Type")), response.status


def check_store(store: Store, product: dict[str, Any], timeout: int, retries: int) -> Result:
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    last_error: Exception | None = None
    http_status: int | None = None

    for attempt in range(retries + 1):
        try:
            html, http_status = fetch_html(store.url, timeout)
            status, reason, price, currency = classify_html(html, store, product)
            return Result(
                store=store.name,
                country=store.country,
                region=store.region,
                url=store.url,
                status=status,
                reason=reason,
                checked_at=checked_at,
                http_status=http_status,
                price=price,
                currency=currency,
            )
        except HTTPError as exc:
            http_status = exc.code
            last_error = exc
            if exc.code not in {408, 425, 429, 500, 502, 503, 504}:
                break
        except (URLError, TimeoutError, ValueError, OSError) as exc:
            last_error = exc
        if attempt < retries:
            time.sleep(1.5 * (attempt + 1))

    return Result(
        store=store.name,
        country=store.country,
        region=store.region,
        url=store.url,
        status=UNKNOWN,
        reason="request failed; availability not inferred",
        checked_at=checked_at,
        http_status=http_status,
        error=f"{type(last_error).__name__}: {last_error}" if last_error else "unknown request error",
    )


def load_config(path: Path) -> tuple[dict[str, Any], list[Store]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    product = data["product"]
    stores: list[Store] = []
    for raw in data["stores"]:
        stores.append(
            Store(
                name=raw["name"],
                country=raw["country"],
                region=raw["region"],
                url=raw["url"],
                positive_patterns=tuple(raw.get("positive_patterns", [])),
                negative_patterns=tuple(raw.get("negative_patterns", [])),
                preorder_patterns=tuple(raw.get("preorder_patterns", [])),
            )
        )
    if not stores:
        raise ValueError("configuration contains no stores")
    return product, stores


def result_fingerprint(results: Iterable[Result]) -> str:
    available = [
        {
            "url": result.url,
            "price": result.price,
            "currency": result.currency,
        }
        for result in results
        if result.status == AVAILABLE
    ]
    encoded = json.dumps(sorted(available, key=lambda item: item["url"]), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16] if available else ""


def build_payload(product: dict[str, Any], results: list[Result], started_at: str) -> dict[str, Any]:
    counts = {status: 0 for status in (AVAILABLE, UNAVAILABLE, PREORDER, UNKNOWN)}
    for result in results:
        counts[result.status] = counts.get(result.status, 0) + 1
    observation = AVAILABLE if counts[AVAILABLE] else (UNKNOWN if counts[UNKNOWN] else UNAVAILABLE)
    return {
        "product": product,
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "observation": observation,
        "fingerprint": result_fingerprint(results),
        "summary": counts,
        "results": [asdict(result) for result in results],
    }


def markdown_report(payload: dict[str, Any]) -> str:
    product = payload["product"]
    counts = payload["summary"]
    lines = [
        f"# Dostępność: {product['name']}",
        "",
        f"Sprawdzenie: `{payload['completed_at']}`  ",
        f"Wynik: **{payload['observation'].upper()}**  ",
        (
            f"Dostępne: {counts[AVAILABLE]} · niedostępne: {counts[UNAVAILABLE]} · "
            f"przedsprzedaż/zamówienie: {counts[PREORDER]} · nieznane: {counts[UNKNOWN]}"
        ),
        "",
        "| Sklep | Kraj | Status | Cena | Sygnał |",
        "|---|---|---|---:|---|",
    ]
    icons = {AVAILABLE: "✅ dostępny", UNAVAILABLE: "❌ brak", PREORDER: "🕓 zamówienie", UNKNOWN: "⚠️ nieznany"}
    for result in payload["results"]:
        price = "—"
        if result.get("price"):
            price = f"{result['price']} {result.get('currency') or ''}".strip()
        reason = str(result.get("reason", "")).replace("|", "\\|")
        lines.append(
            f"| [{result['store']}]({result['url']}) | {result['country']} | "
            f"{icons.get(result['status'], result['status'])} | {price} | {reason} |"
        )
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).with_name("hap_be3_media_stores.json"),
    )
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--delay", type=float, default=0.35, help="polite delay between stores")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    product, stores = load_config(args.config)
    started_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    results: list[Result] = []
    for index, store in enumerate(stores):
        if index and args.delay:
            time.sleep(args.delay)
        result = check_store(store, product, args.timeout, args.retries)
        results.append(result)
        print(f"{result.status:11} {store.country:2} {store.name}: {result.reason}")

    payload = build_payload(product, results, started_at)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown_report(payload), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
