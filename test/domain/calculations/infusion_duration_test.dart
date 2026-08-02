import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/calculations/calculation_trace.dart';
import 'package:kalkulator_lekow/domain/calculations/infusion_equations.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  group('infusion duration equation', () {
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

    test('50 ml at 5 ml/h equals exactly 10 h', () {
      final CalculationResult result =
          InfusionEquations.infusionDurationFromVolumeAndFlow(
            solutionVolume: volume,
            flowRate: flow,
          );

      expect(result.quantity.value, Rational.fromInt(10));
      expect(result.quantity.unit, UnitCatalog.hour);
      expect(
        result.trace.equationId,
        EquationId.infusionDurationFromVolumeAndFlow,
      );
      expect(result.trace.formula, 'T = V / R');
    });

    test('the same duration equals exactly 600 min', () {
      final CalculationResult result =
          InfusionEquations.infusionDurationFromVolumeAndFlow(
            solutionVolume: volume,
            flowRate: flow,
            outputUnit: UnitCatalog.minute,
          );

      expect(result.quantity.value, Rational.fromInt(600));
    });

    test('rejects zero flow before division', () {
      final Quantity zeroFlow = Quantity(
        kind: QuantityKind.flowRate,
        value: Rational.fromInt(0),
        unit: UnitCatalog.millilitresPerHour,
      );

      expect(
        () => InfusionEquations.infusionDurationFromVolumeAndFlow(
          solutionVolume: volume,
          flowRate: zeroFlow,
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
  });
}
