import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/calculations/calculation_trace.dart';
import 'package:kalkulator_lekow/domain/calculations/infusion_equations.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';
import 'package:kalkulator_lekow/domain/units/unit_conversion_exception.dart';

void main() {
  group('solution preparation equations', () {
    final Quantity fourMilligrams = Quantity(
      kind: QuantityKind.drugAmount,
      value: Rational.fromInt(4),
      unit: UnitCatalog.milligram,
    );
    final Quantity fiftyMillilitres = Quantity(
      kind: QuantityKind.solutionVolume,
      value: Rational.fromInt(50),
      unit: UnitCatalog.millilitre,
    );
    final Quantity eightyMicrogramsPerMillilitre = Quantity(
      kind: QuantityKind.concentration,
      value: Rational.fromInt(80),
      unit: UnitCatalog.find('ug/mL'),
    );

    test('4 mg in 50 ml equals exactly 80 µg/ml', () {
      final CalculationResult result =
          InfusionEquations.concentrationFromAmountAndVolume(
            drugAmount: fourMilligrams,
            solutionVolume: fiftyMillilitres,
            outputUnit: UnitCatalog.find('ug/mL'),
          );

      expect(result.quantity, eightyMicrogramsPerMillilitre);
      expect(
        result.trace.equationId,
        EquationId.concentrationFromAmountAndVolume,
      );
      expect(result.trace.formula, 'C = A / V');
      expect(result.trace.inputs, hasLength(2));
      expect(result.trace.inputs.first.unitCode, 'mg');
      expect(result.trace.output.canonicalValue, Rational.fromInt(80000));
    });

    test('inverse equation restores exactly 4 mg', () {
      final CalculationResult result =
          InfusionEquations.drugAmountFromConcentrationAndVolume(
            concentration: eightyMicrogramsPerMillilitre,
            solutionVolume: fiftyMillilitres,
            outputUnit: UnitCatalog.milligram,
          );

      expect(result.quantity, fourMilligrams);
      expect(
        result.trace.equationId,
        EquationId.drugAmountFromConcentrationAndVolume,
      );
    });

    test('second inverse equation restores exactly 50 ml', () {
      final CalculationResult result =
          InfusionEquations.solutionVolumeFromAmountAndConcentration(
            drugAmount: fourMilligrams,
            concentration: eightyMicrogramsPerMillilitre,
          );

      expect(result.quantity, fiftyMillilitres);
      expect(
        result.trace.equationId,
        EquationId.solutionVolumeFromAmountAndConcentration,
      );
    });

    test('default result unit follows the amount unit', () {
      final CalculationResult result =
          InfusionEquations.concentrationFromAmountAndVolume(
            drugAmount: fourMilligrams,
            solutionVolume: fiftyMillilitres,
          );

      expect(result.quantity.value, Rational(BigInt.from(2), BigInt.from(25)));
      expect(result.quantity.unit, UnitCatalog.find('mg/mL'));
    });

    test('IU remains inside its own amount family', () {
      final Quantity activity = Quantity(
        kind: QuantityKind.drugAmount,
        value: Rational.fromInt(500),
        unit: UnitCatalog.internationalUnit,
      );

      final CalculationResult result =
          InfusionEquations.concentrationFromAmountAndVolume(
            drugAmount: activity,
            solutionVolume: fiftyMillilitres,
          );

      expect(result.quantity.value, Rational.fromInt(10));
      expect(result.quantity.unit, UnitCatalog.find('IU/mL'));
    });

    test('rejects zero solution volume before division', () {
      final Quantity zeroVolume = Quantity(
        kind: QuantityKind.solutionVolume,
        value: Rational.fromInt(0),
        unit: UnitCatalog.millilitre,
      );

      expect(
        () => InfusionEquations.concentrationFromAmountAndVolume(
          drugAmount: fourMilligrams,
          solutionVolume: zeroVolume,
        ),
        throwsA(
          isA<ZeroDenominatorException>().having(
            (ZeroDenominatorException error) => error.code,
            'code',
            DomainErrorCode.zeroDenominator,
          ),
        ),
      );
    });

    test('rejects zero concentration before inverse division', () {
      final Quantity zeroConcentration = Quantity(
        kind: QuantityKind.concentration,
        value: Rational.fromInt(0),
        unit: UnitCatalog.find('ug/mL'),
      );

      expect(
        () => InfusionEquations.solutionVolumeFromAmountAndConcentration(
          drugAmount: fourMilligrams,
          concentration: zeroConcentration,
        ),
        throwsA(isA<ZeroDenominatorException>()),
      );
    });

    test('rejects an IU output unit for a mass-derived result', () {
      expect(
        () => InfusionEquations.concentrationFromAmountAndVolume(
          drugAmount: fourMilligrams,
          solutionVolume: fiftyMillilitres,
          outputUnit: UnitCatalog.find('IU/mL'),
        ),
        throwsA(isA<UnitConversionException>()),
      );
    });

    test('rejects inconsistent amount families in inverse equations', () {
      final Quantity activityConcentration = Quantity(
        kind: QuantityKind.concentration,
        value: Rational.fromInt(10),
        unit: UnitCatalog.find('IU/mL'),
      );

      expect(
        () => InfusionEquations.solutionVolumeFromAmountAndConcentration(
          drugAmount: fourMilligrams,
          concentration: activityConcentration,
        ),
        throwsA(isA<QuantityUnitException>()),
      );
    });

    test('rejects a semantically incorrect equation input', () {
      final Quantity bodyMass = Quantity(
        kind: QuantityKind.bodyMass,
        value: Rational.fromInt(70),
        unit: UnitCatalog.kilogram,
      );

      expect(
        () => InfusionEquations.concentrationFromAmountAndVolume(
          drugAmount: bodyMass,
          solutionVolume: fiftyMillilitres,
        ),
        throwsA(isA<EquationInputException>()),
      );
    });
  });
}
