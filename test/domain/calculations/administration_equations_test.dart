import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/calculations/calculation_trace.dart';
import 'package:kalkulator_lekow/domain/calculations/infusion_equations.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  group('administration-rate equations', () {
    final Quantity concentration = Quantity(
      kind: QuantityKind.concentration,
      value: Rational.fromInt(80),
      unit: UnitCatalog.find('ug/mL'),
    );
    final Quantity flow = Quantity(
      kind: QuantityKind.flowRate,
      value: Rational.fromInt(5),
      unit: UnitCatalog.millilitresPerHour,
    );
    final Quantity administrationRate = Quantity(
      kind: QuantityKind.administrationRate,
      value: Rational.fromInt(400),
      unit: UnitCatalog.find('ug/h'),
    );

    test('80 µg/ml at 5 ml/h equals exactly 400 µg/h', () {
      final CalculationResult result =
          InfusionEquations.administrationRateFromConcentrationAndFlow(
            concentration: concentration,
            flowRate: flow,
          );

      expect(result.quantity, administrationRate);
      expect(
        result.trace.equationId,
        EquationId.administrationRateFromConcentrationAndFlow,
      );
      expect(result.trace.formula, 'P = C × R');
    });

    test('the same rate equals exactly 20/3 µg/min', () {
      final CalculationResult result =
          InfusionEquations.administrationRateFromConcentrationAndFlow(
            concentration: concentration,
            flowRate: flow,
            outputUnit: UnitCatalog.find('ug/min'),
          );

      expect(result.quantity.value, Rational(BigInt.from(20), BigInt.from(3)));
    });

    test('inverse equation restores exactly 5 ml/h', () {
      final CalculationResult result =
          InfusionEquations.flowRateFromAdministrationRateAndConcentration(
            administrationRate: administrationRate,
            concentration: concentration,
          );

      expect(result.quantity, flow);
      expect(
        result.trace.equationId,
        EquationId.flowRateFromAdministrationRateAndConcentration,
      );
    });

    test('second inverse equation restores exactly 80 µg/ml', () {
      final CalculationResult result =
          InfusionEquations.concentrationFromAdministrationRateAndFlow(
            administrationRate: administrationRate,
            flowRate: flow,
          );

      expect(result.quantity, concentration);
      expect(
        result.trace.equationId,
        EquationId.concentrationFromAdministrationRateAndFlow,
      );
    });

    test('round-trip remains exact across minute and hour units', () {
      final CalculationResult perMinute =
          InfusionEquations.administrationRateFromConcentrationAndFlow(
            concentration: concentration,
            flowRate: flow,
            outputUnit: UnitCatalog.find('ng/min'),
          );
      final CalculationResult restoredFlow =
          InfusionEquations.flowRateFromAdministrationRateAndConcentration(
            administrationRate: perMinute.quantity,
            concentration: concentration,
            outputUnit: UnitCatalog.millilitresPerHour,
          );

      expect(restoredFlow.quantity, flow);
    });

    test('IU concentration produces IU administration rate', () {
      final Quantity activityConcentration = Quantity(
        kind: QuantityKind.concentration,
        value: Rational.fromInt(100),
        unit: UnitCatalog.find('IU/mL'),
      );
      final Quantity twoMillilitresPerHour = Quantity(
        kind: QuantityKind.flowRate,
        value: Rational.fromInt(2),
        unit: UnitCatalog.millilitresPerHour,
      );

      final CalculationResult result =
          InfusionEquations.administrationRateFromConcentrationAndFlow(
            concentration: activityConcentration,
            flowRate: twoMillilitresPerHour,
          );

      expect(result.quantity.value, Rational.fromInt(200));
      expect(result.quantity.unit, UnitCatalog.find('IU/h'));
    });

    test('rejects zero concentration when calculating flow', () {
      final Quantity zeroConcentration = Quantity(
        kind: QuantityKind.concentration,
        value: Rational.fromInt(0),
        unit: UnitCatalog.find('ug/mL'),
      );

      expect(
        () => InfusionEquations.flowRateFromAdministrationRateAndConcentration(
          administrationRate: administrationRate,
          concentration: zeroConcentration,
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

    test('rejects zero flow when calculating concentration', () {
      final Quantity zeroFlow = Quantity(
        kind: QuantityKind.flowRate,
        value: Rational.fromInt(0),
        unit: UnitCatalog.millilitresPerHour,
      );

      expect(
        () => InfusionEquations.concentrationFromAdministrationRateAndFlow(
          administrationRate: administrationRate,
          flowRate: zeroFlow,
        ),
        throwsA(isA<ZeroDenominatorException>()),
      );
    });

    test('rejects a mass rate combined with IU concentration', () {
      final Quantity activityConcentration = Quantity(
        kind: QuantityKind.concentration,
        value: Rational.fromInt(100),
        unit: UnitCatalog.find('IU/mL'),
      );

      expect(
        () => InfusionEquations.flowRateFromAdministrationRateAndConcentration(
          administrationRate: administrationRate,
          concentration: activityConcentration,
        ),
        throwsA(isA<QuantityUnitException>()),
      );
    });
  });
}
