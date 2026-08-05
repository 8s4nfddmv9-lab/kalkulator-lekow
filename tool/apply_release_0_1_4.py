#!/usr/bin/env python3
"""Apply the reviewed InfusionCalc 0.1.4 stable release patch."""

from __future__ import annotations

import json
from pathlib import Path

OLD_ROOT_TITLE = "InfusionCalc — techniczny kalkulator infuzji"
NEW_ROOT_TITLE = "InfusionCalc — kalkulator infuzji, stężenia, przepływu i dawki"
RELEASE_VERSION = "0.1.4+23"
RELEASE_TAG = "v0.1.4"
RELEASE_DATE = "2026-08-05"


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    source = read(path)
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"Expected exactly one occurrence in {path}: {old!r}; found {count}.",
        )
    write(path, source.replace(old, new, 1))


def replace_block(path: str, start: str, end: str, replacement: str) -> None:
    source = read(path)
    start_index = source.find(start)
    if start_index < 0:
        raise SystemExit(f"Start marker not found in {path}: {start!r}")
    end_index = source.find(end, start_index)
    if end_index < 0:
        raise SystemExit(f"End marker not found in {path}: {end!r}")
    write(path, source[:start_index] + replacement + source[end_index:])


# Root HTML: a longer coherent title plus one semantic, visually hidden h1.
index_path = "web/index.html"
index = read(index_path)
old_title_count = index.count(OLD_ROOT_TITLE)
if old_title_count != 5:
    raise SystemExit(
        f"Expected five root-title occurrences in {index_path}; found {old_title_count}.",
    )
index = index.replace(OLD_ROOT_TITLE, NEW_ROOT_TITLE)

css_anchor = "    .boot-status {\n"
if index.count(css_anchor) != 1:
    raise SystemExit("Root HTML CSS anchor is missing or duplicated.")
visually_hidden_css = """    .seo-heading {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      clip-path: inset(50%);
      white-space: nowrap;
      border: 0;
    }

"""
index = index.replace(css_anchor, visually_hidden_css + css_anchor, 1)

body_anchor = "<body>\n"
if index.count(body_anchor) != 1:
    raise SystemExit("Root HTML body anchor is missing or duplicated.")
h1_markup = f'  <h1 class="seo-heading">{NEW_ROOT_TITLE}</h1>\n'
index = index.replace(body_anchor, body_anchor + h1_markup, 1)
write(index_path, index)


# Source validation must make both the new title and invisible h1 contractual.
validator_path = "tool/validate_web_seo.py"
replace_once(
    validator_path,
    f'ROOT_TITLE = "{OLD_ROOT_TITLE}"',
    f'ROOT_TITLE = "{NEW_ROOT_TITLE}"',
)
validator = read(validator_path)
validator_anchor = "    _validate_application_json_ld(parser.json_ld_documents)\n"
if validator.count(validator_anchor) != 1:
    raise SystemExit("SEO validator application-page anchor is missing or duplicated.")
validator_contract = """    if parser.h1_documents != [ROOT_TITLE]:
        raise WebSeoError(
            "Application page must contain exactly one h1 matching the public title; "
            f"found {parser.h1_documents!r}.",
        )

    expected_h1_markup = f'<h1 class="seo-heading">{ROOT_TITLE}</h1>'
    if expected_h1_markup not in source:
        raise WebSeoError("Application h1 must use the seo-heading class.")

    required_hidden_heading_css = (
        ".seo-heading {",
        "position: absolute;",
        "width: 1px;",
        "height: 1px;",
        "overflow: hidden;",
        "clip-path: inset(50%);",
        "white-space: nowrap;",
    )
    missing_hidden_css = [
        fragment for fragment in required_hidden_heading_css if fragment not in source
    ]
    if missing_hidden_css:
        raise WebSeoError(
            "Application h1 must remain visually hidden without display:none; "
            f"missing CSS: {missing_hidden_css!r}.",
        )

"""
validator = validator.replace(
    validator_anchor,
    validator_contract + validator_anchor,
    1,
)
write(validator_path, validator)


# Production audits must require the released title and deployed h1.
for audit_path in (
    "tool/audit_production_routes.py",
    "tool/validate_production_site.py",
):
    replace_once(audit_path, OLD_ROOT_TITLE, NEW_ROOT_TITLE)

audit_path = "tool/audit_production_routes.py"
audit = read(audit_path)
audit_anchor = """    if parser.title != route.title:
        raise AuditError(
            f"{route.path} title must be {route.title!r}; found {parser.title!r}.",
        )
"""
if audit.count(audit_anchor) != 1:
    raise SystemExit("Production route audit title anchor is missing or duplicated.")
