import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';

/// An exact rational number represented by a reduced numerator and denominator.
///
/// This type is intentionally independent of Flutter and avoids binary
/// floating-point arithmetic in unit conversions and clinical calculations.
final class Rational implements Comparable<Rational> {
  Rational._(this.numerator, this.denominator);

  static final RegExp _decimalPattern = RegExp(
    r'^[+-]?\d+(?:[\.,]\d+)?$',
  );

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

  /// Parses a decimal value without passing through binary floating point.
  ///
  /// A comma or a dot may be used as the decimal separator. Scientific
  /// notation, grouping separators, omitted leading zeros, and trailing
  /// separators are intentionally rejected.
  factory Rational.parseDecimal(String source) {
    final String normalized = source.trim();
    if (!_decimalPattern.hasMatch(normalized)) {
      throw InvalidNumberException(source: source);
    }

    final bool isNegative = normalized.startsWith('-');
    final bool hasExplicitSign =
        isNegative || normalized.startsWith('+');
    final String unsigned = hasExplicitSign
        ? normalized.substring(1)
        : normalized;
    final int dotIndex = unsigned.indexOf('.');
    final int commaIndex = unsigned.indexOf(',');
    final int separatorIndex = dotIndex >= 0 ? dotIndex : commaIndex;

    if (separatorIndex < 0) {
      final BigInt integer = BigInt.parse(unsigned);
      return Rational(isNegative ? -integer : integer);
    }

    final String wholeDigits = unsigned.substring(0, separatorIndex);
    final String fractionDigits = unsigned.substring(separatorIndex + 1);
    final BigInt denominator = BigInt.from(10).pow(fractionDigits.length);
    final BigInt unsignedNumerator =
        BigInt.parse(wholeDigits) * denominator +
        BigInt.parse(fractionDigits);

    return Rational(
      isNegative ? -unsignedNumerator : unsignedNumerator,
      denominator,
    );
  }

  /// The reduced numerator.
  final BigInt numerator;

  /// The positive, reduced denominator.
  final BigInt denominator;

  /// Whether the value equals zero.
  bool get isZero => numerator == BigInt.zero;

  /// Whether the value is below zero.
  bool get isNegative => numerator.isNegative;

  /// Whether the value is above zero.
  bool get isPositive => numerator > BigInt.zero;

  /// Absolute value.
  Rational get absolute => isNegative ? -this : this;

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
  Rational operator -(Rational other) => this + (-other);

  /// Negates this value.
  Rational operator -() => Rational(-numerator, denominator);

  /// Whether this value is smaller than [other].
  bool operator <(Rational other) => compareTo(other) < 0;

  /// Whether this value is smaller than or equal to [other].
  bool operator <=(Rational other) => compareTo(other) <= 0;

  /// Whether this value is greater than [other].
  bool operator >(Rational other) => compareTo(other) > 0;

  /// Whether this value is greater than or equal to [other].
  bool operator >=(Rational other) => compareTo(other) >= 0;

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
