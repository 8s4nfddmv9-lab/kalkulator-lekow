import 'package:kalkulator_lekow/domain/calculations/calculation_trace.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/compound_unit_definition.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';
import 'package:kalkulator_lekow/domain/units/unit_conversion_exception.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';
import 'package:kalkulator_lekow/domain/units/unit_dimension.dart';

/// Exact, bidirectional equations for the infusion-calculator domain.
///
/// Every method validates semantic quantity kinds, dimensions, and zero
/// denominators before producing a typed result with an audit trace. No method
/// accepts or returns `double`.
abstract final class InfusionEquations {
  /// Calculates concentration from drug amount and final solution volume.
  static CalculationResult concentrationFromAmountAndVolume({
    required Quantity drugAmount,
    required Quantity solutionVolume,
    MeasurementUnit? outputUnit,
  }) {
    const EquationId equationId =
        EquationId.concentrationFromAmountAndVolume;
    _expectKind(drugAmount, QuantityKind.drugAmount, equationId);
    _expectKind(solutionVolume, QuantityKind.solutionVolume, equationId);
    _ensureNonZero(solutionVolume, equationId);

    final UnitDimension derivedDimension =
        drugAmount.unit.dimension - solutionVolume.unit.dimension;
    final MeasurementUnit targetUnit = _resolveOutputUnit(
      equationId: equationId,
      derivedDimension: derivedDimension,
      requestedUnit: outputUnit,
      fallbackCode: '${drugAmount.unit.code}/${solutionVolume.unit.code}',
    );

    return _result(
      equationId: equationId,
      inputs: <Quantity>[drugAmount, solutionVolume],
      canonicalValue:
          drugAmount.canonicalValue / solutionVolume.canonicalValue,
      targetUnit: targetUnit,
    );
  }

  /// Calculates drug amount from concentration and final solution volume.
  static CalculationResult drugAmountFromConcentrationAndVolume({
    required Quantity concentration,
    required Quantity solutionVolume,
    MeasurementUnit? outputUnit,
  }) {
    const EquationId equationId =
        EquationId.drugAmountFromConcentrationAndVolume;
    _expectKind(concentration, QuantityKind.concentration, equationId);
    _expectKind(solutionVolume, QuantityKind.solutionVolume, equationId);

    final UnitDimension derivedDimension =
        concentration.unit.dimension + solutionVolume.unit.dimension;
    final UnitDefinition amountUnit = _component(
      quantity: concentration,
      family: _drugFamily(concentration, equationId),
      location: _ComponentLocation.numerator,
      equationId: equationId,
    );
    final MeasurementUnit targetUnit = _resolveOutputUnit(
      equationId: equationId,
      derivedDimension: derivedDimension,
      requestedUnit: outputUnit,
      fallbackCode: amountUnit.code,
    );

    return _result(
      equationId: equationId,
      inputs: <Quantity>[concentration, solutionVolume],
      canonicalValue:
          concentration.canonicalValue * solutionVolume.canonicalValue,
      targetUnit: targetUnit,
    );
  }

  /// Calculates final solution volume from drug amount and concentration.
  static CalculationResult solutionVolumeFromAmountAndConcentration({
    required Quantity drugAmount,
    required Quantity concentration,
    MeasurementUnit? outputUnit,
  }) {
    const EquationId equationId =
        EquationId.solutionVolumeFromAmountAndConcentration;
    _expectKind(drugAmount, QuantityKind.drugAmount, equationId);
    _expectKind(concentration, QuantityKind.concentration, equationId);
    _ensureNonZero(concentration, equationId);

    final UnitDimension derivedDimension =
        drugAmount.unit.dimension - concentration.unit.dimension;
    final UnitDefinition volumeUnit = _component(
      quantity: concentration,
      family: UnitFamily.volume,
      location: _ComponentLocation.denominator,
      equationId: equationId,
    );
    final MeasurementUnit targetUnit = _resolveOutputUnit(
      equationId: equationId,
      derivedDimension: derivedDimension,
      requestedUnit: outputUnit,
      fallbackCode: volumeUnit.code,
    );

    return _result(
      equationId: equationId,
      inputs: <Quantity>[drugAmount, concentration],
      canonicalValue:
          drugAmount.canonicalValue / concentration.canonicalValue,
      targetUnit: targetUnit,
    );
  }

