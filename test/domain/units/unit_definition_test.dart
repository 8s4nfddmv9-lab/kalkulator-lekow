import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';
import 'package:kalkulator_lekow/domain/units/unit_conversion_exception.dart';

void main() {
  group('primitive unit conversions', () {
    test('1 mg equals 1000 µg', () {
      expect(
        UnitCatalog.milligram.conversionFactorTo(UnitCatalog.microgram),
        Rational.fromInt(1000),
      );
    });

    test('1 g equals 1,000,000,000 ng', () {
      expect(
        UnitCatalog.gram.conversionFactorTo(UnitCatalog.nanogram),
        Rational.fromInt(1000000000),
      );
    });

    test('1 hour equals 60 minutes', () {
      expect(
        UnitCatalog.hour.conversionFactorTo(UnitCatalog.minute),
        Rational.fromInt(60),
      );
    });

    test('1 g body mass equals 0.001 kg', () {
      expect(
        UnitCatalog.bodyGram.conversionFactorTo(UnitCatalog.kilogram),
        Rational(BigInt.one, BigInt.from(1000)),
      );
    });

    test('IU cannot be converted to a medicinal mass unit', () {
      expect(
        () => UnitCatalog.internationalUnit.conversionFactorTo(
          UnitCatalog.milligram,
        ),
        throwsA(isA<UnitConversionException>()),
      );
    });
  });
}
