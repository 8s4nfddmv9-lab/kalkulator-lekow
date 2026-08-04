#!/usr/bin/env python3
"""Apply one-time documentation updates for the stable v0.1.3 release."""

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

## [0.1.3] — 2026-08-04

### Wydano

- pierwsze stabilne wydanie publicznego InfusionCalc;
- wersję aplikacji `0.1.3+22` oraz tag `v0.1.3`;
- dwukierunkowy kalkulator ilości leku, objętości, stężenia, przepływu i dawki;
- obsługę jednostek masy oraz oddzielnej rodziny `IU`;
- dawki z `/kg` i bez `/kg`, na minutę i na godzinę;
- instalowalne PWA dla iOS i Androida;
- pełny, samowystarczalny tryb offline po jednorazowym przygotowaniu wersji online.

### Stabilność i bezpieczeństwo techniczne

- dokładna arytmetyka domenowa bez zaokrąglania obliczeń pośrednich;
- wersjonowany zestaw referencyjny i testy odwracalności równań;
- wykrywanie danych sprzecznych, niezgodnych wymiarowo i dzielenia przez zero;
- lokalny CanvasKit, WebAssembly i zweryfikowany fallback Roboto;
- atomowy, wersjonowany cache PWA oraz diagnostyka startu;
- ścisły test uruchomienia po wyczyszczeniu zwykłego cache HTTP i odcięciu sieci;
- działanie offline potwierdzone na fizycznym iPhonie.

### Prywatność i dystrybucja

- brak kont użytkowników i własnego backendu;
- wartości formularza, masa, dawki, stężenia, przepływy i wyniki nie trafiają do analityki;
- minimalna analityka Umami pozostaje opcjonalna dla działania aplikacji;
- kod projektu jest udostępniany na licencji MIT;
- licencje komponentów zewnętrznych są opisane oddzielnie.

### Ograniczenia deklarowanego przeznaczenia

- InfusionCalc pozostaje technicznym kalkulatorem matematycznym;
- brak biblioteki leków, zakresów dawkowania, rekomendacji i interpretacji klinicznej;
- aplikacja nie jest przeznaczona do podejmowania decyzji klinicznych;
- wynik wymaga niezależnej weryfikacji przed jakimkolwiek zastosowaniem klinicznym.

""",
)

readme = Path("README.md")
replace_once(
    readme,
    "## Zakres MVP — v0.1.0\n\nPierwsza działająca wersja obejmuje:",
    "## Zakres stabilnego wydania — v0.1.3\n\nPierwsze stabilne wydanie obejmuje:",
)
replace_once(
    readme,
    "**Wersja publiczna:** `0.1.3-beta.6+21` — samowystarczalny runtime PWA bez zależności od CDN",
    "**Wersja publiczna:** `0.1.3+22` — pierwsze stabilne wydanie (`v0.1.3`)",
)

roadmap = Path("ROADMAP.md")
replace_once(
    roadmap,
    "**Aktualny etap:** `0.1.3-beta.6 — samowystarczalny runtime offline`",
    "**Aktualny etap:** `0.1.3 — pierwsze stabilne wydanie`",
)
replace_once(
    roadmap,
    "### 0.1.3-beta.6 — Samowystarczalny runtime offline **← obecnie**",
    "### 0.1.3-beta.6 — Samowystarczalny runtime offline **✓ ukończono**",
)
replace_once(
    roadmap,
    """**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3 — Dostępność i ergonomia
""",
    """**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3 — Pierwsze stabilne wydanie **← obecnie**

- [x] wersja aplikacji `0.1.3+22`;
- [x] pełny zakres technicznego kalkulatora dwukierunkowego;
- [x] wersjonowane testy referencyjne i polityka precyzji;
- [x] instalowalne PWA na iOS i Androidzie;
- [x] samowystarczalny pakiet offline bez wymaganych CDN;
- [x] potwierdzone uruchomienie i obliczenia offline na fizycznym iPhonie;
- [x] minimalna analityka bez wartości formularza;
- [x] licencja MIT i informacje o komponentach zewnętrznych;
- [x] pełne zielone CI przed scaleniem;
- [x] tag `v0.1.3` i stabilny GitHub Release;
- [x] automatyczne wdrożenie na `https://infusioncalc.eu/`.

**Zgłoszenie:** [issue #44](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/44).  
**Informacje o wydaniu:** [`releases/v0.1.3.md`](releases/v0.1.3.md).

### 0.1.4 — Dostępność i ergonomia
""",
)

print("Updated changelog, README and roadmap for stable v0.1.3.")
