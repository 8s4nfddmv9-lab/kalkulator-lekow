#!/usr/bin/env python3
"""Apply one-time documentation updates for the iOS offline startup hotfix."""

from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"Expected exactly one matching block in {path}, found {count}: "
            f"{old[:160]!r}",
        )
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


changelog = Path("CHANGELOG.md")
replace_once(
    changelog,
    "## [Unreleased]\n\n",
    """## [Unreleased]

## [0.1.3-beta.5] — 2026-08-04

### Poprawiono

- nowy, kompletny service worker nie pozostaje już w stanie `waiting` za starszą wersją kontrolującą Safari albo aplikację z ekranu głównego;
- po poprawnym zapisaniu całej paczki worker używa `skipWaiting()`, a po aktywacji `clients.claim()` bez automatycznego przeładowania formularza;
- manifest offline pomija ukryte techniczne pliki buildu, w tym `.last_build_id`, których statyczny hosting może nie publikować;
- dopasowanie zasobów w cache ignoruje parametry zapytania oraz różnice nagłówka `Vary`;
- ekran startowy po 20 sekundach pokazuje `BOOT_TIMEOUT` albo `BOOT_RUNTIME_ERROR` zamiast pozostawać bez końca na komunikacie uruchamiania.

### Testy

- test manifestu potwierdza wykluczenie ukrytych plików z katalogu głównego i zagnieżdżonych katalogów;
- walidator wymaga `skipWaiting()`, `clients.claim()` oraz odpornego dopasowania cache;
- test ChromeDriver wymaga, aby service worker kontrolował już pierwszą stronę bez wcześniejszego przejścia na `about:blank`;
- CI oraz deploy GitHub Pages sprawdzają markery aktywacji i diagnostyki przed publikacją.

### Granice

- brak zmian w solverze, równaniach, jednostkach, precyzji i danych formularza;
- pierwsze przygotowanie każdej wersji nadal wymaga internetu;
- końcowe potwierdzenie poprawki pozostaje testem na fizycznym iPhonie.

""",
)

readme = Path("README.md")
replace_once(
    readme,
    """Od wersji `0.1.3-beta.4` produkcyjny build tworzy kompletny `offline-manifest.json` obejmujący kod Fluttera, assety, fonty, ikony i pliki renderera obecne w danym wydaniu. Service worker zapisuje cały zestaw atomowo w osobnym, wersjonowanym cache i uruchamia dokument oraz assety tej samej wersji w strategii `cache-first`. Po co najmniej jednym pełnym uruchomieniu online aplikację można uruchomić z ekranu głównego i wykonywać obliczenia bez internetu.
""",
    """Od wersji `0.1.3-beta.4` produkcyjny build tworzy kompletny `offline-manifest.json` obejmujący kod Fluttera, assety, fonty, ikony i pliki renderera obecne w danym wydaniu. Wersja `0.1.3-beta.5` poprawia aktywację na iOS: po atomowym zapisaniu pełnej paczki nowy worker opuszcza stan `waiting`, przejmuje klientów bez przeładowania formularza i pomija ukryte metadane buildu, które nie są publicznymi zasobami. Po co najmniej jednym pełnym uruchomieniu online aplikację można uruchomić z ekranu głównego i wykonywać obliczenia bez internetu.
""",
)
replace_once(
    readme,
    "**Wersja publiczna:** `0.1.3-beta.4+19` — kompletna, wersjonowana paczka PWA działająca offline",
    "**Wersja publiczna:** `0.1.3-beta.5+20` — poprawiona aktywacja trybu offline PWA na iOS",
)

roadmap = Path("ROADMAP.md")
replace_once(
    roadmap,
    "**Aktualny etap:** `0.1.3-beta.4 — pełny tryb offline PWA`",
    "**Aktualny etap:** `0.1.3-beta.5 — poprawka startu offline na iOS`",
)
replace_once(
    roadmap,
    "### 0.1.3-beta.4 — Pełny tryb offline PWA **← obecnie**",
    "### 0.1.3-beta.4 — Pełny tryb offline PWA **✓ ukończono, wykryto regresję iOS**",
)
replace_once(
    roadmap,
    """**Zgłoszenie:** [issue #38](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/38).  
**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3 — Dostępność i ergonomia
""",
    """**Zgłoszenie:** [issue #38](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/38).  
**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3-beta.5 — Poprawka startu offline na iOS **← obecnie**

- [x] potwierdzenie przyczyny: kompletny worker pozostawał w stanie `waiting` za starszą wersją;
- [x] `skipWaiting()` po pełnym, atomowym precache;
- [x] `clients.claim()` po aktywacji bez automatycznego przeładowania formularza;
- [x] wykluczenie `.last_build_id` i innych ukrytych metadanych z manifestu offline;
- [x] odporniejsze dopasowanie cache dla Safari;
- [x] test pierwszej kontroli strony bez opuszczania originu;
- [x] diagnostyczny ekran `BOOT_TIMEOUT` / `BOOT_RUNTIME_ERROR`;
- [x] pełna walidacja w CI i przed deployem GitHub Pages;
- [ ] potwierdzenie uruchomienia i obliczeń w trybie samolotowym na fizycznym iPhonie;
- [ ] potwierdzenie uruchomienia i obliczeń offline na fizycznym urządzeniu z Androidem.

**Zgłoszenie:** [issue #40](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/40).  
**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3 — Dostępność i ergonomia
""",
)

print("Updated changelog, README and roadmap for 0.1.3-beta.5+20.")