audit_h1 = """    if route.path == "/":
        expected_h1 = f'<h1 class="seo-heading">{route.title}</h1>'
        if expected_h1 not in source:
            raise AuditError("The deployed calculator page is missing its semantic h1.")
"""
audit = audit.replace(audit_anchor, audit_anchor + audit_h1, 1)
write(audit_path, audit)

production_path = "tool/validate_production_site.py"
production = read(production_path)
production_anchor = """        if parser.titles != [expected_title]:
            raise ProductionSiteError(
                f"{url} has an unexpected title: {parser.titles!r}.",
            )
"""
if production.count(production_anchor) != 1:
    raise SystemExit("Production-site title anchor is missing or duplicated.")
production_h1 = """        if url == SITE_URL:
            expected_h1 = f'<h1 class="seo-heading">{expected_title}</h1>'
            if expected_h1 not in source:
                raise ProductionSiteError(
                    "The deployed calculator page is missing its semantic h1.",
                )
"""
production = production.replace(
    production_anchor,
    production_anchor + production_h1,
    1,
)
write(production_path, production)


# Stable application and release metadata.
replace_once("pubspec.yaml", "version: 0.1.3+22", f"version: {RELEASE_VERSION}")
replace_once(
    "lib/application/app_metadata.dart",
    "static const String version = '0.1.3+22';",
    f"static const String version = '{RELEASE_VERSION}';",
)
write(
    "release.json",
    json.dumps(
        {
            "tag": RELEASE_TAG,
            "version": RELEASE_VERSION,
            "title": "InfusionCalc v0.1.4",
            "notes_file": "releases/v0.1.4.md",
            "prerelease": False,
        },
        ensure_ascii=False,
        indent=2,
    )
    + "\n",
)

release_notes = """# InfusionCalc v0.1.4

Stabilne wydanie projektu indeksowania i widoczności wyszukiwarkowej. Strona główna `https://infusioncalc.eu/` nadal otwiera bezpośrednio kalkulator — bez landing page, ekranu powitalnego i dodatkowego kliknięcia.

## Indeksowanie i opis strony

- canonical, meta description, Open Graph, Twitter Card i techniczny JSON-LD typu `WebApplication`;
- publiczne `robots.txt` i `sitemap.xml` z czterema kanonicznymi adresami;
- dłuższy tytuł strony głównej: `InfusionCalc — kalkulator infuzji, stężenia, przepływu i dawki`;
- pojedynczy semantyczny nagłówek `<h1>` strony głównej, ukryty wyłącznie wizualnie i bez wpływu na układ kalkulatora;
- lokalny obraz podglądu społecznościowego `1200 × 630`.

## Publiczne strony informacyjne

- `/about/` — angielski opis funkcji technicznych, działania offline, prywatności, ograniczeń i FAQ;
- `/privacy/` — publiczna polityka prywatności;
- `/changelog/` — publiczna historia wydań;
- każda strona ma własny title, description, canonical, Open Graph, Twitter Card i JSON-LD oraz działa bez uruchamiania Fluttera.

## Routing i PWA

- jednoznaczne adresy z końcowym ukośnikiem dla stron informacyjnych;
- własny `404.html` z rzeczywistym statusem HTTP 404 i `noindex,follow`;
- nieistniejący adres nie jest już zamieniany w powłokę kalkulatora;
- statyczne strony i dokument 404 są częścią atomowego, wersjonowanego pakietu offline;
- wejście na `/` nadal natychmiast uruchamia aplikację Flutter.

## Wyszukiwarki

- domena została zweryfikowana w Google Search Console;
- mapa witryny została zgłoszona do Google;
- strona główna i `/about/` zostały zgłoszone do indeksacji;
- witryna została dodana do Bing Webmaster Tools, a test Live URL potwierdził możliwość indeksowania;
- tytuł i semantyczny `<h1>` usuwają dwie uwagi zgłoszone przez Bing dla strony głównej.

## Jakość techniczna

- automatyczna walidacja źródłowego HTML, metadanych, danych strukturalnych, mapy witryny i obrazu społecznościowego;
- testy bezpośrednich wejść, przekierowań i prawdziwego 404 online oraz offline;
- kontrola wdrożonego SHA, statusów HTTP, canonical, HTTPS i pakietu offline po publikacji GitHub Pages;
- Lighthouse mobile i desktop dla kalkulatora oraz trzech stron statycznych;
- kontrolne buildy Androida i iOS Simulator.

## Granice wydania

- brak zmian w solverze, równaniach, jednostkach, precyzji i danych formularza;
- brak bibliotek leków, zakresów dawkowania, rekomendacji i interpretacji klinicznej;
- brak nowych trackerów, reklam, cookies marketingowych i identyfikatorów użytkownika;
- InfusionCalc pozostaje technicznym kalkulatorem matematycznym, a wynik wymaga niezależnej weryfikacji.
"""
write("releases/v0.1.4.md", release_notes)


