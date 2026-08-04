#!/usr/bin/env python3
"""Document the pinned same-origin fallback font used by the offline PWA."""

from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"Expected one matching block in {path}, found {count}: {old[:160]!r}",
        )
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


replace_once(
    Path("CHANGELOG.md"),
    """- finalizer wymaga lokalnych plików JavaScript i WebAssembly CanvasKit, a test przeglądarkowy odrzuca rzeczywiście żądane zewnętrzne zasoby startowe;
- produkcyjny artefakt musi zawierać lokalne pliki JavaScript i WebAssembly CanvasKit.
""",
    """- finalizer wymaga lokalnych plików JavaScript i WebAssembly CanvasKit oraz przypiętego lokalnego fallbacku Roboto;
- bootstrap Fluttera kieruje `fontFallbackBaseUrl` do `fallback-fonts/`, zamiast pobierać Roboto z `fonts.gstatic.com`;
- build pobiera Roboto Regular WOFF2, sprawdza rozmiar, sygnaturę i SHA-256 `35b02ca266b79eb4996590f15817425a1ce9ebf48f84471843233ff614656bf2`;
- kopia licencji SIL Open Font License 1.1 jest dostarczana razem z PWA.
""",
)

replace_once(
    Path("README.md"),
    """Od wersji `0.1.3-beta.4` produkcyjny build tworzy kompletny `offline-manifest.json` obejmujący kod Fluttera, assety, fonty, ikony i pliki renderera obecne w danym wydaniu. Wersja `0.1.3-beta.5` poprawiła aktywację na iOS: po atomowym zapisaniu pełnej paczki nowy worker opuszcza stan `waiting`, przejmuje klientów bez przeładowania formularza i pomija ukryte metadane buildu. Wersja `0.1.3-beta.6` usuwa ostatnią zewnętrzną zależność startową: wszystkie buildy używają `--no-web-resources-cdn`, dlatego CanvasKit i WebAssembly są dostarczane lokalnie z `infusioncalc.eu`, a nie z CDN Fluttera. Po co najmniej jednym pełnym uruchomieniu online aplikację można uruchomić z ekranu głównego i wykonywać obliczenia bez internetu.
""",
    """Od wersji `0.1.3-beta.4` produkcyjny build tworzy kompletny `offline-manifest.json` obejmujący kod Fluttera, assety, fonty, ikony i pliki renderera obecne w danym wydaniu. Wersja `0.1.3-beta.5` poprawiła aktywację na iOS: po atomowym zapisaniu pełnej paczki nowy worker opuszcza stan `waiting`, przejmuje klientów bez przeładowania formularza i pomija ukryte metadane buildu. Wersja `0.1.3-beta.6` usuwa ostatnie zewnętrzne zależności startowe: build używa `--no-web-resources-cdn`, CanvasKit i WebAssembly pochodzą z `infusioncalc.eu`, a przypięty fallback Roboto jest pobierany i weryfikowany podczas buildu oraz obsługiwany z lokalnego katalogu `fallback-fonts/`. Po co najmniej jednym pełnym uruchomieniu online aplikację można uruchomić z ekranu głównego i wykonywać obliczenia bez internetu.
""",
)

replace_once(
    Path("README.md"),
    "- [Analityka](docs/ANALYTICS.md)\n- [Feedback po pierwszych testach]",
    "- [Analityka](docs/ANALYTICS.md)\n- [Informacje o komponentach zewnętrznych](THIRD_PARTY_NOTICES.md)\n- [Feedback po pierwszych testach]",
)

replace_once(
    Path("ROADMAP.md"),
    """- [x] lokalny CanvasKit JavaScript i WebAssembly w paczce aplikacji;
- [x] wymaganie kompletnego lokalnego CanvasKit JavaScript i WebAssembly;
- [x] dynamiczne odrzucanie zewnętrznych zasobów startowych poza opcjonalnym Umami;
""",
    """- [x] lokalny CanvasKit JavaScript i WebAssembly w paczce aplikacji;
- [x] wymaganie kompletnego lokalnego CanvasKit JavaScript i WebAssembly;
- [x] `fontFallbackBaseUrl` skierowany do lokalnego katalogu PWA;
- [x] przypięty Roboto Regular WOFF2 z kontrolą rozmiaru, sygnatury i SHA-256;
- [x] licencja SIL Open Font License 1.1 i `THIRD_PARTY_NOTICES.md`;
- [x] dynamiczne odrzucanie zewnętrznych zasobów startowych poza opcjonalnym Umami;
""",
)

