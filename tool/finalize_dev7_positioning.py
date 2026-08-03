from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding='utf-8')
    if old not in source:
        raise SystemExit(f'Expected block not found in {path}: {old[:120]!r}')
    path.write_text(source.replace(old, new, 1), encoding='utf-8')


def replace_all(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding='utf-8')
    if old not in source:
        raise SystemExit(f'Expected text not found in {path}: {old!r}')
    path.write_text(source.replace(old, new), encoding='utf-8')


readme = Path('README.md')
replace_once(
    readme,
    '> [!WARNING]\n'
    '> Projekt znajduje się na etapie projektowania i prototypowania. Nie jest obecnie zwalidowany, certyfikowany ani przeznaczony do podejmowania decyzji klinicznych. Przed zastosowaniem klinicznym lub publiczną dystrybucją konieczne są niezależna weryfikacja obliczeń, walidacja produktu oraz ocena wymagań prawnych i regulacyjnych.\n',
    '> [!WARNING]\n'
    '> Obecna wersja jest technicznym kalkulatorem przeliczeń. Nie zawiera zaleceń dawkowania, biblioteki leków ani interpretacji klinicznej i nie jest przeznaczona do podejmowania decyzji klinicznych. Wynik jest rezultatem matematycznym, który wymaga niezależnej weryfikacji przed jakimkolwiek zastosowaniem klinicznym.\n',
)
replace_once(
    readme,
    'Poza zakresem MVP pozostają m.in. biblioteka leków, sugerowane dawki, synchronizacja, konta użytkowników i przechowywanie danych pacjentów.\n',
    'Poza zakresem MVP pozostają m.in. biblioteka leków, sugerowane dawki, synchronizacja, konta użytkowników i przechowywanie danych pacjentów.\n\n'
    '**Deklarowane przeznaczenie obecnej wersji:** techniczny kalkulator wykonujący jawne przeliczenia matematyczne i jednostkowe na podstawie danych wpisanych przez użytkownika. Aplikacja nie ocenia poprawności klinicznej danych, nie dobiera terapii i nie służy do podejmowania decyzji klinicznych.\n',
)
replace_once(
    readme,
    'Przed określeniem sposobu dystrybucji i deklarowanego zastosowania należy przeprowadzić formalną ocenę kwalifikacji produktu oraz wymagań dotyczących oprogramowania medycznego. Zakres tej oceny zależy m.in. od deklarowanego przeznaczenia, grupy użytkowników, środowiska użycia i potencjalnych konsekwencji błędnego wyniku.\n',
    'Obecne deklarowane przeznaczenie ogranicza produkt do technicznego kalkulatora przeliczeń, bez zaleceń, interpretacji klinicznej i wspierania decyzji terapeutycznych. Ewentualna przyszła zmiana przeznaczenia, sposobu dystrybucji albo funkcji produktu wymaga osobnej oceny kwalifikacji oraz wymagań prawnych i regulacyjnych.\n',
)
replace_once(
    readme,
    '**Etap:** `0.1.0-dev.6` — preferencje lokalne i utwardzenie walidacji  \n'
    '**Planowana pierwsza wersja:** `0.1.0`  \n'
    '**Platformy docelowe:** iOS i Android  \n'
    '**Model działania:** offline-first\n',
    '**Etap:** `0.1.0-dev.7` — testy właściwościowe i utwardzenie przed MVP  \n'
    '**Planowana pierwsza wersja:** `0.1.0`  \n'
    '**Charakter produktu:** techniczny kalkulator, bez zaleceń klinicznych  \n'
    '**Platformy docelowe:** iOS i Android  \n'
    '**Model działania:** offline-first\n',
)

changelog = Path('CHANGELOG.md')
replace_once(
    changelog,
    '## [0.1.0-dev.6] — w przygotowaniu\n',
    '''## [0.1.0-dev.7] — w przygotowaniu

### Dodano

- 3000 deterministycznych prób dokładnej odwracalności podstawowych równań;
- 4000 porównań solvera po kontrolowanym przetasowaniu kolejności wejść;
- pełną macierz zgodnych konwersji jednostek MVP w obie strony;
- testy rozdzielenia IU i jednostek masy we wszystkich rodzinach wielkości;
- testy graniczne wektorów wymiarów, jednostek prostych i jednostek złożonych;
- przypięty graf zależności w `pubspec.lock` oraz jego egzekwowanie w CI;
- obowiązkowy próg co najmniej 90% pokrycia liniowego kodu `lib/domain/`;
- jednoznaczne oznaczenie produktu jako technicznego kalkulatora bez zaleceń i interpretacji klinicznej.

### Wyniki automatycznej walidacji

- `127/127` testów zakończonych powodzeniem;
- `93,47%` pokrycia liniowego warstwy domenowej (`716/766` linii);
- poprawne buildy kontrolne Androida i iOS;
- zielone formatowanie i analiza statyczna bez ostrzeżeń.

### Deklarowane przeznaczenie

- aplikacja wykonuje techniczne przeliczenia matematyczne i jednostkowe na podstawie danych użytkownika;
- nie zawiera biblioteki leków, zaleceń dawkowania ani interpretacji klinicznej;
- nie jest przeznaczona do podejmowania decyzji klinicznych.

## [0.1.0-dev.6] — 2026-08-03
''',
)
replace_all(
    changelog,
    'aplikacja pozostaje prototypem nieprzeznaczonym do podejmowania decyzji klinicznych.',
    'aplikacja pozostaje technicznym kalkulatorem nieprzeznaczonym do podejmowania decyzji klinicznych.',
)

