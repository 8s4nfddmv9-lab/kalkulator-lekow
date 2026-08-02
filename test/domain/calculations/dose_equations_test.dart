import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/calculations/calculation_trace.dart';
import 'package:kalkulator_lekow/domain/calculations/infusion_equations.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  group('weight-normalized dose equations', () {
    final Quantity administrationRate = Quantity(
      kind: QuantityKind.administrationRate,
      value: Rational.fromInt(400),
      unit: UnitCatalog.find('ug/h'),
    );
    final Quantity bodyMass = Quantity(
      kind: QuantityKind.bodyMass,
      value: Rational.fromInt(70),
      unit: UnitCatalog.kilogram,
    );

    test('400 µg/h over 70 kg equals exactly 2/21 µg/kg/min', () {
      final CalculationResult result = InfusionEquations
          .weightNormalizedDoseFromAdministrationRateAndBodyMass(
            administrationRate: administrationRate,
            bodyMass: bodyMass,
            outputUnit: UnitCatalog.find('ug/kg/min'),
          );

      expect(
        result.quantity.value,
        Rational(BigInt.from(2), BigInt.from(21)),
      );
      expect(
        result.trace.equationId,
        EquationId.weightNormalizedDoseFromAdministrationRateAndBodyMass,
      );
      expect(result.trace.formula, 'D = P / W');
    });

    test('0.1 µg/kg/min at 70 kg equals exactly 420 µg/h', () {
      final Quantity dose = Quantity.parse(
        kind: QuantityKind.weightNormalizedDose,
        source: '0.1',
        unit: UnitCatalog.find('ug/kg/min'),
      );

      final CalculationResult result = InfusionEquations
          .administrationRateFromWeightNormalizedDoseAndBodyMass(
            weightNormalizedDose: dose,
            bodyMass: bodyMass,
            outputUnit: UnitCatalog.find('ug/h'),
          );

      expect(result.quantity.value, Rational.fromInt(420));
      expect(
        result.trace.equationId,
        EquationId.administrationRateFromWeightNormalizedDoseAndBodyMass,
      );
    });

    test('body mass entered in grams produces the same exact result', () {
      final Quantity bodyMassInGrams = Quantity(
        kind: QuantityKind.bodyMass,
        value: Rational.fromInt(70000),
        unit: UnitCatalog.bodyGram,
      );

      final CalculationResult kilogramsResult = InfusionEquations
          .weightNormalizedDoseFromAdministrationRateAndBodyMass(
            administrationRate: administrationRate,
            bodyMass: bodyMass,
            outputUnit: UnitCatalog.find('ug/kg/min'),
          );
      final CalculationResult gramsResult = InfusionEquations
          .weightNormalizedDoseFromAdministrationRateAndBodyMass(
            administrationRate: administrationRate,
            bodyMass: bodyMassInGrams,
            outputUnit: UnitCatalog.find('ug/kg/min'),
          );

      expect(gramsResult.quantity, kilogramsResult.quantity);
    });

    test('IU rates remain IU rates after body-mass normalization', () {
      final Quantity activityRate = Quantity(
        kind: QuantityKind.administrationRate,
        value: Rational.fromInt(600),
        unit: UnitCatalog.find('IU/h'),
      );

      final CalculationResult result = InfusionEquations
          .weightNormalizedDoseFromAdministrationRateAndBodyMass(
            administrationRate: activityRate,
            bodyMass: bodyMass,
          );

      expect(result.quantity.unit, UnitCatalog.find('IU/kg/h'));
      expect(
        result.quantity.value,
        Rational(BigInt.from(60), BigInt.from(7)),
      );
    });

    test('rejects zero body mass in both directions', () {
      final Quantity zeroBodyMass = Quantity(
        kind: QuantityKind.bodyMass,
        value: Rational.fromInt(0),
        unit: UnitCatalog.kilogram,
      );
      final Quantity dose = Quantity.parse(
        kind: QuantityKind.weightNormalizedDose,
        source: '0.1',
        unit: UnitCatalog.find('ug/kg/min'),
      );

      expect(
        () => InfusionEquations
            .weightNormalizedDoseFromAdministrationRateAndBodyMass(
              administrationRate: administrationRate,
              bodyMass: zeroBodyMass,
            ),
        throwsA(
          isA<ZeroDenominatorException>().having(
            (ZeroDenominatorException error) => error.code,
            'code',
            DomainErrorCode.zeroDenominator,
          ),
        ),
      );
      expect(
        () => InfusionEquations
            .administrationRateFromWeightNormalizedDoseAndBodyMass(
              weightNormalizedDose: dose,
              bodyMass: zeroBodyMass,
            ),
        throwsA(isA<ZeroDenominatorException>()),
      );
    });

    test('no registered equation can produce patient body mass', () {
      expect(
        EquationId.values.every(
          (EquationId equationId) =>
              equationId.targetKind != QuantityKind.bodyMass,
        ),
        isTrue,
      );
    });
  });
}