# Versioned project changelog.
changelog = read("CHANGELOG.md")
release_tail_marker = "## [0.1.3] — 2026-08-04\n"
release_tail_index = changelog.find(release_tail_marker)
if release_tail_index < 0:
    raise SystemExit("CHANGELOG 0.1.3 marker was not found.")
changelog_header = """# Changelog

Wszystkie istotne zmiany projektu są dokumentowane w tym pliku.

## [Unreleased]

## [0.1.4] — 2026-08-05

### Wydano

- stabilną wersję aplikacji `0.1.4+23` oraz tag `v0.1.4`;
- kompletny projekt indeksowania i widoczności wyszukiwarkowej bez landing page przed kalkulatorem;
- dłuższy title strony głównej i pojedynczy semantyczny, wizualnie ukryty `<h1>`;
- canonical, meta description, Open Graph, Twitter Card i techniczny JSON-LD;
- `robots.txt`, `sitemap.xml` i lokalny obraz podglądu `1200 × 630`;
- statyczne strony `/about/`, `/privacy/` i `/changelog/`;
- własny dokument 404, przekierowania kanoniczne oraz testy routingu online i offline;
- weryfikację domeny i zgłoszenie mapy witryny w Google Search Console;
- dodanie witryny do Bing Webmaster Tools i pozytywny test Live URL.

### Stabilność i granice

- strona główna nadal otwiera bezpośrednio kalkulator bez dodatkowego kliknięcia;
- pełny, samowystarczalny tryb offline pozostaje zachowany;
- automatyczne testy obejmują metadane, H1, statusy HTTP, canonical, sitemap, 404, Lighthouse i wdrożony build;
- brak zmian w solverze, równaniach, jednostkach, precyzji i danych formularza;
- brak nowych trackerów, reklam, cookies marketingowych i identyfikatorów użytkownika.

"""
write("CHANGELOG.md", changelog_header + changelog[release_tail_index:])


# Roadmap: close 0.1.4 and move the active stage to 0.1.5.
roadmap_path = "ROADMAP.md"
roadmap = read(roadmap_path)
roadmap = roadmap.replace(
    "**Aktualny etap:** `0.1.4-beta.1 — routing, 404 i walidacja produkcyjna`",
    "**Aktualny etap:** `0.1.5 — dostępność i ergonomia`",
    1,
)
roadmap = roadmap.replace(
    "- [ ] produkcyjne potwierdzenie metadanych w końcowej bramce `0.1.4`.",
    "- [x] produkcyjne potwierdzenie metadanych w końcowej bramce `0.1.4`.",
    1,
)
roadmap = roadmap.replace(
    "### 0.1.4-beta.1 — Routing, 404 i produkcyjna walidacja **← obecnie**",
    "### 0.1.4-beta.1 — Routing, 404 i produkcyjna walidacja **✓ ukończono**",
    1,
)
roadmap = roadmap.replace(
    "- [ ] zielony Lighthouse mobile i desktop dla wszystkich czterech stron;",
    "- [x] zielony Lighthouse mobile i desktop dla wszystkich czterech stron;",
    1,
)
roadmap = roadmap.replace(
    "- [ ] pełne zielone CI, scalenie i pomiar wdrożonej domeny.",
    "- [x] pełne zielone CI, scalenie i pomiar wdrożonej domeny.",
    1,
)
write(roadmap_path, roadmap)

