import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/units/compound_unit_definition.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';
import 'package:kalkulator_lekow/domain/units/unit_dimension.dart';

void main() {
  group('UnitDimension boundaries', () {
    test('default vector is dimensionless', () {
      const UnitDimension dimension = UnitDimension();

      expect(dimension.isDimensionless, isTrue);
      expect(dimension.hasMixedDrugAmountFamilies, isFalse);
      expect(dimension.toString(), 'dimensionless');
    });

    test('arithmetic and scaling operate on every dimension axis', () {
      const UnitDimension left = UnitDimension(
        medicineMassExponent: 1,
        volumeExponent: -1,
        timeExponent: -1,
      );
      const UnitDimension right = UnitDimension(
        biologicalActivityExponent: 1,
        bodyMassExponent: -1,
        timeExponent: 1,
      );

      final UnitDimension sum = left + right;
      final UnitDimension difference = left - right;
      final UnitDimension scaled = difference.scaled(-2);

      expect(sum.hasMixedDrugAmountFamilies, isTrue);
      expect(sum.isDimensionless, isFalse);
      expect(
        sum.toString(),
        'medicineMass·IU·volume^-1·bodyMass^-1',
      );
      expect(
        difference,
        const UnitDimension(
          medicineMassExponent: 1,
          biologicalActivityExponent: -1,
          volumeExponent: -1,
          bodyMassExponent: 1,
          timeExponent: -2,
        ),
      );
      expect(
        scaled,
        const UnitDimension(
          medicineMassExponent: -2,
          biologicalActivityExponent: 2,
          volumeExponent: 2,
          bodyMassExponent: -2,
          timeExponent: 4,
        ),
      );
      expect(scaled.hashCode, scaled.hashCode);
    });
  });

  group('MeasurementUnit value semantics', () {
    test('equivalent primitive definitions compare by value', () {
      final UnitDefinition first = UnitDefinition(
        code: 'custom_min',
        symbol: 'min',
        family: UnitFamily.time,
        toCanonical: Rational.fromInt(1),
      );
      final UnitDefinition second = UnitDefinition(
        code: 'custom_min',
        symbol: 'min',
        family: UnitFamily.time,
        toCanonical: Rational.fromInt(1),
      );
      final UnitDefinition different = UnitDefinition(
        code: 'custom_h',
        symbol: 'h',
        family: UnitFamily.time,
        toCanonical: Rational.fromInt(60),
      );

      expect(first, second);
      expect(first.hashCode, second.hashCode);
      expect(first, isNot(different));
      expect(first.toString(), 'min');
      expect(first.isCompatibleWith(different), isTrue);
    });

    test('every primitive family maps to one separate dimension axis', () {
      expect(
        UnitFamily.medicineMass.dimension,
        const UnitDimension(medicineMassExponent: 1),
      );
      expect(
        UnitFamily.biologicalActivity.dimension,
        const UnitDimension(biologicalActivityExponent: 1),
      );
      expect(
        UnitFamily.volume.dimension,
        const UnitDimension(volumeExponent: 1),
      );
      expect(
        UnitFamily.bodyMass.dimension,
        const UnitDimension(bodyMassExponent: 1),
      );
      expect(
        UnitFamily.time.dimension,
        const UnitDimension(timeExponent: 1),
      );
    });
  });

  group('CompoundUnitDefinition validation', () {
    test('rejects an empty numerator', () {
      expect(
        () => CompoundUnitDefinition(
          code: 'invalid',
          symbol: 'invalid',
          numeratorUnits: const <UnitDefinition>[],
          denominatorUnits: <UnitDefinition>[UnitCatalog.hour],
        ),
        throwsArgumentError,
      );
    });

    test('rejects an empty denominator', () {
      expect(
        () => CompoundUnitDefinition(
          code: 'invalid',
          symbol: 'invalid',
          numeratorUnits: <UnitDefinition>[UnitCatalog.microgram],
          denominatorUnits: const <UnitDefinition>[],
        ),
        throwsArgumentError,
      );
    });

    test('rejects a unit mixing medicinal mass and IU', () {
      expect(
        () => CompoundUnitDefinition(
          code: 'mg.IU/h',
          symbol: 'mg·IU/h',
          numeratorUnits: <UnitDefinition>[
            UnitCatalog.milligram,
            UnitCatalog.internationalUnit,
          ],
          denominatorUnits: <UnitDefinition>[UnitCatalog.hour],
        ),
        throwsArgumentError,
      );
    });

    test('freezes component lists passed by the caller', () {
      final List<UnitDefinition> numerator = <UnitDefinition>[
        UnitCatalog.microgram,
      ];
      final List<UnitDefinition> denominator = <UnitDefinition>[
        UnitCatalog.hour,
      ];
      final CompoundUnitDefinition unit = CompoundUnitDefinition(
        code: 'test_ug/h',
        symbol: 'µg/h',
        numeratorUnits: numerator,
        denominatorUnits: denominator,
      );

      numerator.add(UnitCatalog.milligram);
      denominator.add(UnitCatalog.kilogram);

      expect(unit.numeratorUnits, <UnitDefinition>[UnitCatalog.microgram]);
      expect(unit.denominatorUnits, <UnitDefinition>[UnitCatalog.hour]);
      expect(() => unit.numeratorUnits.add(UnitCatalog.gram), throwsUnsupportedError);
    });
  });
}
