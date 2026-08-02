/// Stable identifiers of fields present in the calculator form.
enum CalculatorFieldId {
  /// Patient body mass. This field is always user-provided.
  bodyMass,

  /// Amount of medicinal substance or biological activity.
  drugAmount,

  /// Total solution volume.
  solutionVolume,

  /// Drug concentration in the solution.
  concentration,

  /// Pump flow rate.
  flowRate,

  /// Absolute or weight-normalized administration rate.
  dose,

  /// Calculated infusion duration.
  infusionDuration,
}

/// Provenance and validation state of a calculator field.
enum FieldOrigin {
  /// No value is currently available.
  empty,

  /// The value was explicitly entered by the user.
  userInput,

  /// The value was derived by the calculation engine.
  calculated,

  /// Redundant user inputs do not agree.
  conflict,

  /// The entered value cannot be parsed or validated.
  invalid,
}

/// Immutable application-layer state of one calculator field.
final class CalculatorFieldState<T> {
  const CalculatorFieldState._({
    required this.id,
    required this.origin,
    this.value,
  });

  /// Creates an empty field state.
  const CalculatorFieldState.empty(CalculatorFieldId id)
    : this._(id: id, origin: FieldOrigin.empty);

  /// Creates a field state explicitly supplied by the user.
  const CalculatorFieldState.userInput({
    required CalculatorFieldId id,
    required T value,
  }) : this._(id: id, origin: FieldOrigin.userInput, value: value);

  /// Creates a calculated field state.
  ///
  /// Patient body mass is deliberately excluded from calculation targets.
  factory CalculatorFieldState.calculated({
    required CalculatorFieldId id,
    required T value,
  }) {
    if (id == CalculatorFieldId.bodyMass) {
      throw ArgumentError.value(
        id,
        'id',
        'Patient body mass cannot be a calculated field.',
      );
    }

    return CalculatorFieldState<T>._(
      id: id,
      origin: FieldOrigin.calculated,
      value: value,
    );
  }

  /// Field identifier.
  final CalculatorFieldId id;

  /// Source and validation state of the value.
  final FieldOrigin origin;

  /// Typed value when present.
  final T? value;

  /// Whether the state contains a usable value.
  bool get hasValue => value != null;
}
