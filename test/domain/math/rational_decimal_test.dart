import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';

void main() {
  group('Rational.parseDecimal', () {
    test('accepts comma and dot with identical exact results', () {
      final Rational expected = Rational(BigInt.one, BigInt.from(20));

      expect(Rational.parseDecimal('0,05'), expected);
      expect(Rational.parseDecimal('0.05'), expected);
    });

    test('normalizes signs, whitespace, and trailing decimal zeros', () {
      expect(
        Rational.parseDecimal('  -12.500  '),
        Rational(BigInt.from(-25), BigInt.from(2)),
      );
      expect(Rational.parseDecimal('+00042'), Rational.fromInt(42));
    });

    test('keeps very small values exact', () {
      expect(
        Rational.parseDecimal('0.000000001'),
        Rational(BigInt.one, BigInt.from(1000000000)),
      );
    });

    test('rejects unsupported or ambiguous number notation', () {
      for (final String source in <String>[
        '',
        '.',
        ',5',
        '1.',
        '1,',
        '1,2.3',
        '1e3',
        '1 000',
        '--1',
      ]) {
        expect(
          () => Rational.parseDecimal(source),
          throwsA(
            isA<InvalidNumberException>().having(
              (InvalidNumberException error) => error.code,
              'code',
              DomainErrorCode.invalidNumber,
            ),
          ),
          reason: source,
        );
      }
    });
  });
}
