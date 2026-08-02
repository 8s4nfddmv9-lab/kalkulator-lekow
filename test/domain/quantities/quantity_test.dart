import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';
import 'package:kalkulator_lekow/domain/units/unit_conversion_exception.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';

void main() {
  group('Quantity', () {
    test('parses comma input and exposes an exact canonical value', () {
      final Quantity quantity = Quantity.parse(
        kind: QuantityKind.drugAmount,
        source: '4,25',
        unit: UnitCatalog.milligram,
      );

      expect(
        quantity.canonicalValue,
        Rational.fromInt(4250000),
      );
    });

    test('converts 1 mg to exactly 1000 µg', () {
      final Quantity milligram = Quantity(
        kind: QuantityKind.drugAmount,
        value: Rational.fromInt(1),
        unit: UnitCatalog.milligram,
      );

      final Quantity micrograms = milligram.convertTo(
        UnitCatalog.microgram,
      );

      expect(micrograms.value, Rational.fromInt(1000));
      expect(micrograms.unit, UnitCatalog.microgram);
      expect(milligram.isPhysicallyEquivalentTo(micrograms), isTrue);
    });

    test('all medicinal mass conversions are exactly reversible', () {
      for (final UnitDefinition source in UnitCatalog.medicineMassUnits) {
        for (final UnitDefinition target in UnitCatalog.medicineMassUnits) {
          final Quantity original = Quantity(
            kind: QuantityKind.drugAmount,
            value: Rational.parseDecimal('123.456'),
            unit: source,
          );

          final Quantity roundTrip = original.convertTo(target).convertTo(
            source,
          );

          expect(
            roundTrip,
            original,
            reason: '${source.code} -> ${target.code} -> ${source.code}',
          );
        }
      }
    });

    test('converts body grams to kilograms without binary rounding', () {
      final Quantity bodyMass = Quantity(
        kind: QuantityKind.bodyMass,
        value: Rational.fromInt(3500),
        unit: UnitCatalog.bodyGram,
      );

      final Quantity kilograms = bodyMass.convertTo(UnitCatalog.kilogram);

      expect(kilograms.value, Rational(BigInt.from(7), BigInt.from(2)));
    });

    test('supports both mass and IU concentration kinds', () {
      final Quantity massConcentration = Quantity(
        kind: QuantityKind.concentration,
        value: Rational.fromInt(80),
        unit: UnitCatalog.find('ug/mL'),
      );
      final Quantity activityConcentration = Quantity(
        kind: QuantityKind.concentration,
        value: Rational.fromInt(100),
        unit: UnitCatalog.find('IU/mL'),
      );

      expect(massConcentration.kind, QuantityKind.concentration);
      expect(activityConcentration.kind, QuantityKind.concentration);
    });

    test('rejects a medicinal mass unit for patient body mass', () {
      expect(
        () => Quantity(
          kind: QuantityKind.bodyMass,
          value: Rational.fromInt(70),
          unit: UnitCatalog.milligram,
        ),
        throwsA(
          isA<QuantityUnitException>().having(
            (QuantityUnitException error) => error.code,
            'code',
            DomainErrorCode.incompatibleUnitFamily,
          ),
        ),
      );
    });

    test('rejects negative clinical quantities', () {
      expect(
        () => Quantity.parse(
          kind: QuantityKind.flowRate,
          source: '-1',
          unit: UnitCatalog.millilitresPerHour,
        ),
        throwsA(
          isA<NegativeValueException>().having(
            (NegativeValueException error) => error.code,
            'code',
            DomainErrorCode.negativeValue,
          ),
        ),
      );
    });

    test('allows zero so denominator rules remain equation-specific', () {
      final Quantity quantity = Quantity(
        kind: QuantityKind.solutionVolume,
        value: Rational.fromInt(0),
        unit: UnitCatalog.millilitre,
      );

      expect(quantity.isZero, isTrue);
    });

    test('never converts IU to medicinal mass', () {
      final Quantity activity = Quantity(
        kind: QuantityKind.drugAmount,
        value: Rational.fromInt(1000),
        unit: UnitCatalog.internationalUnit,
      );

      expect(
        () => activity.convertTo(UnitCatalog.milligram),
        throwsA(isA<UnitConversionException>()),
      );
    });

    test('converts weight-normalized time units exactly', () {
      final MeasurementUnit hourly = UnitCatalog.find('mg/kg/h');
      final MeasurementUnit perMinute = UnitCatalog.find('mg/kg/min');
      final Quantity dose = Quantity(
        kind: QuantityKind.weightNormalizedDose,
        value: Rational.fromInt(6),
        unit: hourly,
      );

      final Quantity converted = dose.convertTo(perMinute);

      expect(
        converted.value,
        Rational(BigInt.one, BigInt.from(10)),
      );
    });
  });
}
