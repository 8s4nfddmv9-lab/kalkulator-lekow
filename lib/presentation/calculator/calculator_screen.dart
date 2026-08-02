import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:kalkulator_lekow/application/calculator_session.dart';
import 'package:kalkulator_lekow/domain/calculations/calculation_trace.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/solver/solver_models.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';
import 'package:kalkulator_lekow/domain/units/unit_conversion_exception.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';
import 'package:kalkulator_lekow/presentation/calculator/widgets/calculation_field.dart';
import 'package:kalkulator_lekow/presentation/formatting/rational_decimal_formatter.dart';

/// Single-screen, real-time infusion calculator.
class CalculatorScreen extends StatefulWidget {
  /// Creates the calculator screen.
  const CalculatorScreen({super.key});

  @override
  State<CalculatorScreen> createState() => _CalculatorScreenState();
}

class _CalculatorScreenState extends State<CalculatorScreen> {
  late final CalculatorSession _session;
  late SolverSolution _solution;
  late final Map<QuantityKind, TextEditingController> _controllers;
  late final Map<QuantityKind, MeasurementUnit> _presentationUnits;

  final Map<QuantityKind, String> _inputErrors = <QuantityKind, String>{};
  String? _globalMessage;
  bool _dosePerKilogram = true;
  bool _isSynchronizing = false;

  static const List<QuantityKind> _editableKinds = <QuantityKind>[
    QuantityKind.bodyMass,
    QuantityKind.drugAmount,
    QuantityKind.solutionVolume,
    QuantityKind.concentration,
    QuantityKind.flowRate,
    QuantityKind.administrationRate,
    QuantityKind.weightNormalizedDose,
  ];

  @override
  void initState() {
    super.initState();
    _session = CalculatorSession();
    _solution = _session.solution;
    _controllers = <QuantityKind, TextEditingController>{
      for (final QuantityKind kind in _editableKinds)
        kind: TextEditingController(),
    };
    _presentationUnits = <QuantityKind, MeasurementUnit>{
      QuantityKind.bodyMass: UnitCatalog.kilogram,
      QuantityKind.drugAmount: UnitCatalog.milligram,
      QuantityKind.solutionVolume: UnitCatalog.millilitre,
      QuantityKind.concentration: UnitCatalog.find('ug/mL'),
      QuantityKind.flowRate: UnitCatalog.millilitresPerHour,
      QuantityKind.administrationRate: UnitCatalog.find('ug/min'),
      QuantityKind.weightNormalizedDose: UnitCatalog.find('ug/kg/min'),
      QuantityKind.infusionDuration: UnitCatalog.hour,
    };
  }

