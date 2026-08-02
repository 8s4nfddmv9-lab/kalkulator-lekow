import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';

/// Closed catalog of primitive units approved for the first calculator scope.
abstract final class UnitCatalog {
  /// Nanogram; canonical unit for medicinal substance mass.
  static final UnitDefinition nanogram = UnitDefinition(
    code: 'ng',
    symbol: 'ng',
    family: UnitFamily.medicineMass,
    toCanonical: Rational.fromInt(1),
  );

  /// Microgram. The UI uses µg; the internal code remains ASCII-friendly.
  static final UnitDefinition microgram = UnitDefinition(
    code: 'ug',
    symbol: 'µg',
    family: UnitFamily.medicineMass,
    toCanonical: Rational.fromInt(1000),
  );

  /// Milligram.
  static final UnitDefinition milligram = UnitDefinition(
    code: 'mg',
    symbol: 'mg',
    family: UnitFamily.medicineMass,
    toCanonical: Rational.fromInt(1000000),
  );

  /// Gram.
  static final UnitDefinition gram = UnitDefinition(
    code: 'g',
    symbol: 'g',
    family: UnitFamily.medicineMass,
    toCanonical: Rational.fromInt(1000000000),
  );

  /// International unit; intentionally isolated from medicinal mass units.
  static final UnitDefinition internationalUnit = UnitDefinition(
    code: 'IU',
    symbol: 'IU',
    family: UnitFamily.biologicalActivity,
    toCanonical: Rational.fromInt(1),
  );

  /// Millilitre; canonical volume unit in the MVP.
  static final UnitDefinition millilitre = UnitDefinition(
    code: 'mL',
    symbol: 'ml',
    family: UnitFamily.volume,
    toCanonical: Rational.fromInt(1),
  );

  /// Kilogram; canonical body-mass unit used by dose equations.
  static final UnitDefinition kilogram = UnitDefinition(
    code: 'kg',
    symbol: 'kg',
    family: UnitFamily.bodyMass,
    toCanonical: Rational.fromInt(1),
  );

  /// Gram of body mass, supported as an input convenience for neonates.
  static final UnitDefinition bodyGram = UnitDefinition(
    code: 'body_g',
    symbol: 'g',
    family: UnitFamily.bodyMass,
    toCanonical: Rational(BigInt.one, BigInt.from(1000)),
  );

  /// Minute; canonical time unit for administration-rate equations.
  static final UnitDefinition minute = UnitDefinition(
    code: 'min',
    symbol: 'min',
    family: UnitFamily.time,
    toCanonical: Rational.fromInt(1),
  );

  /// Hour.
  static final UnitDefinition hour = UnitDefinition(
    code: 'h',
    symbol: 'h',
    family: UnitFamily.time,
    toCanonical: Rational.fromInt(60),
  );

  /// Ordered medicinal-mass units shown in selectors.
  static final List<UnitDefinition> medicineMassUnits = List.unmodifiable(
    <UnitDefinition>[nanogram, microgram, milligram, gram],
  );

  /// Amount units shown in the first UI prototype.
  static final List<UnitDefinition> medicineAmountUnits = List.unmodifiable(
    <UnitDefinition>[...medicineMassUnits, internationalUnit],
  );
}