  /// Calculates non-weight-normalized administration rate from concentration
  /// and volumetric flow.
  static CalculationResult administrationRateFromConcentrationAndFlow({
    required Quantity concentration,
    required Quantity flowRate,
    MeasurementUnit? outputUnit,
  }) {
    const EquationId equationId =
        EquationId.administrationRateFromConcentrationAndFlow;
    _expectKind(concentration, QuantityKind.concentration, equationId);
    _expectKind(flowRate, QuantityKind.flowRate, equationId);

    final UnitDimension derivedDimension =
        concentration.unit.dimension + flowRate.unit.dimension;
    final UnitDefinition amountUnit = _component(
      quantity: concentration,
      family: _drugFamily(concentration, equationId),
      location: _ComponentLocation.numerator,
      equationId: equationId,
    );
    final UnitDefinition timeUnit = _component(
      quantity: flowRate,
      family: UnitFamily.time,
      location: _ComponentLocation.denominator,
      equationId: equationId,
    );
    final MeasurementUnit targetUnit = _resolveOutputUnit(
      equationId: equationId,
      derivedDimension: derivedDimension,
      requestedUnit: outputUnit,
      fallbackCode: '${amountUnit.code}/${timeUnit.code}',
    );

    return _result(
      equationId: equationId,
      inputs: <Quantity>[concentration, flowRate],
      canonicalValue:
          concentration.canonicalValue * flowRate.canonicalValue,
      targetUnit: targetUnit,
    );
  }

  /// Calculates volumetric flow from administration rate and concentration.
  static CalculationResult flowRateFromAdministrationRateAndConcentration({
    required Quantity administrationRate,
    required Quantity concentration,
    MeasurementUnit? outputUnit,
  }) {
    const EquationId equationId =
        EquationId.flowRateFromAdministrationRateAndConcentration;
    _expectKind(
      administrationRate,
      QuantityKind.administrationRate,
      equationId,
    );
    _expectKind(concentration, QuantityKind.concentration, equationId);
    _ensureNonZero(concentration, equationId);

    final UnitDimension derivedDimension =
        administrationRate.unit.dimension - concentration.unit.dimension;
    final UnitDefinition volumeUnit = _component(
      quantity: concentration,
      family: UnitFamily.volume,
      location: _ComponentLocation.denominator,
      equationId: equationId,
    );
    final UnitDefinition timeUnit = _component(
      quantity: administrationRate,
      family: UnitFamily.time,
      location: _ComponentLocation.denominator,
      equationId: equationId,
    );
    final MeasurementUnit targetUnit = _resolveOutputUnit(
      equationId: equationId,
      derivedDimension: derivedDimension,
      requestedUnit: outputUnit,
      fallbackCode: '${volumeUnit.code}/${timeUnit.code}',
    );

    return _result(
      equationId: equationId,
      inputs: <Quantity>[administrationRate, concentration],
      canonicalValue:
          administrationRate.canonicalValue / concentration.canonicalValue,
      targetUnit: targetUnit,
    );
  }

  /// Calculates concentration from administration rate and volumetric flow.
  static CalculationResult concentrationFromAdministrationRateAndFlow({
    required Quantity administrationRate,
    required Quantity flowRate,
    MeasurementUnit? outputUnit,
  }) {
    const EquationId equationId =
        EquationId.concentrationFromAdministrationRateAndFlow;
    _expectKind(
      administrationRate,
      QuantityKind.administrationRate,
      equationId,
    );
    _expectKind(flowRate, QuantityKind.flowRate, equationId);
    _ensureNonZero(flowRate, equationId);

    final UnitDimension derivedDimension =
        administrationRate.unit.dimension - flowRate.unit.dimension;
    final UnitDefinition amountUnit = _component(
      quantity: administrationRate,
      family: _drugFamily(administrationRate, equationId),
      location: _ComponentLocation.numerator,
      equationId: equationId,
    );
    final UnitDefinition volumeUnit = _component(
      quantity: flowRate,
      family: UnitFamily.volume,
      location: _ComponentLocation.numerator,
      equationId: equationId,
    );
    final MeasurementUnit targetUnit = _resolveOutputUnit(
      equationId: equationId,
      derivedDimension: derivedDimension,
      requestedUnit: outputUnit,
      fallbackCode: '${amountUnit.code}/${volumeUnit.code}',
    );

    return _result(
      equationId: equationId,
      inputs: <Quantity>[administrationRate, flowRate],
      canonicalValue:
          administrationRate.canonicalValue / flowRate.canonicalValue,
      targetUnit: targetUnit,
    );
  }