  @override
  void dispose() {
    for (final TextEditingController controller in _controllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  QuantityKind get _visibleDoseKind => _dosePerKilogram
      ? QuantityKind.weightNormalizedDose
      : QuantityKind.administrationRate;

  TextEditingController _controller(QuantityKind kind) => _controllers[kind]!;

  @override
  Widget build(BuildContext context) {
    final List<String> problemMessages = _problemMessages();
    final SolverFact? latestResult = _latestCalculatedFact();
    final SolverFact? durationFact = _solution.fact(
      QuantityKind.infusionDuration,
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('Kalkulator leków'),
        actions: <Widget>[
          IconButton(
            tooltip: 'Wyczyść wszystkie pola',
            onPressed: _clearAll,
            icon: const Icon(Icons.delete_outline),
          ),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
          children: <Widget>[
            const _PrototypeWarning(),
            if (problemMessages.isNotEmpty) ...<Widget>[
              const SizedBox(height: 12),
              _ProblemSummary(messages: problemMessages),
            ],
            const SizedBox(height: 20),
            const _SectionHeading(
              title: 'Pacjent',
              subtitle:
                  'Masa jest wyłącznie daną wejściową i nigdy nie jest wyliczana.',
            ),
            _buildField(
              kind: QuantityKind.bodyMass,
              label: 'Masa pacjenta',
              helperText: 'Wymagana tylko dla dawek zawierających /kg.',
            ),
            const _SectionHeading(
              title: 'Roztwór',
              subtitle: 'Dowolne dwa z trzech parametrów wyznaczają trzeci.',
            ),
            _buildField(kind: QuantityKind.drugAmount, label: 'Ilość leku'),
            _buildField(
              kind: QuantityKind.solutionVolume,
              label: 'Objętość roztworu',
            ),
            _buildField(kind: QuantityKind.concentration, label: 'Stężenie'),
            const _SectionHeading(
              title: 'Podawanie',
              subtitle:
                  'Zmiana przepływu lub dawki natychmiast przelicza pozostałe wartości.',
            ),
            _buildField(kind: QuantityKind.flowRate, label: 'Przepływ'),
            Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Wrap(
                  spacing: 12,
                  runSpacing: 8,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: <Widget>[
                    const Text('Dawka zależna od masy:'),
                    FilterChip(
                      key: const Key('per-kilogram-toggle'),
                      label: const Text('/kg'),
                      selected: _dosePerKilogram,
                      onSelected: _toggleDosePerKilogram,
                    ),
                    Text(
                      _dosePerKilogram
                          ? 'masa pacjenta jest uwzględniana'
                          : 'szybkość podaży bez /kg',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
            ),
            _buildField(
              kind: _visibleDoseKind,
              label: 'Dawka / szybkość podaży',
              helperText: _dosePerKilogram
                  ? 'Wynik wymaga wpisanej masy pacjenta.'
                  : 'Ta wartość nie zależy od masy pacjenta.',
              valueFieldKey: const Key('dose-value-field'),
            ),
            if (durationFact != null) ...<Widget>[
              const SizedBox(height: 4),
              _InfusionDurationCard(
                text: _formatFact(durationFact, UnitCatalog.hour),
              ),
            ],
            if (latestResult?.trace != null) ...<Widget>[
              const SizedBox(height: 8),
              _CalculationDetailsCard(
                trace: latestResult!.trace!,
                formattedOutput: _formatFact(
                  latestResult,
                  _presentationUnits[latestResult.quantity.kind] ??
                      latestResult.quantity.unit,
                ),
                onCopy: () => _copyFact(latestResult),
              ),
            ],
            const SizedBox(height: 12),
            Text(
              'Wyniki są aktualizowane bez przycisku „Oblicz”. '
              'Zaokrąglanie dotyczy wyłącznie prezentacji.',
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  CalculationField _buildField({
    required QuantityKind kind,
    required String label,
    String? helperText,
    Key? valueFieldKey,
  }) {
    final List<MeasurementUnit> units = _unitsFor(kind);
    final MeasurementUnit selectedUnit = _presentationUnits[kind]!;

    return CalculationField(
      label: label,
      controller: _controller(kind),
      units: units
          .map((MeasurementUnit unit) => unit.symbol)
          .toList(growable: false),
      selectedUnit: selectedUnit.symbol,
      onChanged: (String text) => _handleTextChanged(kind, text),
      onUnitChanged: (String symbol) {
        final MeasurementUnit unit = units.firstWhere(
          (MeasurementUnit candidate) => candidate.symbol == symbol,
        );
        _handleUnitChanged(kind, unit);
      },
      appearance: _appearanceFor(kind),
      helperText: helperText,
      errorText: _errorTextFor(kind),
      valueFieldKey: valueFieldKey ?? Key('value-${kind.name}'),
    );
  }

  List<MeasurementUnit> _unitsFor(QuantityKind kind) => switch (kind) {
    QuantityKind.bodyMass => <MeasurementUnit>[...UnitCatalog.bodyMassUnits],
    QuantityKind.drugAmount => <MeasurementUnit>[
      ...UnitCatalog.medicineAmountUnits,
    ],
    QuantityKind.solutionVolume => <MeasurementUnit>[UnitCatalog.millilitre],
    QuantityKind.concentration => <MeasurementUnit>[
      ...UnitCatalog.concentrationUnits,
    ],
    QuantityKind.flowRate => <MeasurementUnit>[UnitCatalog.millilitresPerHour],
    QuantityKind.administrationRate => <MeasurementUnit>[
      ...UnitCatalog.administrationRateUnits,
    ],
    QuantityKind.weightNormalizedDose => <MeasurementUnit>[
      ...UnitCatalog.weightNormalizedDoseUnits,
    ],
    QuantityKind.infusionDuration || QuantityKind.time => <MeasurementUnit>[
      UnitCatalog.minute,
      UnitCatalog.hour,
    ],
  };

  CalculationFieldAppearance _appearanceFor(QuantityKind kind) {
    if (_inputErrors.containsKey(kind)) {
      return CalculationFieldAppearance.invalid;
    }
    if (_solution.hasConflict(kind)) {
      return CalculationFieldAppearance.conflict;
    }
    final SolverFact? input = _solution.userInputs[kind];
    if (input != null) {
      return CalculationFieldAppearance.userInput;
    }
    final SolverFact? fact = _solution.fact(kind);
    if (fact?.origin == SolverFactOrigin.calculated) {
      return CalculationFieldAppearance.calculated;
    }
    return CalculationFieldAppearance.empty;
  }

  String? _errorTextFor(QuantityKind kind) {
    final String? localError = _inputErrors[kind];
    if (localError != null) {
      return localError;
    }

    final SolverConflict? conflict = _solution.conflicts[kind];
    if (conflict != null) {
      final Quantity candidate = conflict.candidateInExistingUnit;
      return 'Z pozostałych danych wynika '
          '${RationalDecimalFormatter.format(candidate.value)} '
          '${candidate.unit.symbol}.';
    }

    for (final SolverDiagnostic diagnostic in _solution.diagnostics) {
      if (diagnostic.involvedUserInputs.contains(kind)) {
        return _messageForDomainError(diagnostic.error);
      }
    }
    return null;
  }

  void _handleTextChanged(QuantityKind kind, String text) {
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

  void _recordInvalidInput(QuantityKind kind, String message) {
    SolverSolution safeSolution = _session.solution;
    try {
      safeSolution = _session.clear(kind);
    } on Object {
      // The transactional session has already restored the last safe state.
    }

    setState(() {
      _solution = safeSolution;
      _inputErrors[kind] = message;
      _globalMessage = null;
      _synchronizeControllers();
    });
  }

  void _handleUnitChanged(QuantityKind kind, MeasurementUnit newUnit) {
    final MeasurementUnit currentUnit = _presentationUnits[kind]!;
    if (newUnit == currentUnit) {
      return;
    }

    final SolverFact? explicitInput = _solution.userInputs[kind];
    final SolverFact? displayedFact = _solution.fact(kind);

    if (explicitInput != null) {
      try {
        final Quantity converted = explicitInput.quantity.convertTo(newUnit);
        final SolverSolution solution = _session.edit(converted);
        setState(() {
          _presentationUnits[kind] = newUnit;
          _inputErrors.remove(kind);
          _globalMessage = null;
          _solution = solution;
          _setControllerText(
            kind,
            RationalDecimalFormatter.format(converted.value),
          );
          _synchronizeControllers();
        });
      } on UnitConversionException {
        final SolverSolution solution = _session.clear(kind);
        setState(() {
          _presentationUnits[kind] = newUnit;
          _inputErrors.remove(kind);
          _globalMessage =
              'Jednostek IU nie można automatycznie przeliczać na jednostki '
              'masy. Wartość pola została wyczyszczona.';
          _solution = solution;
          _setControllerText(kind, '');
          _synchronizeControllers();
        });
      }
      return;
    }

    if (displayedFact != null) {
      try {
        displayedFact.quantity.convertTo(newUnit);
      } on UnitConversionException {
        setState(() {
          _globalMessage =
              'Wyliczonej wartości nie można pokazać w wybranej rodzinie '
              'jednostek. Najpierw zmień lub wyczyść dane źródłowe.';
        });
        return;
      }
    }

    setState(() {
      _presentationUnits[kind] = newUnit;
      _inputErrors.remove(kind);
      _globalMessage = null;
      _synchronizeControllers();
    });
  }

  void _toggleDosePerKilogram(bool enabled) {
    setState(() {
      _dosePerKilogram = enabled;
      _globalMessage = null;
      _synchronizeControllers();
    });
  }

  void _clearAll() {
    setState(() {
      _inputErrors.clear();
      _globalMessage = null;
      _solution = _session.reset();
      _isSynchronizing = true;
      try {
        for (final TextEditingController controller in _controllers.values) {
          controller.clear();
        }
      } finally {
        _isSynchronizing = false;
      }
    });
  }

  void _synchronizeControllers() {
    _isSynchronizing = true;
    try {
      for (final QuantityKind kind in _editableKinds) {
        if (_inputErrors.containsKey(kind)) {
          continue;
        }
        if (_solution.userInputs.containsKey(kind)) {
          continue;
        }

        final SolverFact? fact = _solution.fact(kind);
        if (fact == null) {
          _setControllerText(kind, '');
          continue;
        }

        final MeasurementUnit targetUnit = _presentationUnits[kind]!;
        try {
          final Quantity converted = fact.quantity.convertTo(targetUnit);
          _setControllerText(
            kind,
            RationalDecimalFormatter.format(converted.value),
          );
        } on UnitConversionException {
          _setControllerText(kind, '');
        }
      }
    } finally {
      _isSynchronizing = false;
    }
  }

  void _setControllerText(QuantityKind kind, String text) {
    final TextEditingController controller = _controller(kind);
    if (controller.text == text) {
      return;
    }
    controller.value = TextEditingValue(
      text: text,
      selection: TextSelection.collapsed(offset: text.length),
    );
  }

  List<String> _problemMessages() {
    final List<String> messages = <String>[];
    final String? globalMessage = _globalMessage;
    if (globalMessage != null) {
      messages.add(globalMessage);
    }

    for (final MapEntry<QuantityKind, String> entry in _inputErrors.entries) {
      messages.add('${_labelFor(entry.key)}: ${entry.value}');
    }
    for (final SolverConflict conflict in _solution.conflicts.values) {
      final Quantity expected = conflict.candidateInExistingUnit;
      messages.add(
        '${_labelFor(conflict.kind)} jest niespójne. Z pozostałych danych '
        'wynika ${RationalDecimalFormatter.format(expected.value)} '
        '${expected.unit.symbol}.',
      );
    }
    for (final SolverDiagnostic diagnostic in _solution.diagnostics) {
      messages.add(_messageForDomainError(diagnostic.error));
    }
    return messages.toSet().toList(growable: false);
  }

  SolverFact? _latestCalculatedFact() {
    final List<SolverFact> calculated = _solution.calculatedFacts
        .where(
          (SolverFact fact) =>
              fact.quantity.kind != QuantityKind.infusionDuration,
        )
        .toList(growable: false);
    if (calculated.isEmpty) {
      return null;
    }
    calculated.sort((SolverFact left, SolverFact right) {
      final int sequence = right.latestEditSequence.compareTo(
        left.latestEditSequence,
      );
      if (sequence != 0) {
        return sequence;
      }
      return right.quantity.kind.index.compareTo(left.quantity.kind.index);
    });
    return calculated.first;
  }

  String _formatFact(SolverFact fact, MeasurementUnit unit) {
    try {
      final Quantity converted = fact.quantity.convertTo(unit);
      return '${RationalDecimalFormatter.format(converted.value)} '
          '${converted.unit.symbol}';
    } on UnitConversionException {
      return '${RationalDecimalFormatter.format(fact.quantity.value)} '
          '${fact.quantity.unit.symbol}';
    }
  }

  Future<void> _copyFact(SolverFact fact) async {
    final MeasurementUnit targetUnit =
        _presentationUnits[fact.quantity.kind] ?? fact.quantity.unit;
    final String text = _formatFact(fact, targetUnit);
    await Clipboard.setData(ClipboardData(text: text));
    if (!mounted) {
      return;
    }
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text('Skopiowano: $text')));
  }

  String _messageForDomainError(DomainException error) => switch (error.code) {
    DomainErrorCode.invalidNumber =>
      'Wpisz liczbę z przecinkiem albo kropką, np. 0,05.',
    DomainErrorCode.negativeValue => 'Wartość nie może być ujemna.',
    DomainErrorCode.zeroDenominator =>
      'Ta wartość musi być większa od zera, aby wykonać obliczenie.',
    DomainErrorCode.incompatibleUnitFamily =>
      'Jednostki są niezgodne. IU nie można automatycznie przeliczyć na '
          'ng, µg, mg ani g.',
    DomainErrorCode.missingBodyMass =>
      'Do obliczenia dawki zawierającej /kg potrzebna jest masa pacjenta.',
    DomainErrorCode.insufficientData =>
      'Brakuje danych do jednoznacznego obliczenia.',
    DomainErrorCode.conflictingInputs =>
      'Podane wartości są wzajemnie niespójne.',
    DomainErrorCode.outOfTechnicalRange =>
      'Wartość przekracza obsługiwany zakres techniczny.',
    DomainErrorCode.cyclicDerivation =>
      'Nie można bezpiecznie ustalić kolejności obliczeń.',
  };

  static String _labelFor(QuantityKind kind) => switch (kind) {
    QuantityKind.bodyMass => 'Masa pacjenta',
    QuantityKind.drugAmount => 'Ilość leku',
    QuantityKind.solutionVolume => 'Objętość roztworu',
    QuantityKind.concentration => 'Stężenie',
    QuantityKind.flowRate => 'Przepływ',
    QuantityKind.administrationRate => 'Szybkość podaży',
    QuantityKind.weightNormalizedDose => 'Dawka /kg',
    QuantityKind.infusionDuration => 'Czas infuzji',
    QuantityKind.time => 'Czas',
  };
}

class _PrototypeWarning extends StatelessWidget {
  const _PrototypeWarning();

  @override
  Widget build(BuildContext context) => Semantics(
    label: 'Ostrzeżenie: prototyp nie jest przeznaczony do użycia klinicznego.',
    child: Card(
      color: Theme.of(context).colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Icon(
              Icons.warning_amber_rounded,
              color: Theme.of(context).colorScheme.onErrorContainer,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'Prototyp — nie używać do podejmowania decyzji klinicznych.',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onErrorContainer,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

class _ProblemSummary extends StatelessWidget {
  const _ProblemSummary({required this.messages});

  final List<String> messages;

  @override
  Widget build(BuildContext context) => Semantics(
    liveRegion: true,
    child: Card(
      color: Theme.of(context).colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Text(
              'Sprawdź dane',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Theme.of(context).colorScheme.onErrorContainer,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            for (final String message in messages)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  '• $message',
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.onErrorContainer,
                  ),
                ),
              ),
          ],
        ),
      ),
    ),
  );
}

class _SectionHeading extends StatelessWidget {
  const _SectionHeading({required this.title, required this.subtitle});

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(top: 4, bottom: 12),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(title, style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 4),
        Text(subtitle, style: Theme.of(context).textTheme.bodyMedium),
      ],
    ),
  );
}

class _InfusionDurationCard extends StatelessWidget {
  const _InfusionDurationCard({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) => Card(
    child: ListTile(
      leading: const Icon(Icons.timer_outlined),
      title: const Text('Czas opróżnienia roztworu'),
      subtitle: const Text('Wyliczony z objętości i przepływu'),
      trailing: Text(
        text,
        key: const Key('infusion-duration-value'),
        style: Theme.of(context).textTheme.titleMedium,
      ),
    ),
  );
}

class _CalculationDetailsCard extends StatelessWidget {
  const _CalculationDetailsCard({
    required this.trace,
    required this.formattedOutput,
    required this.onCopy,
  });

  final CalculationTrace trace;
  final String formattedOutput;
  final VoidCallback onCopy;

  @override
  Widget build(BuildContext context) => Card(
    child: ExpansionTile(
      key: const Key('calculation-details'),
      leading: const Icon(Icons.function_outlined),
      title: const Text('Szczegóły obliczenia'),
      subtitle: Text(formattedOutput),
      childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      children: <Widget>[
        Align(
          alignment: Alignment.centerLeft,
          child: SelectableText(
            trace.formula,
            style: Theme.of(context).textTheme.titleMedium,
          ),
        ),
        const SizedBox(height: 8),
        for (final CalculationOperand input in trace.inputs)
          Align(
            alignment: Alignment.centerLeft,
            child: Text(
              '${_CalculatorScreenState._labelFor(input.kind)}: '
              '${RationalDecimalFormatter.format(input.value)} '
              '${input.unitSymbol}',
            ),
          ),
        const SizedBox(height: 8),
        Align(
          alignment: Alignment.centerLeft,
          child: Text(
            'Wynik: $formattedOutput',
            style: const TextStyle(fontWeight: FontWeight.w700),
          ),
        ),
        const SizedBox(height: 8),
        Align(
          alignment: Alignment.centerRight,
          child: TextButton.icon(
            onPressed: onCopy,
            icon: const Icon(Icons.copy_outlined),
            label: const Text('Kopiuj wynik'),
          ),
        ),
      ],
    ),
  );
}
