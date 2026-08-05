#!/usr/bin/env python3
"""Apply the reviewed 0.1.4-beta.1 routing and documentation patch."""

from __future__ import annotations

from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"{path}: expected one occurrence of patch anchor, found {count}:\n{old}",
        )
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


def patch_offline_pwa() -> None:
    path = Path("tool/offline_pwa.py")
    replace_once(
        path,
        'NAVIGATION_FALLBACK = "./index.html"\n',
        'NAVIGATION_FALLBACK = "./index.html"\n'
        'NOT_FOUND_DOCUMENT = "./404.html"\n',
    )
    replace_once(
        path,
        '        "./index.html",\n'
        '        "./about/index.html",',
        '        "./index.html",\n'
        '        "./404.html",\n'
        '        "./about/index.html",',
    )
    replace_once(
        path,
        '        "navigation_fallback": NAVIGATION_FALLBACK,\n'
        '        "file_count": len(files),',
        '        "navigation_fallback": NAVIGATION_FALLBACK,\n'
        '        "not_found_document": NOT_FOUND_DOCUMENT,\n'
        '        "file_count": len(files),',
    )
    replace_once(
        path,
        '        "offline_strategy": "versioned-cache-first",\n'
        '        "offline_file_count": len(files),',
        '        "offline_strategy": "versioned-cache-first",\n'
        '        "offline_not_found_document": '
        'NOT_FOUND_DOCUMENT.removeprefix("./"),\n'
        '        "offline_file_count": len(files),',
    )
    replace_once(
        path,
        '    if manifest.get("navigation_fallback") != NAVIGATION_FALLBACK:\n'
        '        raise OfflinePwaError("Offline navigation fallback must be index.html.")\n'
        '    if manifest.get("file_count") != len(files):',
        '    if manifest.get("navigation_fallback") != NAVIGATION_FALLBACK:\n'
        '        raise OfflinePwaError("Offline navigation fallback must be index.html.")\n'
        '    if manifest.get("not_found_document") != NOT_FOUND_DOCUMENT:\n'
        '        raise OfflinePwaError("Offline not-found document must be 404.html.")\n'
        '    if manifest.get("file_count") != len(files):',
    )
    replace_once(
        path,
        '        "cache.match(INDEX_DOCUMENT",\n'
        '        "function navigationDocumentFor(url)",\n'
        '        "relativePath.endsWith(\'/\')",\n'
        '        "cache.match(navigationDocument",\n'
        '        "cachedNavigationOrNetwork(request)",',
        '        "const NOT_FOUND_DOCUMENT = \'./404.html\';",\n'
        '        "const CANONICAL_DOCUMENTS = new Map([",\n'
        '        "const CANONICAL_REDIRECTS = new Map([",\n'
        '        "function canonicalRedirectFor(url)",\n'
        '        "Response.redirect(redirectUrl.href, 308)",\n'
        '        "cache.match(navigationDocument",\n'
        '        "async function cachedNotFoundResponse(cache)",\n'
        '        "status: 404",\n'
        '        "cachedNavigationOrNetwork(request)",',
    )


def patch_finalizer() -> None:
    path = Path("tool/finalize_web_pwa.py")
    replace_once(
        path,
        "from validate_web_seo import WebSeoError, validate_web_seo\n",
        "from validate_web_routing import WebRoutingError, validate_web_routing\n"
        "from validate_web_seo import WebSeoError, validate_web_seo\n",
    )
    replace_once(
        path,
        '    "index.html",\n'
        '    "flutter.js",',
        '    "index.html",\n'
        '    "404.html",\n'
        '    "flutter.js",',
    )
    replace_once(
        path,
        "        validate_web_seo(build_dir)\n\n"
        "        manifest_path = build_dir / \"manifest.json\"",
        "        validate_web_seo(build_dir)\n"
        "        validate_web_routing(build_dir)\n\n"
        "        manifest_path = build_dir / \"manifest.json\"",
    )
    replace_once(
        path,
        "        OfflinePwaError,\n"
        "        WebSeoError,\n",
        "        OfflinePwaError,\n"
        "        WebRoutingError,\n"
        "        WebSeoError,\n",
    )


