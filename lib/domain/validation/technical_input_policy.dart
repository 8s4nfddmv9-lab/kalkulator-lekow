import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';

/// Generous technical limits that prevent pathological numeric input while
/// remaining far outside the expected scale of supported calculations.
abstract final class TechnicalInputPolicy {
  /// Maximum total characters, including sign and separator.
  static const int maxSourceCharacters = 64;

  /// Maximum digits before the decimal separator.
  static const int maxIntegerDigits = 24;

  /// Maximum digits after the decimal separator.
  static const int maxFractionDigits = 18;

  /// Maximum significant digits after leading zeros are ignored.
  static const int maxSignificantDigits = 24;

  static final RegExp _decimalPattern = RegExp(r'^[+-]?\d+(?:[\.,]\d+)?$');

  /// Validates only technical complexity. Invalid syntax remains the
  /// responsibility of the exact decimal parser so error precedence stays
  /// deterministic.
  static void validate(String source) {
    final String normalized = source.trim();
    if (normalized.length > maxSourceCharacters) {
      throw OutOfTechnicalRangeException(
        source: source,
        limit: '$maxSourceCharacters-character input length',
      );
    }
    if (!_decimalPattern.hasMatch(normalized)) {
      return;
    }

    final bool hasSign =
        normalized.startsWith('-') || normalized.startsWith('+');
    final String unsigned = hasSign ? normalized.substring(1) : normalized;
    final int dotIndex = unsigned.indexOf('.');
    final int commaIndex = unsigned.indexOf(',');
    final int separatorIndex = dotIndex >= 0 ? dotIndex : commaIndex;
    final String integerDigits = separatorIndex < 0
        ? unsigned
        : unsigned.substring(0, separatorIndex);
    final String fractionDigits = separatorIndex < 0
        ? ''
        : unsigned.substring(separatorIndex + 1);

    if (integerDigits.length > maxIntegerDigits) {
      throw OutOfTechnicalRangeException(
        source: source,
        limit: '$maxIntegerDigits integer digits',
      );
    }
    if (fractionDigits.length > maxFractionDigits) {
      throw OutOfTechnicalRangeException(
        source: source,
        limit: '$maxFractionDigits fractional digits',
      );
    }

    final String allDigits = '$integerDigits$fractionDigits';
    final String significantDigits = allDigits.replaceFirst(RegExp(r'^0+'), '');
    final int significantDigitCount = significantDigits.isEmpty
        ? 1
        : significantDigits.length;
    if (significantDigitCount > maxSignificantDigits) {
      throw OutOfTechnicalRangeException(
        source: source,
        limit: '$maxSignificantDigits significant digits',
      );
    }
  }
}
