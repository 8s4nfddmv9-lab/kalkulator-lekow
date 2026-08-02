import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/application/calculator_session.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/solver/solver_models.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  Quantity quantity(
    QuantityKind kind,
    String value,
    String unitCode,
  ) => Quantity.parse(
    kind: kind,
    source: value,
    unit: UnitCatalog.find(unitCode),
  );

  group('CalculatorSession', () {
    test('editing calculated concentration promotes it and demotes oldest input', () {
      final CalculatorSession session = CalculatorSession();
      session.edit(quantity(QuantityKind.drugAmount, '4', 'mg'));
      session.edit(quantity(QuantityKind.solutionVolume, '50', 'mL'));

      expect(
        session.solution.fact(QuantityKind.concentration)!.origin,
        SolverFactOrigin.calculated,
      );

      session.edit(quantity(QuantityKind.concentration, '100', 'ug/mL'));

      expect(session.inputs.containsKey(QuantityKind.drugAmount), isFalse);
      expect(session.inputs.containsKey(QuantityKind.solutionVolume), isTrue);
      expect(session.inputs.containsKey(QuantityKind.concentration), isTrue);
      expect(session.solution.conflicts, isEmpty);
      expect(
        session.solution.fact(QuantityKind.drugAmount)!.origin,
        SolverFactOrigin.calculated,
      );
      expect(
        session.solution.fact(QuantityKind.drugAmount)!.quantity.convertTo(
          UnitCatalog.milligram,
        ).value,
        Rational.fromInt(5),
      );
    });

    test('editing calculated dose replaces flow and recalculates 5.25 ml/h', () {
      final CalculatorSession session = CalculatorSession();
      session.edit(quantity(QuantityKind.drugAmount, '4', 'mg'));
      session.edit(quantity(QuantityKind.solutionVolume, '50', 'mL'));
      session.edit(quantity(QuantityKind.flowRate, '5', 'mL/h'));
      session.edit(quantity(QuantityKind.bodyMass, '70', 'kg'));

      expect(
        session.solution.fact(QuantityKind.weightNormalizedDose)!.origin,
        SolverFactOrigin.calculated,
      );

      session.edit(
        quantity(
          QuantityKind.weightNormalizedDose,
          '0.1',
          'ug/kg/min',
        ),
      );

      expect(session.inputs.containsKey(QuantityKind.flowRate), isFalse);
      expect(session.inputs.containsKey(QuantityKind.bodyMass), isTrue);
      expect(
        session.inputs[QuantityKind.weightNormalizedDose]!.quantity.value,
        Rational(BigInt.one, BigInt.from(10)),
      );
      expect(session.solution.conflicts, isEmpty);
      expect(
        session.solution.fact(QuantityKind.flowRate)!.quantity.convertTo(
          UnitCatalog.millilitresPerHour,
        ).value,
        Rational(BigInt.from(21), BigInt.from(4)),
      );
    });

    test('explicit replacement overrides the automatic takeover choice', () {
      final CalculatorSession session = CalculatorSession();
      session.edit(quantity(QuantityKind.drugAmount, '4', 'mg'));
      session.edit(quantity(QuantityKind.solutionVolume, '50', 'mL'));

      session.edit(
        quantity(QuantityKind.concentration, '100', 'ug/mL'),
        replaceInputKind: QuantityKind.solutionVolume,
      );

      expect(session.inputs.containsKey(QuantityKind.drugAmount), isTrue);
      expect(session.inputs.containsKey(QuantityKind.solutionVolume), isFalse);
      expect(
        session.solution.fact(QuantityKind.solutionVolume)!.quantity.value,
        Rational.fromInt(40),
      );
    });

    test('editing an existing user input does not demote another input', () {
      final CalculatorSession session = CalculatorSession();
      session.edit(quantity(QuantityKind.drugAmount, '4', 'mg'));
      session.edit(quantity(QuantityKind.solutionVolume, '50', 'mL'));
      session.edit(quantity(QuantityKind.solutionVolume, '40', 'mL'));

      expect(session.inputs.containsKey(QuantityKind.drugAmount), isTrue);
      expect(session.inputs.containsKey(QuantityKind.solutionVolume), isTrue);
      expect(session.solution.conflicts, isEmpty);
      expect(
        session.solution.fact(QuantityKind.concentration)!.quantity.convertTo(
          UnitCatalog.find('ug/mL'),
        ).value,
        Rational.fromInt(100),
      );
    });

    test('patient body mass cannot be selected for replacement', () {
      final CalculatorSession session = CalculatorSession();
      session.edit(quantity(QuantityKind.bodyMass, '70', 'kg'));
      session.edit(quantity(QuantityKind.administrationRate, '400', 'ug/h'));

      expect(
        () => session.edit(
          quantity(
            QuantityKind.weightNormalizedDose,
            '0.1',
            'ug/kg/min',
          ),
          replaceInputKind: QuantityKind.bodyMass,
        ),
        throwsArgumentError,
      );
      expect(session.inputs.containsKey(QuantityKind.bodyMass), isTrue);
    });

    test('clear and reset immediately recalculate the reachable state', () {
      final CalculatorSession session = CalculatorSession();
      session.edit(quantity(QuantityKind.drugAmount, '4', 'mg'));
      session.edit(quantity(QuantityKind.solutionVolume, '50', 'mL'));

      session.clear(QuantityKind.solutionVolume);
      expect(session.solution.fact(QuantityKind.concentration), isNull);
      expect(session.inputs, hasLength(1));

      session.reset();
      expect(session.inputs, isEmpty);
      expect(session.solution.facts, isEmpty);
      expect(session.solution.conflicts, isEmpty);
    });

    test('calculated-only duration cannot be promoted to user input', () {
      final CalculatorSession session = CalculatorSession();

      expect(
        () => session.edit(
          quantity(QuantityKind.infusionDuration, '10', 'h'),
        ),
        throwsArgumentError,
      );
    });
  });
}
