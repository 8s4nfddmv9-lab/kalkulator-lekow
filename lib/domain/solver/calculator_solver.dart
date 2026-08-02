import 'package:kalkulator_lekow/domain/calculations/calculation_trace.dart';
import 'package:kalkulator_lekow/domain/calculations/infusion_equations.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/solver/solver_models.dart';

/// Deterministic fixed-point solver over the approved infusion equations.
///
/// Explicit user inputs are never overwritten. When redundant information is
/// inconsistent, the affected quantity kind is blocked and all calculated
/// descendants that traversed it are removed.
final class CalculatorSolver {
  /// Creates a solver with an exact relative comparison tolerance.
  CalculatorSolver({Rational? relativeTolerance})
    : relativeTolerance =
          relativeTolerance ??
          Rational(BigInt.one, BigInt.from(10).pow(12)) {
    if (this.relativeTolerance.isNegative) {
      throw ArgumentError.value(
        this.relativeTolerance,
        'relativeTolerance',
        'Relative tolerance cannot be negative.',
      );
    }
  }

  /// Maximum accepted relative difference between redundant exact values.
  final Rational relativeTolerance;

  /// Solves every value reachable from [inputs] without choosing between
  /// conflicting facts.
  SolverSolution solve(Iterable<SolverInput> inputs) {
    final Map<QuantityKind, SolverInput> normalizedInputs = _normalizeInputs(
      inputs,
    );
    final Map<QuantityKind, SolverFact> userFacts =
        <QuantityKind, SolverFact>{};
    for (final QuantityKind kind in QuantityKind.values) {
      final SolverInput? input = normalizedInputs[kind];
      if (input != null) {
        userFacts[kind] = SolverFact.userInput(input);
      }
    }

    final Map<QuantityKind, SolverFact> facts =
        Map<QuantityKind, SolverFact>.of(userFacts);
    final Map<QuantityKind, SolverConflict> conflicts =
        <QuantityKind, SolverConflict>{};
    final Set<QuantityKind> blockedKinds = <QuantityKind>{};

    bool changed = true;
    int pass = 0;
    while (changed) {
      pass += 1;
      if (pass > QuantityKind.values.length * _rules.length + 1) {
        throw StateError('Calculator solver did not reach a fixed point.');
      }

      changed = false;
      bool restartAfterConflict = false;

      for (final _SolverRule rule in _rules) {
        final QuantityKind targetKind = rule.equationId.targetKind;
        if (blockedKinds.contains(targetKind) ||
            rule.sourceKinds.any(blockedKinds.contains)) {
          continue;
        }

        final List<SolverFact> sourceFacts = <SolverFact>[];
        bool hasEverySource = true;
        for (final QuantityKind sourceKind in rule.sourceKinds) {
          final SolverFact? source = facts[sourceKind];
          if (source == null) {
            hasEverySource = false;
            break;
          }
          sourceFacts.add(source);
        }
        if (!hasEverySource) {
          continue;
        }

        // Do not re-enter a quantity already traversed by the source path.
        if (sourceFacts.any(
          (SolverFact source) => source.pathKinds.contains(targetKind),
        )) {
          continue;
        }

        final CalculationResult candidateResult = rule.evaluate(sourceFacts);
        final SolverFact candidateFact = SolverFact.calculated(
          result: candidateResult,
          sources: sourceFacts,
        );
        final SolverFact? existingFact = facts[targetKind];

        if (existingFact == null) {
          facts[targetKind] = candidateFact;
          changed = true;
          continue;
        }

        if (_areEquivalent(
          existingFact.quantity,
          candidateFact.quantity,
        )) {
          continue;
        }

        conflicts.putIfAbsent(
          targetKind,
          () => _buildConflict(
            targetKind: targetKind,
            existingFact: existingFact,
            candidateResult: candidateResult,
            candidateFact: candidateFact,
          ),
        );
        blockedKinds.add(targetKind);
        facts.remove(targetKind);
        _removeCalculatedDescendants(
          facts: facts,
          blockedKind: targetKind,
        );
        changed = true;
        restartAfterConflict = true;
        break;
      }

      if (restartAfterConflict) {
        continue;
      }
    }

    for (final QuantityKind blockedKind in blockedKinds) {
      facts.remove(blockedKind);
    }

    return SolverSolution(
      userInputs: userFacts,
      facts: facts,
      conflicts: conflicts,
    );
  }

