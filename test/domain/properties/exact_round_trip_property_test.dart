import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/calculations/infusion_equations.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/solver/calculator_solver.dart';
import 'package:kalkulator_lekow/domain/solver/solver_models.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';

void main() {
  group('deterministic exact-arithmetic properties', () {
    test('solution preparation is exactly reversible for 1000 cases', () {
      final Random random = Random(0xA110C);

      for (int index = 0; index < 1000; index++) {
        final UnitDefinition amountUnit = UnitCatalog.medicineAmountUnits[
          random.nextInt(UnitCatalog.medicineAmountUnits.length),
        ];
        final Quantity amount = Quantity(
          kind: QuantityKind.drugAmount,
          value: _positiveRational(random),
          unit: amountUnit,
        );
        final Quantity volume = Quantity(
          kind: QuantityKind.solutionVolume,
          value: _positiveRational(random),
          unit: UnitCatalog.millilitre,
        );

        final Quantity concentration = InfusionEquations
            .concentrationFromAmountAndVolume(
              drugAmount: amount,
              solutionVolume: volume,
            )
            .quantity;
        final Quantity restoredAmount = InfusionEquations
            .drugAmountFromConcentrationAndVolume(
              concentration: concentration,
              solutionVolume: volume,
              outputUnit: amountUnit,
            )
            .quantity;
        final Quantity restoredVolume = InfusionEquations
            .solutionVolumeFromAmountAndConcentration(
              drugAmount: amount,
              concentration: concentration,
              outputUnit: UnitCatalog.millilitre,
            )
            .quantity;

        expect(
          restoredAmount.isPhysicallyEquivalentTo(amount),
          isTrue,
          reason: 'amount round-trip case $index',
        );
        expect(
          restoredVolume.isPhysicallyEquivalentTo(volume),
          isTrue,
          reason: 'volume round-trip case $index',
        );
      }
    });

    test('administration equations are exactly reversible for 1000 cases', () {
      final Random random = Random(0xF10A);

      for (int index = 0; index < 1000; index++) {
        final UnitDefinition amountUnit = UnitCatalog.medicineAmountUnits[
          random.nextInt(UnitCatalog.medicineAmountUnits.length),
        ];
        final concentrationUnit = UnitCatalog.find('${amountUnit.code}/mL');
        final flowUnit = UnitCatalog.flowRateUnits[
          random.nextInt(UnitCatalog.flowRateUnits.length),
        ];
        final Quantity concentration = Quantity(
          kind: QuantityKind.concentration,
          value: _positiveRational(random),
          unit: concentrationUnit,
        );
        final Quantity flowRate = Quantity(
          kind: QuantityKind.flowRate,
          value: _positiveRational(random),
          unit: flowUnit,
        );

        final Quantity administrationRate = InfusionEquations
            .administrationRateFromConcentrationAndFlow(
              concentration: concentration,
              flowRate: flowRate,
            )
            .quantity;
        final Quantity restoredFlow = InfusionEquations
            .flowRateFromAdministrationRateAndConcentration(
              administrationRate: administrationRate,
              concentration: concentration,
              outputUnit: flowUnit,
            )
            .quantity;
        final Quantity restoredConcentration = InfusionEquations
            .concentrationFromAdministrationRateAndFlow(
              administrationRate: administrationRate,
              flowRate: flowRate,
              outputUnit: concentrationUnit,
            )
            .quantity;

        expect(
          restoredFlow.isPhysicallyEquivalentTo(flowRate),
          isTrue,
          reason: 'flow round-trip case $index',
        );
        expect(
          restoredConcentration.isPhysicallyEquivalentTo(concentration),
          isTrue,
          reason: 'concentration round-trip case $index',
        );
      }
    });

    test('weight-normalized dose is exactly reversible for 1000 cases', () {
      final Random random = Random(0xD05E);

      for (int index = 0; index < 1000; index++) {
        final administrationUnit = UnitCatalog.administrationRateUnits[
          random.nextInt(UnitCatalog.administrationRateUnits.length),
        ];
        final UnitDefinition bodyMassUnit = UnitCatalog.bodyMassUnits[
          random.nextInt(UnitCatalog.bodyMassUnits.length),
        ];
        final Quantity administrationRate = Quantity(
          kind: QuantityKind.administrationRate,
          value: _positiveRational(random),
          unit: administrationUnit,
        );
        final Quantity bodyMass = Quantity(
          kind: QuantityKind.bodyMass,
          value: _positiveRational(random),
          unit: bodyMassUnit,
        );

        final Quantity dose = InfusionEquations
            .weightNormalizedDoseFromAdministrationRateAndBodyMass(
              administrationRate: administrationRate,
              bodyMass: bodyMass,
            )
            .quantity;
        final Quantity restoredRate = InfusionEquations
            .administrationRateFromWeightNormalizedDoseAndBodyMass(
              weightNormalizedDose: dose,
              bodyMass: bodyMass,
              outputUnit: administrationUnit,
            )
            .quantity;

        expect(
          restoredRate.isPhysicallyEquivalentTo(administrationRate),
          isTrue,
          reason: 'dose round-trip case $index',
        );
      }
    });

    test('solver result is independent of iterable order for 500 cases', () {
      final Random random = Random(0x5017E);
      final CalculatorSolver solver = CalculatorSolver();

      for (int index = 0; index < 500; index++) {
        final List<SolverInput> inputs = <SolverInput>[
          SolverInput(
            quantity: Quantity(
              kind: QuantityKind.drugAmount,
              value: _positiveRational(random),
              unit: UnitCatalog.milligram,
            ),
            editSequence: 1,
          ),
          SolverInput(
            quantity: Quantity(
              kind: QuantityKind.solutionVolume,
              value: _positiveRational(random),
              unit: UnitCatalog.millilitre,
            ),
            editSequence: 2,
          ),
          SolverInput(
            quantity: Quantity(
              kind: QuantityKind.flowRate,
              value: _positiveRational(random),
              unit: UnitCatalog.millilitresPerHour,
            ),
            editSequence: 3,
          ),
          SolverInput(
            quantity: Quantity(
              kind: QuantityKind.bodyMass,
              value: _positiveRational(random),
              unit: UnitCatalog.kilogram,
            ),
            editSequence: 4,
          ),
        ];
        final SolverSolution baseline = solver.solve(inputs);

        for (int permutation = 0; permutation < 8; permutation++) {
          final List<SolverInput> shuffled = List<SolverInput>.of(inputs)
            ..shuffle(random);
          final SolverSolution candidate = solver.solve(shuffled);

          for (final QuantityKind kind in QuantityKind.values) {
            final Quantity? expected = baseline.fact(kind)?.quantity;
            final Quantity? actual = candidate.fact(kind)?.quantity;
            expect(
              actual?.canonicalValue,
              expected?.canonicalValue,
              reason: 'case $index, permutation $permutation, ${kind.name}',
            );
          }
          expect(
            candidate.conflicts.keys,
            unorderedEquals(baseline.conflicts.keys),
          );
        }
      }
    });
  });
}

Rational _positiveRational(Random random) => Rational(
  BigInt.from(random.nextInt(999999) + 1),
  BigInt.from(random.nextInt(997) + 1),
);