stable_roadmap = """### 0.1.4 — Indeksowanie i widoczność wyszukiwarkowa **✓ ukończono**

- [x] stabilna wersja aplikacji `0.1.4+23`;
- [x] Google Search Console i weryfikacja własności domeny;
- [x] Bing Webmaster Tools i pozytywny test Live URL;
- [x] przesłanie `sitemap.xml`;
- [x] kontrola `/` oraz `/about/` i zgłoszenie do indeksacji w Google;
- [x] produkcyjna obserwacja canonical, renderowania i błędów indeksowania;
- [x] dłuższy title i semantyczny, wizualnie ukryty `<h1>` strony głównej;
- [x] tag `v0.1.4` i stabilny GitHub Release;
- [x] automatyczne wdrożenie na `https://infusioncalc.eu/` bez landing page.

**Zgłoszenie:** [issue #46](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/46).  
**Informacje o wydaniu:** [`releases/v0.1.4.md`](releases/v0.1.4.md).

"""
replace_block(
    roadmap_path,
    "### 0.1.4 — Indeksowanie i widoczność wyszukiwarkowa\n",
    "### 0.1.5 — Dostępność i ergonomia\n",
    stable_roadmap,
)
replace_once(
    roadmap_path,
    "Dokończyć automatyczne testy `0.1.4-beta.1`, scalić po zielonym CI i potwierdzić wdrożony build na domenie. Następnie skonfigurować Google Search Console, Bing Webmaster Tools i przygotować stabilne `v0.1.4`.",
    "Rozpocząć `0.1.5 — dostępność i ergonomia`, zachowując stabilny kontrakt obliczeń, bezpośrednie wejście do kalkulatora i pełne działanie offline.",
)


# README status and documentation links.
replace_once(
    "README.md",
    "**Wersja publiczna:** `0.1.3+22` — pierwsze stabilne wydanie (`v0.1.3`)",
    "**Wersja publiczna:** `0.1.4+23` — stabilne wydanie indeksowania i widoczności (`v0.1.4`)",
)
readme = read("README.md")
readme_anchor = "- [Audyt bazowy SEO 0.1.4](docs/SEO_BASELINE_AUDIT_0.1.4_2026-08-04.md)\n"
readme_addition = (
    readme_anchor
    + "- [Produkcyjna checklista SEO 0.1.4](docs/SEO_PRODUCTION_CHECKLIST.md)\n"
    + "- [Informacje o wydaniu 0.1.4](releases/v0.1.4.md)\n"
)
if readme.count(readme_anchor) != 1:
    raise SystemExit("README SEO documentation anchor is missing or duplicated.")
readme = readme.replace(readme_anchor, readme_addition, 1)
write("README.md", readme)


# Public changelog page: promote the SEO project to the latest stable release.
public_changelog_path = "web/changelog/index.html"
latest_section = """    <section class="section" aria-labelledby="latest-title">
      <p class="eyebrow">Najnowsze stabilne wydanie</p>
      <h2 id="latest-title">0.1.4 — indeksowanie i widoczność wyszukiwarkowa</h2>
      <div class="release-list">
        <article class="release">
          <p class="release__meta">v0.1.4 · 5 sierpnia 2026</p>
          <h2>Kalkulator dostępny bezpośrednio, a jednocześnie gotowy do wyszukiwania</h2>
          <ul>
            <li>strona główna nadal natychmiast otwiera kalkulator — bez landing page i dodatkowego kliknięcia;</li>
            <li>canonical, Open Graph, Twitter Card, JSON-LD, <code>robots.txt</code> i <code>sitemap.xml</code>;</li>
            <li>dłuższy title oraz semantyczny, wizualnie ukryty nagłówek <code>h1</code>;</li>
            <li>statyczne strony <code>/about/</code>, <code>/privacy/</code> i <code>/changelog/</code>;</li>
            <li>własny dokument 404 i kanoniczne przekierowania także w trybie offline;</li>
            <li>weryfikacja Google Search Console i Bing Webmaster Tools;</li>
            <li>automatyczne testy metadanych, tras, statusów HTTP, Lighthouse i pełnego pakietu offline.</li>
          </ul>
          <div class="notice">
            <strong>Zakres obliczeń nie uległ zmianie.</strong>
            Brak biblioteki leków, rekomendacji dawkowania i interpretacji klinicznej.
          </div>
        </article>
      </div>
    </section>

"""
replace_block(
    public_changelog_path,
    '    <section class="section" aria-labelledby="development-title">\n',
    '    <section class="section" aria-labelledby="stable-title">\n',
    latest_section,
)
replace_once(
    public_changelog_path,
    '      <p class="eyebrow">Stabilne wydanie</p>',
    '      <p class="eyebrow">Poprzednie stabilne wydanie</p>',
)


