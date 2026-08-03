import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';
import 'package:kalkulator_lekow/domain/units/unit_conversion_exception.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';

void main() {
  group('complete MVP unit matrix', () {
    test('every catalog code is unique and resolves to the same unit', () {
      final Set<String> codes = <String>{};

      for (final MeasurementUnit unit in UnitCatalog.allUnits) {
        expect(codes.add(unit.code), isTrue, reason: unit.code);
        expect(UnitCatalog.find(unit.code), same(unit));
      }
    });

    test('every compatible presentation conversion is exactly reversible', () {
      final Map<QuantityKind, List<MeasurementUnit>>
      matrix = <QuantityKind, List<MeasurementUnit>>{
        QuantityKind.bodyMass: <MeasurementUnit>[...UnitCatalog.bodyMassUnits],
        QuantityKind.drugAmount: <MeasurementUnit>[
          ...UnitCatalog.medicineAmountUnits,
        ],
        QuantityKind.solutionVolume: <MeasurementUnit>[UnitCatalog.millilitre],
        QuantityKind.concentration: <MeasurementUnit>[
          ...UnitCatalog.concentrationUnits,
        ],
        QuantityKind.flowRate: <MeasurementUnit>[...UnitCatalog.flowRateUnits],
        QuantityKind.administrationRate: <MeasurementUnit>[
          ...UnitCatalog.administrationRateUnits,
        ],
        QuantityKind.weightNormalizedDose: <MeasurementUnit>[
          ...UnitCatalog.weightNormalizedDoseUnits,
        ],
        QuantityKind.time: <MeasurementUnit>[...UnitCatalog.timeUnits],
        QuantityKind.infusionDuration: <MeasurementUnit>[
          ...UnitCatalog.timeUnits,
        ],
      };

      for (final MapEntry<QuantityKind, List<MeasurementUnit>> entry
          in matrix.entries) {
        for (final MeasurementUnit sourceUnit in entry.value) {
          final Quantity source = Quantity(
            kind: entry.key,
            value: Rational(BigInt.from(1234567), BigInt.from(89)),
            unit: sourceUnit,
          );

          for (final MeasurementUnit targetUnit in entry.value) {
            if (!sourceUnit.isCompatibleWith(targetUnit)) {
              continue;
            }
            final Quantity restored = source
                .convertTo(targetUnit)
                .convertTo(sourceUnit);
            expect(
              restored,
              source,
              reason:
                  '${entry.key.name}: ${sourceUnit.code} -> '
                  '${targetUnit.code} -> ${sourceUnit.code}',
            );
          }
        }
      }
    });

    test('mass and IU remain incompatible in every compound family', () {
      final Quantity amount = Quantity(
        kind: QuantityKind.drugAmount,
        value: Rational.fromInt(1),
        unit: UnitCatalog.milligram,
      );
      final Quantity concentration = Quantity(
        kind: QuantityKind.concentration,
        value: Rational.fromInt(1),
        unit: UnitCatalog.find('mg/mL'),
      );
      final Quantity administrationRate = Quantity(
        kind: QuantityKind.administrationRate,
        value: Rational.fromInt(1),
        unit: UnitCatalog.find('mg/h'),
      );
      final Quantity normalizedDose = Quantity(
        kind: QuantityKind.weightNormalizedDose,
        value: Rational.fromInt(1),
        unit: UnitCatalog.find('mg/kg/h'),
      );

      expect(
        () => amount.convertTo(UnitCatalog.internationalUnit),
        throwsA(isA<UnitConversionException>()),
      );
      expect(
        () => concentration.convertTo(UnitCatalog.find('IU/mL')),
        throwsA(isA<UnitConversionException>()),
      );
      expect(
        () => administrationRate.convertTo(UnitCatalog.find('IU/h')),
        throwsA(isA<UnitConversionException>()),
      );
      expect(
        () => normalizedDose.convertTo(UnitCatalog.find('IU/kg/h')),
        throwsA(isA<UnitConversionException>()),
      );
    });
  });
}
