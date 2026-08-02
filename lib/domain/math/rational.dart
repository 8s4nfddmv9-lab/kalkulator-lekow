/// An exact rational number represented by a reduced numerator and denominator.
///
/// This type is intentionally independent of Flutter and avoids binary
/// floating-point arithmetic in unit conversion factors.
final class Rational implements Comparable<Rational> {
  Rational._(this.numerator, this.denominator);

  /// Creates and normalizes a rational number.
  factory Rational(BigInt numerator, [BigInt? denominator]) {
    final BigInt resolvedDenominator = denominator ?? BigInt.one;
    if (resolvedDenominator == BigInt.zero) {
      throw ArgumentError.value(
        resolvedDenominator,
        'denominator',
        'Denominator cannot be zero.',
      );
    }

    if (numerator == BigInt.zero) {
      return Rational._(BigInt.zero, BigInt.one);
    }

    final bool isNegative = resolvedDenominator.isNegative;
    final BigInt signedNumerator = isNegative ? -numerator : numerator;
    final BigInt positiveDenominator = resolvedDenominator.abs();
    final BigInt divisor = signedNumerator.abs().gcd(positiveDenominator);

    return Rational._(
      signedNumerator ~/ divisor,
      positiveDenominator ~/ divisor,
    );
  }

  /// Creates a rational number from an integer.
  factory Rational.fromInt(int value) => Rational(BigInt.from(value));

  /// The reduced numerator.
  final BigInt numerator;

  /// The positive, reduced denominator.
  final BigInt denominator;

  /// Whether the value equals zero.
  bool get isZero => numerator == BigInt.zero;

  /// Returns the reciprocal of this value.
  Rational reciprocal() {
    if (isZero) {
      throw StateError('Zero does not have a reciprocal.');
    }
    return Rational(denominator, numerator);
  }

  /// Multiplies two exact rational values.
  Rational operator *(Rational other) =>
      Rational(numerator * other.numerator, denominator * other.denominator);

  /// Divides two exact rational values.
  Rational operator /(Rational other) {
    if (other.isZero) {
      throw ArgumentError.value(other, 'other', 'Cannot divide by zero.');
    }
    return this * other.reciprocal();
  }

  /// Adds two exact rational values.
  Rational operator +(Rational other) => Rational(
    numerator * other.denominator + other.numerator * denominator,
    denominator * other.denominator,
  );

  /// Subtracts two exact rational values.
  Rational operator -(Rational other) =>
      this + Rational(-other.numerator, other.denominator);

  @override
  int compareTo(Rational other) =>
      (numerator * other.denominator).compareTo(other.numerator * denominator);

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Rational &&
          numerator == other.numerator &&
          denominator == other.denominator;

  @override
  int get hashCode => Object.hash(numerator, denominator);

  @override
  String toString() => denominator == BigInt.one
      ? numerator.toString()
      : '$numerator/$denominator';
}
