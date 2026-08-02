import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/units/unit_conversion_exception.dart';

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

/// Definition of a primitive unit and its exact canonical conversion factor.
final class UnitDefinition {
  /// Creates a unit definition.
  UnitDefinition({
    required this.code,
    required this.symbol,
    required this.family,
    required this.toCanonical,
  });

  /// Stable internal identifier, using ASCII where practical.
  final String code;

  /// Human-readable symbol presented in the interface.
  final String symbol;

  /// Physical family of the unit.
  final UnitFamily family;

  /// Exact multiplier converting this unit to its family canonical unit.
  final Rational toCanonical;

  /// Whether values can be converted between this and [other].
  bool isCompatibleWith(UnitDefinition other) => family == other.family;

  /// Exact multiplier converting a number in this unit to [target].
  Rational conversionFactorTo(UnitDefinition target) {
    if (!isCompatibleWith(target)) {
      throw UnitConversionException(
        sourceCode: code,
        sourceFamily: family.name,
        targetCode: target.code,
        targetFamily: target.family.name,
      );
    }
    return toCanonical / target.toCanonical;
  }

  @override
  String toString() => symbol;
}
