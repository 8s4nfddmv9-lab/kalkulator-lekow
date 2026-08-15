import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';
import 'package:kalkulator_lekow/application/calculator_session.dart';
import 'package:kalkulator_lekow/application/calculator_unit_options.dart';
import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';
import 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';
import 'package:kalkulator_lekow/domain/calculations/calculation_trace.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/solver/solver_models.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';
import 'package:kalkulator_lekow/domain/units/unit_conversion_exception.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';
import 'package:kalkulator_lekow/presentation/calculator/widgets/calculation_field.dart';
import 'package:kalkulator_lekow/presentation/common/app_footer.dart';
import 'package:kalkulator_lekow/presentation/formatting/rational_decimal_formatter.dart';
import 'package:kalkulator_lekow/presentation/localization/app_localizations.dart';
import 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_banner.dart';

typedef _LocalizedMessage = String Function(AppLocalizations localizations);

/// Single-screen, real-time infusion calculator.
class CalculatorScreen extends StatefulWidget {
  /// Creates the calculator screen.
  const CalculatorScreen({
    this.preferencesStore = const VolatileCalculatorPreferencesStore(),
    this.pwaInstallPromptStore = const EphemeralPwaInstallPromptStore(),
    this.analyticsTracker = const NoopAnalyticsTracker(),
    this.onLanguageToggle,
    super.key,
  });

  /// Store used only for non-clinical presentation preferences.
  final CalculatorPreferencesStore preferencesStore;

  /// Store used for the optional PWA installation reminder postponement.
  final PwaInstallPromptStore pwaInstallPromptStore;

  /// Privacy-reviewed analytics sink isolated from calculator values.
  final AnalyticsTracker analyticsTracker;

  /// Changes between the supported Polish and English interface languages.
  final VoidCallback? onLanguageToggle;

  @override
  State<CalculatorScreen> createState() => _CalculatorScreenState();
}

class _CalculatorScreenState extends State<CalculatorScreen> {
  late final CalculatorSession _session;
  late SolverSolution _solution;
  late final Map<QuantityKind, TextEditingController> _controllers;
  late final Map<QuantityKind, FocusNode> _focusNodes;
  late final Map<QuantityKind, MeasurementUnit> _presentationUnits;
  late final CalculatorPreferencesStore _preferencesStore;
  Future<void> _preferencesWriteQueue = Future<void>.value();

  final Map<QuantityKind, _LocalizedMessage> _inputErrors =
      <QuantityKind, _LocalizedMessage>{};
  final Set<QuantityKind> _draftKinds = <QuantityKind>{};
  _LocalizedMessage? _globalMessage;
  bool _dosePerKilogram = true;
  bool _isSynchronizing = false;
  bool _hasLocalPreferenceEdit = false;

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
    _preferencesStore = widget.preferencesStore;
    _controllers = <QuantityKind, TextEditingController>{
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
    _presentationUnits = <QuantityKind, MeasurementUnit>{
      for (final QuantityKind kind in CalculatorPreferences.persistedKinds)
        kind: defaults.unitFor(kind),
    };
    _dosePerKilogram = defaults.dosePerKilogram;
    unawaited(_restorePreferences());
  }

  @override
  void dispose() {
    for (final TextEditingController controller in _controllers.values) {
      controller.dispose();
    }
    for (final FocusNode focusNode in _focusNodes.values) {
      focusNode.dispose();
    }
    super.dispose();
  }

  QuantityKind get _visibleDoseKind => _dosePerKilogram
      ? QuantityKind.weightNormalizedDose
      : QuantityKind.administrationRate;

  bool get _hasActiveNumericState =>
      _solution.userInputs.isNotEmpty ||
      _inputErrors.isNotEmpty ||
      _draftKinds.isNotEmpty;

  bool get _shouldIgnorePendingPreferenceRestore =>
      _hasLocalPreferenceEdit || _hasActiveNumericState;

  TextEditingController _controller(QuantityKind kind) => _controllers[kind]!;

  FocusNode _focusNode(QuantityKind kind) => _focusNodes[kind]!;

