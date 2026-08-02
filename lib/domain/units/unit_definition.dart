import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/units/unit_conversion_exception.dart';
import 'package:kalkulator_lekow/domain/units/unit_dimension.dart';

/// Primitive physical families used by the calculator domain.
enum UnitFamily {
  /// Mass of a medicinal substance, for example ng, µg, mg, or g.
  medicineMass,

  /// Biological activity expressed in international units.
  biologicalActivity,

  /// Fluid volume.
  volume,

  /// Patient body mass.
  bodyMass,

  /// Time duration.
  time,
}

/// Maps each primitive family to one explicit dimension axis.
extension UnitFamilyDimension on UnitFamily {
  /// Dimension represented by this primitive family.
  UnitDimension get dimension => switch (this) {
    UnitFamily.medicineMass => const UnitDimension(medicineMassExponent: 1),
    UnitFamily.biologicalActivity => const UnitDimension(
      biologicalActivityExponent: 1,
    ),
    UnitFamily.volume => const UnitDimension(volumeExponent: 1),
    UnitFamily.bodyMass => const UnitDimension(bodyMassExponent: 1),
    UnitFamily.time => const UnitDimension(timeExponent: 1),
  };
}

/// Common contract for primitive and structured compound units.
abstract base class MeasurementUnit {
  /// Creates a measurement unit.
  MeasurementUnit({
    required this.code,
    required this.symbol,
    required this.dimension,
    required this.toCanonical,
  });

  /// Stable internal identifier, using ASCII where practical.
  final String code;

  /// Human-readable symbol presented in the interface.
  final String symbol;

  /// Full dimension vector of this unit.
  final UnitDimension dimension;

  /// Exact multiplier converting this unit to its canonical dimension unit.
  final Rational toCanonical;

  /// Whether values can be converted between this and [other].
  bool isCompatibleWith(MeasurementUnit other) => dimension == other.dimension;

  /// Exact multiplier converting a number in this unit to [target].
  Rational conversionFactorTo(MeasurementUnit target) {
    if (!isCompatibleWith(target)) {
      throw UnitConversionException(
        sourceCode: code,
        sourceDimension: dimension.toString(),
        targetCode: target.code,
        targetDimension: target.dimension.toString(),
      );
    }
    return toCanonical / target.toCanonical;
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is MeasurementUnit &&
          code == other.code &&
          symbol == other.symbol &&
          dimension == other.dimension &&
          toCanonical == other.toCanonical;

  @override
  int get hashCode => Object.hash(code, symbol, dimension, toCanonical);

  @override
  String toString() => symbol;
}

/// Definition of a primitive unit and its exact canonical conversion factor.
final class UnitDefinition extends MeasurementUnit {
  /// Creates a primitive unit definition.
  UnitDefinition({
    required super.code,
    required super.symbol,
    required this.family,
    required super.toCanonical,
  }) : super(dimension: family.dimension);

  /// Physical family of the primitive unit.
  final UnitFamily family;
}
