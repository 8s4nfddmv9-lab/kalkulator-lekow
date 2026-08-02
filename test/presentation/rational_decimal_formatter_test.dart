import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/presentation/formatting/rational_decimal_formatter.dart';

void main() {
  group('RationalDecimalFormatter', () {
    test(
      'formats integers and terminating decimals without trailing zeros',
      () {
        expect(RationalDecimalFormatter.format(Rational.fromInt(80)), '80');
        expect(
          RationalDecimalFormatter.format(
            Rational(BigInt.from(21), BigInt.from(4)),
          ),
          '5,25',
        );
      },
    );

    test('formats repeating clinical values with adaptive precision', () {
      expect(
        RationalDecimalFormatter.format(
          Rational(BigInt.from(2), BigInt.from(21)),
        ),
        '0,095238095',
      );
    });

    test('never omits the zero before the decimal separator', () {
      expect(
        RationalDecimalFormatter.format(Rational(BigInt.one, BigInt.from(20))),
        '0,05',
      );
    });

    test(
      'uses scientific notation rather than displaying non-zero as zero',
      () {
        expect(
          RationalDecimalFormatter.format(
            Rational(BigInt.one, BigInt.from(10).pow(20)),
          ),
          '1e-20',
        );
      },
    );

    test('rounds only the display text', () {
      final Rational exact = Rational(BigInt.from(2), BigInt.from(3));

      expect(
        RationalDecimalFormatter.format(
          exact,
          significantDigits: 4,
          maxFractionDigits: 4,
        ),
        '0,6667',
      );
      expect(exact, Rational(BigInt.from(2), BigInt.from(3)));
    });
  });
}
