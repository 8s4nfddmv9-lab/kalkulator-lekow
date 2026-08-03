import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  group('TechnicalInputPolicy', () {
    test('accepts a very small exact value within the supported scale', () {
      final Quantity quantity = Quantity.parse(
        kind: QuantityKind.drugAmount,
        source: '0,000000000000000001',
        unit: UnitCatalog.microgram,
      );

      expect(quantity.value.toString(), '1/1000000000000000000');
    });

    test('rejects more than eighteen fractional digits', () {
      expect(
        () => Quantity.parse(
          kind: QuantityKind.drugAmount,
          source: '0.0000000000000000001',
          unit: UnitCatalog.microgram,
        ),
        throwsA(
          isA<OutOfTechnicalRangeException>().having(
            (OutOfTechnicalRangeException error) => error.code,
            'code',
            DomainErrorCode.outOfTechnicalRange,
          ),
        ),
      );
    });

    test('rejects more than twenty-four integer digits', () {
      expect(
        () => Quantity.parse(
          kind: QuantityKind.solutionVolume,
          source: '1234567890123456789012345',
          unit: UnitCatalog.millilitre,
        ),
        throwsA(isA<OutOfTechnicalRangeException>()),
      );
    });

    test('rejects more than twenty-four significant digits', () {
      expect(
        () => Quantity.parse(
          kind: QuantityKind.drugAmount,
          source: '123456789012.1234567890123',
          unit: UnitCatalog.microgram,
        ),
        throwsA(isA<OutOfTechnicalRangeException>()),
      );
    });

    test('keeps invalid syntax classified as an invalid number', () {
      expect(
        () => Quantity.parse(
          kind: QuantityKind.drugAmount,
          source: '1e3',
          unit: UnitCatalog.microgram,
        ),
        throwsA(
          isA<InvalidNumberException>().having(
            (InvalidNumberException error) => error.code,
            'code',
            DomainErrorCode.invalidNumber,
          ),
        ),
      );
    });
  });
}
