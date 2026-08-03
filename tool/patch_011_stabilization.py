from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding='utf-8')
    if old not in source:
        raise SystemExit(f'Expected block not found in {path}: {old[:180]!r}')
    path.write_text(source.replace(old, new, 1), encoding='utf-8')


screen = Path('lib/presentation/calculator/calculator_screen.dart')
replace_once(
    screen,
    "              helperText: _dosePerKilogram\n"
    "                  ? 'Wynik wymaga wpisanej masy pacjenta.'\n"
    "                  : 'Ta wartość nie zależy od masy pacjenta.',\n",
    "              helperText: _dosePerKilogram\n"
    "                  ? 'Masa jest potrzebna do przeliczenia dawki /kg na ' \n"
    "                      'szybkość podaży lub przepływ.'\n"
    "                  : 'Ta wartość nie zależy od masy pacjenta.',\n",
)
replace_once(
    screen,
    "  void _toggleDosePerKilogram(bool enabled) {\n"
    "    setState(() {\n"
    "      _dosePerKilogram = enabled;\n"
    "      _globalMessage = null;\n"
    "      _synchronizeControllers();\n"
    "    });\n"
    "    _queuePreferencesSave();\n"
    "  }\n\n"
    "  Future<void> _restorePreferences() async {\n",
    "  void _toggleDosePerKilogram(bool enabled) {\n"
    "    if (enabled == _dosePerKilogram) {\n"
    "      return;\n"
    "    }\n\n"
    "    final QuantityKind outgoingKind = _visibleDoseKind;\n"
    "    final QuantityKind incomingKind = enabled\n"
    "        ? QuantityKind.weightNormalizedDose\n"
    "        : QuantityKind.administrationRate;\n"
    "    final SolverFact? outgoingInput = _solution.userInputs[outgoingKind];\n"
    "    final SolverFact? incomingInput = _solution.userInputs[incomingKind];\n"
    "    SolverSolution solution = _solution;\n"
    "    MeasurementUnit? transferredUnit;\n"
    "    Quantity? transferredQuantity;\n\n"
    "    if (outgoingInput != null && incomingInput == null) {\n"
    "      final SolverFact? counterpart = _solution.fact(incomingKind);\n"
    "      if (counterpart?.origin != SolverFactOrigin.calculated) {\n"
    "        setState(() {\n"
    "          _globalMessage =\n"
    "              'Do przeliczenia wpisanej wartości potrzebna jest masa ' \n"
    "              'pacjenta i spójne dane. Wpisz masę albo usuń konflikt ' \n"
    "              'przed zmianą trybu.';\n"
    "        });\n"
    "        return;\n"
    "      }\n\n"
    "      transferredUnit = _presentationUnitForFact(\n"
    "        incomingKind,\n"
    "        counterpart!.quantity,\n"
    "      );\n"
    "      transferredQuantity = counterpart.quantity.convertTo(\n"
    "        transferredUnit,\n"
    "      );\n"
    "      solution = _session.edit(\n"
    "        transferredQuantity,\n"
    "        replaceInputKind: outgoingKind,\n"
    "      );\n"
    "    } else if (outgoingInput != null && incomingInput != null) {\n"
    "      // A legacy session may contain explicit values in both modes. The\n"
    "      // selected mode wins so the other value cannot remain hidden.\n"
    "      solution = _session.clear(outgoingKind);\n"
    "    }\n\n"
    "    setState(() {\n"
    "      _dosePerKilogram = enabled;\n"
    "      _solution = solution;\n"
    "      _inputErrors\n"
    "        ..remove(outgoingKind)\n"
    "        ..remove(incomingKind);\n"
    "      _globalMessage = null;\n"
    "      if (transferredUnit != null) {\n"
    "        _presentationUnits[incomingKind] = transferredUnit;\n"
    "      }\n"
    "      if (transferredQuantity != null) {\n"
    "        _setControllerText(\n"
    "          incomingKind,\n"
    "          RationalDecimalFormatter.format(transferredQuantity.value),\n"
    "        );\n"
    "      }\n"
    "      _synchronizeControllers();\n"
    "    });\n"
    "    _queuePreferencesSave();\n"
    "  }\n\n"
    "  MeasurementUnit _presentationUnitForFact(\n"
    "    QuantityKind kind,\n"
    "    Quantity quantity,\n"
    "  ) {\n"
    "    final MeasurementUnit preferred = _presentationUnits[kind]!;\n"
    "    if (quantity.unit.isCompatibleWith(preferred)) {\n"
    "      return preferred;\n"
    "    }\n"
    "    if (CalculatorUnitOptions.supports(kind, quantity.unit)) {\n"
    "      return quantity.unit;\n"
    "    }\n"
    "    return _unitsFor(kind).firstWhere(\n"
    "      (MeasurementUnit candidate) =>\n"
    "          quantity.unit.isCompatibleWith(candidate),\n"
    "    );\n"
    "  }\n\n"
    "  Future<void> _restorePreferences() async {\n",
)

