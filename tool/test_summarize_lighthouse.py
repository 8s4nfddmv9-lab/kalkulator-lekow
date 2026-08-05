#!/usr/bin/env python3
"""Deterministic tests for the production Lighthouse summary helper."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from summarize_lighthouse import (
    LighthouseSummaryError,
    _markdown,
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
                },
            ),
            encoding="utf-8",
        )
        return path

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


if __name__ == "__main__":
    unittest.main()
