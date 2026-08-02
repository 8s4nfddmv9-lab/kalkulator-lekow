import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/solver/calculator_solver.dart';
import 'package:kalkulator_lekow/domain/solver/solver_models.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  test('zero denominator becomes a diagnostic instead of an exception', () {
    final CalculatorSolver solver = CalculatorSolver();

    final SolverSolution solution = solver.solve(<SolverInput>[
      SolverInput(
        quantity: Quantity(
          kind: QuantityKind.drugAmount,
          value: Rational.fromInt(4),
          unit: UnitCatalog.milligram,
        ),
        editSequence: 1,
      ),
      SolverInput(
        quantity: Quantity(
          kind: QuantityKind.solutionVolume,
          value: Rational.fromInt(0),
          unit: UnitCatalog.millilitre,
        ),
        editSequence: 2,
      ),
    ]);

    expect(solution.fact(QuantityKind.drugAmount), isNotNull);
    expect(solution.fact(QuantityKind.solutionVolume), isNotNull);
    expect(solution.fact(QuantityKind.concentration), isNull);
    expect(solution.diagnostics, hasLength(1));
    expect(
      solution.diagnostics.single.error.code,
      DomainErrorCode.zeroDenominator,
    );
  });

  test('an incompatible IU and mass path does not block unrelated facts', () {
    final CalculatorSolver solver = CalculatorSolver();

    final SolverSolution solution = solver.solve(<SolverInput>[
      SolverInput(
        quantity: Quantity(
          kind: QuantityKind.drugAmount,
          value: Rational.fromInt(4),
          unit: UnitCatalog.milligram,
        ),
        editSequence: 1,
      ),
      SolverInput(
        quantity: Quantity(
          kind: QuantityKind.concentration,
          value: Rational.fromInt(100),
          unit: UnitCatalog.find('IU/mL'),
        ),
        editSequence: 2,
      ),
      SolverInput(
        quantity: Quantity(
          kind: QuantityKind.bodyMass,
          value: Rational.fromInt(70),
          unit: UnitCatalog.kilogram,
        ),
        editSequence: 3,
      ),
    ]);

    expect(solution.fact(QuantityKind.bodyMass), isNotNull);
    expect(solution.fact(QuantityKind.solutionVolume), isNull);
    expect(
      solution.diagnostics.any(
        (SolverDiagnostic diagnostic) =>
            diagnostic.error.code ==
            DomainErrorCode.incompatibleUnitFamily,
      ),
      isTrue,
    );
  });
}