  Map<QuantityKind, SolverInput> _normalizeInputs(
    Iterable<SolverInput> inputs,
  ) {
    final List<SolverInput> orderedInputs = inputs.toList(growable: false)
      ..sort((SolverInput left, SolverInput right) {
        final int sequenceComparison = left.editSequence.compareTo(
          right.editSequence,
        );
        if (sequenceComparison != 0) {
          return sequenceComparison;
        }
        return left.quantity.kind.index.compareTo(right.quantity.kind.index);
      });
    final Map<QuantityKind, SolverInput> result =
        <QuantityKind, SolverInput>{};

    for (final SolverInput input in orderedInputs) {
      if (input.editSequence < 0) {
        throw ArgumentError.value(
          input.editSequence,
          'editSequence',
          'Edit sequence cannot be negative.',
        );
      }
      if (input.quantity.kind == QuantityKind.time ||
          input.quantity.kind == QuantityKind.infusionDuration) {
        throw ArgumentError.value(
          input.quantity.kind,
          'quantity.kind',
          'This quantity is calculated-only in the MVP form.',
        );
      }

      final SolverInput? existing = result[input.quantity.kind];
      if (existing != null && existing.editSequence == input.editSequence) {
        throw ArgumentError(
          'Duplicate input for ${input.quantity.kind.name} has the same '
          'edit sequence.',
        );
      }
      result[input.quantity.kind] = input;
    }
    return result;
  }

  bool _areEquivalent(Quantity left, Quantity right) {
    if (left.kind != right.kind ||
        !left.unit.isCompatibleWith(right.unit)) {
      return false;
    }

    final Rational leftCanonical = left.canonicalValue;
    final Rational rightCanonical = right.canonicalValue;
    if (leftCanonical == rightCanonical) {
      return true;
    }

    final Rational difference = (leftCanonical - rightCanonical).absolute;
    final Rational leftMagnitude = leftCanonical.absolute;
    final Rational rightMagnitude = rightCanonical.absolute;
    final Rational scale = leftMagnitude >= rightMagnitude
        ? leftMagnitude
        : rightMagnitude;
    if (scale.isZero) {
      return true;
    }
    return difference / scale <= relativeTolerance;
  }

  SolverConflict _buildConflict({
    required QuantityKind targetKind,
    required SolverFact existingFact,
    required CalculationResult candidateResult,
    required SolverFact candidateFact,
  }) {
    final bool compatible = existingFact.quantity.unit.isCompatibleWith(
      candidateFact.quantity.unit,
    );
    final Quantity candidateInExistingUnit = compatible
        ? candidateFact.quantity.convertTo(existingFact.quantity.unit)
        : candidateFact.quantity;
    final Rational relativeDifference = compatible
        ? _relativeDifference(
            existingFact.quantity.canonicalValue,
            candidateFact.quantity.canonicalValue,
          )
        : Rational.fromInt(1);
    final Set<QuantityKind> involvedUserInputs = <QuantityKind>{
      ...existingFact.rootInputKinds,
      ...candidateFact.rootInputKinds,
    };

    return SolverConflict(
      kind: targetKind,
      existingFact: existingFact,
      candidateResult: candidateResult,
      candidateInExistingUnit: candidateInExistingUnit,
      relativeDifference: relativeDifference,
      involvedUserInputs: involvedUserInputs,
    );
  }

  static Rational _relativeDifference(Rational left, Rational right) {
    if (left == right) {
      return Rational.fromInt(0);
    }
    final Rational difference = (left - right).absolute;
    final Rational leftMagnitude = left.absolute;
    final Rational rightMagnitude = right.absolute;
    final Rational scale = leftMagnitude >= rightMagnitude
        ? leftMagnitude
        : rightMagnitude;
    return scale.isZero ? Rational.fromInt(0) : difference / scale;
  }

  static void _removeCalculatedDescendants({
    required Map<QuantityKind, SolverFact> facts,
    required QuantityKind blockedKind,
  }) {
    final List<QuantityKind> descendants = facts.entries
        .where(
          (MapEntry<QuantityKind, SolverFact> entry) =>
              entry.value.origin == SolverFactOrigin.calculated &&
              entry.value.pathKinds.contains(blockedKind),
        )
        .map((MapEntry<QuantityKind, SolverFact> entry) => entry.key)
        .toList(growable: false);
    for (final QuantityKind descendant in descendants) {
      facts.remove(descendant);
    }
  }

