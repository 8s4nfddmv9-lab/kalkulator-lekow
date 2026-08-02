import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';

void main() {
  group('Rational', () {
    test('reduces numerator and denominator', () {
      expect(
        Rational(BigInt.from(10), BigInt.from(20)),
        Rational(BigInt.one, BigInt.from(2)),
      );
    });

    test('normalizes a negative denominator', () {
      expect(
        Rational(BigInt.from(3), BigInt.from(-4)),
        Rational(BigInt.from(-3), BigInt.from(4)),
      );
    });

    test('keeps multiplication and division exact', () {
      final Rational oneSixtieth = Rational(BigInt.one, BigInt.from(60));
      final Rational result = oneSixtieth * Rational.fromInt(60);

      expect(result, Rational.fromInt(1));
      expect(result / Rational.fromInt(10), Rational(BigInt.one, BigInt.from(10)));
    });

    test('rejects a zero denominator', () {
      expect(
        () => Rational(BigInt.one, BigInt.zero),
        throwsArgumentError,
      );
    });

    test('rejects division by zero', () {
      expect(
        () => Rational.fromInt(1) / Rational.fromInt(0),
        throwsArgumentError,
      );
    });
  });
}
