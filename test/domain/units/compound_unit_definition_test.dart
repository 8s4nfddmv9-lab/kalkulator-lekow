import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';
import 'package:kalkulator_lekow/domain/units/unit_conversion_exception.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';

void main() {
  group('compound unit conversions', () {
    test('1 µg/ml equals 0.001 mg/ml', () {
      final MeasurementUnit microgramsPerMillilitre = UnitCatalog.find('ug/mL');
      final MeasurementUnit milligramsPerMillilitre = UnitCatalog.find('mg/mL');

      expect(
        microgramsPerMillilitre.conversionFactorTo(milligramsPerMillilitre),
        Rational(BigInt.one, BigInt.from(1000)),
      );
    });

    test('1 ml/h equals exactly 1/60 ml/min', () {
      expect(
        UnitCatalog.millilitresPerHour.conversionFactorTo(
          UnitCatalog.millilitresPerMinute,
        ),
        Rational(BigInt.one, BigInt.from(60)),
      );
    });

    test('dose conversion preserves the body-mass denominator', () {
      final MeasurementUnit hourly = UnitCatalog.find('ug/kg/h');
      final MeasurementUnit perMinute = UnitCatalog.find('ug/kg/min');

      expect(
        hourly.conversionFactorTo(perMinute),
        Rational(BigInt.one, BigInt.from(60)),
      );
      expect(perMinute.conversionFactorTo(hourly), Rational.fromInt(60));
    });

    test('IU concentration is incompatible with mass concentration', () {
      final MeasurementUnit activity = UnitCatalog.find('IU/mL');
      final MeasurementUnit mass = UnitCatalog.find('ug/mL');

      expect(
        () => activity.conversionFactorTo(mass),
        throwsA(isA<UnitConversionException>()),
      );
    });
  });

  group('unit aliases', () {
    test('accepts mcg and both Unicode micro symbols', () {
      final MeasurementUnit canonical = UnitCatalog.find('ug/mL');

      expect(UnitCatalog.find('mcg/ml'), canonical);
      expect(UnitCatalog.find('µg / ml'), canonical);
      expect(UnitCatalog.find('μg/mL'), canonical);
    });

    test('matches IU and ml case-insensitively', () {
      expect(UnitCatalog.find('iu/ML'), UnitCatalog.find('IU/mL'));
    });
  });
}
