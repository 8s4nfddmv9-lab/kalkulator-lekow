#!/usr/bin/env python3
"""Summarize Lighthouse reports and enforce stable non-performance gates."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CATEGORY_KEYS = (
    "performance",
    "accessibility",
    "best-practices",
    "seo",
)


class LighthouseSummaryError(RuntimeError):
    """Raised when a report is malformed or fails a required gate."""


@dataclass(frozen=True)
class PageScores:
    page: str
    final_url: str
    performance: float
    accessibility: float
    best_practices: float
    seo: float


def _score(categories: dict[str, Any], key: str, path: Path) -> float:
    category = categories.get(key)
    if not isinstance(category, dict):
        raise LighthouseSummaryError(f"{path} is missing Lighthouse category {key!r}.")
    value = category.get("score")
    if not isinstance(value, (int, float)):
        raise LighthouseSummaryError(f"{path} has no numeric score for {key!r}.")
    result = float(value)
    if not 0 <= result <= 1:
        raise LighthouseSummaryError(
            f"{path} has an out-of-range score for {key!r}: {result}.",
        )
    return result


def _read(path: Path) -> PageScores:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LighthouseSummaryError(f"Cannot read Lighthouse report {path}: {error}") from error
    if not isinstance(payload, dict):
        raise LighthouseSummaryError(f"Lighthouse report root must be an object: {path}")
    categories = payload.get("categories")
    if not isinstance(categories, dict):
        raise LighthouseSummaryError(f"Lighthouse report has no categories object: {path}")
    final_url = payload.get("finalUrl")
    if not isinstance(final_url, str) or not final_url:
        raise LighthouseSummaryError(f"Lighthouse report has no finalUrl: {path}")

    return PageScores(
        page=path.stem,
        final_url=final_url,
        performance=_score(categories, "performance", path),
        accessibility=_score(categories, "accessibility", path),
        best_practices=_score(categories, "best-practices", path),
        seo=_score(categories, "seo", path),
    )


def _percent(value: float) -> str:
    return f"{round(value * 100):d}"


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
            f"{_percent(score.accessibility)} | {_percent(score.best_practices)} | "
            f"{_percent(score.seo)} |",
        )
    lines.extend(
        [
            "",
            "Performance is recorded for trend analysis but is not a hard CI gate, "
            "because production network and runner variance can change it independently "
            "of the committed application.",
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
    parser.add_argument("--minimum-seo", type=float, default=0.95)
    args = parser.parse_args()

    try:
        scores = sorted((_read(path) for path in args.reports), key=lambda item: item.page)
        failures: list[str] = []
        for score in scores:
            gates = {
                "accessibility": (score.accessibility, args.minimum_accessibility),
                "best-practices": (score.best_practices, args.minimum_best_practices),
                "seo": (score.seo, args.minimum_seo),
            }
            for category, (actual, minimum) in gates.items():
                if actual < minimum:
                    failures.append(
                        f"{score.page}: {category} {_percent(actual)} < {_percent(minimum)}",
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
                            "seo": args.minimum_seo,
                            "performance": None,
                        },
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
