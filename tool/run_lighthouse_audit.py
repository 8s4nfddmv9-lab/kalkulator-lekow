#!/usr/bin/env python3
"""Run pinned Lighthouse audits for every canonical InfusionCalc page."""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import os
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Any

from smoke_test_public_routes import GitHubPagesLikeHandler

LIGHTHOUSE_VERSION = "13.3.0"
PAGE_PATHS = {
    "calculator": "/",
    "about": "/about/",
    "privacy": "/privacy/",
    "changelog": "/changelog/",
}
PROFILES = ("mobile", "desktop")
CATEGORY_KEYS = ("performance", "accessibility", "best-practices", "seo")

ROOT_THRESHOLDS = {
    "mobile": {
        "performance": 0.35,
        "accessibility": 0.80,
        "best-practices": 0.90,
        "seo": 0.95,
    },
    "desktop": {
        "performance": 0.50,
        "accessibility": 0.80,
        "best-practices": 0.90,
        "seo": 0.95,
    },
}
STATIC_THRESHOLDS = {
    "mobile": {
        "performance": 0.70,
        "accessibility": 0.90,
        "best-practices": 0.90,
        "seo": 0.95,
    },
    "desktop": {
        "performance": 0.80,
        "accessibility": 0.90,
        "best-practices": 0.90,
        "seo": 0.95,
    },
}


class LighthouseAuditError(RuntimeError):
    """Raised when Lighthouse cannot run or a quality floor is violated."""


def _find_chrome() -> str:
    chrome = next(
        (
            path
            for name in (
                "google-chrome",
                "google-chrome-stable",
                "chromium",
                "chromium-browser",
            )
            if (path := shutil.which(name))
        ),
        None,
    )
    if chrome is None:
        raise LighthouseAuditError(
            "Lighthouse requires Chrome or Chromium on PATH.",
        )
    return chrome


def _run_lighthouse(
    *,
    url: str,
    profile: str,
    output_path: Path,
    chrome: str,
) -> dict[str, Any]:
    command = [
        "npx",
        "--yes",
        f"lighthouse@{LIGHTHOUSE_VERSION}",
        url,
        "--quiet",
        "--output=json",
        f"--output-path={output_path}",
        "--only-categories=performance,accessibility,best-practices,seo",
        "--max-wait-for-load=90000",
        "--blocked-url-patterns=https://cloud.umami.is/*",
        (
            "--chrome-flags=--headless=new --no-sandbox "
            "--disable-dev-shm-usage --ignore-certificate-errors"
        ),
    ]
    if profile == "desktop":
        command.append("--preset=desktop")

    environment = os.environ.copy()
    environment["CHROME_PATH"] = chrome
    completed = subprocess.run(
        command,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=environment,
        timeout=180,
    )
    if completed.returncode != 0:
        raise LighthouseAuditError(
            f"Lighthouse failed for {profile} {url}:\n{completed.stdout}",
        )

    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise LighthouseAuditError(
            f"Cannot read Lighthouse result {output_path}: {error}",
        ) from error
    if not isinstance(payload, dict):
        raise LighthouseAuditError(
            f"Lighthouse result {output_path} is not a JSON object.",
        )
    return payload


def _scores(payload: dict[str, Any], *, label: str) -> dict[str, float]:
    categories = payload.get("categories")
    if not isinstance(categories, dict):
        raise LighthouseAuditError(f"{label} has no Lighthouse categories.")

    scores: dict[str, float] = {}
    for key in CATEGORY_KEYS:
        category = categories.get(key)
        score = category.get("score") if isinstance(category, dict) else None
        if not isinstance(score, (int, float)):
            raise LighthouseAuditError(
                f"{label} category {key!r} has no numeric score.",
            )
        scores[key] = float(score)
    return scores