  /// Calculates a body-mass-normalized dose from administration rate and
  /// patient body mass.
  static CalculationResult weightNormalizedDoseFromAdministrationRateAndBodyMass({
    required Quantity administrationRate,
    required Quantity bodyMass,
    MeasurementUnit? outputUnit,
  }) {
    const EquationId equationId =
        EquationId.weightNormalizedDoseFromAdministrationRateAndBodyMass;
    _expectKind(
      administrationRate,
      QuantityKind.administrationRate,
      equationId,
    );
    _expectKind(bodyMass, QuantityKind.bodyMass, equationId);
    _ensureNonZero(bodyMass, equationId);

    final UnitDimension derivedDimension =
        administrationRate.unit.dimension - bodyMass.unit.dimension;
    final UnitDefinition amountUnit = _component(
      quantity: administrationRate,
      family: _drugFamily(administrationRate, equationId),
      location: _ComponentLocation.numerator,
      equationId: equationId,
    );
    final UnitDefinition timeUnit = _component(
      quantity: administrationRate,
      family: UnitFamily.time,
      location: _ComponentLocation.denominator,
      equationId: equationId,
    );
    final MeasurementUnit targetUnit = _resolveOutputUnit(
      equationId: equationId,
      derivedDimension: derivedDimension,
      requestedUnit: outputUnit,
      fallbackCode: '${amountUnit.code}/${UnitCatalog.kilogram.code}/${timeUnit.code}',
    );

    return _result(
      equationId: equationId,
      inputs: <Quantity>[administrationRate, bodyMass],
      canonicalValue:
          administrationRate.canonicalValue / bodyMass.canonicalValue,
      targetUnit: targetUnit,
    );
  }

  /// Calculates administration rate from a body-mass-normalized dose and
  /// patient body mass.
  ///
  /// No inverse equation calculating body mass is registered anywhere in this
  /// class.
  static CalculationResult administrationRateFromWeightNormalizedDoseAndBodyMass({
    required Quantity weightNormalizedDose,
    required Quantity bodyMass,
    MeasurementUnit? outputUnit,
  }) {
    const EquationId equationId =
        EquationId.administrationRateFromWeightNormalizedDoseAndBodyMass;
    _expectKind(
      weightNormalizedDose,
      QuantityKind.weightNormalizedDose,
      equationId,
    );
    _expectKind(bodyMass, QuantityKind.bodyMass, equationId);
    _ensureNonZero(bodyMass, equationId);

    final UnitDimension derivedDimension =
        weightNormalizedDose.unit.dimension + bodyMass.unit.dimension;
    final UnitDefinition amountUnit = _component(
      quantity: weightNormalizedDose,
      family: _drugFamily(weightNormalizedDose, equationId),
      location: _ComponentLocation.numerator,
      equationId: equationId,
    );
    final UnitDefinition timeUnit = _component(
      quantity: weightNormalizedDose,
      family: UnitFamily.time,
      location: _ComponentLocation.denominator,
      equationId: equationId,
    );
    final MeasurementUnit targetUnit = _resolveOutputUnit(
      equationId: equationId,
      derivedDimension: derivedDimension,
      requestedUnit: outputUnit,
      fallbackCode: '${amountUnit.code}/${timeUnit.code}',
    );

    return _result(
      equationId: equationId,
      inputs: <Quantity>[weightNormalizedDose, bodyMass],
      canonicalValue:
          weightNormalizedDose.canonicalValue * bodyMass.canonicalValue,
      targetUnit: targetUnit,
    );
  }

  /// Calculates infusion duration from final solution volume and flow rate.
  static CalculationResult infusionDurationFromVolumeAndFlow({
    required Quantity solutionVolume,
    required Quantity flowRate,
    MeasurementUnit? outputUnit,
  }) {
    const EquationId equationId =
        EquationId.infusionDurationFromVolumeAndFlow;
    _expectKind(solutionVolume, QuantityKind.solutionVolume, equationId);
    _expectKind(flowRate, QuantityKind.flowRate, equationId);
    _ensureNonZero(flowRate, equationId);

    final UnitDimension derivedDimension =
        solutionVolume.unit.dimension - flowRate.unit.dimension;
    final UnitDefinition timeUnit = _component(
      quantity: flowRate,
      family: UnitFamily.time,
      location: _ComponentLocation.denominator,
      equationId: equationId,
    );
    final MeasurementUnit targetUnit = _resolveOutputUnit(
      equationId: equationId,
      derivedDimension: derivedDimension,
      requestedUnit: outputUnit,
      fallbackCode: timeUnit.code,
    );

    return _result(
      equationId: equationId,
      inputs: <Quantity>[solutionVolume, flowRate],
      canonicalValue:
          solutionVolume.canonicalValue / flowRate.canonicalValue,
      targetUnit: targetUnit,
    );
  }

