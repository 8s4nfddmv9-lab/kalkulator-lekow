#!/usr/bin/env python3
"""Align documentation with runtime-request validation after beta.6 CI review."""

from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"Expected exactly one match in {path}, found {count}: {old[:160]!r}",
        )
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


replace_once(
    Path("CHANGELOG.md"),
    "- finalizer odrzuca wygenerowany runtime zawierający znane adresy CDN renderera lub fontów;",
    "- finalizer wymaga lokalnych plików JavaScript i WebAssembly CanvasKit, a test przeglądarkowy odrzuca rzeczywiście żądane zewnętrzne zasoby startowe;",
)

replace_once(
    Path("ROADMAP.md"),
    "- [x] statyczne odrzucanie adresów CDN renderera i fontów;",
    "- [x] wymaganie kompletnego lokalnego CanvasKit JavaScript i WebAssembly;",
)

replace_once(
    Path("docs/OFFLINE_PWA.md"),
    "Domyślna konfiguracja Flutter Web może używać zewnętrznego CDN dla renderera. Taki build może pozornie przejść test offline w przeglądarce, jeżeli renderer pozostaje w zwykłym HTTP cache po uruchomieniu online, ale zawiedzie na czystej instalacji lub w Home Screen PWA bez internetu. Finalizer i test przeglądarkowy jawnie odrzucają tę zależność.",
    "Domyślna konfiguracja Flutter Web może używać zewnętrznego CDN dla renderera. Taki build może pozornie przejść test offline w przeglądarce, jeżeli renderer pozostaje w zwykłym HTTP cache po uruchomieniu online, ale zawiedzie na czystej instalacji lub w Home Screen PWA bez internetu. Finalizer wymaga kompletnego lokalnego pakietu renderera, a test przeglądarkowy po wyczyszczeniu zwykłego cache odrzuca rzeczywiście pobierane zewnętrzne zasoby startowe. Same nieużywane stałe awaryjne pozostawione w wygenerowanym loaderze nie są traktowane jako żądanie sieciowe.",
)

replace_once(
    Path("docs/OFFLINE_PWA.md"),
    "- wygenerowany runtime zawiera znany adres CDN renderera lub fontów;",
    "- produkcyjny artefakt nie zawiera kompletnego lokalnego pakietu CanvasKit;",
)

replace_once(
    Path("DEPLOYMENT.md"),
    "Przed publikacją `tool/finalize_web_pwa.py` odrzuca znane adresy CDN i brak lokalnego renderera. `tool/smoke_test_offline_pwa.py` dodatkowo czyści zwykły HTTP cache, odcina serwer i sieć oraz potwierdza uruchomienie wyłącznie z CacheStorage service workera. GitHub Pages nie zostanie wdrożony, jeżeli którakolwiek z tych bramek zawiedzie.",
    "Przed publikacją `tool/finalize_web_pwa.py` wymaga kompletnego lokalnego renderera CanvasKit. `tool/smoke_test_offline_pwa.py` czyści zwykły HTTP cache, odcina serwer i sieć, odrzuca rzeczywiście żądane zewnętrzne zasoby startowe oraz potwierdza uruchomienie wyłącznie z CacheStorage service workera. GitHub Pages nie zostanie wdrożony, jeżeli którakolwiek z tych bramek zawiedzie.",
)

print("Aligned offline runtime documentation with actual-request validation.")