# Execution plan and production checklist now reflect completed registration.
seo_plan_path = "docs/SEO_DISCOVERABILITY_0.1.4.md"
seo_plan = read(seo_plan_path)
seo_plan = seo_plan.replace(
    "**Status:** w realizacji — `0.1.4-dev.1` i `0.1.4-dev.2` scalone; `0.1.4-beta.1` w toku",
    "**Status:** ukończono — stabilne `v0.1.4`",
    1,
)
write(seo_plan_path, seo_plan)
seo_state = """## Stan realizacji — 5 sierpnia 2026

- [x] ukończono i zapisano audyt bazowy;
- [x] scalono `0.1.4-dev.1` z fundamentami metadanych, robots, sitemap i walidatora;
- [x] wdrożono statyczne `/about/`, `/privacy/` i `/changelog/`;
- [x] rozszerzono routing service workera i pakiet offline o strony informacyjne oraz twarde 404;
- [x] przeprowadzono Lighthouse, pełne CI i automatyczną walidację wdrożonej domeny;
- [x] zweryfikowano domenę i przesłano sitemapę w Google Search Console;
- [x] dodano witrynę do Bing Webmaster Tools i potwierdzono możliwość indeksowania na żywo;
- [x] dodano dłuższy title i semantyczny, wizualnie ukryty `<h1>`;
- [x] przygotowano stabilne wydanie `0.1.4+23` oraz tag `v0.1.4`.

"""
replace_block(
    seo_plan_path,
    "## Stan realizacji — 5 sierpnia 2026\n",
    "## 1. Cel projektu\n",
    seo_state,
)

checklist_path = "docs/SEO_PRODUCTION_CHECKLIST.md"
checklist = read(checklist_path)
checklist = checklist.replace(
    "**Etap:** `0.1.4-beta.1 — routing, 404 i walidacja produkcyjna`",
    "**Etap:** `0.1.4 — stabilne wydanie`",
    1,
)
write(checklist_path, checklist)
for start, end in (
    ("## 3. Automatyczne bramy przed scaleniem\n", "## 4. Automatyczna kontrola po wdrożeniu\n"),
    ("## 4. Automatyczna kontrola po wdrożeniu\n", "## 5. Google Search Console — czynności właściciela domeny\n"),
    ("## 7. Kontrola podglądów i danych strukturalnych\n", "## 8. Monitoring po wydaniu\n"),
):
    checklist = read(checklist_path)
    start_index = checklist.find(start)
    end_index = checklist.find(end, start_index)
    if start_index < 0 or end_index < 0:
        raise SystemExit(f"Checklist section markers are missing: {start!r}")
    section = checklist[start_index:end_index].replace("- [ ]", "- [x]")
    write(checklist_path, checklist[:start_index] + section + checklist[end_index:])

for pending, completed in (
    ("- [ ] dodać usługę typu **Domena** dla `infusioncalc.eu`;", "- [x] dodać usługę typu **Domena** dla `infusioncalc.eu`;"),
    ("- [ ] dodać rekord TXT otrzymany od Google w panelu DNS;", "- [x] dodać rekord TXT otrzymany od Google w panelu DNS;"),
    ("- [ ] zakończyć weryfikację własności;", "- [x] zakończyć weryfikację własności;"),
    ("- [ ] przesłać `https://infusioncalc.eu/sitemap.xml`;", "- [x] przesłać `https://infusioncalc.eu/sitemap.xml`;"),
    ("- [ ] sprawdzić inspekcją adresy `/` i `/about/`;", "- [x] sprawdzić inspekcją adresy `/` i `/about/`;"),
    ("- [ ] zgłosić `/` i `/about/` do indeksacji;", "- [x] zgłosić `/` i `/about/` do indeksacji;"),
    ("- [ ] dodać lub zaimportować witrynę;", "- [x] dodać lub zaimportować witrynę;"),
    ("- [ ] zweryfikować własność domeny;", "- [x] zweryfikować własność domeny;"),
    ("- [ ] przesłać `sitemap.xml`;", "- [x] przesłać `sitemap.xml`;"),
):
    replace_once(checklist_path, pending, completed)
replace_once(
    checklist_path,
    "- [ ] sprawdzić `/` oraz `/about/`;",
    "- [x] sprawdzić `/` narzędziem Live URL;\n- [ ] sprawdzić `/about/` po pierwszym odczycie mapy witryny;",
)


# Remove obsolete one-time workflows left by the beta implementation process.
helper_workflows = (
    ".github/workflows/apply-beta1-routing.yml",
    ".github/workflows/cleanup-beta1-helpers.yml",
    ".github/workflows/finalize-beta1.yml",
    ".github/workflows/finalize-beta1-v2.yml",
    ".github/workflows/patch-beta1-accessibility.yml",
    ".github/workflows/record-beta1-production-evidence.yml",
    ".github/workflows/update-beta1-docs.yml",
)
for helper in helper_workflows:
    path = Path(helper)
    if not path.is_file():
        raise SystemExit(f"Expected one-time helper workflow is missing: {helper}")
    path.unlink()

print("Applied the stable InfusionCalc 0.1.4 release patch.")
