import 'package:kalkulator_lekow/domain/math/rational.dart';

/// Deterministic display-only formatter for exact rational values.
///
/// Calculations remain exact. Rounding is applied only to the returned text.
abstract final class RationalDecimalFormatter {
  /// Formats [value] with a comma decimal separator and adaptive precision.
  static String format(
    Rational value, {
    int significantDigits = 8,
    int maxFractionDigits = 12,
  }) {
    if (significantDigits < 1) {
      throw ArgumentError.value(
        significantDigits,
        'significantDigits',
        'At least one significant digit is required.',
      );
    }
    if (maxFractionDigits < 0) {
      throw ArgumentError.value(
        maxFractionDigits,
        'maxFractionDigits',
        'Maximum fraction digits cannot be negative.',
      );
    }
    if (value.isZero) {
      return '0';
    }

    final bool negative = value.isNegative;
    final Rational absolute = value.absolute;
    final BigInt integerPart = absolute.numerator ~/ absolute.denominator;
    final int fractionDigits;

    if (integerPart > BigInt.zero) {
      final int integerDigits = integerPart.toString().length;
      fractionDigits = _clamp(
        significantDigits - integerDigits,
        0,
        maxFractionDigits,
      );
    } else {
      int firstSignificantPosition = 0;
      Rational probe = absolute;
      while (probe < Rational.fromInt(1) &&
          firstSignificantPosition <= maxFractionDigits) {
        probe = probe * Rational.fromInt(10);
        firstSignificantPosition += 1;
      }
      final int leadingFractionZeros = firstSignificantPosition - 1;
      fractionDigits = _clamp(
        leadingFractionZeros + significantDigits,
        0,
        maxFractionDigits,
      );
    }

    final String fixed = _formatFixed(absolute, fractionDigits: fractionDigits);
    if (fixed != '0') {
      return negative ? '-$fixed' : fixed;
    }

    final String scientific = _formatScientific(
      absolute,
      significantDigits: significantDigits,
    );
    return negative ? '-$scientific' : scientific;
  }

  static String _formatFixed(Rational value, {required int fractionDigits}) {
    final BigInt scale = BigInt.from(10).pow(fractionDigits);
    final BigInt scaledNumerator = value.numerator * scale;
    BigInt rounded = scaledNumerator ~/ value.denominator;
    final BigInt remainder = scaledNumerator.remainder(value.denominator);
    if (remainder * BigInt.from(2) >= value.denominator) {
      rounded += BigInt.one;
    }

    final BigInt whole = rounded ~/ scale;
    if (fractionDigits == 0) {
      return whole.toString();
    }

    String fraction = (rounded.remainder(
      scale,
    )).toString().padLeft(fractionDigits, '0');
    fraction = fraction.replaceFirst(RegExp(r'0+$'), '');
    return fraction.isEmpty ? whole.toString() : '$whole,$fraction';
  }

  static String _formatScientific(
    Rational value, {
    required int significantDigits,
  }) {
    int exponent = 0;
    Rational mantissa = value;
    final Rational ten = Rational.fromInt(10);

    if (mantissa >= Rational.fromInt(1)) {
      while (mantissa >= ten) {
        mantissa = mantissa / ten;
        exponent += 1;
      }
    } else {
      while (mantissa < Rational.fromInt(1)) {
        mantissa = mantissa * ten;
        exponent -= 1;
      }
    }

    String mantissaText = _formatFixed(
      mantissa,
      fractionDigits: significantDigits - 1,
    );

    // Half-up rounding can carry a normalized 9.99… mantissa to 10. Keep the
    // scientific representation canonical by moving that carry into the
    // exponent instead of returning forms such as `10e-20`.
    if (mantissaText == '10') {
      mantissaText = '1';
      exponent += 1;
    }

    final String sign = exponent >= 0 ? '+' : '';
    return '${mantissaText}e$sign$exponent';
  }

  static int _clamp(int value, int minimum, int maximum) {
    if (value < minimum) {
      return minimum;
    }
    if (value > maximum) {
      return maximum;
    }
    return value;
  }
}
