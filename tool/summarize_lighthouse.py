#!/usr/bin/env python3
"""Summarize Lighthouse reports and enforce stable non-performance gates."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

EXPECTED_FLUTTER_DEPRECATION = (
    "Intl.v8BreakIterator is deprecated. Please use Intl.Segmenter instead."
)


class LighthouseSummaryError(RuntimeError):
    """Raised when a report is malformed or fails a required gate."""


@dataclass(frozen=True)
class PageScores:
    page: str
    final_url: str
    performance: float | None
    accessibility: float
    best_practices: float
    seo: float
    known_flutter_deprecation: bool


def _optional_score(
    categories: dict[str, Any],
    key: str,
    path: Path,
) -> float | None:
    category = categories.get(key)
    if not isinstance(category, dict):
        return None

    value = category.get("score")
    if value is None:
        return None
    if not isinstance(value, (int, float)):
        raise LighthouseSummaryError(
            f"{path} has a non-numeric score for {key!r}: {value!r}.",
        )

    result = float(value)
    if not 0 <= result <= 1:
        raise LighthouseSummaryError(
            f"{path} has an out-of-range score for {key!r}: {result}.",
        )
    return result


def _required_score(
    categories: dict[str, Any],
    key: str,
    path: Path,
) -> float:
    result = _optional_score(categories, key, path)
    if result is None:
        raise LighthouseSummaryError(
            f"{path} has no numeric score for required category {key!r}.",
        )
    return result


def _deprecation_warnings(
    payload: dict[str, Any],
    *,
    path: Path,
) -> list[str]:
    audits = payload.get("audits")
    if not isinstance(audits, dict):
        raise LighthouseSummaryError(
            f"Lighthouse report has no audits object: {path}",
        )

    audit = audits.get("deprecations")
    if not isinstance(audit, dict):
        raise LighthouseSummaryError(
            f"Lighthouse report has no deprecations audit: {path}",
        )

    details = audit.get("details")
    if details is None:
        return []
    if not isinstance(details, dict):
        raise LighthouseSummaryError(
            f"Lighthouse deprecations details are malformed: {path}",
        )

    items = details.get("items", [])
    if not isinstance(items, list):
        raise LighthouseSummaryError(
            f"Lighthouse deprecations items are malformed: {path}",
        )

    warnings: list[str] = []
    for item in items:
        value = item.get("value") if isinstance(item, dict) else None
        if not isinstance(value, str) or not value.strip():
            raise LighthouseSummaryError(
                f"Lighthouse report contains a malformed deprecation: {path}",
            )
        warnings.append(value.strip())
    return warnings


def _validate_deprecations(
    payload: dict[str, Any],
    *,
    page: str,
    path: Path,
) -> bool:
    warnings = _deprecation_warnings(payload, path=path)

    if page != "root":
        if warnings:
            raise LighthouseSummaryError(
                f"{path} contains unexpected deprecated APIs: {warnings!r}.",
            )
        return False

    if not warnings:
        return False
    if warnings != [EXPECTED_FLUTTER_DEPRECATION]:
        raise LighthouseSummaryError(
            f"{path} contains an unexpected root deprecation set: {warnings!r}.",
        )
    return True


def _read(path: Path) -> PageScores:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LighthouseSummaryError(
            f"Cannot read Lighthouse report {path}: {error}",
        ) from error
    if not isinstance(payload, dict):
        raise LighthouseSummaryError(
            f"Lighthouse report root must be an object: {path}",
        )

    categories = payload.get("categories")
    if not isinstance(categories, dict):
        raise LighthouseSummaryError(
            f"Lighthouse report has no categories object: {path}",
        )

    final_url = payload.get("finalUrl")
    if not isinstance(final_url, str) or not final_url:
        raise LighthouseSummaryError(
            f"Lighthouse report has no finalUrl: {path}",
        )

    page = path.stem
    return PageScores(
        page=page,
        final_url=final_url,
        performance=_optional_score(categories, "performance", path),
        accessibility=_required_score(categories, "accessibility", path),
        best_practices=_required_score(categories, "best-practices", path),
        seo=_required_score(categories, "seo", path),
        known_flutter_deprecation=_validate_deprecations(
            payload,
            page=page,
            path=path,
        ),
    )


def _percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{round(value * 100):d}"


def _best_practices_minimum(
    score: PageScores,
    *,
    standard_minimum: float,
    root_flutter_minimum: float,
) -> float:
    if score.page == "root" and score.known_flutter_deprecation:
        return root_flutter_minimum
    return standard_minimum


def _quality_failures(
    scores: list[PageScores],
    *,
    minimum_accessibility: float,
    minimum_best_practices: float,
    minimum_root_best_practices_with_known_flutter_warning: float,
    minimum_seo: float,
) -> list[str]:
    failures: list[str] = []
    for score in scores:
        gates = {
            "accessibility": (
                score.accessibility,
                minimum_accessibility,
            ),
            "best-practices": (
                score.best_practices,
                _best_practices_minimum(
                    score,
                    standard_minimum=minimum_best_practices,
                    root_flutter_minimum=(
                        minimum_root_best_practices_with_known_flutter_warning
                    ),
                ),
            ),
            "seo": (score.seo, minimum_seo),
        }
        for category, (actual, minimum) in gates.items():
            if actual < minimum:
                failures.append(
                    f"{score.page}: {category} "
                    f"{_percent(actual)} < {_percent(minimum)}",
                )
    return failures


def _markdown(scores: list[PageScores]) -> str:
    lines = [
        "## Lighthouse — deployed InfusionCalc",
        "",
        "| Page | Performance | Accessibility | Best Practices | SEO |",
        "|---|---:|---:|---:|---:|",
    ]
    for score in scores:
        lines.append(
            "| "
            f"`{score.page}` | {_percent(score.performance)} | "
            f"{_percent(score.accessibility)} | "
            f"{_percent(score.best_practices)} | "
            f"{_percent(score.seo)} |",
        )
    lines.extend(
        [
            "",
            "Performance is recorded for trend analysis but is not a hard CI gate, "
            "because production network, renderer timing and runner variance can "
            "change it independently of the committed application. A missing "
            "performance score is recorded as `n/a`.",
            "",
        ],
    )

    flutter_pages = [
        score.page for score in scores if score.known_flutter_deprecation
    ]
    if flutter_pages:
        lines.extend(
            [
                "The Flutter calculator emitted exactly one allow-listed engine "
                f"warning on {', '.join(sorted(flutter_pages))}: "
                f"`{EXPECTED_FLUTTER_DEPRECATION}`. The reduced root "
                "best-practices floor applies only when this exact warning is the "
                "complete deprecation set. Every additional or different warning, "
                "and every warning on a static page, fails the audit.",
                "",
            ],
        )

    lines.extend(
        [
            "Accessibility, best practices and SEO remain mandatory numeric gates.",
            "",
        ],
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--minimum-accessibility", type=float, default=0.90)
    parser.add_argument("--minimum-best-practices", type=float, default=0.90)
    parser.add_argument(
        "--minimum-root-best-practices-with-known-flutter-warning",
        type=float,
        default=0.80,
    )
    parser.add_argument("--minimum-seo", type=float, default=0.95)
    args = parser.parse_args()

    try:
        scores = sorted(
            (_read(path) for path in args.reports),
            key=lambda item: item.page,
        )
        failures = _quality_failures(
            scores,
            minimum_accessibility=args.minimum_accessibility,
            minimum_best_practices=args.minimum_best_practices,
            minimum_root_best_practices_with_known_flutter_warning=(
                args.minimum_root_best_practices_with_known_flutter_warning
            ),
            minimum_seo=args.minimum_seo,
        )

        markdown = _markdown(scores)
        if args.markdown_output:
            args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
            args.markdown_output.write_text(markdown, encoding="utf-8")
        if args.json_output:
            args.json_output.parent.mkdir(parents=True, exist_ok=True)
            args.json_output.write_text(
                json.dumps(
                    {
                        "scores": [asdict(score) for score in scores],
                        "gates": {
                            "accessibility": args.minimum_accessibility,
                            "best_practices": args.minimum_best_practices,
                            "root_best_practices_with_known_flutter_warning": (
                                args.minimum_root_best_practices_with_known_flutter_warning
                            ),
                            "seo": args.minimum_seo,
                            "performance": None,
                        },
                        "allow_listed_flutter_deprecation": (
                            EXPECTED_FLUTTER_DEPRECATION
                        ),
                        "failures": failures,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

        print(markdown)
        if failures:
            raise LighthouseSummaryError(
                "Lighthouse quality gates failed: " + "; ".join(failures),
            )
    except LighthouseSummaryError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
