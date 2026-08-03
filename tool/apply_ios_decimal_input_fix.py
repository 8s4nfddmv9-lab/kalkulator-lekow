from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    if old not in source:
        raise SystemExit(f"Expected block not found in {path}: {old[:240]!r}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


screen = Path("lib/presentation/calculator/calculator_screen.dart")
replace_once(
    screen,
    """  late final Map<QuantityKind, TextEditingController> _controllers;
  late final Map<QuantityKind, MeasurementUnit> _presentationUnits;
""",
    """  late final Map<QuantityKind, TextEditingController> _controllers;
  late final Map<QuantityKind, FocusNode> _focusNodes;
  late final Map<QuantityKind, MeasurementUnit> _presentationUnits;
""",
)
replace_once(
    screen,
    """  final Map<QuantityKind, String> _inputErrors = <QuantityKind, String>{};
  String? _globalMessage;
""",
    """  final Map<QuantityKind, String> _inputErrors = <QuantityKind, String>{};
  final Set<QuantityKind> _draftKinds = <QuantityKind>{};
  String? _globalMessage;
""",
)
replace_once(
    screen,
    """    _controllers = <QuantityKind, TextEditingController>{
      for (final QuantityKind kind in _editableKinds)
        kind: TextEditingController(),
    };
    final CalculatorPreferences defaults = CalculatorPreferences.defaults();
""",
    """    _controllers = <QuantityKind, TextEditingController>{
      for (final QuantityKind kind in _editableKinds)
        kind: TextEditingController(),
    };
    _focusNodes = <QuantityKind, FocusNode>{
      for (final QuantityKind kind in _editableKinds)
        kind: FocusNode(debugLabel: 'calculator-${kind.name}'),
    };
    for (final QuantityKind kind in _editableKinds) {
      _focusNodes[kind]!.addListener(() => _handleFocusChanged(kind));
    }
    final CalculatorPreferences defaults = CalculatorPreferences.defaults();
""",
)
replace_once(
    screen,
    """  void dispose() {
    for (final TextEditingController controller in _controllers.values) {
      controller.dispose();
    }
    super.dispose();
  }
""",
    """  void dispose() {
    for (final TextEditingController controller in _controllers.values) {
      controller.dispose();
    }
    for (final FocusNode focusNode in _focusNodes.values) {
      focusNode.dispose();
    }
    super.dispose();
  }
""",
)
replace_once(
    screen,
    """  bool get _hasActiveNumericState =>
      _solution.userInputs.isNotEmpty || _inputErrors.isNotEmpty;

  bool get _shouldIgnorePendingPreferenceRestore =>
      _hasLocalPreferenceEdit || _hasActiveNumericState;

  TextEditingController _controller(QuantityKind kind) => _controllers[kind]!;
""",
    """  bool get _hasActiveNumericState =>
      _solution.userInputs.isNotEmpty ||
      _inputErrors.isNotEmpty ||
      _draftKinds.isNotEmpty;

  bool get _shouldIgnorePendingPreferenceRestore =>
      _hasLocalPreferenceEdit || _hasActiveNumericState;

  TextEditingController _controller(QuantityKind kind) => _controllers[kind]!;

  FocusNode _focusNode(QuantityKind kind) => _focusNodes[kind]!;
""",
)
replace_once(
    screen,
    """    return CalculationField(
      label: label,
      controller: _controller(kind),
""",
    """    return CalculationField(
      key: ValueKey<String>('calculation-field-${kind.name}'),
      label: label,
      controller: _controller(kind),
      focusNode: _focusNode(kind),
""",
)
replace_once(
    screen,
    """  CalculationFieldAppearance _appearanceFor(QuantityKind kind) {
    if (_inputErrors.containsKey(kind)) {
      return CalculationFieldAppearance.invalid;
    }
    if (_solution.hasConflict(kind)) {
""",
    """  CalculationFieldAppearance _appearanceFor(QuantityKind kind) {
    if (_inputErrors.containsKey(kind)) {
      return CalculationFieldAppearance.invalid;
    }
    if (_draftKinds.contains(kind)) {
      return CalculationFieldAppearance.userInput;
    }
    if (_solution.hasConflict(kind)) {
""",
)
replace_once(
    screen,
    """  void _handleTextChanged(QuantityKind kind, String text) {
    if (_isSynchronizing) {
      return;
    }

    final String normalized = text.trim();
    if (normalized.isEmpty) {
      setState(() {
        _inputErrors.remove(kind);
        _globalMessage = null;
        _solution = _session.clear(kind);
        _synchronizeControllers();
      });
      return;
    }

    try {
      final Quantity quantity = Quantity.parse(
        kind: kind,
        source: normalized,
        unit: _presentationUnits[kind]!,
      );
      _validatePositiveInput(quantity);
      final SolverSolution solution = _session.edit(quantity);

      setState(() {
        _inputErrors.remove(kind);
        _globalMessage = null;
        _solution = solution;
        _synchronizeControllers();
      });
    } on DomainException catch (error) {
      _recordInvalidInput(kind, _messageForDomainError(error));
    } on ArgumentError catch (error) {
      _recordInvalidInput(
        kind,
        error.message?.toString() ?? 'Nieprawidłowa wartość.',
      );
    }
  }

  void _validatePositiveInput(Quantity quantity) {
    final bool mustBePositive = switch (quantity.kind) {
      QuantityKind.bodyMass ||
      QuantityKind.solutionVolume ||
      QuantityKind.concentration ||
      QuantityKind.flowRate => true,
      _ => false,
    };
    if (mustBePositive && quantity.isZero) {
      throw ArgumentError.value(
        quantity.value,
        quantity.kind.name,
        'Wartość musi być większa od zera.',
      );
    }
  }
""",
    """  void _handleTextChanged(
    QuantityKind kind,
    String text, {
    bool commitDraft = false,
  }) {
    if (_isSynchronizing) {
      return;
    }

    final String normalized = text.trim();
    if (normalized.isEmpty) {
      setState(() {
        _draftKinds.remove(kind);
        _inputErrors.remove(kind);
        _globalMessage = null;
        _solution = _session.clear(kind);
        _synchronizeControllers();
      });
      return;
    }

    if (!commitDraft && _isTransientEditingText(kind, normalized)) {
      _recordDraftInput(kind);
      return;
    }

    try {
      final Quantity quantity = Quantity.parse(
        kind: kind,
        source: normalized,
        unit: _presentationUnits[kind]!,
      );
      _validatePositiveInput(quantity);
      final SolverSolution solution = _session.edit(quantity);

      setState(() {
        _draftKinds.remove(kind);
        _inputErrors.remove(kind);
        _globalMessage = null;
        _solution = solution;
        _synchronizeControllers();
      });
    } on DomainException catch (error) {
      _recordInvalidInput(kind, _messageForDomainError(error));
    } on ArgumentError catch (error) {
      _recordInvalidInput(
        kind,
        error.message?.toString() ?? 'Nieprawidłowa wartość.',
      );
    }
  }

  void _handleFocusChanged(QuantityKind kind) {
    if (!mounted ||
        _focusNode(kind).hasFocus ||
        !_draftKinds.contains(kind)) {
      return;
    }
    _handleTextChanged(kind, _controller(kind).text, commitDraft: true);
  }

  bool _isTransientEditingText(QuantityKind kind, String text) {
    if (RegExp(r'^\\d+[,.]$').hasMatch(text)) {
      return true;
    }
    return _requiresStrictlyPositive(kind) &&
        RegExp(r'^0(?:[,.]0*)?$').hasMatch(text);
  }

  void _recordDraftInput(QuantityKind kind) {
    final SolverSolution solution = _session.clear(kind);
    setState(() {
      _solution = solution;
      _draftKinds.add(kind);
      _inputErrors.remove(kind);
      _globalMessage = null;
      _synchronizeControllers();
    });
  }

  void _validatePositiveInput(Quantity quantity) {
    if (_requiresStrictlyPositive(quantity.kind) && quantity.isZero) {
      throw ArgumentError.value(
        quantity.value,
        quantity.kind.name,
        'Wartość musi być większa od zera.',
      );
    }
  }

  static bool _requiresStrictlyPositive(QuantityKind kind) => switch (kind) {
    QuantityKind.bodyMass ||
    QuantityKind.solutionVolume ||
    QuantityKind.concentration ||
    QuantityKind.flowRate => true,
    _ => false,
  };
""",
)
replace_once(
    screen,
    """    setState(() {
      _solution = safeSolution;
      _inputErrors[kind] = message;
""",
    """    setState(() {
      _solution = safeSolution;
      _draftKinds.remove(kind);
      _inputErrors[kind] = message;
""",
)
replace_once(
    screen,
    """      _inputErrors
        ..remove(outgoingKind)
        ..remove(incomingKind);
      _globalMessage = null;
""",
    """      _inputErrors
        ..remove(outgoingKind)
        ..remove(incomingKind);
      _draftKinds
        ..remove(outgoingKind)
        ..remove(incomingKind);
      _globalMessage = null;
""",
)
replace_once(
    screen,
    """    setState(() {
      _inputErrors.clear();
      _globalMessage = null;
""",
    """    setState(() {
      _inputErrors.clear();
      _draftKinds.clear();
      _globalMessage = null;
""",
)
replace_once(
    screen,
    """      for (final QuantityKind kind in _editableKinds) {
        if (_inputErrors.containsKey(kind)) {
          continue;
        }
""",
    """      for (final QuantityKind kind in _editableKinds) {
        if (_inputErrors.containsKey(kind) || _draftKinds.contains(kind)) {
          continue;
        }
""",
)

screen_tests = Path("test/presentation/calculator_screen_test.dart")
replace_once(
    screen_tests,
    """  testWidgets('shows an inline error for a zero body mass', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-bodyMass', '0');

    expect(find.text('Wartość musi być większa od zera.'), findsOneWidget);
    await _reveal(tester, find.text('Sprawdź dane'));
    expect(find.text('Sprawdź dane'), findsOneWidget);
  });
""",
    """  testWidgets('prefixes comma and dot entered into an empty field', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());
    final Finder field = find.byKey(const Key('value-concentration'));
    await _reveal(tester, field);
    await tester.showKeyboard(field);

    tester.testTextInput.enterText(',');
    await tester.pump();

    expect(tester.widget<TextField>(field).controller!.text, '0,');
    _expectKeyboardActive(tester, field);

    tester.testTextInput.enterText('');
    await tester.pump();
    tester.testTextInput.enterText('.');
    await tester.pump();

    expect(tester.widget<TextField>(field).controller!.text, '0,');
    _expectKeyboardActive(tester, field);
  });

  testWidgets('keeps keyboard active while typing and deleting a fraction', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());
    final Finder field = find.byKey(const Key('value-concentration'));
    await _reveal(tester, field);
    await tester.showKeyboard(field);

    for (final String text in <String>[
      '0',
      '0,',
      '0,0',
      '0,05',
      '0,0',
      '0,',
      '0',
    ]) {
      tester.testTextInput.enterText(text);
      await tester.pump();

      expect(tester.widget<TextField>(field).controller!.text, text);
      expect(find.text('Wartość musi być większa od zera.'), findsNothing);
      _expectKeyboardActive(tester, field);
    }
  });

  testWidgets('shows an inline error for a zero body mass after editing', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-bodyMass', '0');
    expect(find.text('Wartość musi być większa od zera.'), findsNothing);

    await tester.tap(find.byKey(const Key('value-drugAmount')));
    await tester.pumpAndSettle();

    expect(find.text('Wartość musi być większa od zera.'), findsOneWidget);
    await _reveal(tester, find.text('Sprawdź dane'));
    expect(find.text('Sprawdź dane'), findsOneWidget);
  });
""",
)
replace_once(
    screen_tests,
    """Future<void> _enter(WidgetTester tester, String key, String value) async {
""",
    """void _expectKeyboardActive(WidgetTester tester, Finder field) {
  final TextField textField = tester.widget<TextField>(field);
  expect(textField.focusNode, isNotNull);
  expect(textField.focusNode!.hasFocus, isTrue);
  expect(tester.testTextInput.isVisible, isTrue);
}

Future<void> _enter(WidgetTester tester, String key, String value) async {
""",
)

pubspec = Path("pubspec.yaml")
replace_once(pubspec, "version: 0.1.2-beta.2+14", "version: 0.1.2-beta.3+15")

readme = Path("README.md")
replace_once(
    readme,
    "**Wersja publiczna:** `0.1.2-beta.2+14` — publiczne PWA",
    "**Wersja publiczna:** `0.1.2-beta.3+15` — pierwsze poprawki UX publicznego PWA",
)

roadmap = Path("ROADMAP.md")
replace_once(
    roadmap,
    "**Aktualny etap:** `0.1.2-beta.2 — publiczne PWA i pierwsze testy użytkowe`",
    "**Aktualny etap:** `0.1.2-beta.3 — pierwsze poprawki po testach użytkowych`",
)
replace_once(
    roadmap,
    "### 0.1.2-beta.2 — Publiczne PWA **← obecnie**",
    "### 0.1.2-beta.2 — Publiczne PWA **✓ ukończono**",
)
replace_once(
    roadmap,
    """**Dokumentacja:** [`DEPLOYMENT.md`](DEPLOYMENT.md), [`docs/PRIVACY.md`](docs/PRIVACY.md) i [issue #18](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18).

### 0.1.3 — Dostępność i ergonomia
""",
    """**Dokumentacja:** [`DEPLOYMENT.md`](DEPLOYMENT.md), [`docs/PRIVACY.md`](docs/PRIVACY.md) i [issue #18](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18).

### 0.1.2-beta.3 — Pierwsze poprawki UX **← obecnie**

- [x] wpisanie `,` lub `.` w pustym polu tworzy `0,`;
- [x] przejściowe prefiksy `0`, `0,`, `0,0` nie zamykają klawiatury;
- [x] fokus pola jest stabilny podczas przebudowy interfejsu;
- [x] kasowanie ułamka nie przerywa edycji na iPhonie;
- [x] walidacja zera lub niedokończonego separatora następuje po opuszczeniu pola;
- [x] testy regresji fokusu, klawiatury i formatowania separatora;
- [ ] potwierdzenie poprawki na fizycznym iPhonie w publicznym PWA.

**Zgłoszenie:** [issue #29](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/29).

### 0.1.3 — Dostępność i ergonomia
""",
)

changelog = Path("CHANGELOG.md")
replace_once(
    changelog,
    """## [Unreleased]

### Dodano

- stopkę InfusionCalc z sekcjami `Changelog`, `Privacy`, `GitHub` i `Contact`;
- lokalny komunikat prywatności i dokument `docs/PRIVACY.md`;
- centralne issue #18 do zbierania feedbacku z pierwszych testów;
- dokument `DEPLOYMENT.md` opisujący wspieraną i archiwalne ścieżki wdrożenia.

### Zmieniono

- GitHub Pages i `https://infusioncalc.eu/` są główną ścieżką publicznej dystrybucji;
- workflow niepodpisanego IPA oraz mini-PC/Docker/Tailscale są oznaczone jako archiwalne i uruchamiane wyłącznie ręcznie.

### Jakość

- cały projekt: `151/151` testów;
- pokrycie liniowe `lib/domain/`: `93,99%` (`720/766` linii);
- poprawne buildy kontrolne Androida i iOS.

## [0.1.2-beta.2] — 2026-08-03
""",
    """## [Unreleased]

## [0.1.2-beta.3] — 2026-08-03

### Poprawiono

- wpisanie przecinka lub kropki jako pierwszego znaku automatycznie tworzy zapis `0,`;
- klawiatura numeryczna i fokus pozostają aktywne podczas wpisywania oraz kasowania ułamków przechodzących przez `0`, `0,` i kolejne zera;
- przejściowe, niedokończone prefiksy dziesiętne nie są zgłaszane jako błąd w trakcie edycji;
- zero i niedokończony separator nadal są walidowane po opuszczeniu pola.

### Dodano

- trwałe węzły fokusu dla wszystkich pól kalkulatora;
- testy regresji połączenia klawiatury, fokusu oraz automatycznego zera przed separatorem;
- stopkę InfusionCalc z sekcjami `Changelog`, `Privacy`, `GitHub` i `Contact`;
- lokalny komunikat prywatności i dokument `docs/PRIVACY.md`;
- centralne issue #18 do zbierania feedbacku z pierwszych testów;
- dokument `DEPLOYMENT.md` opisujący wspieraną i archiwalne ścieżki wdrożenia.

### Zmieniono

- GitHub Pages i `https://infusioncalc.eu/` są główną ścieżką publicznej dystrybucji;
- workflow niepodpisanego IPA oraz mini-PC/Docker/Tailscale są oznaczone jako archiwalne i uruchamiane wyłącznie ręcznie.

## [0.1.2-beta.2] — 2026-08-03
""",
)
