from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    if source.count(old) != 1:
        raise SystemExit(
            f"Expected exactly one documentation block in {path}: {old[:180]!r}",
        )
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


readme = Path("README.md")
replace_once(
    readme,
    """Aplikacja nie ma własnego backendu. Serwer dostarcza wyłącznie statyczne pliki, a obliczenia wykonują się lokalnie w przeglądarce. Manifest PWA i service worker umożliwiają dodanie aplikacji do ekranu początkowego oraz korzystanie z wcześniej załadowanej wersji bez aktywnego połączenia.
""",
    """Aplikacja nie ma własnego backendu. Serwer dostarcza wyłącznie statyczne pliki, a obliczenia wykonują się lokalnie w przeglądarce.

Od wersji `0.1.3-beta.4` produkcyjny build tworzy kompletny `offline-manifest.json` obejmujący kod Fluttera, assety, fonty, ikony i pliki renderera obecne w danym wydaniu. Service worker zapisuje cały zestaw atomowo w osobnym, wersjonowanym cache i uruchamia dokument oraz assety tej samej wersji w strategii `cache-first`. Po co najmniej jednym pełnym uruchomieniu online aplikację można uruchomić z ekranu głównego i wykonywać obliczenia bez internetu.

Pierwsze pobranie oraz pobranie nowego wydania wymagają internetu. Zewnętrzne linki do GitHub nie są częścią paczki offline. Szczegółowy opis, ograniczenia systemowe i procedura testu na iPhonie oraz Androidzie znajdują się w [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).
""",
)
replace_once(
    readme,
    "- [Wdrożenie i ścieżki dystrybucji](DEPLOYMENT.md)\n- [Prywatność](docs/PRIVACY.md)",
    "- [Wdrożenie i ścieżki dystrybucji](DEPLOYMENT.md)\n- [Pełny tryb offline PWA](docs/OFFLINE_PWA.md)\n- [Prywatność](docs/PRIVACY.md)",
)
replace_once(
    readme,
    "**Wersja publiczna:** `0.1.3-beta.3+18` — minimalna, prywatna analityka Umami Cloud",
    "**Wersja publiczna:** `0.1.3-beta.4+19` — kompletna, wersjonowana paczka PWA działająca offline",
)

changelog = Path("CHANGELOG.md")
replace_once(
    changelog,
    "## [Unreleased]\n\n",
    """## [Unreleased]

## [0.1.3-beta.4] — 2026-08-04

### Dodano

- automatycznie generowany `offline-manifest.json` obejmujący wszystkie lokalne pliki produkcyjnego buildu Flutter Web;
- pełne wstępne zapisanie `main.dart.js`, assetów, fontów, ikon i plików renderera;
- atomową instalację nowego cache — niepełna paczka jest usuwana i nie zastępuje poprzedniej wersji;
- wersjonowaną strategię `cache-first` dla nawigacji i zasobów;
- sprawdzanie aktualizacji service workera po uruchomieniu online i po odzyskaniu połączenia;
- moduł `tool/offline_pwa.py`, deterministyczne testy oraz walidację produkcyjnego artefaktu;
- dokument `docs/OFFLINE_PWA.md` z procedurą testu na iPhonie i Androidzie.

### Zmieniono

- rejestrację service workera na `updateViaCache: none` bez automatycznego przeładowania bieżącego formularza;
- komunikat i dokumentację prywatności o informację, że cache offline zawiera wyłącznie publiczny kod i statyczne zasoby;
- workflow CI i GitHub Pages tak, aby odrzucały niekompletną albo niespójną paczkę offline.

### Offline

- po co najmniej jednym pełnym uruchomieniu online zainstalowany InfusionCalc może uruchomić kalkulator bez internetu;
- Umami nie jest wymagane do działania i zdarzenia offline nie są trwale kolejkowane;
- zewnętrzne linki GitHub mogą pozostawać niedostępne bez połączenia.

### Granice

- pierwsze pobranie i pobranie każdej nowej wersji wymagają internetu;
- system operacyjny może usunąć cache przy czyszczeniu danych lub presji na pamięć;
- brak zmian w solverze, równaniach, jednostkach, precyzji i danych formularza.

""",
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
- [x] wstępne zapisanie kodu Fluttera, assetów, fontów, ikon i rendererów;
- [x] atomowa instalacja kompletnej paczki wersji;
- [x] osobny cache dla każdego buildu;
- [x] strategia `cache-first` bez mieszania plików różnych wersji;
- [x] aktualizacja service workera po odzyskaniu internetu;
- [x] działanie kalkulatora niezależne od Umami;
- [x] polityka prywatności obejmująca code-only offline cache;
- [x] testy narzędzi i pełna walidacja artefaktu w CI;
- [x] dokumentowana procedura testu na iPhonie i Androidzie;
- [ ] potwierdzenie uruchomienia i obliczeń w trybie samolotowym na fizycznym iPhonie;
- [ ] potwierdzenie uruchomienia i obliczeń offline na fizycznym urządzeniu z Androidem.

**Zgłoszenie:** [issue #38](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/38).  
**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3 — Dostępność i ergonomia
""",
)

print("Updated README, changelog and roadmap for the full offline PWA release.")
