import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/calculations/calculation_trace.dart';
import 'package:kalkulator_lekow/domain/calculations/infusion_equations.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  group('reference calculation chains', () {
    test('4 mg, 50 ml and 5 ml/h produce the reference dose', () {
      final Quantity amount = Quantity(
        kind: QuantityKind.drugAmount,
        value: Rational.fromInt(4),
        unit: UnitCatalog.milligram,
      );
      final Quantity volume = Quantity(
        kind: QuantityKind.solutionVolume,
        value: Rational.fromInt(50),
        unit: UnitCatalog.millilitre,
      );
      final Quantity flow = Quantity(
        kind: QuantityKind.flowRate,
        value: Rational.fromInt(5),
        unit: UnitCatalog.millilitresPerHour,
      );
      final Quantity bodyMass = Quantity(
        kind: QuantityKind.bodyMass,
        value: Rational.fromInt(70),
        unit: UnitCatalog.kilogram,
      );

      final CalculationResult concentration =
          InfusionEquations.concentrationFromAmountAndVolume(
            drugAmount: amount,
            solutionVolume: volume,
            outputUnit: UnitCatalog.find('ug/mL'),
          );
      final CalculationResult administrationRate =
          InfusionEquations.administrationRateFromConcentrationAndFlow(
            concentration: concentration.quantity,
            flowRate: flow,
            outputUnit: UnitCatalog.find('ug/h'),
          );
      final CalculationResult dose = InfusionEquations
          .weightNormalizedDoseFromAdministrationRateAndBodyMass(
            administrationRate: administrationRate.quantity,
            bodyMass: bodyMass,
            outputUnit: UnitCatalog.find('ug/kg/min'),
          );

      expect(concentration.quantity.value, Rational.fromInt(80));
      expect(administrationRate.quantity.value, Rational.fromInt(400));
      expect(
        dose.quantity.value,
        Rational(BigInt.from(2), BigInt.from(21)),
      );
      expect(dose.trace.inputs.first.canonicalValue, Rational.fromInt(20000) / Rational.fromInt(3));
    });

    test('0.1 µg/kg/min at 70 kg and 80 µg/ml gives 5.25 ml/h', () {
      final Quantity desiredDose = Quantity.parse(
        kind: QuantityKind.weightNormalizedDose,
        source: '0,1',
        unit: UnitCatalog.find('ug/kg/min'),
      );
      final Quantity bodyMass = Quantity(
        kind: QuantityKind.bodyMass,
        value: Rational.fromInt(70),
        unit: UnitCatalog.kilogram,
      );
      final Quantity concentration = Quantity(
        kind: QuantityKind.concentration,
        value: Rational.fromInt(80),
        unit: UnitCatalog.find('ug/mL'),
      );

      final CalculationResult administrationRate = InfusionEquations
          .administrationRateFromWeightNormalizedDoseAndBodyMass(
            weightNormalizedDose: desiredDose,
            bodyMass: bodyMass,
            outputUnit: UnitCatalog.find('ug/h'),
          );
      final CalculationResult flow =
          InfusionEquations.flowRateFromAdministrationRateAndConcentration(
            administrationRate: administrationRate.quantity,
            concentration: concentration,
            outputUnit: UnitCatalog.millilitresPerHour,
          );

      expect(administrationRate.quantity.value, Rational.fromInt(420));
      expect(
        flow.quantity.value,
        Rational(BigInt.from(21), BigInt.from(4)),
      );
      expect(
        flow.trace.equationId,
        EquationId.flowRateFromAdministrationRateAndConcentration,
      );
    });

    test('direct and inverse paths are exact for representative values', () {
      final List<Rational> amounts = <Rational>[
        Rational(BigInt.one, BigInt.from(1000)),
        Rational.fromInt(1),
        Rational.fromInt(4),
        Rational.parseDecimal('123.456'),
      ];
      final List<Rational> volumes = <Rational>[
        Rational.fromInt(1),
        Rational.fromInt(20),
        Rational.fromInt(50),
        Rational.parseDecimal('99.9'),
      ];

      for (final Rational amountValue in amounts) {
        for (final Rational volumeValue in volumes) {
          final Quantity amount = Quantity(
            kind: QuantityKind.drugAmount,
            value: amountValue,
            unit: UnitCatalog.milligram,
          );
          final Quantity volume = Quantity(
            kind: QuantityKind.solutionVolume,
            value: volumeValue,
            unit: UnitCatalog.millilitre,
          );
          final CalculationResult concentration =
              InfusionEquations.concentrationFromAmountAndVolume(
                drugAmount: amount,
                solutionVolume: volume,
              );
          final CalculationResult restoredAmount =
              InfusionEquations.drugAmountFromConcentrationAndVolume(
                concentration: concentration.quantity,
                solutionVolume: volume,
                outputUnit: amount.unit,
              );
          final CalculationResult restoredVolume =
              InfusionEquations.solutionVolumeFromAmountAndConcentration(
                drugAmount: amount,
                concentration: concentration.quantity,
                outputUnit: volume.unit,
              );

          expect(restoredAmount.quantity, amount);
          expect(restoredVolume.quantity, volume);
        }
      }
    });
  });
}
