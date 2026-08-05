#!/usr/bin/env python3
"""Deterministic tests for the production Lighthouse summary helper."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from summarize_lighthouse import (
    EXPECTED_FLUTTER_DEPRECATION,
    LighthouseSummaryError,
    _markdown,
    _quality_failures,
    _read,
)


class LighthouseSummaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.directory = Path(self.temporary_directory.name)

    def _write_report(
        self,
        name: str,
        *,
        performance: float | None = 0.75,
        accessibility: float | None = 1.0,
        best_practices: float | None = 1.0,
        seo: float | None = 1.0,
        deprecations: list[str] | None = None,
    ) -> Path:
        path = self.directory / f"{name}.json"
        path.write_text(
            json.dumps(
                {
                    "finalUrl": f"https://infusioncalc.eu/{name}/",
                    "categories": {
                        "performance": {"score": performance},
                        "accessibility": {"score": accessibility},
                        "best-practices": {"score": best_practices},
                        "seo": {"score": seo},
                    },
                    "audits": {
                        "deprecations": {
                            "score": 1 if not deprecations else 0,
                            "details": {
                                "items": [
                                    {"value": warning}
                                    for warning in (deprecations or [])
                                ],
                            },
                        },
                    },
                },
            ),
            encoding="utf-8",
        )
        return path

    def _failures(self, *scores):
        return _quality_failures(
            list(scores),
            minimum_accessibility=0.90,
            minimum_best_practices=0.90,
            minimum_root_best_practices_with_known_flutter_warning=0.80,
            minimum_seo=0.95,
        )

    def test_missing_performance_is_recorded_as_not_available(self) -> None:
        scores = _read(self._write_report("root", performance=None))

        self.assertIsNone(scores.performance)
        self.assertEqual(scores.accessibility, 1.0)
        self.assertIn("| `root` | n/a | 100 | 100 | 100 |", _markdown([scores]))

    def test_numeric_performance_is_preserved_for_trend_reporting(self) -> None:
        scores = _read(self._write_report("about", performance=0.87))

        self.assertEqual(scores.performance, 0.87)
        self.assertIn("| `about` | 87 | 100 | 100 | 100 |", _markdown([scores]))

    def test_missing_gated_category_remains_a_hard_error(self) -> None:
        report = self._write_report("privacy", accessibility=None)

        with self.assertRaisesRegex(
            LighthouseSummaryError,
            "required category 'accessibility'",
        ):
            _read(report)

    def test_out_of_range_optional_score_is_rejected(self) -> None:
        report = self._write_report("changelog", performance=1.2)

        with self.assertRaisesRegex(
            LighthouseSummaryError,
            "out-of-range score for 'performance'",
        ):
            _read(report)

    def test_exact_root_flutter_deprecation_is_allow_listed(self) -> None:
        scores = _read(
            self._write_report(
                "root",
                best_practices=0.81,
                deprecations=[EXPECTED_FLUTTER_DEPRECATION],
            ),
        )

        self.assertTrue(scores.known_flutter_deprecation)
        self.assertEqual(self._failures(scores), [])
        self.assertIn(EXPECTED_FLUTTER_DEPRECATION, _markdown([scores]))

    def test_unexpected_root_deprecation_is_rejected(self) -> None:
        report = self._write_report(
            "root",
            deprecations=["Some new deprecated API."],
        )

        with self.assertRaisesRegex(
            LighthouseSummaryError,
            "unexpected root deprecation set",
        ):
            _read(report)

    def test_any_static_page_deprecation_is_rejected(self) -> None:
        report = self._write_report(
            "about",
            deprecations=[EXPECTED_FLUTTER_DEPRECATION],
        )

        with self.assertRaisesRegex(
            LighthouseSummaryError,
            "unexpected deprecated APIs",
        ):
            _read(report)

    def test_static_page_keeps_standard_best_practices_floor(self) -> None:
        scores = _read(
            self._write_report(
                "about",
                best_practices=0.81,
            ),
        )

        self.assertEqual(
            self._failures(scores),
            ["about: best-practices 81 < 90"],
        )

    def test_root_allowance_does_not_accept_a_larger_regression(self) -> None:
        scores = _read(
            self._write_report(
                "root",
                best_practices=0.79,
                deprecations=[EXPECTED_FLUTTER_DEPRECATION],
            ),
        )

        self.assertEqual(
            self._failures(scores),
            ["root: best-practices 79 < 80"],
        )


if __name__ == "__main__":
    unittest.main()
