#!/usr/bin/env python3
"""Enforce a deterministic line-coverage threshold for a source subtree."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("lcov", type=Path, help="Path to an LCOV info file.")
    parser.add_argument(
        "--prefix",
        default="lib/domain/",
        help="Normalized source-path fragment included in the calculation.",
    )
    parser.add_argument(
        "--minimum",
        type=float,
        default=90.0,
        help="Minimum accepted line coverage percentage.",
    )
    return parser.parse_args()


def normalized(path: str) -> str:
    return path.replace("\\", "/")


def included(source_file: str, prefix: str) -> bool:
    source = normalized(source_file)
    normalized_prefix = normalized(prefix).strip("/") + "/"
    return source.startswith(normalized_prefix) or f"/{normalized_prefix}" in source


def read_coverage(
    lcov_path: Path,
    prefix: str,
) -> dict[str, dict[int, int]]:
    if not lcov_path.is_file():
        raise SystemExit(f"Coverage file does not exist: {lcov_path}")

    records: dict[str, dict[int, int]] = defaultdict(dict)
    current_source: str | None = None

    for raw_line in lcov_path.read_text(encoding="utf-8").splitlines():
        if raw_line.startswith("SF:"):
            candidate = raw_line[3:]
            current_source = candidate if included(candidate, prefix) else None
            continue
        if raw_line.startswith("DA:") and current_source is not None:
            line_data = raw_line[3:].split(",", maxsplit=2)
            line_number = int(line_data[0])
            hit_count = int(line_data[1])
            previous = records[current_source].get(line_number, 0)
            records[current_source][line_number] = max(previous, hit_count)
            continue
        if raw_line == "end_of_record":
            current_source = None

    return dict(records)


def main() -> int:
    args = parse_arguments()
    records = read_coverage(args.lcov, args.prefix)
    if not records:
        raise SystemExit(
            f'No covered source records matched prefix "{args.prefix}".'
        )

    total_lines = sum(len(lines) for lines in records.values())
    covered_lines = sum(
        1 for lines in records.values() for count in lines.values() if count > 0
    )
    percentage = 100.0 * covered_lines / total_lines

    print(
        f"Scoped coverage for {args.prefix}: "
        f"{covered_lines}/{total_lines} lines = {percentage:.2f}%"
    )
    for source_file in sorted(records):
        lines = records[source_file]
        file_covered = sum(count > 0 for count in lines.values())
        file_percentage = 100.0 * file_covered / len(lines)
        print(
            f"  {normalized(source_file)}: "
            f"{file_covered}/{len(lines)} = {file_percentage:.2f}%"
        )

    if percentage + 1e-9 < args.minimum:
        print(
            f"Coverage gate failed: {percentage:.2f}% is below "
            f"the required {args.minimum:.2f}%.",
        )
        return 1

    print(f"Coverage gate passed (minimum {args.minimum:.2f}%).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
