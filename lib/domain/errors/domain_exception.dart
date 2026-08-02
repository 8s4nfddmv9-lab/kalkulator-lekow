/// Stable machine-readable error codes used by the calculator domain.
enum DomainErrorCode {
  /// A textual value cannot be parsed as an exact decimal number.
  invalidNumber,

  /// A value is negative where the clinical domain permits only non-negative
  /// quantities.
  negativeValue,

  /// A calculation would divide by zero.
  zeroDenominator,

  /// Units or dimensions cannot participate in the requested operation.
  incompatibleUnitFamily,

  /// A weight-normalized dose was requested without body mass.
  missingBodyMass,

  /// The supplied facts do not determine a unique result.
  insufficientData,

  /// Redundant user inputs imply different physical values.
  conflictingInputs,

  /// A value exceeds an explicitly supported technical range.
  outOfTechnicalRange,

  /// A derivation attempted to revisit an existing dependency path.
  cyclicDerivation,
}

/// Base type for deterministic, machine-readable domain failures.
abstract base class DomainException implements Exception {
  /// Creates a domain failure.
  const DomainException({required this.code, required this.message});

  /// Stable error code suitable for application-layer mapping.
  final DomainErrorCode code;

  /// Locale-independent diagnostic text intended for logs and tests.
  final String message;

  @override
  String toString() => '${code.name}: $message';
}

/// Thrown when text is not a supported exact decimal representation.
final class InvalidNumberException extends DomainException {
  /// Creates an invalid-number failure.
  const InvalidNumberException({required this.source})
    : super(
        code: DomainErrorCode.invalidNumber,
        message: 'Cannot parse "$source" as an exact decimal number.',
      );

  /// Original, unmodified user text.
  final String source;
}

/// Thrown when a negative clinical quantity is created.
final class NegativeValueException extends DomainException {
  /// Creates a negative-value failure.
  const NegativeValueException({required this.value})
    : super(
        code: DomainErrorCode.negativeValue,
        message: 'Negative clinical quantity is not allowed: $value.',
      );

  /// Exact textual representation of the rejected value.
  final String value;
}

/// Thrown when a unit does not represent the requested quantity kind.
final class QuantityUnitException extends DomainException {
  /// Creates a quantity-unit mismatch.
  const QuantityUnitException({
    required this.quantityKind,
    required this.unitCode,
    required this.unitDimension,
  }) : super(
         code: DomainErrorCode.incompatibleUnitFamily,
         message:
             'Unit $unitCode ($unitDimension) is not valid for '
             '$quantityKind.',
       );

  /// Stable quantity-kind name.
  final String quantityKind;

  /// Stable internal unit code.
  final String unitCode;

  /// Stable dimension description.
  final String unitDimension;
}
