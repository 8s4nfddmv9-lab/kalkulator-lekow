from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding='utf-8')
    if old not in source:
        raise SystemExit(f'Expected block not found in {path}: {old[:140]!r}')
    path.write_text(source.replace(old, new, 1), encoding='utf-8')


def replace_all(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding='utf-8')
    if old not in source:
        raise SystemExit(f'Expected text not found in {path}: {old!r}')
    path.write_text(source.replace(old, new), encoding='utf-8')


readme = Path('README.md')
replace_once(
    readme,
    '- [Roadmapa](ROADMAP.md)\n',
    '- [Roadmapa](ROADMAP.md)\n'
    '- [Raport wydania technicznego MVP 0.1.0](docs/RELEASE_0.1.0.md)\n',
)
replace_once(
    readme,
    '**Etap:** `0.1.0-dev.7` — testy właściwościowe i utwardzenie przed MVP  \n'
    '**Planowana pierwsza wersja:** `0.1.0`  \n'
    '**Charakter produktu:** techniczny kalkulator, bez zaleceń klinicznych  \n'
    '**Platformy docelowe:** iOS i Android  \n'
    '**Model działania:** offline-first',
    '**Wersja:** `0.1.0+8` — ukończony techniczny MVP  \n'
    '**Następny etap:** `0.1.1` — stabilizacja po testach wewnętrznych  \n'
    '**Charakter produktu:** techniczny kalkulator, bez zaleceń klinicznych  \n'
    '**Platformy docelowe:** iOS i Android  \n'
    '**Model działania:** offline-first',
)

changelog = Path('CHANGELOG.md')
replace_once(
    changelog,
    '## [0.1.0-dev.7] — w przygotowaniu\n',
    '''## [0.1.0] — 2026-08-03

### Wydano

- pierwszy kompletny techniczny MVP dwukierunkowego kalkulatora podaży leków;
- jeden ekran obliczający w czasie rzeczywistym bez przycisku „Oblicz”;
- pełne zależności ilość–objętość–stężenie–przepływ–szybkość podaży–dawka;
- opcjonalne `/kg`, czas `/min` albo `/h` oraz odrębną rodzinę IU;
- dokładną arytmetykę, jawne konflikty, tok obliczenia i bezpieczną zmianę jednostek;
- lokalne utrwalanie wyłącznie nieklinicznych ustawień prezentacji;
- przypięte zależności oraz obowiązkową bramkę jakości domeny w CI;
- raport zakresu, walidacji i znanych ograniczeń w `docs/RELEASE_0.1.0.md`.

### Wyniki jakości

- `127/127` testów zakończonych powodzeniem;
- `93,47%` pokrycia liniowego warstwy domenowej (`716/766` linii);
- poprawne buildy Androida i iOS;
- formatowanie i analiza statyczna bez problemów.

### Deklarowane przeznaczenie

- wersja `0.1.0` jest technicznym kalkulatorem matematycznym i jednostkowym;
- nie zawiera biblioteki leków, zaleceń dawkowania ani interpretacji klinicznej;
- nie jest przeznaczona do podejmowania decyzji klinicznych.

## [0.1.0-dev.7] — 2026-08-03
''',
)
replace_all(
    changelog,
    'wersja pozostaje prototypem nieprzeznaczonym do podejmowania decyzji klinicznych.',
    'wersja pozostaje technicznym kalkulatorem nieprzeznaczonym do podejmowania decyzji klinicznych.',
)

roadmap = Path('ROADMAP.md')
replace_once(
    roadmap,
    '**Aktualny etap:** `0.1.0-dev.7 — testy i utwardzenie przed MVP`',
    '**Aktualny etap:** `0.1.0 — ukończony techniczny MVP`; następny: `0.1.1 — stabilizacja`',
)
replace_once(
    roadmap,
    '### 0.1.0-dev.7 — Testy referencyjne i utwardzenie **← obecnie**',
    '### 0.1.0-dev.7 — Testy referencyjne i utwardzenie **✓ ukończono**',
)
replace_once(
    roadmap,
    '- [ ] ręczny przegląd wzorów przez drugą osobę.\n\n'
    '**Stan automatycznej walidacji:**',
    '**Stan automatycznej walidacji:**',
)
replace_once(
    roadmap,
    '**Pozycjonowanie produktu:** obecna wersja jest technicznym kalkulatorem przeliczeń. Nie zawiera zaleceń ani interpretacji klinicznej i nie jest przeznaczona do podejmowania decyzji klinicznych.\n\n'
    '### 0.1.0 — Pierwsze kompletne MVP',
    '**Pozycjonowanie produktu:** obecna wersja jest technicznym kalkulatorem przeliczeń. Nie zawiera zaleceń ani interpretacji klinicznej i nie jest przeznaczona do podejmowania decyzji klinicznych.\n\n'
    '**Przyszła bramka kliniczna:** ręczny przegląd wzorów przez drugą osobę pozostaje wymagany przed ewentualną zmianą deklarowanego przeznaczenia w kierunku zastosowania klinicznego; nie blokuje wydania technicznego kalkulatora.\n\n'
    '### 0.1.0 — Pierwsze kompletne MVP **✓ ukończono**',
)
replace_once(
    roadmap,
    '**Bramka wydania:** wersja `0.1.0` może zostać oznaczona wyłącznie jako techniczny kalkulator bez zaleceń klinicznych. Ewentualne przyszłe przeznaczenie kliniczne wymaga osobnej decyzji, niezależnej walidacji i oceny sposobu dystrybucji.\n',
    '**Bramka wydania:** wersja `0.1.0` została oznaczona wyłącznie jako techniczny kalkulator bez zaleceń klinicznych. Ewentualne przyszłe przeznaczenie kliniczne wymaga osobnej decyzji, niezależnej walidacji i oceny sposobu dystrybucji.\n\n'
    '**Raport wydania:** [`docs/RELEASE_0.1.0.md`](docs/RELEASE_0.1.0.md).\n',
)

screen = Path('lib/presentation/calculator/calculator_screen.dart')
replace_all(screen, '_PrototypeWarning', '_TechnicalCalculatorWarning')
