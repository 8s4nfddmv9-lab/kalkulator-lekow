/// Exponents of the primitive dimensions supported by the calculator.
///
/// Medicinal mass and biological activity are deliberately separate axes, so
/// IU can never become compatible with ng, µg, mg, or g by accident.
final class UnitDimension {
  /// Creates a dimension vector.
  const UnitDimension({
    this.medicineMassExponent = 0,
    this.biologicalActivityExponent = 0,
    this.volumeExponent = 0,
    this.bodyMassExponent = 0,
    this.timeExponent = 0,
  });

  /// Exponent of medicinal-substance mass.
  final int medicineMassExponent;

  /// Exponent of biological activity expressed in IU.
  final int biologicalActivityExponent;

  /// Exponent of fluid volume.
  final int volumeExponent;

  /// Exponent of patient body mass.
  final int bodyMassExponent;

  /// Exponent of time.
  final int timeExponent;

  /// Whether medicinal mass and IU occur in the same expression.
  bool get hasMixedDrugAmountFamilies =>
      medicineMassExponent != 0 && biologicalActivityExponent != 0;

  /// Whether every primitive exponent equals zero.
  bool get isDimensionless =>
      medicineMassExponent == 0 &&
      biologicalActivityExponent == 0 &&
      volumeExponent == 0 &&
      bodyMassExponent == 0 &&
      timeExponent == 0;

  /// Adds exponents component by component.
  UnitDimension operator +(UnitDimension other) => UnitDimension(
    medicineMassExponent:
        medicineMassExponent + other.medicineMassExponent,
    biologicalActivityExponent:
        biologicalActivityExponent + other.biologicalActivityExponent,
    volumeExponent: volumeExponent + other.volumeExponent,
    bodyMassExponent: bodyMassExponent + other.bodyMassExponent,
    timeExponent: timeExponent + other.timeExponent,
  );

  /// Subtracts exponents component by component.
  UnitDimension operator -(UnitDimension other) => UnitDimension(
    medicineMassExponent:
        medicineMassExponent - other.medicineMassExponent,
    biologicalActivityExponent:
        biologicalActivityExponent - other.biologicalActivityExponent,
    volumeExponent: volumeExponent - other.volumeExponent,
    bodyMassExponent: bodyMassExponent - other.bodyMassExponent,
    timeExponent: timeExponent - other.timeExponent,
  );

  /// Multiplies every exponent by [factor].
  UnitDimension scaled(int factor) => UnitDimension(
    medicineMassExponent: medicineMassExponent * factor,
    biologicalActivityExponent: biologicalActivityExponent * factor,
    volumeExponent: volumeExponent * factor,
    bodyMassExponent: bodyMassExponent * factor,
    timeExponent: timeExponent * factor,
  );

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is UnitDimension &&
          medicineMassExponent == other.medicineMassExponent &&
          biologicalActivityExponent ==
              other.biologicalActivityExponent &&
          volumeExponent == other.volumeExponent &&
          bodyMassExponent == other.bodyMassExponent &&
          timeExponent == other.timeExponent;

  @override
  int get hashCode => Object.hash(
    medicineMassExponent,
    biologicalActivityExponent,
    volumeExponent,
    bodyMassExponent,
    timeExponent,
  );

  @override
  String toString() {
    final List<String> components = <String>[
      if (medicineMassExponent != 0)
        _formatComponent('medicineMass', medicineMassExponent),
      if (biologicalActivityExponent != 0)
        _formatComponent('IU', biologicalActivityExponent),
      if (volumeExponent != 0)
        _formatComponent('volume', volumeExponent),
      if (bodyMassExponent != 0)
        _formatComponent('bodyMass', bodyMassExponent),
      if (timeExponent != 0) _formatComponent('time', timeExponent),
    ];
    return components.isEmpty ? 'dimensionless' : components.join('·');
  }

  static String _formatComponent(String name, int exponent) =>
      exponent == 1 ? name : '$name^$exponent';
}
