#!/usr/bin/env python3
"""Apply one-time documentation updates for the CDN-free offline runtime fix."""

from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"Expected exactly one matching block in {path}, found {count}: "
            f"{old[:180]!r}",
        )
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


changelog = Path("CHANGELOG.md")
replace_once(
    changelog,
    "## [Unreleased]\n\n",
    """## [Unreleased]

## [0.1.3-beta.6] — 2026-08-04

### Poprawiono

- wszystkie buildy Flutter Web używają `--no-web-resources-cdn`, dzięki czemu renderer CanvasKit, WebAssembly i pozostałe zasoby startowe są dostarczane z `infusioncalc.eu`;
- usunięto zależność uruchomienia od domyślnego CDN Fluttera, która na iPhonie powodowała zatrzymanie na ekranie `Uruchamianie InfusionCalc…` po odłączeniu internetu;
- finalizer odrzuca wygenerowany runtime zawierający znane adresy CDN renderera lub fontów;
- produkcyjny artefakt musi zawierać lokalne pliki JavaScript i WebAssembly CanvasKit.

### Testy

- ChromeDriver odrzuca każdy zewnętrzny zasób startowy poza opcjonalnym skryptem Umami;
- przed próbą offline test czyści i wyłącza zwykły HTTP cache, zachowując wyłącznie wersjonowany CacheStorage service workera;
- lokalny serwer i sieć są odcinane przed ponownym uruchomieniem, więc wynik nie może zależeć od wcześniejszego cache CDN;
- workflow GitHub Pages, CI i archiwalny build mini-PC korzystają z tej samej konfiguracji bez CDN.

### Granice

- brak zmian w solverze, równaniach, jednostkach, precyzji i danych formularza;
- Umami pozostaje opcjonalne i nie jest wymagane do uruchomienia kalkulatora;
- pierwsze przygotowanie danej wersji nadal wymaga internetu;
- końcowe potwierdzenie poprawki pozostaje testem na fizycznym iPhonie.

""",
)

readme = Path("README.md")
replace_once(
    readme,
    """Od wersji `0.1.3-beta.4` produkcyjny build tworzy kompletny `offline-manifest.json` obejmujący kod Fluttera, assety, fonty, ikony i pliki renderera obecne w danym wydaniu. Wersja `0.1.3-beta.5` poprawia aktywację na iOS: po atomowym zapisaniu pełnej paczki nowy worker opuszcza stan `waiting`, przejmuje klientów bez przeładowania formularza i pomija ukryte metadane buildu, które nie są publicznymi zasobami. Po co najmniej jednym pełnym uruchomieniu online aplikację można uruchomić z ekranu głównego i wykonywać obliczenia bez internetu.
""",
    """Od wersji `0.1.3-beta.4` produkcyjny build tworzy kompletny `offline-manifest.json` obejmujący kod Fluttera, assety, fonty, ikony i pliki renderera obecne w danym wydaniu. Wersja `0.1.3-beta.5` poprawiła aktywację na iOS: po atomowym zapisaniu pełnej paczki nowy worker opuszcza stan `waiting`, przejmuje klientów bez przeładowania formularza i pomija ukryte metadane buildu. Wersja `0.1.3-beta.6` usuwa ostatnią zewnętrzną zależność startową: wszystkie buildy używają `--no-web-resources-cdn`, dlatego CanvasKit i WebAssembly są dostarczane lokalnie z `infusioncalc.eu`, a nie z CDN Fluttera. Po co najmniej jednym pełnym uruchomieniu online aplikację można uruchomić z ekranu głównego i wykonywać obliczenia bez internetu.
""",
)
replace_once(
    readme,
    "**Wersja publiczna:** `0.1.3-beta.5+20` — poprawiona aktywacja trybu offline PWA na iOS",
    "**Wersja publiczna:** `0.1.3-beta.6+21` — samowystarczalny runtime PWA bez zależności od CDN",
)

roadmap = Path("ROADMAP.md")
replace_once(
    roadmap,
    "**Aktualny etap:** `0.1.3-beta.5 — poprawka startu offline na iOS`",
    "**Aktualny etap:** `0.1.3-beta.6 — samowystarczalny runtime offline`",
)
replace_once(
    roadmap,
    "### 0.1.3-beta.5 — Poprawka startu offline na iOS **← obecnie**",
    "### 0.1.3-beta.5 — Poprawka aktywacji workera na iOS **✓ ukończono, wykryto zależność CDN**",
)
replace_once(
    roadmap,
    """**Zgłoszenie:** [issue #40](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/40).  
**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3 — Dostępność i ergonomia
""",
    """**Zgłoszenie:** [issue #40](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/40).  
**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3-beta.6 — Samowystarczalny runtime offline **← obecnie**

- [x] wszystkie buildy Flutter Web z `--no-web-resources-cdn`;
- [x] lokalny CanvasKit JavaScript i WebAssembly w paczce aplikacji;
- [x] statyczne odrzucanie adresów CDN renderera i fontów;
- [x] dynamiczne odrzucanie zewnętrznych zasobów startowych poza opcjonalnym Umami;
- [x] czyszczenie i wyłączenie zwykłego HTTP cache przed testem offline;
- [x] ponowne uruchomienie po odcięciu lokalnego serwera i sieci;
- [x] spójna konfiguracja CI, GitHub Pages i archiwalnego builda mini-PC;
- [x] wersja `0.1.3-beta.6+21` oraz zaktualizowana dokumentacja;
- [ ] potwierdzenie uruchomienia i obliczeń w trybie samolotowym na fizycznym iPhonie;
- [ ] potwierdzenie uruchomienia i obliczeń offline na fizycznym urządzeniu z Androidem.

**Zgłoszenie:** [issue #40](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/40).  
**Pull request:** [PR #43](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/pull/43).  
**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3 — Dostępność i ergonomia
""",
)