  static CalculationResult _result({
    required EquationId equationId,
    required List<Quantity> inputs,
    required Rational canonicalValue,
    required MeasurementUnit targetUnit,
  }) {
    final Quantity quantity = Quantity(
      kind: equationId.targetKind,
      value: canonicalValue / targetUnit.toCanonical,
      unit: targetUnit,
    );
    return CalculationResult(
      quantity: quantity,
      trace: CalculationTrace(
        equationId: equationId,
        inputs: inputs,
        output: quantity,
      ),
    );
  }

  static MeasurementUnit _resolveOutputUnit({
    required EquationId equationId,
    required UnitDimension derivedDimension,
    required MeasurementUnit? requestedUnit,
    required String fallbackCode,
  }) {
    if (!equationId.targetKind.acceptsDimension(derivedDimension)) {
      throw QuantityUnitException(
        quantityKind: equationId.targetKind.name,
        unitCode: 'derived:${equationId.name}',
        unitDimension: derivedDimension.toString(),
      );
    }

    final MeasurementUnit targetUnit =
        requestedUnit ?? UnitCatalog.find(fallbackCode);
    if (!equationId.targetKind.accepts(targetUnit)) {
      throw QuantityUnitException(
        quantityKind: equationId.targetKind.name,
        unitCode: targetUnit.code,
        unitDimension: targetUnit.dimension.toString(),
      );
    }
    if (targetUnit.dimension != derivedDimension) {
      throw UnitConversionException(
        sourceCode: 'derived:${equationId.name}',
        sourceDimension: derivedDimension.toString(),
        targetCode: targetUnit.code,
        targetDimension: targetUnit.dimension.toString(),
      );
    }
    return targetUnit;
  }

  static void _expectKind(
    Quantity quantity,
    QuantityKind expectedKind,
    EquationId equationId,
  ) {
    if (quantity.kind != expectedKind) {
      throw EquationInputException(
        equationId: equationId.name,
        expectedKind: expectedKind.name,
        actualKind: quantity.kind.name,
      );
    }
  }

  static void _ensureNonZero(
    Quantity denominator,
    EquationId equationId,
  ) {
    if (denominator.isZero) {
      throw ZeroDenominatorException(
        equationId: equationId.name,
        denominatorKind: denominator.kind.name,
      );
    }
  }

  static UnitFamily _drugFamily(
    Quantity quantity,
    EquationId equationId,
  ) {
    if (quantity.unit.dimension.medicineMassExponent != 0 &&
        quantity.unit.dimension.biologicalActivityExponent == 0) {
      return UnitFamily.medicineMass;
    }
    if (quantity.unit.dimension.biologicalActivityExponent != 0 &&
        quantity.unit.dimension.medicineMassExponent == 0) {
      return UnitFamily.biologicalActivity;
    }
    throw QuantityUnitException(
      quantityKind: quantity.kind.name,
      unitCode: quantity.unit.code,
      unitDimension: quantity.unit.dimension.toString(),
    );
  }

  static UnitDefinition _component({
    required Quantity quantity,
    required UnitFamily family,
    required _ComponentLocation location,
    required EquationId equationId,
  }) {
    final MeasurementUnit measurementUnit = quantity.unit;
    if (measurementUnit is UnitDefinition) {
      if (location == _ComponentLocation.numerator &&
          measurementUnit.family == family) {
        return measurementUnit;
      }
      throw QuantityUnitException(
        quantityKind: quantity.kind.name,
        unitCode: measurementUnit.code,
        unitDimension: measurementUnit.dimension.toString(),
      );
    }
    if (measurementUnit is! CompoundUnitDefinition) {
      throw QuantityUnitException(
        quantityKind: quantity.kind.name,
        unitCode: measurementUnit.code,
        unitDimension: measurementUnit.dimension.toString(),
      );
    }

    final List<UnitDefinition> components =
        location == _ComponentLocation.numerator
        ? measurementUnit.numeratorUnits
        : measurementUnit.denominatorUnits;
    final List<UnitDefinition> matches = components
        .where((UnitDefinition unit) => unit.family == family)
        .toList(growable: false);
    if (matches.length != 1) {
      throw QuantityUnitException(
        quantityKind: quantity.kind.name,
        unitCode: '${measurementUnit.code}@${equationId.name}',
        unitDimension: measurementUnit.dimension.toString(),
      );
    }
    return matches.single;
  }
}

enum _ComponentLocation { numerator, denominator }
