from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    if source.count(old) != 1:
        raise SystemExit(
            f"Expected exactly one occurrence in {path}: {old[:160]!r}",
        )
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


readme = Path("README.md")
replace_once(
    readme,
    """Umami Cloud rejestruje podstawowe odsłony i stałe zdarzenia użyteczności, takie jak otwarcie informacji czy kroki instalacji PWA. Zakres danych, twarde wyłączenia oraz sposób dostępu do panelu opisuje [`docs/ANALYTICS.md`](docs/ANALYTICS.md).

Historyczne warianty instalacji niepodpisanego IPA oraz hostowania na mini-PC pozostają w repozytorium jako ręczne, archiwalne ścieżki techniczne.
""",
    """Umami Cloud rejestruje podstawowe odsłony i stałe zdarzenia użyteczności, takie jak otwarcie informacji czy kroki instalacji PWA. Zakres danych, twarde wyłączenia oraz sposób dostępu do panelu opisuje [`docs/ANALYTICS.md`](docs/ANALYTICS.md).

Po pierwszym kompletnym uruchomieniu online service worker zapisuje cały lokalny zestaw aplikacji: kod Fluttera, `main.dart.js`, zasoby, fonty, CanvasKit, manifest i ikony. Dzięki temu zainstalowane PWA może uruchomić kalkulator bez połączenia z internetem. Każdy produkcyjny build generuje audytowalny `offline-assets.json`, a publikacja jest blokowana, jeśli któregokolwiek wymaganego pliku brakuje. Szczegóły i procedurę testu opisuje [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

Historyczne warianty instalacji niepodpisanego IPA oraz hostowania na mini-PC pozostają w repozytorium jako ręczne, archiwalne ścieżki techniczne.
""",
)
replace_once(
    readme,
    """- [Wdrożenie i ścieżki dystrybucji](DEPLOYMENT.md)
- [Prywatność](docs/PRIVACY.md)
- [Analityka](docs/ANALYTICS.md)
""",
    """- [Wdrożenie i ścieżki dystrybucji](DEPLOYMENT.md)
- [Pełny tryb offline PWA](docs/OFFLINE_PWA.md)
- [Prywatność](docs/PRIVACY.md)
- [Analityka](docs/ANALYTICS.md)
""",
)
replace_once(
    readme,
    "**Wersja publiczna:** `0.1.3-beta.3+18` — minimalna, prywatna analityka Umami Cloud",
    "**Wersja publiczna:** `0.1.3-beta.4+19` — kompletny, walidowany tryb offline PWA",
)

roadmap = Path("ROADMAP.md")
replace_once(
    roadmap,
    "**Aktualny etap:** `0.1.3-beta.3 — prywatna analityka produktu`",
    "**Aktualny etap:** `0.1.3-beta.4 — pełny tryb offline PWA`",
)
replace_once(
    roadmap,
    "### 0.1.3-beta.3 — Prywatna analityka produktu **← obecnie**",
    "### 0.1.3-beta.3 — Prywatna analityka produktu **✓ ukończono**",
)
replace_once(
    roadmap,
    """**Zgłoszenie:** [issue #36](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/36).

### 0.1.3 — Dostępność i ergonomia
""",
    """**Zgłoszenie:** [issue #36](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/36).

### 0.1.3-beta.4 — Pełny tryb offline PWA **← obecnie**

- [x] automatyczny manifest wszystkich lokalnych plików produkcyjnego buildu;
- [x] pełny precache `main.dart.js`, Fluttera, `assets/`, fontów i CanvasKit;
- [x] atomowa instalacja nowej wersji dopiero po zapisaniu kompletnego zestawu;
- [x] cache-first dla lokalnych zasobów aplikacji;
- [x] fallback na lokalny `index.html` przy nawigacji bez internetu;
- [x] wersjonowany cache i usuwanie poprzednich oraz historycznych cache;
- [x] audytowalne `offline-assets.json` i `pwa-build-info.json`;
- [x] niezależny walidator uruchamiany w CI i przed deployem GitHub Pages;
- [x] dokumentacja prywatności, ograniczeń i testu urządzeniowego;
- [ ] potwierdzenie uruchomienia oraz obliczenia w trybie samolotowym na fizycznym iPhonie;
- [ ] potwierdzenie trybu offline na co najmniej jednym urządzeniu z Androidem.

**Zgłoszenie:** [issue #38](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/38).

**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3 — Dostępność i ergonomia
""",
)

changelog = Path("CHANGELOG.md")
replace_once(
    changelog,
    "## [Unreleased]\n\n## [0.1.3-beta.3] — 2026-08-04",
    """## [Unreleased]

## [0.1.3-beta.4] — 2026-08-04

### Dodano

- automatyczne generowanie kompletnego `offline-assets.json` po produkcyjnym buildzie Flutter Web;
- pełny precache kodu Fluttera, `main.dart.js`, zasobów, fontów, CanvasKit, manifestu, ikon i lokalnych skryptów PWA;
- wersjonowane `pwa-build-info.json` z liczbą plików i sumą SHA-256 listy zasobów;
- niezależny walidator kompletności zestawu offline uruchamiany w CI i przed publikacją GitHub Pages;
- dokument `docs/OFFLINE_PWA.md` z procedurą testu na iPhonie i Androidzie.

### Zmieniono

- service worker instaluje nową wersję dopiero po zapisaniu całego zestawu aplikacji;
- lokalne zasoby korzystają ze strategii cache-first, a nawigacja bez internetu wraca do lokalnego `index.html`;
- aktywacja usuwa cache poprzednich wersji, w tym historyczny prefiks `kalkulator-lekow-`;
- workflow GitHub Pages blokuje deploy bez kompletnego, zweryfikowanego zestawu offline;
- wersję aplikacji na `0.1.3-beta.4+19`.

### Prywatność i granice

- cache zawiera wyłącznie statyczny kod, zasoby i techniczne metadane buildu;
- wartości formularza, masa, dawka, przepływ, wyniki i historia nie są zapisywane w cache;
- brak zmian w solverze, równaniach, jednostkach, precyzji i analityce;
- zewnętrzne linki oraz wysyłka Umami nadal wymagają internetu, ale nie wpływają na kalkulator.

## [0.1.3-beta.3] — 2026-08-04""",
)

print("Updated README, ROADMAP and CHANGELOG for complete offline PWA support.")
