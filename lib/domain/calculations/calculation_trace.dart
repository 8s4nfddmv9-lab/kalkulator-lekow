import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';

/// Stable identifiers for every bidirectional equation in the MVP domain.
enum EquationId {
  /// `concentration = drugAmount / solutionVolume`.
  concentrationFromAmountAndVolume,

  /// `drugAmount = concentration × solutionVolume`.
  drugAmountFromConcentrationAndVolume,

  /// `solutionVolume = drugAmount / concentration`.
  solutionVolumeFromAmountAndConcentration,

  /// `administrationRate = concentration × flowRate`.
  administrationRateFromConcentrationAndFlow,

  /// `flowRate = administrationRate / concentration`.
  flowRateFromAdministrationRateAndConcentration,

  /// `concentration = administrationRate / flowRate`.
  concentrationFromAdministrationRateAndFlow,

  /// `weightNormalizedDose = administrationRate / bodyMass`.
  weightNormalizedDoseFromAdministrationRateAndBodyMass,

  /// `administrationRate = weightNormalizedDose × bodyMass`.
  administrationRateFromWeightNormalizedDoseAndBodyMass,

  /// `infusionDuration = solutionVolume / flowRate`.
  infusionDurationFromVolumeAndFlow,
}

/// Formula metadata used by audit and presentation layers.
extension EquationMetadata on EquationId {
  /// Locale-independent symbolic formula.
  String get formula => switch (this) {
    EquationId.concentrationFromAmountAndVolume => 'C = A / V',
    EquationId.drugAmountFromConcentrationAndVolume => 'A = C × V',
    EquationId.solutionVolumeFromAmountAndConcentration => 'V = A / C',
    EquationId.administrationRateFromConcentrationAndFlow => 'P = C × R',
    EquationId.flowRateFromAdministrationRateAndConcentration => 'R = P / C',
    EquationId.concentrationFromAdministrationRateAndFlow => 'C = P / R',
    EquationId.weightNormalizedDoseFromAdministrationRateAndBodyMass =>
      'D = P / W',
    EquationId.administrationRateFromWeightNormalizedDoseAndBodyMass =>
      'P = D × W',
    EquationId.infusionDurationFromVolumeAndFlow => 'T = V / R',
  };

  /// Semantic role of the equation result.
  QuantityKind get targetKind => switch (this) {
    EquationId.concentrationFromAmountAndVolume ||
    EquationId.concentrationFromAdministrationRateAndFlow =>
      QuantityKind.concentration,
    EquationId.drugAmountFromConcentrationAndVolume =>
      QuantityKind.drugAmount,
    EquationId.solutionVolumeFromAmountAndConcentration =>
      QuantityKind.solutionVolume,
    EquationId.administrationRateFromConcentrationAndFlow ||
    EquationId.administrationRateFromWeightNormalizedDoseAndBodyMass =>
      QuantityKind.administrationRate,
    EquationId.flowRateFromAdministrationRateAndConcentration =>
      QuantityKind.flowRate,
    EquationId.weightNormalizedDoseFromAdministrationRateAndBodyMass =>
      QuantityKind.weightNormalizedDose,
    EquationId.infusionDurationFromVolumeAndFlow =>
      QuantityKind.infusionDuration,
  };
}

/// Exact snapshot of one calculation input or output.
final class CalculationOperand {
  /// Captures a quantity without losing its selected unit or canonical value.
  CalculationOperand.fromQuantity(Quantity quantity)
    : kind = quantity.kind,
      value = quantity.value,
      unitCode = quantity.unit.code,
      unitSymbol = quantity.unit.symbol,
      canonicalValue = quantity.canonicalValue;

  /// Semantic role of the operand.
  final QuantityKind kind;

  /// Exact value in the selected unit.
  final Rational value;

  /// Stable internal unit code.
  final String unitCode;

  /// Human-readable unit symbol at calculation time.
  final String unitSymbol;

  /// Exact value in the canonical unit for its dimension.
  final Rational canonicalValue;
}

/// Immutable, auditable record of how a result was derived.
final class CalculationTrace {
  /// Creates a trace from exact source and target quantities.
  CalculationTrace({
    required this.equationId,
    required List<Quantity> inputs,
    required Quantity output,
  }) : inputs = List<CalculationOperand>.unmodifiable(
         inputs.map(CalculationOperand.fromQuantity),
       ),
       output = CalculationOperand.fromQuantity(output);

  /// Equation that produced the result.
  final EquationId equationId;

  /// Exact source operands in formula order.
  final List<CalculationOperand> inputs;

  /// Exact derived operand.
  final CalculationOperand output;

  /// Symbolic formula associated with [equationId].
  String get formula => equationId.formula;
}

/// A calculated quantity paired with its complete derivation trace.
final class CalculationResult {
  /// Creates a calculation result.
  const CalculationResult({required this.quantity, required this.trace});

  /// Exact derived quantity.
  final Quantity quantity;

  /// Audit information for the derivation.
  final CalculationTrace trace;
}