offline = Path("docs/OFFLINE_PWA.md")
replace_once(
    offline,
    """Pierwsze pobranie aplikacji oraz pobranie każdej nowej wersji wymagają połączenia z internetem.

## Jak przygotowywana jest wersja offline
""",
    """Pierwsze pobranie aplikacji oraz pobranie każdej nowej wersji wymagają połączenia z internetem.

## Samowystarczalny runtime Fluttera

Produkcyjny build jest wykonywany z opcją `--no-web-resources-cdn`. Kod uruchamiający Fluttera, `main.dart.js`, lokalny CanvasKit, pliki WebAssembly, fonty, ikony i pozostałe assety pochodzą z tego samego originu `infusioncalc.eu`.

Domyślna konfiguracja Flutter Web może używać zewnętrznego CDN dla renderera. Taki build może pozornie przejść test offline w przeglądarce, jeżeli renderer pozostaje w zwykłym HTTP cache po uruchomieniu online, ale zawiedzie na czystej instalacji lub w Home Screen PWA bez internetu. Finalizer i test przeglądarkowy jawnie odrzucają tę zależność.

Umami Cloud pozostaje jedynym opcjonalnym skryptem zewnętrznym. Jego brak, blokada lub niedostępność nie wpływają na uruchomienie Fluttera ani obliczenia.

## Jak przygotowywana jest wersja offline
""",
)
replace_once(
    offline,
    """- skrypt `main.dart.js`, assety, fonty i renderer są odczytywane z tego samego cache;
- aplikacja nie łączy dokumentu jednej wersji z kodem albo assetami innego wydania;
""",
    """- skrypt `main.dart.js`, lokalny CanvasKit, WebAssembly, assety i fonty są odczytywane z tego samego cache;
- aplikacja nie łączy dokumentu jednej wersji z kodem albo assetami innego wydania;
- uruchomienie kalkulatora nie wymaga połączenia z CDN Fluttera, Google Fonts ani innym zewnętrznym originem;
""",
)
replace_once(
    offline,
    """- worker nie aktywuje się po kompletnym precache albo nie przejmuje klientów;
- konfiguracja aktualizacji service workera jest niekompletna.

Dodatkowo `tool/smoke_test_offline_pwa.py` uruchamia produkcyjny build w prawdziwym profilu Google Chrome przez ChromeDriver. Test wymaga, aby worker kontrolował już pierwsze uruchomienie bez przechodzenia na `about:blank`, następnie zamyka lokalny serwer, włącza ścisły tryb offline i potwierdza ponowne wyrenderowanie tej samej wersji wyłącznie z service workera.
""",
    """- worker nie aktywuje się po kompletnym precache albo nie przejmuje klientów;
- konfiguracja aktualizacji service workera jest niekompletna;
- wygenerowany runtime zawiera znany adres CDN renderera lub fontów;
- brakuje lokalnego JavaScript albo WebAssembly CanvasKit.

Dodatkowo `tool/smoke_test_offline_pwa.py` uruchamia produkcyjny build w prawdziwym profilu Google Chrome przez ChromeDriver. Test wymaga, aby worker kontrolował już pierwsze uruchomienie bez przechodzenia na `about:blank`, oraz odrzuca wszystkie zewnętrzne zasoby startowe poza opcjonalnym Umami. Następnie czyści i wyłącza zwykły HTTP cache, zachowując CacheStorage service workera, zamyka lokalny serwer, odcina sieć i potwierdza ponowne wyrenderowanie tej samej wersji wyłącznie z lokalnej paczki PWA.
""",
)

deployment = Path("DEPLOYMENT.md")
replace_once(
    deployment,
    """Aplikacja jest statycznym PWA. Obliczenia wykonują się lokalnie w przeglądarce; GitHub Pages dostarcza wyłącznie pliki aplikacji.

## Archiwalne ścieżki alternatywne
""",
    """Aplikacja jest statycznym PWA. Obliczenia wykonują się lokalnie w przeglądarce; GitHub Pages dostarcza wyłącznie pliki aplikacji.

## Wymagany build bez CDN

Każdy webowy artefakt InfusionCalc musi być budowany jako samowystarczalny runtime:

```bash
flutter build web \\
  --release \\
  --base-href / \\
  --no-web-resources-cdn
```

Opcja `--no-web-resources-cdn` jest obowiązkowa dla produkcji i archiwalnego kontenera mini-PC. Zapewnia lokalne pliki CanvasKit, WebAssembly i innych zasobów Fluttera zamiast zależności od zewnętrznego CDN.

Przed publikacją `tool/finalize_web_pwa.py` odrzuca znane adresy CDN i brak lokalnego renderera. `tool/smoke_test_offline_pwa.py` dodatkowo czyści zwykły HTTP cache, odcina serwer i sieć oraz potwierdza uruchomienie wyłącznie z CacheStorage service workera. GitHub Pages nie zostanie wdrożony, jeżeli którakolwiek z tych bramek zawiedzie.

## Archiwalne ścieżki alternatywne
""",
)
replace_once(
    deployment,
    """- GitHub Pages jest jedyną automatyczną ścieżką wdrożenia publicznego.
- Alternatywne workflow uruchamia się wyłącznie ręcznie przez `workflow_dispatch`.
""",
    """- GitHub Pages jest jedyną automatyczną ścieżką wdrożenia publicznego.
- Każdy build webowy używa `--no-web-resources-cdn` i przechodzi walidację samowystarczalnego runtime.
- Alternatywne workflow uruchamia się wyłącznie ręcznie przez `workflow_dispatch`.
""",
)

print("Updated project documentation for 0.1.3-beta.6+21.")