  static final List<_SolverRule> _rules = <_SolverRule>[
    _SolverRule(
      equationId: EquationId.concentrationFromAmountAndVolume,
      sourceKinds: const <QuantityKind>[
        QuantityKind.drugAmount,
        QuantityKind.solutionVolume,
      ],
      evaluate: (List<SolverFact> sources) =>
          InfusionEquations.concentrationFromAmountAndVolume(
            drugAmount: sources[0].quantity,
            solutionVolume: sources[1].quantity,
          ),
    ),
    _SolverRule(
      equationId: EquationId.drugAmountFromConcentrationAndVolume,
      sourceKinds: const <QuantityKind>[
        QuantityKind.concentration,
        QuantityKind.solutionVolume,
      ],
      evaluate: (List<SolverFact> sources) =>
          InfusionEquations.drugAmountFromConcentrationAndVolume(
            concentration: sources[0].quantity,
            solutionVolume: sources[1].quantity,
          ),
    ),
    _SolverRule(
      equationId: EquationId.solutionVolumeFromAmountAndConcentration,
      sourceKinds: const <QuantityKind>[
        QuantityKind.drugAmount,
        QuantityKind.concentration,
      ],
      evaluate: (List<SolverFact> sources) =>
          InfusionEquations.solutionVolumeFromAmountAndConcentration(
            drugAmount: sources[0].quantity,
            concentration: sources[1].quantity,
          ),
    ),
    _SolverRule(
      equationId: EquationId.administrationRateFromConcentrationAndFlow,
      sourceKinds: const <QuantityKind>[
        QuantityKind.concentration,
        QuantityKind.flowRate,
      ],
      evaluate: (List<SolverFact> sources) =>
          InfusionEquations.administrationRateFromConcentrationAndFlow(
            concentration: sources[0].quantity,
            flowRate: sources[1].quantity,
          ),
    ),
    _SolverRule(
      equationId: EquationId.flowRateFromAdministrationRateAndConcentration,
      sourceKinds: const <QuantityKind>[
        QuantityKind.administrationRate,
        QuantityKind.concentration,
      ],
      evaluate: (List<SolverFact> sources) =>
          InfusionEquations.flowRateFromAdministrationRateAndConcentration(
            administrationRate: sources[0].quantity,
            concentration: sources[1].quantity,
          ),
    ),
    _SolverRule(
      equationId: EquationId.concentrationFromAdministrationRateAndFlow,
      sourceKinds: const <QuantityKind>[
        QuantityKind.administrationRate,
        QuantityKind.flowRate,
      ],
      evaluate: (List<SolverFact> sources) =>
          InfusionEquations.concentrationFromAdministrationRateAndFlow(
            administrationRate: sources[0].quantity,
            flowRate: sources[1].quantity,
          ),
    ),
    _SolverRule(
      equationId:
          EquationId.weightNormalizedDoseFromAdministrationRateAndBodyMass,
      sourceKinds: const <QuantityKind>[
        QuantityKind.administrationRate,
        QuantityKind.bodyMass,
      ],
      evaluate: (List<SolverFact> sources) => InfusionEquations
          .weightNormalizedDoseFromAdministrationRateAndBodyMass(
            administrationRate: sources[0].quantity,
            bodyMass: sources[1].quantity,
          ),
    ),
    _SolverRule(
      equationId:
          EquationId.administrationRateFromWeightNormalizedDoseAndBodyMass,
      sourceKinds: const <QuantityKind>[
        QuantityKind.weightNormalizedDose,
        QuantityKind.bodyMass,
      ],
      evaluate: (List<SolverFact> sources) => InfusionEquations
          .administrationRateFromWeightNormalizedDoseAndBodyMass(
            weightNormalizedDose: sources[0].quantity,
            bodyMass: sources[1].quantity,
          ),
    ),
    _SolverRule(
      equationId: EquationId.infusionDurationFromVolumeAndFlow,
      sourceKinds: const <QuantityKind>[
        QuantityKind.solutionVolume,
        QuantityKind.flowRate,
      ],
      evaluate: (List<SolverFact> sources) =>
          InfusionEquations.infusionDurationFromVolumeAndFlow(
            solutionVolume: sources[0].quantity,
            flowRate: sources[1].quantity,
          ),
    ),
  ];
}

typedef _RuleEvaluator = CalculationResult Function(List<SolverFact> sources);

final class _SolverRule {
  const _SolverRule({
    required this.equationId,
    required this.sourceKinds,
    required this.evaluate,
  });

  final EquationId equationId;
  final List<QuantityKind> sourceKinds;
  final _RuleEvaluator evaluate;
}