roadmap = Path('ROADMAP.md')
replace_once(
    roadmap,
    '**Aktualny etap:** `0.1.0-dev.6 — preferencje i utwardzenie`',
    '**Aktualny etap:** `0.1.0-dev.7 — testy i utwardzenie przed MVP`',
)
replace_once(
    roadmap,
    '- brak funkcji klinicznej bez testów referencyjnych;',
    '- techniczne MVP nie zawiera rekomendacji dawkowania ani interpretacji klinicznej;',
)
replace_once(
    roadmap,
    '### 0.1.0-dev.6 — Utrwalanie ustawień i obsługa błędów **← obecnie**',
    '### 0.1.0-dev.6 — Utrwalanie ustawień i obsługa błędów **✓ ukończono**',
)
replace_once(
    roadmap,
    '### 0.1.0-dev.7 — Testy referencyjne i utwardzenie',
    '### 0.1.0-dev.7 — Testy referencyjne i utwardzenie **← obecnie**',
)
for item in (
    'przypadki referencyjne dla każdej jednostki',
    'testy odwracalności',
    'testy właściwości',
    'testy konfliktów',
    'testy kolejności edycji',
    'testy obliczeń kaskadowych',
    'testy lokalizacji separatora dziesiętnego',
    'testy widgetów',
    'testy integracyjne głównych scenariuszy',
    'minimalny próg pokrycia kodu domenowego',
):
    replace_once(roadmap, f'- [ ] {item};', f'- [x] {item};')
replace_once(
    roadmap,
    '- [ ] ręczny przegląd wzorów przez drugą osobę.\n\n### 0.1.0 — Pierwsze kompletne MVP',
    '- [ ] ręczny przegląd wzorów przez drugą osobę.\n\n'
    '**Stan automatycznej walidacji:** `127/127` testów, `93,47%` pokrycia warstwy domenowej oraz poprawne buildy Androida i iOS.\n\n'
    '**Pozycjonowanie produktu:** obecna wersja jest technicznym kalkulatorem przeliczeń. Nie zawiera zaleceń ani interpretacji klinicznej i nie jest przeznaczona do podejmowania decyzji klinicznych.\n\n'
    '### 0.1.0 — Pierwsze kompletne MVP',
)
replace_once(
    roadmap,
    '**Bramka wydania:** wersja może być przekazana wyłącznie jako jasno oznaczony prototyp testowy, dopóki nie zostanie ukończona niezależna walidacja i ocena sposobu dystrybucji.',
    '**Bramka wydania:** wersja `0.1.0` może zostać oznaczona wyłącznie jako techniczny kalkulator bez zaleceń klinicznych. Ewentualne przyszłe przeznaczenie kliniczne wymaga osobnej decyzji, niezależnej walidacji i oceny sposobu dystrybucji.',
)

vision = Path('docs/VISION.md')
replace_once(
    vision,
    '> Użytkownik wpisuje dowolne znane parametry, a aplikacja natychmiast pokazuje wszystkie wartości, które można z nich jednoznacznie obliczyć.\n\n'
    'Aplikacja nie narzuca osobnego trybu pracy,',
    '> Użytkownik wpisuje dowolne znane parametry, a aplikacja natychmiast pokazuje wszystkie wartości, które można z nich jednoznacznie obliczyć.\n\n'
    '**Obecne deklarowane przeznaczenie:** techniczny kalkulator przeliczeń matematycznych i jednostkowych. Aplikacja nie dobiera terapii, nie interpretuje klinicznie wyniku i nie jest przeznaczona do podejmowania decyzji klinicznych.\n\n'
    'Aplikacja nie narzuca osobnego trybu pracy,',
)
replace_once(
    vision,
    'Przed oznaczeniem wersji jako przeznaczonej do rzeczywistego użycia wszystkie krytyczne równania, przypadki referencyjne i zachowania interfejsu powinny zostać niezależnie zweryfikowane przez co najmniej jedną osobę inną niż autor implementacji.',
    'Przed jakąkolwiek przyszłą zmianą deklarowanego przeznaczenia w kierunku zastosowania klinicznego wszystkie krytyczne równania, przypadki referencyjne i zachowania interfejsu powinny zostać niezależnie zweryfikowane przez co najmniej jedną osobę inną niż autor implementacji.',
)

ux = Path('docs/UX_SPEC.md')
replace_once(
    ux,
    'Na górze stale widoczne jest oznaczenie prototypu testowego. W prawym górnym rogu znajduje się akcja „Wyczyść”.',
    'Na górze stale widoczne jest oznaczenie, że aplikacja jest technicznym kalkulatorem nieprzeznaczonym do podejmowania decyzji klinicznych. W prawym górnym rogu znajduje się akcja „Wyczyść”.',
)

screen = Path('lib/presentation/calculator/calculator_screen.dart')
replace_once(
    screen,
    "    label: 'Ostrzeżenie: prototyp nie jest przeznaczony do użycia klinicznego.',",
    "    label: 'Ostrzeżenie: techniczny kalkulator nie jest przeznaczony do podejmowania decyzji klinicznych.',",
)
replace_once(
    screen,
    "                'Prototyp — nie używać do podejmowania decyzji klinicznych.',",
    "                'Techniczny kalkulator — nie jest przeznaczony do podejmowania decyzji klinicznych.',",
)

test = Path('test/presentation/calculator_screen_test.dart')
replace_once(
    test,
    "      find.text('Prototyp — nie używać do podejmowania decyzji klinicznych.'),",
    "      find.text(\n"
    "        'Techniczny kalkulator — nie jest przeznaczony do podejmowania ' \n"
    "        'decyzji klinicznych.',\n"
    "      ),",
)

pubspec = Path('pubspec.yaml')
replace_once(
    pubspec,
    'description: Offline, bidirectional infusion calculator prototype for iOS and Android.',
    'description: Offline technical bidirectional infusion calculator for iOS and Android.',
)
