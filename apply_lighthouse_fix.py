#!/usr/bin/env python3
"""Apply the reviewed Lighthouse baseline correction for 0.1.4-beta.1."""

from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"{path}: expected one patch anchor, found {count}:\n{old}",
        )
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


def patch_css() -> None:
    path = Path("web/site.css")
    replace_once(
        path,
        ".hero__icon {\n"
        "  width: clamp(96px, 15vw, 150px);\n"
        "  border-radius: 30px;",
        ".hero__icon {\n"
        "  width: clamp(96px, 15vw, 150px);\n"
        "  height: auto;\n"
        "  aspect-ratio: 1;\n"
        "  border-radius: 30px;",
    )


def patch_lighthouse_runner() -> None:
    path = Path("tool/run_lighthouse_audit.py")
    replace_once(
        path,
        'CATEGORY_KEYS = ("performance", "accessibility", "best-practices", "seo")\n\n'
        "ROOT_THRESHOLDS = {",
        'CATEGORY_KEYS = ("performance", "accessibility", "best-practices", "seo")\n'
        "EXPECTED_FLUTTER_DEPRECATION = (\n"
        '    "Intl.v8BreakIterator is deprecated. Please use Intl.Segmenter instead."\n'
        ")\n\n"
        "ROOT_THRESHOLDS = {",
    )
    source = path.read_text(encoding="utf-8")
    source = source.replace(
        '        "best-practices": 0.90,\n',
        '        "best-practices": 0.80,\n',
        2,
    )
    path.write_text(source, encoding="utf-8")

    replace_once(
        path,
        "\ndef _thresholds(page_name: str, profile: str) -> dict[str, float]:\n",
        '''\ndef _deprecation_warnings(
    payload: dict[str, Any],
    *,
    label: str,
) -> list[str]:
    audits = payload.get("audits")
    if not isinstance(audits, dict):
        raise LighthouseAuditError(f"{label} has no Lighthouse audit map.")

    audit = audits.get("deprecations")
    if not isinstance(audit, dict):
        raise LighthouseAuditError(f"{label} has no deprecations audit.")

    details = audit.get("details")
    if details is None:
        return []
    if not isinstance(details, dict):
        raise LighthouseAuditError(
            f"{label} has malformed deprecations details.",
        )

    items = details.get("items", [])
    if not isinstance(items, list):
        raise LighthouseAuditError(
            f"{label} has malformed deprecations items.",
        )

    warnings: list[str] = []
    for item in items:
        value = item.get("value") if isinstance(item, dict) else None
        if not isinstance(value, str) or not value.strip():
            raise LighthouseAuditError(
                f"{label} contains a malformed deprecation warning: {item!r}.",
            )
        warnings.append(value.strip())
    return warnings


def _validate_deprecations(
    payload: dict[str, Any],
    *,
    page_name: str,
    profile: str,
) -> bool:
    label = f"{page_name}/{profile}"
    warnings = _deprecation_warnings(payload, label=label)

    if page_name != "calculator":
        if warnings:
            raise LighthouseAuditError(
                f"{label} contains unexpected deprecated APIs: {warnings!r}.",
            )
        return False

    if not warnings:
        return False
    if warnings != [EXPECTED_FLUTTER_DEPRECATION]:
        raise LighthouseAuditError(
            f"{label} contains an unexpected deprecation set: {warnings!r}.",
        )
    return True


def _thresholds(page_name: str, profile: str) -> dict[str, float]:
''',
    )
    replace_once(
        path,
        "    rows: list[tuple[str, str, dict[str, float]]] = []\n"
        "    failures: list[str] = []",
        "    rows: list[tuple[str, str, dict[str, float]]] = []\n"
        "    known_flutter_warning_profiles: list[str] = []\n"
        "    failures: list[str] = []",
    )
    replace_once(
        path,
        "                _validate_specific_audits(\n"
        "                    payload,\n"
        "                    page_name=page_name,\n"
        "                    profile=profile,\n"
        "                )\n"
        "                rows.append((page_name, profile, scores))",
        "                _validate_specific_audits(\n"
        "                    payload,\n"
        "                    page_name=page_name,\n"
        "                    profile=profile,\n"
        "                )\n"
        "                if _validate_deprecations(\n"
        "                    payload,\n"
        "                    page_name=page_name,\n"
        "                    profile=profile,\n"
        "                ):\n"
        "                    known_flutter_warning_profiles.append(profile)\n"
        "                rows.append((page_name, profile, scores))",
    )
    replace_once(
        path,
        '            "The calculator has deliberately lower initial performance and "\n'
        '            "accessibility floors than the static pages. This stage records a "\n'
        '            "repeatable baseline; later releases may tighten the thresholds "\n'
        '            "without hiding regressions.",\n'
        '            "",\n'
        "        ],\n"
        "    )\n"
        "    if failures:",
        '            "The calculator has deliberately lower initial performance, "\n'
        '            "accessibility and best-practices floors than the static pages. "\n'
        '            "This stage records a repeatable baseline; later releases may "\n'
        '            "tighten the thresholds without hiding regressions.",\n'
        '            "",\n'
        "        ],\n"
        "    )\n"
        "    if known_flutter_warning_profiles:\n"
        "        summary_lines.extend(\n"
        "            [\n"
        '                "## Known Flutter engine baseline",\n'
        '                "",\n'
        "                \"The calculator emitted exactly one known warning in \"\n"
        "                + \", \".join(sorted(known_flutter_warning_profiles))\n"
        "                + \" profiles: `\"\n"
        "                + EXPECTED_FLUTTER_DEPRECATION\n"
        "                + \"` The exact warning is accepted only on the Flutter \"\n"
        "                + \"calculator; every additional or different deprecation \"\n"
        "                + \"fails CI.\",\n"
        '                "",\n'
        "            ],\n"
        "        )\n"
        "    if failures:",
    )


def patch_documentation() -> None:
    path = Path("docs/SEO_PRODUCTION_CHECKLIST.md")
    replace_once(
        path,
        "Raporty Lighthouse są zapisywane jako artefakt CI. Początkowe progi dla "
        "Flutterowego kalkulatora są celowo łagodniejsze niż dla lekkich stron "
        "statycznych; wyniki tworzą wersjonowany punkt odniesienia do późniejszego "
        "zaostrzania.",
        "Raporty Lighthouse są zapisywane jako artefakt CI. Początkowe progi dla "
        "Flutterowego kalkulatora są celowo łagodniejsze niż dla lekkich stron "
        "statycznych; wyniki tworzą wersjonowany punkt odniesienia do późniejszego "
        "zaostrzania. Kalkulator może zgłosić wyłącznie jeden jawnie zapisany "
        "komunikat silnika Fluttera dotyczący `Intl.v8BreakIterator`; brak tego "
        "komunikatu jest poprawny, natomiast każda dodatkowa albo inna deprecacja "
        "zatrzymuje CI.",
    )


def main() -> None:
    patch_css()
    patch_lighthouse_runner()
    patch_documentation()
    print("Applied the reviewed Lighthouse baseline correction.")


if __name__ == "__main__":
    main()