def patch_offline_tests() -> None:
    path = Path("tool/test_offline_pwa.py")
    replace_once(
        path,
        '            "index.html": "<html></html>",\n'
        '            "about/index.html":',
        '            "index.html": "<html></html>",\n'
        '            "404.html": (\n'
        '                \'<html><body data-page="not-found">404</body></html>\'\n'
        '            ),\n'
        '            "about/index.html":',
    )
    replace_once(
        path,
        '        self.assertIn("./main.dart.js", files)\n'
        '        self.assertIn("./flutter.js", files)',
        '        self.assertIn("./main.dart.js", files)\n'
        '        self.assertIn("./flutter.js", files)\n'
        '        self.assertIn("./404.html", files)',
    )
    replace_once(
        path,
        '        self.assertIn("function navigationDocumentFor(url)", worker_source)\n'
        '        self.assertIn("relativePath.endsWith(\'/\')", worker_source)\n'
        '        self.assertIn("cache.match(navigationDocument", worker_source)\n'
        '        self.assertIn("cachedNavigationOrNetwork(request)", worker_source)\n',
        '        self.assertIn(\n'
        '            "const NOT_FOUND_DOCUMENT = \'./404.html\';",\n'
        '            worker_source,\n'
        '        )\n'
        '        self.assertIn("const CANONICAL_DOCUMENTS = new Map([", worker_source)\n'
        '        self.assertIn("const CANONICAL_REDIRECTS = new Map([", worker_source)\n'
        '        self.assertIn("function canonicalRedirectFor(url)", worker_source)\n'
        '        self.assertIn("Response.redirect(redirectUrl.href, 308)", worker_source)\n'
        '        self.assertIn("cache.match(navigationDocument", worker_source)\n'
        '        self.assertIn("async function cachedNotFoundResponse(cache)", worker_source)\n'
        '        self.assertIn("status: 404", worker_source)\n'
        '        self.assertIn("cachedNavigationOrNetwork(request)", worker_source)\n'
        '        self.assertNotIn("relativePath.endsWith(\'/\')", worker_source)\n',
    )
    replace_once(
        path,
        "    def test_validation_rejects_one_missing_manifest_entry(self) -> None:\n",
        "    def test_validation_rejects_missing_not_found_document(self) -> None:\n"
        "        (self.build_dir / \"404.html\").unlink()\n"
        "        self._finalize()\n\n"
        "        with self.assertRaisesRegex(\n"
        "            OfflinePwaError,\n"
        "            \"Critical offline files are missing\",\n"
        "        ):\n"
        "            validate_offline_build(self.build_dir, build_id=self.build_id)\n\n"
        "    def test_validation_rejects_one_missing_manifest_entry(self) -> None:\n",
    )


def patch_roadmap() -> None:
    path = Path("ROADMAP.md")
    replace_once(
        path,
        "**Aktualny etap:** `0.1.4-dev.2 — statyczne strony informacyjne`",
        "**Aktualny etap:** `0.1.4-beta.1 — routing, 404 i walidacja produkcyjna`",
    )
    replace_once(
        path,
        "### 0.1.4-dev.2 — Statyczne strony informacyjne **← obecnie**",
        "### 0.1.4-dev.2 — Statyczne strony informacyjne **✓ ukończono**",
    )
    replace_once(
        path,
        "- [x] wersja aplikacji `0.1.4-dev.2+23`;\n"
        "- [ ] scalenie PR i produkcyjne potwierdzenie po wdrożeniu.",
        "- [x] publiczne metadane wersji pozostawione na stabilnym `0.1.3+22` "
        "do czasu release candidate;\n"
        "- [x] scalenie PR #49 do `main` i poprawne wdrożenie przez GitHub Pages.",
    )
    replace_once(
        path,
        "### 0.1.4-beta.1 — Routing, 404 i produkcyjna walidacja\n\n"
        "- [ ] spójna polityka końcowych ukośników i bezpośrednich wejść;\n"
        "- [ ] własny `404.html` bez soft 404;\n"
        "- [ ] rozszerzona mapa witryny;\n"
        "- [ ] przeglądarkowe testy wszystkich publicznych adresów;\n"
        "- [ ] Lighthouse mobile i desktop;\n"
        "- [ ] weryfikacja podglądu linku i danych strukturalnych;\n"
        "- [ ] kontrola działania offline po aktualizacji.",
        "### 0.1.4-beta.1 — Routing, 404 i produkcyjna walidacja "
        "**← obecnie**\n\n"
        "- [x] jednoznaczna polityka końcowych ukośników i przekierowania "
        "kanoniczne także offline;\n"
        "- [x] własny statyczny `404.html` z `noindex,follow`, bez canonical "
        "i bez powłoki kalkulatora;\n"
        "- [x] mapa witryny ograniczona do czterech kanonicznych adresów "
        "i jawnie wykluczająca stronę błędu;\n"
        "- [x] przeglądarkowy test prawidłowych tras i 404 online oraz offline;\n"
        "- [ ] zielony Lighthouse mobile i desktop dla wszystkich czterech stron;\n"
        "- [x] automatyczna weryfikacja metadanych, obrazu podglądu i danych "
        "strukturalnych;\n"
        "- [x] produkcyjny walidator statusów HTTP, przekierowań, HTTPS, "
        "robots, sitemap i wdrożonego build ID;\n"
        "- [ ] pełne zielone CI, scalenie i pomiar wdrożonej domeny.",
    )
    replace_once(
        path,
        "Dokończyć przegląd i scalenie `0.1.4-dev.2`, następnie rozpocząć "
        "`0.1.4-beta.1`: routing końcowych ukośników, własne `404.html`, "
        "testy bezpośrednich wejść oraz produkcyjną walidację Lighthouse.",
        "Dokończyć automatyczne testy `0.1.4-beta.1`, scalić po zielonym CI "
        "i potwierdzić wdrożony build na domenie. Następnie skonfigurować "
        "Google Search Console, Bing Webmaster Tools i przygotować stabilne "
        "`v0.1.4`.",
    )


