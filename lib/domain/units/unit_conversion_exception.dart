import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';

/// Thrown when conversion is requested between incompatible dimensions.
final class UnitConversionException extends DomainException {
  /// Creates an incompatible conversion error.
  const UnitConversionException({
    required this.sourceCode,
    required this.sourceDimension,
    required this.targetCode,
    required this.targetDimension,
  }) : super(
         code: DomainErrorCode.incompatibleUnitFamily,
         message:
             'Cannot convert $sourceCode ($sourceDimension) to '
             '$targetCode ($targetDimension).',
       );

  /// Stable code of the source unit.
  final String sourceCode;

  /// Stable description of the source dimension.
  final String sourceDimension;

  /// Stable code of the target unit.
  final String targetCode;

  /// Stable description of the target dimension.
  final String targetDimension;
}