  @override
  Widget build(BuildContext context) {
    final AppLocalizations l10n = AppLocalizations.of(context);
    final List<String> problemMessages = _problemMessages();
    final SolverFact? latestResult = _latestCalculatedFact();
    final SolverFact? durationFact = _solution.fact(
      QuantityKind.infusionDuration,
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('InfusionCalc'),
        actions: <Widget>[
          IconButton(
            tooltip: l10n.clearAllTooltip,
            onPressed: _clearAll,
            icon: const Icon(Icons.delete_outline),
          ),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
          children: <Widget>[
            _TopUtilityRow(
              analyticsTracker: widget.analyticsTracker,
              onLanguageToggle: widget.onLanguageToggle,
            ),
            PwaInstallBanner(
              promptStore: widget.pwaInstallPromptStore,
              analyticsTracker: widget.analyticsTracker,
            ),
            if (problemMessages.isNotEmpty) ...<Widget>[
              const SizedBox(height: 12),
              _ProblemSummary(messages: problemMessages),
            ],
            const SizedBox(height: 20),
            _SectionHeading(
              title: l10n.patientSectionTitle,
              subtitle: l10n.patientSectionSubtitle,
            ),
            _buildField(
              kind: QuantityKind.bodyMass,
              label: l10n.quantityLabel(QuantityKind.bodyMass),
              helperText: l10n.bodyMassHelper,
            ),
            _SectionHeading(
              title: l10n.solutionSectionTitle,
              subtitle: l10n.solutionSectionSubtitle,
            ),
            _buildField(
              kind: QuantityKind.drugAmount,
              label: l10n.quantityLabel(QuantityKind.drugAmount),
            ),
            _buildField(
              kind: QuantityKind.solutionVolume,
              label: l10n.quantityLabel(QuantityKind.solutionVolume),
            ),
            _buildField(
              kind: QuantityKind.concentration,
              label: l10n.quantityLabel(QuantityKind.concentration),
            ),
            _SectionHeading(
              title: l10n.administrationSectionTitle,
              subtitle: l10n.administrationSectionSubtitle,
            ),
            _buildField(
              kind: QuantityKind.flowRate,
              label: l10n.quantityLabel(QuantityKind.flowRate),
            ),
            Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Wrap(
                  spacing: 12,
                  runSpacing: 8,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: <Widget>[
                    Text(l10n.weightBasedDoseLabel),
                    FilterChip(
                      key: const Key('per-kilogram-toggle'),
                      label: const Text('/kg'),
                      selected: _dosePerKilogram,
                      onSelected: _toggleDosePerKilogram,
                    ),
                    Text(
                      _dosePerKilogram
                          ? l10n.bodyMassIncluded
                          : l10n.administrationRateWithoutKilogram,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
            ),
            _buildField(
              kind: _visibleDoseKind,
              label: l10n.doseFieldLabel,
              helperText: _dosePerKilogram
                  ? l10n.weightBasedDoseHelper
                  : l10n.nonWeightBasedDoseHelper,
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
              l10n.liveCalculationNote,
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            AppFooter(
              key: const Key('app-footer'),
              analyticsTracker: widget.analyticsTracker,
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
      key: ValueKey<String>('calculation-field-${kind.name}'),
      fieldId: kind.name,
      label: label,
      controller: _controller(kind),
      focusNode: _focusNode(kind),
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

  List<MeasurementUnit> _unitsFor(QuantityKind kind) =>
      CalculatorUnitOptions.forKind(kind);

  CalculationFieldAppearance _appearanceFor(QuantityKind kind) {
    if (_inputErrors.containsKey(kind)) {
      return CalculationFieldAppearance.invalid;
    }
    if (_draftKinds.contains(kind)) {
      return CalculationFieldAppearance.userInput;
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
    final _LocalizedMessage? localError = _inputErrors[kind];
    if (localError != null) {
      return localError(AppLocalizations.of(context));
    }

    final SolverConflict? conflict = _solution.conflicts[kind];
    if (conflict != null) {
      final Quantity candidate = conflict.candidateInExistingUnit;
      return AppLocalizations.of(context).conflictingFieldExpected(
        RationalDecimalFormatter.format(candidate.value),
        candidate.unit.symbol,
      );
    }

    for (final SolverDiagnostic diagnostic in _solution.diagnostics) {
      if (diagnostic.involvedUserInputs.contains(kind)) {
        return _messageForDomainError(diagnostic.error);
      }
    }
    return null;
  }

  void _handleTextChanged(
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
      if (_requiresStrictlyPositive(kind) && quantity.isZero) {
        _recordInvalidInput(
          kind,
          (AppLocalizations l10n) => l10n.valueMustBePositive,
        );
        return;
      }
      final SolverSolution solution = _session.edit(quantity);

      setState(() {
        _draftKinds.remove(kind);
        _inputErrors.remove(kind);
        _globalMessage = null;
        _solution = solution;
        _synchronizeControllers();
      });
    } on DomainException catch (error) {
      _recordInvalidInput(
        kind,
        (AppLocalizations l10n) => l10n.domainError(error.code),
      );
    } on ArgumentError {
      _recordInvalidInput(kind, (AppLocalizations l10n) => l10n.invalidValue);
    }
  }

  void _handleFocusChanged(QuantityKind kind) {
    if (!mounted || _focusNode(kind).hasFocus || !_draftKinds.contains(kind)) {
      return;
    }
    _handleTextChanged(kind, _controller(kind).text, commitDraft: true);
  }

  bool _isTransientEditingText(QuantityKind kind, String text) {
    if (RegExp(r'^\d+[,.]$').hasMatch(text)) {
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

  static bool _requiresStrictlyPositive(QuantityKind kind) => switch (kind) {
    QuantityKind.bodyMass ||
    QuantityKind.solutionVolume ||
    QuantityKind.concentration ||
    QuantityKind.flowRate => true,
    _ => false,
  };

  void _recordInvalidInput(QuantityKind kind, _LocalizedMessage message) {
    SolverSolution safeSolution = _session.solution;
    try {
      safeSolution = _session.clear(kind);
    } on Object {
      // The transactional session has already restored the last safe state.
    }

    setState(() {
      _solution = safeSolution;
      _draftKinds.remove(kind);
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
        _queuePreferencesSave();
      } on UnitConversionException {
        final SolverSolution solution = _session.clear(kind);
        setState(() {
          _presentationUnits[kind] = newUnit;
          _inputErrors.remove(kind);
          _globalMessage = (AppLocalizations l10n) =>
              l10n.incompatibleUnitCleared;
          _solution = solution;
          _setControllerText(kind, '');
          _synchronizeControllers();
        });
        _queuePreferencesSave();
      }
      return;
    }

    if (displayedFact != null) {
      try {
        displayedFact.quantity.convertTo(newUnit);
      } on UnitConversionException {
        setState(() {
          _globalMessage = (AppLocalizations l10n) =>
              l10n.calculatedUnitFamilyUnavailable;
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
    _queuePreferencesSave();
  }

  void _toggleDosePerKilogram(bool enabled) {
    if (enabled == _dosePerKilogram) {
      return;
    }

    final QuantityKind outgoingKind = _visibleDoseKind;
    final QuantityKind incomingKind = enabled
        ? QuantityKind.weightNormalizedDose
        : QuantityKind.administrationRate;
    final SolverFact? outgoingInput = _solution.userInputs[outgoingKind];
    final SolverFact? incomingInput = _solution.userInputs[incomingKind];
    SolverSolution solution = _solution;
    MeasurementUnit? transferredUnit;
    Quantity? transferredQuantity;

    if (outgoingInput != null && incomingInput == null) {
      final SolverFact? counterpart = _solution.fact(incomingKind);
      if (counterpart?.origin != SolverFactOrigin.calculated) {
        setState(() {
          _globalMessage = (AppLocalizations l10n) =>
              l10n.doseModeNeedsBodyMass;
        });
        return;
      }

      transferredUnit = _presentationUnitForFact(
        incomingKind,
        counterpart!.quantity,
      );
      transferredQuantity = counterpart.quantity.convertTo(transferredUnit);
      solution = _session.edit(
        transferredQuantity,
        replaceInputKind: outgoingKind,
      );
    } else if (outgoingInput != null && incomingInput != null) {
      // A legacy session may contain explicit values in both modes. The
      // selected mode wins so the other value cannot remain hidden.
      solution = _session.clear(outgoingKind);
    }

    setState(() {
      _dosePerKilogram = enabled;
      _solution = solution;
      _inputErrors
        ..remove(outgoingKind)
        ..remove(incomingKind);
      _draftKinds
        ..remove(outgoingKind)
        ..remove(incomingKind);
      _globalMessage = null;
      if (transferredUnit != null) {
        _presentationUnits[incomingKind] = transferredUnit;
      }
      if (transferredQuantity != null) {
        _setControllerText(
          incomingKind,
          RationalDecimalFormatter.format(transferredQuantity.value),
        );
      }
      _synchronizeControllers();
    });
    _queuePreferencesSave();
  }

  MeasurementUnit _presentationUnitForFact(
    QuantityKind kind,
    Quantity quantity,
  ) {
    final MeasurementUnit preferred = _presentationUnits[kind]!;
    if (quantity.unit.isCompatibleWith(preferred)) {
      return preferred;
    }
    if (CalculatorUnitOptions.supports(kind, quantity.unit)) {
      return quantity.unit;
    }
    return _unitsFor(kind).firstWhere(
      (MeasurementUnit candidate) => quantity.unit.isCompatibleWith(candidate),
    );
  }

  Future<void> _restorePreferences() async {
    try {
      final CalculatorPreferences preferences = await _preferencesStore.load();
      if (!mounted || _shouldIgnorePendingPreferenceRestore) {
        return;
      }
      setState(() {
        for (final QuantityKind kind in CalculatorPreferences.persistedKinds) {
          _presentationUnits[kind] = preferences.unitFor(kind);
        }
        _dosePerKilogram = preferences.dosePerKilogram;
        _synchronizeControllers();
      });
    } on Object {
      if (!mounted || _shouldIgnorePendingPreferenceRestore) {
        return;
      }
      setState(() {
        _globalMessage = (AppLocalizations l10n) => l10n.preferencesReadFailed;
      });
    }
  }

  CalculatorPreferences _currentPreferences() => CalculatorPreferences(
    unitCodes: <QuantityKind, String>{
      for (final QuantityKind kind in CalculatorPreferences.persistedKinds)
        kind: _presentationUnits[kind]!.code,
    },
    dosePerKilogram: _dosePerKilogram,
  );

  void _queuePreferencesSave() {
    _hasLocalPreferenceEdit = true;
    final CalculatorPreferences snapshot = _currentPreferences();
    _preferencesWriteQueue = _preferencesWriteQueue.then(
      (_) => _savePreferencesSnapshot(snapshot),
    );
  }

  Future<void> _savePreferencesSnapshot(CalculatorPreferences snapshot) async {
    try {
      await _preferencesStore.save(snapshot);
    } on Object {
      if (!mounted) {
        return;
      }
      setState(() {
        _globalMessage = (AppLocalizations l10n) => l10n.preferencesSaveFailed;
      });
    }
  }

  void _clearAll() {
    setState(() {
      _inputErrors.clear();
      _draftKinds.clear();
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
        if (_inputErrors.containsKey(kind) || _draftKinds.contains(kind)) {
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
    final AppLocalizations l10n = AppLocalizations.of(context);
    final List<String> messages = <String>[];
    final _LocalizedMessage? globalMessage = _globalMessage;
    if (globalMessage != null) {
      messages.add(globalMessage(l10n));
    }

    for (final MapEntry<QuantityKind, _LocalizedMessage> entry
        in _inputErrors.entries) {
      messages.add('${l10n.quantityLabel(entry.key)}: ${entry.value(l10n)}');
    }
    for (final SolverConflict conflict in _solution.conflicts.values) {
      final Quantity expected = conflict.candidateInExistingUnit;
      messages.add(
        l10n.conflictingInputSummary(
          l10n.quantityLabel(conflict.kind),
          RationalDecimalFormatter.format(expected.value),
          expected.unit.symbol,
        ),
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
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(AppLocalizations.of(context).copiedResult(text))),
    );
  }

  String _messageForDomainError(DomainException error) =>
      AppLocalizations.of(context).domainError(error.code);
}

class _TopUtilityRow extends StatelessWidget {
  const _TopUtilityRow({
    required this.analyticsTracker,
    required this.onLanguageToggle,
  });

  final AnalyticsTracker analyticsTracker;
  final VoidCallback? onLanguageToggle;

  @override
  Widget build(BuildContext context) {
    final AppLocalizations l10n = AppLocalizations.of(context);
    final VoidCallback? toggle = onLanguageToggle;
    return Row(
      key: const Key('top-utility-row'),
      children: <Widget>[
        IconButton(
          key: const Key('technical-warning-button'),
          tooltip: l10n.technicalWarningTooltip,
          onPressed: () => _showWarning(context),
          color: Theme.of(context).colorScheme.error,
          icon: const Icon(Icons.warning_amber_rounded),
        ),
        const Spacer(),
        if (toggle != null)
          Semantics(
            label: l10n.languageSwitchTooltip,
            button: true,
            onTap: toggle,
            excludeSemantics: true,
            child: Tooltip(
              message: l10n.languageSwitchTooltip,
              child: SizedBox.square(
                dimension: 48,
                child: TextButton(
                  key: const Key('language-switch-button'),
                  style: TextButton.styleFrom(
                    minimumSize: const Size.square(48),
                    padding: EdgeInsets.zero,
                    tapTargetSize: MaterialTapTargetSize.padded,
                  ),
                  onPressed: toggle,
                  child: Text(
                    l10n.languageSwitchLabel,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }

  Future<void> _showWarning(BuildContext context) {
    analyticsTracker.track(AnalyticsEvent.warningOpened);
    return showDialog<void>(
      context: context,
      builder: (BuildContext dialogContext) {
        final AppLocalizations l10n = AppLocalizations.of(dialogContext);
        return AlertDialog(
          key: const Key('technical-warning-dialog'),
          title: Text(l10n.technicalWarningTitle),
          content: Text(l10n.technicalWarningText),
          actions: <Widget>[
            FilledButton(
              key: const Key('technical-warning-acknowledge-button'),
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: Text(l10n.acknowledge),
            ),
          ],
        );
      },
    );
  }
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
              AppLocalizations.of(context).checkData,
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
  Widget build(BuildContext context) {
    final AppLocalizations l10n = AppLocalizations.of(context);
    return Card(
      child: ListTile(
        leading: const Icon(Icons.timer_outlined),
        title: Text(l10n.infusionDurationTitle),
        subtitle: Text(l10n.infusionDurationSubtitle),
        trailing: Text(
          text,
          key: const Key('infusion-duration-value'),
          style: Theme.of(context).textTheme.titleMedium,
        ),
      ),
    );
  }
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
  Widget build(BuildContext context) {
    final AppLocalizations l10n = AppLocalizations.of(context);
    return Card(
      child: ExpansionTile(
        key: const Key('calculation-details'),
        leading: const Icon(Icons.calculate_outlined),
        title: Text(l10n.calculationDetailsTitle),
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
                '${l10n.quantityLabel(input.kind)}: '
                '${RationalDecimalFormatter.format(input.value)} '
                '${input.unitSymbol}',
              ),
            ),
          const SizedBox(height: 8),
          Align(
            alignment: Alignment.centerLeft,
            child: Text(
              l10n.calculationResult(formattedOutput),
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
          const SizedBox(height: 8),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton.icon(
              onPressed: onCopy,
              icon: const Icon(Icons.copy_outlined),
              label: Text(l10n.copyResult),
            ),
          ),
        ],
      ),
    );
  }
}