def patch_changelog() -> None:
    path = Path("CHANGELOG.md")
    marker = "## [Unreleased]\n\n"
    entry = """## [Unreleased]

### Dodano — `0.1.4-beta.1`

- własny statyczny `404.html` z metadanymi `noindex,follow`, bez canonical i bez uruchamiania Fluttera;
- jednoznaczne przekierowania `/about`, `/privacy`, `/changelog` i wariantów `index.html` do adresów z końcowym ukośnikiem;
- osobny walidator routingu, test przeglądarkowy tras online/offline oraz kontrolę wdrożonej domeny po publikacji GitHub Pages;
- powtarzalny audyt Lighthouse mobile i desktop dla kalkulatora oraz trzech stron informacyjnych;
- wersjonowaną checklistę produkcyjnego SEO i rejestracji w wyszukiwarkach.

### Routing i 404

- service worker rozpoznaje wyłącznie jawnie wspierane dokumenty i nie zamienia nieistniejących adresów w powłokę kalkulatora;
- nieznana nawigacja offline zwraca cache strony błędu z rzeczywistym statusem `404`;
- `404.html` wchodzi do atomowego pakietu offline, ale pozostaje poza `sitemap.xml`;
- publiczne metadane aplikacji pozostają na stabilnym `0.1.3+22` do czasu właściwego release candidate.

### Bramy jakości

- CI sprawdza źródłowy kontrakt 404, składnię service workera i kompletność manifestu offline;
- ChromeDriver odróżnia kalkulator, strony statyczne i stronę błędu przed oraz po odcięciu sieci;
- workflow wdrożeniowy po publikacji sprawdza oczekiwany build ID, statusy HTTP, canonical, przekierowania, HTTPS, robots, sitemap i obraz społecznościowy.

"""
    source = path.read_text(encoding="utf-8")
    if source.count(marker) != 1:
        raise SystemExit("CHANGELOG.md: unexpected Unreleased marker count.")
    path.write_text(source.replace(marker, entry, 1), encoding="utf-8")


def patch_seo_plan() -> None:
    path = Path("docs/SEO_DISCOVERABILITY_0.1.4.md")
    replace_once(
        path,
        "**Status:** w realizacji — `0.1.4-dev.1` scalone, "
        "`0.1.4-dev.2` w toku",
        "**Status:** w realizacji — `0.1.4-dev.1` i `0.1.4-dev.2` "
        "scalone; `0.1.4-beta.1` w toku",
    )
    replace_once(
        path,
        "- [ ] scalić `0.1.4-dev.2` po zielonych testach i potwierdzić "
        "produkcyjne adresy.",
        "- [x] scalono `0.1.4-dev.2` i poprawnie wdrożono statyczne strony "
        "przez GitHub Pages;\n"
        "- [x] przygotowano twardy kontrakt 404, przekierowania z końcowym "
        "ukośnikiem i testy online/offline;\n"
        "- [ ] zakończyć Lighthouse, pełne CI i automatyczną walidację "
        "wdrożonej domeny.",
    )


def main() -> None:
    patch_offline_pwa()
    patch_finalizer()
    patch_offline_tests()
    patch_roadmap()
    patch_changelog()
    patch_seo_plan()
    print("Applied InfusionCalc 0.1.4-beta.1 routing patch.")


if __name__ == "__main__":
    main()