def _validate_specific_audits(
    payload: dict[str, Any],
    *,
    page_name: str,
    profile: str,
) -> None:
    audits = payload.get("audits")
    if not isinstance(audits, dict):
        raise LighthouseAuditError(
            f"{page_name}/{profile} has no Lighthouse audit map.",
        )

    required_passes = (
        "document-title",
        "meta-description",
        "http-status-code",
        "is-crawlable",
        "crawlable-anchors",
    )
    for audit_id in required_passes:
        audit = audits.get(audit_id)
        score = audit.get("score") if isinstance(audit, dict) else None
        if score != 1:
            title = audit.get("title") if isinstance(audit, dict) else audit_id
            display = (
                audit.get("displayValue") if isinstance(audit, dict) else None
            )
            raise LighthouseAuditError(
                f"{page_name}/{profile} failed {audit_id} ({title}): {display}",
            )


def _thresholds(page_name: str, profile: str) -> dict[str, float]:
    if page_name == "calculator":
        return ROOT_THRESHOLDS[profile]
    return STATIC_THRESHOLDS[profile]


def _format_score(score: float) -> str:
    return str(round(score * 100))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir", nargs="?", type=Path, default=Path("build/web"))
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("lighthouse-reports"),
    )
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    if not (build_dir / "index.html").is_file():
        raise SystemExit(f"Web build does not exist: {build_dir}")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    chrome = _find_chrome()
    if shutil.which("npx") is None:
        raise SystemExit("Lighthouse audit requires npx on PATH.")

    GitHubPagesLikeHandler.request_log = []
    handler = functools.partial(
        GitHubPagesLikeHandler,
        directory=str(build_dir),
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"

    rows: list[tuple[str, str, dict[str, float]]] = []
    failures: list[str] = []
    try:
        for page_name, path in PAGE_PATHS.items():
            for profile in PROFILES:
                output_path = output_dir / f"{page_name}-{profile}.json"
                payload = _run_lighthouse(
                    url=f"{origin}{path}",
                    profile=profile,
                    output_path=output_path,
                    chrome=chrome,
                )
                scores = _scores(
                    payload,
                    label=f"{page_name}/{profile}",
                )
                _validate_specific_audits(
                    payload,
                    page_name=page_name,
                    profile=profile,
                )
                rows.append((page_name, profile, scores))

                for category, minimum in _thresholds(
                    page_name,
                    profile,
                ).items():
                    actual = scores[category]
                    if actual + 1e-9 < minimum:
                        failures.append(
                            f"{page_name}/{profile} {category}: "
                            f"{_format_score(actual)} < "
                            f"{_format_score(minimum)}",
                        )
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)

    summary_lines = [
        "# InfusionCalc Lighthouse baseline",
        "",
        f"Pinned Lighthouse: `{LIGHTHOUSE_VERSION}`",
        "",
        "| Page | Profile | Performance | Accessibility | Best Practices | SEO |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for page_name, profile, scores in rows:
        summary_lines.append(
            "| "
            + " | ".join(
                (
                    page_name,
                    profile,
                    _format_score(scores["performance"]),
                    _format_score(scores["accessibility"]),
                    _format_score(scores["best-practices"]),
                    _format_score(scores["seo"]),
                ),
            )
            + " |",
        )
    summary_lines.extend(
        [
            "",
            "The calculator has deliberately lower initial performance and "
            "accessibility floors than the static pages. This stage records a "
            "repeatable baseline; later releases may tighten the thresholds "
            "without hiding regressions.",
            "",
        ],
    )
    if failures:
        summary_lines.append("## Failed quality floors")
        summary_lines.append("")
        summary_lines.extend(f"- {failure}" for failure in failures)

    summary_path = output_dir / "summary.md"
    summary_path.write_text(
        "\n".join(summary_lines) + "\n",
        encoding="utf-8",
    )
    print(summary_path.read_text(encoding="utf-8"))

    if failures:
        raise SystemExit(
            "Lighthouse quality floors failed:\n- " + "\n- ".join(failures),
        )


if __name__ == "__main__":
    main()