replace_once(
    Path("docs/OFFLINE_PWA.md"),
    """Produkcyjny build jest wykonywany z opcją `--no-web-resources-cdn`. Kod uruchamiający Fluttera, `main.dart.js`, lokalny CanvasKit, pliki WebAssembly, fonty, ikony i pozostałe assety pochodzą z tego samego originu `infusioncalc.eu`.

Domyślna konfiguracja Flutter Web może używać zewnętrznego CDN dla renderera. Taki build może pozornie przejść test offline w przeglądarce, jeżeli renderer pozostaje w zwykłym HTTP cache po uruchomieniu online, ale zawiedzie na czystej instalacji lub w Home Screen PWA bez internetu. Finalizer wymaga kompletnego lokalnego pakietu renderera, a test przeglądarkowy po wyczyszczeniu zwykłego cache odrzuca rzeczywiście pobierane zewnętrzne zasoby startowe. Same nieużywane stałe awaryjne pozostawione w wygenerowanym loaderze nie są traktowane jako żądanie sieciowe.
""",
    """Produkcyjny build jest wykonywany z opcją `--no-web-resources-cdn`. Kod uruchamiający Fluttera, `main.dart.js`, lokalny CanvasKit, pliki WebAssembly, fonty, ikony i pozostałe assety pochodzą z tego samego originu `infusioncalc.eu`.

Domyślna konfiguracja Flutter Web może używać zewnętrznego CDN dla renderera, a CanvasKit może poprosić `fonts.gstatic.com` o fallback Roboto. Taki build może pozornie przejść test offline, jeżeli te pliki pozostają w zwykłym HTTP cache po uruchomieniu online, ale zawiedzie na czystej instalacji lub w Home Screen PWA bez internetu.

Dlatego `_flutter.loader.load()` otrzymuje `fontFallbackBaseUrl: 'fallback-fonts/'`. Skrypt `tool/prepare_web_fallback_fonts.py` pobiera dokładnie przypięty plik Roboto Regular WOFF2, weryfikuje rozmiar `63464` bajtów, sygnaturę WOFF2 i SHA-256 `35b02ca266b79eb4996590f15817425a1ce9ebf48f84471843233ff614656bf2`. Font oraz licencja SIL Open Font License 1.1 trafiają do pełnego manifestu offline.

Finalizer wymaga kompletnego lokalnego CanvasKit i zweryfikowanego fontu, a test przeglądarkowy po wyczyszczeniu zwykłego cache odrzuca rzeczywiście pobierane zewnętrzne zasoby startowe. Same nieużywane stałe awaryjne pozostawione w wygenerowanym loaderze nie są traktowane jako żądanie sieciowe.
""",
)

replace_once(
    Path("docs/OFFLINE_PWA.md"),
    """2. uwzględnia kod aplikacji, bootstrap Fluttera, assety, fonty, ikony i pliki renderera obecne w danym buildzie;
3. pomija ukryte techniczne metadane buildu, takie jak `.last_build_id`, które nie są potrzebne aplikacji i mogą nie być publikowane przez statyczny hosting;
""",
    """2. uwzględnia kod aplikacji, bootstrap Fluttera, lokalny CanvasKit, zweryfikowany fallback Roboto, licencję fontu, pozostałe assety i ikony;
3. pomija ukryte techniczne metadane buildu, takie jak `.last_build_id`, które nie są potrzebne aplikacji i mogą nie być publikowane przez statyczny hosting;
""",
)

replace_once(
    Path("DEPLOYMENT.md"),
    """Opcja `--no-web-resources-cdn` jest obowiązkowa dla produkcji i archiwalnego kontenera mini-PC. Zapewnia lokalne pliki CanvasKit, WebAssembly i innych zasobów Fluttera zamiast zależności od zewnętrznego CDN.

Przed publikacją `tool/finalize_web_pwa.py` wymaga kompletnego lokalnego renderera CanvasKit. `tool/smoke_test_offline_pwa.py` czyści zwykły HTTP cache, odcina serwer i sieć, odrzuca rzeczywiście żądane zewnętrzne zasoby startowe oraz potwierdza uruchomienie wyłącznie z CacheStorage service workera. GitHub Pages nie zostanie wdrożony, jeżeli którakolwiek z tych bramek zawiedzie.
""",
    """Opcja `--no-web-resources-cdn` jest obowiązkowa dla produkcji i archiwalnego kontenera mini-PC. Zapewnia lokalne pliki CanvasKit, WebAssembly i innych zasobów Fluttera zamiast zależności od zewnętrznego CDN.

Przed buildem `tool/prepare_web_fallback_fonts.py` pobiera przypięty Roboto Regular WOFF2 i odrzuca plik o innym rozmiarze, sygnaturze lub SHA-256. Bootstrap ustawia `fontFallbackBaseUrl: 'fallback-fonts/'`, dlatego CanvasKit nie potrzebuje `fonts.gstatic.com`. Licencja OFL jest publikowana w `fallback-fonts/roboto/OFL.txt`, a pełne informacje znajdują się w `THIRD_PARTY_NOTICES.md`.

Przed publikacją `tool/finalize_web_pwa.py` wymaga kompletnego lokalnego renderera CanvasKit i zweryfikowanego fallbacku fontu. `tool/smoke_test_offline_pwa.py` czyści zwykły HTTP cache, odcina serwer i sieć, odrzuca rzeczywiście żądane zewnętrzne zasoby startowe oraz potwierdza uruchomienie wyłącznie z CacheStorage service workera. GitHub Pages nie zostanie wdrożony, jeżeli którakolwiek z tych bramek zawiedzie.
""",
)

print("Updated documentation for the local Roboto fallback.")