quantity = Path('lib/domain/quantities/quantity.dart')
replace_once(
    quantity,
    "import 'package:kalkulator_lekow/domain/validation/clinical_input_policy.dart';",
    "import 'package:kalkulator_lekow/domain/validation/technical_input_policy.dart';",
)
replace_once(
    quantity,
    '    ClinicalInputPolicy.validate(source);',
    '    TechnicalInputPolicy.validate(source);',
)

errors = Path('lib/domain/errors/domain_exception.dart')
replace_once(
    errors,
    '  /// A value is negative where the clinical domain permits only non-negative\n'
    '  /// quantities.\n',
    '  /// A value is negative where the calculator permits only non-negative\n'
    '  /// quantities.\n',
)
replace_once(
    errors,
    '/// Thrown when a negative clinical quantity is created.',
    '/// Thrown when a negative calculator quantity is created.',
)
replace_once(
    errors,
    "        message: 'Negative clinical quantity is not allowed: $value.',",
    "        message: 'Negative calculator quantity is not allowed: $value.',",
)

pubspec = Path('pubspec.yaml')
replace_once(pubspec, 'version: 0.1.0+8', 'version: 0.1.1-dev.1+9')

readme = Path('README.md')
replace_once(
    readme,
    '**Wersja:** `0.1.0+8` — ukończony techniczny MVP  \n'
    '**Następny etap:** `0.1.1` — stabilizacja po testach wewnętrznych  \n',
    '**Wersja rozwojowa:** `0.1.1-dev.1+9` — stabilizacja stanu formularza  \n'
    '**Ostatnie stabilne MVP:** `0.1.0+8`  \n',
)

changelog = Path('CHANGELOG.md')
replace_once(
    changelog,
    '## [0.1.0] — 2026-08-03\n',
    '''## [0.1.1-dev.1] — w przygotowaniu

### Poprawiono

- przełączanie dawki `/kg` i szybkości podaży przenosi jawne wejście zamiast pozostawiać niewidoczny warunek;
- zmiana trybu bez masy pacjenta jest odrzucana z czytelnym komunikatem, dzięki czemu wpisana wartość nie znika;
- przełączanie zachowuje rodzinę IU albo jednostek masy oraz bezpiecznie dobiera zgodną jednostkę prezentacji;
- zmiana masy po przełączeniu nie zmienia wartości, którą użytkownik świadomie ustawił jako nowe wejście;
- doprecyzowano opis roli masy przy dawce `/kg`;
- wewnętrzna polityka limitów liczbowych została nazwana techniczną, zgodnie z przeznaczeniem produktu.

### Testy regresji

- przeniesienie wejścia `/kg` → bez `/kg`;
- przeniesienie wejścia bez `/kg` → `/kg`;
- odmowa ukrycia wejścia bez dostępnej masy;
- zachowanie rodziny IU podczas przełączania.

## [0.1.0] — 2026-08-03
''',
)

roadmap = Path('ROADMAP.md')
replace_once(
    roadmap,
    '**Aktualny etap:** `0.1.0 — ukończony techniczny MVP`; następny: `0.1.1 — stabilizacja`',
    '**Aktualny etap:** `0.1.1-dev.1 — stabilizacja stanu formularza`',
)
replace_once(
    roadmap,
    '### 0.1.1 — Poprawki po testach wewnętrznych\n\n'
    '- [ ] poprawki błędów obliczeń i stanu;\n'
    '- [ ] doprecyzowanie komunikatów;\n'
    '- [ ] korekty formatowania;\n'
    '- [ ] testy regresji dla każdego znalezionego błędu;\n'
    '- [ ] dokumentacja znanych ograniczeń.\n',
    '### 0.1.1 — Poprawki po testach wewnętrznych **← obecnie**\n\n'
    '- [x] poprawki błędów obliczeń i stanu;\n'
    '- [x] doprecyzowanie komunikatów;\n'
    '- [ ] korekty formatowania;\n'
    '- [x] testy regresji dla każdego znalezionego błędu;\n'
    '- [x] dokumentacja znanych ograniczeń.\n\n'
    '**Pierwsza poprawka:** bezpieczne, transakcyjne przełączanie dawki `/kg` i szybkości podaży bez pozostawiania niewidocznych wejść.\n',
)
