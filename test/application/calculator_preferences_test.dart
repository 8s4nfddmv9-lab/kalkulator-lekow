import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/application/calculator_unit_options.dart';
import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  group('CalculatorPreferences', () {
    test('defaults expose one supported unit for every persisted kind', () {
      final CalculatorPreferences preferences =
          CalculatorPreferences.defaults();

      for (final QuantityKind kind in CalculatorPreferences.persistedKinds) {
        expect(
          CalculatorUnitOptions.supports(kind, preferences.unitFor(kind)),
          isTrue,
          reason: kind.name,
        );
      }
      expect(preferences.dosePerKilogram, isTrue);
    });

    test('unknown and incompatible stored codes fall back safely', () {
      final CalculatorPreferences preferences = CalculatorPreferences(
        unitCodes: <QuantityKind, String>{
          QuantityKind.bodyMass: UnitCatalog.milligram.code,
          QuantityKind.drugAmount: 'removed_unit',
          QuantityKind.concentration: UnitCatalog.internationalUnit.code,
        },
        dosePerKilogram: false,
      );

      expect(preferences.unitFor(QuantityKind.bodyMass), UnitCatalog.kilogram);
      expect(
        preferences.unitFor(QuantityKind.drugAmount),
        UnitCatalog.milligram,
      );
      expect(
        preferences.unitFor(QuantityKind.concentration),
        UnitCatalog.find('ug/mL'),
      );
      expect(preferences.dosePerKilogram, isFalse);
    });

    test('preference model contains presentation settings only', () {
      final CalculatorPreferences preferences = CalculatorPreferences(
        unitCodes: <QuantityKind, String>{
          QuantityKind.drugAmount: UnitCatalog.microgram.code,
        },
        dosePerKilogram: false,
      );

      expect(preferences.unitCodes, <QuantityKind, String>{
        QuantityKind.drugAmount: UnitCatalog.microgram.code,
      });
      expect(preferences.dosePerKilogram, isFalse);
    });
  });
}
