import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';
import 'package:kalkulator_lekow/domain/units/unit_dimension.dart';

/// A structured unit built from explicit numerator and denominator units.
///
/// Compound units are never parsed as arbitrary algebraic strings. The catalog
/// creates approved structures such as µg/ml, ml/h, and IU/kg/h.
final class CompoundUnitDefinition extends MeasurementUnit {
  CompoundUnitDefinition._({
    required super.code,
    required super.symbol,
    required super.dimension,
    required super.toCanonical,
    required this.numeratorUnits,
    required this.denominatorUnits,
  });

  /// Creates and validates a compound unit.
  factory CompoundUnitDefinition({
    required String code,
    required String symbol,
    required List<UnitDefinition> numeratorUnits,
    required List<UnitDefinition> denominatorUnits,
  }) {
    if (numeratorUnits.isEmpty) {
      throw ArgumentError.value(
        numeratorUnits,
        'numeratorUnits',
        'A compound unit must have at least one numerator component.',
      );
    }
    if (denominatorUnits.isEmpty) {
      throw ArgumentError.value(
        denominatorUnits,
        'denominatorUnits',
        'A compound unit must have at least one denominator component.',
      );
    }

    final List<UnitDefinition> frozenNumerator =
        List<UnitDefinition>.unmodifiable(numeratorUnits);
    final List<UnitDefinition> frozenDenominator =
        List<UnitDefinition>.unmodifiable(denominatorUnits);
    UnitDimension dimension = const UnitDimension();
    Rational toCanonical = Rational.fromInt(1);

    for (final UnitDefinition unit in frozenNumerator) {
      dimension = dimension + unit.dimension;
      toCanonical = toCanonical * unit.toCanonical;
    }
    for (final UnitDefinition unit in frozenDenominator) {
      dimension = dimension - unit.dimension;
      toCanonical = toCanonical / unit.toCanonical;
    }

    if (dimension.hasMixedDrugAmountFamilies) {
      throw ArgumentError.value(
        dimension,
        'dimension',
        'A unit cannot combine medicinal mass and biological activity.',
      );
    }

    return CompoundUnitDefinition._(
      code: code,
      symbol: symbol,
      dimension: dimension,
      toCanonical: toCanonical,
      numeratorUnits: frozenNumerator,
      denominatorUnits: frozenDenominator,
    );
  }

  /// Primitive units in the numerator, in presentation order.
  final List<UnitDefinition> numeratorUnits;

  /// Primitive units in the denominator, in presentation order.
  final List<UnitDefinition> denominatorUnits;
}
