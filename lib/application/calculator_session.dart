import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/solver/calculator_solver.dart';
import 'package:kalkulator_lekow/domain/solver/solver_models.dart';

/// Stateful application boundary that turns user edits into solver inputs.
///
/// Editing a calculated value promotes it to an explicit input. When possible,
/// the oldest replaceable root input is demoted so the newly edited value can
/// drive a recalculation instead of creating an unnecessary third constraint.
final class CalculatorSession {
  /// Creates an empty session.
  CalculatorSession({CalculatorSolver? solver})
    : _solver = solver ?? CalculatorSolver() {
    _solution = _solver.solve(const <SolverInput>[]);
  }

  final CalculatorSolver _solver;
  final Map<QuantityKind, SolverInput> _inputs = <QuantityKind, SolverInput>{};
  late SolverSolution _solution;
  int _lastEditSequence = 0;

  /// Current complete solver output.
  SolverSolution get solution => _solution;

  /// Current explicit input values.
  Map<QuantityKind, SolverInput> get inputs =>
      Map<QuantityKind, SolverInput>.unmodifiable(_inputs);

  /// Adds or changes one user input and immediately resolves the form.
  ///
  /// [replaceInputKind] may explicitly select an existing input to demote when
  /// the edited value was previously calculated. Patient body mass can never
  /// be selected for automatic or explicit replacement.
  SolverSolution edit(Quantity quantity, {QuantityKind? replaceInputKind}) {
    _validateEditableKind(quantity.kind);

    final SolverFact? previousFact = _solution.fact(quantity.kind);
    final bool takesOverCalculatedValue =
        previousFact?.origin == SolverFactOrigin.calculated;
    if (takesOverCalculatedValue) {
      final QuantityKind? replacement = replaceInputKind != null
          ? _validateExplicitReplacement(
              editedKind: quantity.kind,
              replacementKind: replaceInputKind,
            )
          : _selectAutomaticReplacement(
              editedKind: quantity.kind,
              previousFact: previousFact!,
            );
      if (replacement != null) {
        _inputs.remove(replacement);
      }
    } else if (replaceInputKind != null) {
      throw ArgumentError(
        'An explicit replacement is valid only when taking over a calculated '
        'value.',
      );
    }

    _lastEditSequence += 1;
    _inputs[quantity.kind] = SolverInput(
      quantity: quantity,
      editSequence: _lastEditSequence,
    );
    return _resolve();
  }

  /// Removes one explicit input and resolves every still reachable result.
  SolverSolution clear(QuantityKind kind) {
    _inputs.remove(kind);
    return _resolve();
  }

  /// Removes every user input and returns to an empty form.
  SolverSolution reset() {
    _inputs.clear();
    return _resolve();
  }

  SolverSolution _resolve() {
    _solution = _solver.solve(_inputs.values);
    return _solution;
  }

  QuantityKind? _selectAutomaticReplacement({
    required QuantityKind editedKind,
    required SolverFact previousFact,
  }) {
    final Set<QuantityKind> allowedCandidates =
        _replacementCandidates[editedKind] ?? const <QuantityKind>{};
    SolverInput? selectedInput;

    for (final QuantityKind candidateKind in allowedCandidates) {
      if (!previousFact.rootInputKinds.contains(candidateKind)) {
        continue;
      }
      final SolverInput? candidateInput = _inputs[candidateKind];
      if (candidateInput == null) {
        continue;
      }
      if (selectedInput == null ||
          candidateInput.editSequence < selectedInput.editSequence) {
        selectedInput = candidateInput;
      }
    }
    return selectedInput?.quantity.kind;
  }

  QuantityKind _validateExplicitReplacement({
    required QuantityKind editedKind,
    required QuantityKind replacementKind,
  }) {
    if (replacementKind == editedKind) {
      throw ArgumentError.value(
        replacementKind,
        'replaceInputKind',
        'The edited input cannot replace itself.',
      );
    }
    if (replacementKind == QuantityKind.bodyMass) {
      throw ArgumentError.value(
        replacementKind,
        'replaceInputKind',
        'Patient body mass is protected from takeover replacement.',
      );
    }
    if (!_inputs.containsKey(replacementKind)) {
      throw ArgumentError.value(
        replacementKind,
        'replaceInputKind',
        'Only an existing user input can be replaced.',
      );
    }
    return replacementKind;
  }

  static void _validateEditableKind(QuantityKind kind) {
    if (kind == QuantityKind.time || kind == QuantityKind.infusionDuration) {
      throw ArgumentError.value(
        kind,
        'quantity.kind',
        'This quantity is calculated-only in the MVP form.',
      );
    }
  }

  static const Map<QuantityKind, Set<QuantityKind>> _replacementCandidates =
      <QuantityKind, Set<QuantityKind>>{
        QuantityKind.drugAmount: <QuantityKind>{
          QuantityKind.concentration,
          QuantityKind.solutionVolume,
        },
        QuantityKind.solutionVolume: <QuantityKind>{
          QuantityKind.drugAmount,
          QuantityKind.concentration,
        },
        QuantityKind.concentration: <QuantityKind>{
          QuantityKind.drugAmount,
          QuantityKind.solutionVolume,
          QuantityKind.flowRate,
          QuantityKind.administrationRate,
        },
        QuantityKind.flowRate: <QuantityKind>{
          QuantityKind.weightNormalizedDose,
          QuantityKind.administrationRate,
          QuantityKind.concentration,
        },
        QuantityKind.administrationRate: <QuantityKind>{
          QuantityKind.flowRate,
          QuantityKind.weightNormalizedDose,
          QuantityKind.concentration,
        },
        QuantityKind.weightNormalizedDose: <QuantityKind>{
          QuantityKind.flowRate,
          QuantityKind.administrationRate,
        },
      };
}
