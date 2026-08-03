from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding='utf-8')
    if old not in source:
        raise SystemExit(f'Expected block not found in {path}: {old[:180]!r}')
    path.write_text(source.replace(old, new, 1), encoding='utf-8')


screen = Path('lib/presentation/calculator/calculator_screen.dart')
replace_once(
    screen,
    "  QuantityKind get _visibleDoseKind => _dosePerKilogram\n"
    "      ? QuantityKind.weightNormalizedDose\n"
    "      : QuantityKind.administrationRate;\n\n"
    "  TextEditingController _controller(QuantityKind kind) => _controllers[kind]!;\n",
    "  QuantityKind get _visibleDoseKind => _dosePerKilogram\n"
    "      ? QuantityKind.weightNormalizedDose\n"
    "      : QuantityKind.administrationRate;\n\n"
    "  bool get _hasActiveNumericState =>\n"
    "      _solution.userInputs.isNotEmpty || _inputErrors.isNotEmpty;\n\n"
    "  bool get _shouldIgnorePendingPreferenceRestore =>\n"
    "      _hasLocalPreferenceEdit || _hasActiveNumericState;\n\n"
    "  TextEditingController _controller(QuantityKind kind) => _controllers[kind]!;\n",
)
replace_once(
    screen,
    "      if (!mounted || _hasLocalPreferenceEdit) {\n"
    "        return;\n"
    "      }\n"
    "      setState(() {\n"
    "        for (final QuantityKind kind in CalculatorPreferences.persistedKinds) {\n",
    "      if (!mounted || _shouldIgnorePendingPreferenceRestore) {\n"
    "        return;\n"
    "      }\n"
    "      setState(() {\n"
    "        for (final QuantityKind kind in CalculatorPreferences.persistedKinds) {\n",
)
replace_once(
    screen,
    "    } on Object {\n"
    "      if (!mounted || _hasLocalPreferenceEdit) {\n"
    "        return;\n"
    "      }\n",
    "    } on Object {\n"
    "      if (!mounted || _shouldIgnorePendingPreferenceRestore) {\n"
    "        return;\n"
    "      }\n",
)

pubspec = Path('pubspec.yaml')
replace_once(pubspec, 'version: 0.1.1-dev.1+9', 'version: 0.1.1-dev.2+10')

readme = Path('README.md')
replace_once(
    readme,
    '**Wersja rozwojowa:** `0.1.1-dev.1+9` — stabilizacja stanu formularza  ',
    '**Wersja rozwojowa:** `0.1.1-dev.2+10` — bezpieczne przywracanie preferencji  ',
)

changelog = Path('CHANGELOG.md')
replace_once(
    changelog,
    '## [0.1.1-dev.1] — w przygotowaniu\n',
    '''## [0.1.1-dev.2] — w przygotowaniu

### Poprawiono

- opóźniony odczyt zapisanych jednostek nie może już zmienić etykiety jednostki po wpisaniu wartości podczas uruchamiania aplikacji;
- preferencje nie są nakładane, gdy formularz zawiera jawne wejście albo nieprawidłowy tekst;
- po całkowitym wyczyszczeniu przejściowych wartości oczekujące preferencje mogą zostać bezpiecznie zastosowane;
- liczba, widoczna jednostka i wartość używana przez solver pozostają zawsze zgodne.

### Testy regresji

- szybkie wpisanie `1 mg` przed zakończeniem odczytu preferencji nadal daje `1000 µg/ml` dla `1 ml` i pozostawia etykietę `mg`;
- zapisany tryb oraz jednostka mogą zostać przywrócone, gdy użytkownik przed zakończeniem odczytu wyczyści cały formularz.

## [0.1.1-dev.1] — 2026-08-03
''',
)

roadmap = Path('ROADMAP.md')
replace_once(
    roadmap,
    '**Aktualny etap:** `0.1.1-dev.1 — stabilizacja stanu formularza`',
    '**Aktualny etap:** `0.1.1-dev.2 — bezpieczne przywracanie preferencji`',
)
replace_once(
    roadmap,
    '**Pierwsza poprawka:** bezpieczne, transakcyjne przełączanie dawki `/kg` i szybkości podaży bez pozostawiania niewidocznych wejść.\n',
    '**Pierwsza poprawka:** bezpieczne, transakcyjne przełączanie dawki `/kg` i szybkości podaży bez pozostawiania niewidocznych wejść.\n\n'
    '**Druga poprawka:** opóźniony odczyt preferencji nie może zmienić jednostki prezentacji po rozpoczęciu wpisywania danych; zapobiega to rozbieżności między widoczną liczbą a wartością solvera.\n',
)
