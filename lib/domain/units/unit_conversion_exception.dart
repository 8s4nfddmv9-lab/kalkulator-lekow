/// Thrown when conversion is requested between incompatible unit families.
final class UnitConversionException implements Exception {
  /// Creates an incompatible conversion error.
  const UnitConversionException({
    required this.sourceCode,
    required this.sourceFamily,
    required this.targetCode,
    required this.targetFamily,
  });

  /// Stable code of the source unit.
  final String sourceCode;

  /// Name of the source unit family.
  final String sourceFamily;

  /// Stable code of the target unit.
  final String targetCode;

  /// Name of the target unit family.
  final String targetFamily;

  @override
  String toString() =>
      'Cannot convert $sourceCode ($sourceFamily) to '
      '$targetCode ($targetFamily).';
}
