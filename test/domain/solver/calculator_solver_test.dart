import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/solver/calculator_solver.dart';
import 'package:kalkulator_lekow/domain/solver/solver_models.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  final CalculatorSolver solver = CalculatorSolver();

  Quantity quantity(QuantityKind kind, String value, String unitCode) =>
      Quantity.parse(
        kind: kind,
        source: value,
        unit: UnitCatalog.find(unitCode),
      );

  SolverInput input(
    QuantityKind kind,
    String value,
    String unitCode,
    int editSequence,
  ) => SolverInput(
    quantity: quantity(kind, value, unitCode),
    editSequence: editSequence,
  );

  group('CalculatorSolver', () {
    test('derives every reachable value through a calculation chain', () {
      final SolverSolution solution = solver.solve(<SolverInput>[
        input(QuantityKind.bodyMass, '70', 'kg', 1),
        input(QuantityKind.drugAmount, '4', 'mg', 2),
        input(QuantityKind.solutionVolume, '50', 'mL', 3),
        input(QuantityKind.flowRate, '5', 'mL/h', 4),
      ]);

      expect(solution.conflicts, isEmpty);
      expect(
        solution
            .fact(QuantityKind.concentration)!
            .quantity
            .convertTo(UnitCatalog.find('ug/mL'))
            .value,
        Rational.fromInt(80),
      );
      expect(
        solution
            .fact(QuantityKind.administrationRate)!
            .quantity
            .convertTo(UnitCatalog.find('ug/h'))
            .value,
        Rational.fromInt(400),
      );
      expect(
        solution
            .fact(QuantityKind.weightNormalizedDose)!
            .quantity
            .convertTo(UnitCatalog.find('ug/kg/min'))
            .value,
        Rational(BigInt.from(2), BigInt.from(21)),
      );
      expect(
        solution
            .fact(QuantityKind.infusionDuration)!
            .quantity
            .convertTo(UnitCatalog.hour)
            .value,
        Rational.fromInt(10),
      );
      expect(solution.facts, hasLength(8));
    });

    test(
      'solves flow from desired dose without requiring amount or volume',
      () {
        final SolverSolution solution = solver.solve(<SolverInput>[
          input(QuantityKind.weightNormalizedDose, '0.1', 'ug/kg/min', 1),
          input(QuantityKind.bodyMass, '70', 'kg', 2),
          input(QuantityKind.concentration, '80', 'ug/mL', 3),
        ]);

        expect(solution.conflicts, isEmpty);
        expect(
          solution
              .fact(QuantityKind.administrationRate)!
              .quantity
              .convertTo(UnitCatalog.find('ug/h'))
              .value,
          Rational.fromInt(420),
        );
        expect(
          solution
              .fact(QuantityKind.flowRate)!
              .quantity
              .convertTo(UnitCatalog.millilitresPerHour)
              .value,
          Rational(BigInt.from(21), BigInt.from(4)),
        );
      },
    );

    test('does not derive a normalized dose without body mass', () {
      final SolverSolution solution = solver.solve(<SolverInput>[
        input(QuantityKind.concentration, '80', 'ug/mL', 1),
        input(QuantityKind.flowRate, '5', 'mL/h', 2),
      ]);

      expect(solution.fact(QuantityKind.administrationRate), isNotNull);
      expect(solution.fact(QuantityKind.weightNormalizedDose), isNull);
      expect(solution.fact(QuantityKind.bodyMass), isNull);
    });

    test('never derives patient body mass from two dose values', () {
      final SolverSolution solution = solver.solve(<SolverInput>[
        input(QuantityKind.administrationRate, '420', 'ug/h', 1),
        input(QuantityKind.weightNormalizedDose, '0.1', 'ug/kg/min', 2),
      ]);

      expect(solution.fact(QuantityKind.bodyMass), isNull);
      expect(solution.userInputs.containsKey(QuantityKind.bodyMass), isFalse);
    });

    test('accepts consistent redundant user inputs', () {
      final SolverSolution solution = solver.solve(<SolverInput>[
        input(QuantityKind.drugAmount, '4', 'mg', 1),
        input(QuantityKind.solutionVolume, '50', 'mL', 2),
        input(QuantityKind.concentration, '80', 'ug/mL', 3),
      ]);

      expect(solution.conflicts, isEmpty);
      expect(
        solution.fact(QuantityKind.concentration)!.origin,
        SolverFactOrigin.userInput,
      );
      expect(
        solution.fact(QuantityKind.concentration)!.quantity.value,
        Rational.fromInt(80),
      );
    });

    test('reports a conflict instead of overwriting concentration', () {
      final SolverSolution solution = solver.solve(<SolverInput>[
        input(QuantityKind.drugAmount, '4', 'mg', 1),
        input(QuantityKind.solutionVolume, '50', 'mL', 2),
        input(QuantityKind.concentration, '100', 'ug/mL', 3),
      ]);

      final SolverConflict conflict =
          solution.conflicts[QuantityKind.concentration]!;
      expect(solution.fact(QuantityKind.concentration), isNull);
      expect(
        solution.userInputs[QuantityKind.concentration]!.quantity.value,
        Rational.fromInt(100),
      );
      expect(conflict.conflictKind, SolverConflictKind.userInputMismatch);
      expect(conflict.candidateInExistingUnit.value, Rational.fromInt(80));
      expect(conflict.relativeDifference, Rational(BigInt.one, BigInt.from(5)));
      expect(conflict.involvedUserInputs, <QuantityKind>{
        QuantityKind.drugAmount,
        QuantityKind.solutionVolume,
        QuantityKind.concentration,
      });
    });

    test('does not propagate a conflicted concentration into drug rate', () {
      final SolverSolution solution = solver.solve(<SolverInput>[
        input(QuantityKind.drugAmount, '4', 'mg', 1),
        input(QuantityKind.solutionVolume, '50', 'mL', 2),
        input(QuantityKind.concentration, '100', 'ug/mL', 3),
        input(QuantityKind.flowRate, '5', 'mL/h', 4),
        input(QuantityKind.bodyMass, '70', 'kg', 5),
      ]);

      expect(solution.hasConflict(QuantityKind.concentration), isTrue);
      expect(solution.fact(QuantityKind.administrationRate), isNull);
      expect(solution.fact(QuantityKind.weightNormalizedDose), isNull);
      expect(solution.fact(QuantityKind.infusionDuration), isNotNull);
    });

    test('detects disagreement between independent dose paths', () {
      final SolverSolution solution = solver.solve(<SolverInput>[
        input(QuantityKind.concentration, '80', 'ug/mL', 1),
        input(QuantityKind.flowRate, '5', 'mL/h', 2),
        input(QuantityKind.bodyMass, '70', 'kg', 3),
        input(QuantityKind.weightNormalizedDose, '0.1', 'ug/kg/min', 4),
      ]);

      expect(solution.hasConflict(QuantityKind.weightNormalizedDose), isTrue);
      expect(
        solution.conflicts[QuantityKind.weightNormalizedDose]!.conflictKind,
        SolverConflictKind.userInputMismatch,
      );
      expect(
        solution.userInputs[QuantityKind.weightNormalizedDose]!.quantity.value,
        Rational(BigInt.one, BigInt.from(10)),
      );
    });

    test('is deterministic regardless of input iterable order', () {
      final List<SolverInput> inputs = <SolverInput>[
        input(QuantityKind.bodyMass, '70', 'kg', 1),
        input(QuantityKind.drugAmount, '4', 'mg', 2),
        input(QuantityKind.solutionVolume, '50', 'mL', 3),
        input(QuantityKind.flowRate, '5', 'mL/h', 4),
      ];

      final SolverSolution forward = solver.solve(inputs);
      final SolverSolution reversed = solver.solve(inputs.reversed);

      expect(reversed.conflicts.keys, forward.conflicts.keys);
      for (final QuantityKind kind in forward.facts.keys) {
        expect(
          reversed
              .fact(kind)!
              .quantity
              .isPhysicallyEquivalentTo(forward.fact(kind)!.quantity),
          isTrue,
          reason: kind.name,
        );
        expect(
          reversed.fact(kind)!.trace?.equationId,
          forward.fact(kind)!.trace?.equationId,
          reason: kind.name,
        );
      }
    });

    test('accepts redundant values inside the exact relative tolerance', () {
      final SolverSolution solution = solver.solve(<SolverInput>[
        input(QuantityKind.drugAmount, '1', 'mg', 1),
        input(QuantityKind.solutionVolume, '10', 'mL', 2),
        input(QuantityKind.concentration, '0.10000000000005', 'mg/mL', 3),
      ]);

      expect(solution.conflicts, isEmpty);
    });

    test('rejects redundant values outside the relative tolerance', () {
      final SolverSolution solution = solver.solve(<SolverInput>[
        input(QuantityKind.drugAmount, '1', 'mg', 1),
        input(QuantityKind.solutionVolume, '10', 'mL', 2),
        input(QuantityKind.concentration, '0.10000000001', 'mg/mL', 3),
      ]);

      expect(solution.hasConflict(QuantityKind.concentration), isTrue);
    });

    test('keeps the latest duplicate input and records its edit sequence', () {
      final SolverSolution solution = solver.solve(<SolverInput>[
        input(QuantityKind.solutionVolume, '20', 'mL', 1),
        input(QuantityKind.solutionVolume, '50', 'mL', 2),
      ]);

      expect(
        solution.userInputs[QuantityKind.solutionVolume]!.quantity.value,
        Rational.fromInt(50),
      );
      expect(
        solution.userInputs[QuantityKind.solutionVolume]!.latestEditSequence,
        2,
      );
    });

    test('rejects calculated-only quantities as explicit inputs', () {
      expect(
        () => solver.solve(<SolverInput>[
          input(QuantityKind.infusionDuration, '10', 'h', 1),
        ]),
        throwsArgumentError,
      );
    });
  });
}
