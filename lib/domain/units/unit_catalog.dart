import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/units/compound_unit_definition.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';

/// Closed catalog of units approved for the first calculator scope.
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

  /// Body-mass input units.
  static final List<UnitDefinition> bodyMassUnits = List.unmodifiable(
    <UnitDefinition>[kilogram, bodyGram],
  );

  /// Supported time units.
  static final List<UnitDefinition> timeUnits = List.unmodifiable(
    <UnitDefinition>[minute, hour],
  );

  /// Approved concentration units, generated from the amount catalog.
  static final List<CompoundUnitDefinition> concentrationUnits =
      List<CompoundUnitDefinition>.unmodifiable(<CompoundUnitDefinition>[
        for (final UnitDefinition amountUnit in medicineAmountUnits)
          _ratio(
            numerator: amountUnit,
            denominators: <UnitDefinition>[millilitre],
          ),
      ]);

  /// Canonical internal flow unit.
  static final CompoundUnitDefinition millilitresPerMinute = _ratio(
    numerator: millilitre,
    denominators: <UnitDefinition>[minute],
  );

  /// Flow unit presented by the MVP interface.
  static final CompoundUnitDefinition millilitresPerHour = _ratio(
    numerator: millilitre,
    denominators: <UnitDefinition>[hour],
  );

  /// All supported flow-rate units, including the internal canonical form.
  static final List<CompoundUnitDefinition> flowRateUnits =
      List<CompoundUnitDefinition>.unmodifiable(<CompoundUnitDefinition>[
        millilitresPerMinute,
        millilitresPerHour,
      ]);

  /// Drug-administration rates without a body-mass denominator.
  static final List<CompoundUnitDefinition> administrationRateUnits =
      List<CompoundUnitDefinition>.unmodifiable(<CompoundUnitDefinition>[
        for (final UnitDefinition amountUnit in medicineAmountUnits)
          for (final UnitDefinition timeUnit in timeUnits)
            _ratio(
              numerator: amountUnit,
              denominators: <UnitDefinition>[timeUnit],
            ),
      ]);

  /// Drug-administration rates normalized to patient body mass.
  static final List<CompoundUnitDefinition> weightNormalizedDoseUnits =
      List<CompoundUnitDefinition>.unmodifiable(<CompoundUnitDefinition>[
        for (final UnitDefinition amountUnit in medicineAmountUnits)
          for (final UnitDefinition timeUnit in timeUnits)
            _ratio(
              numerator: amountUnit,
              denominators: <UnitDefinition>[kilogram, timeUnit],
            ),
      ]);

  /// Every unit that may occur in the MVP domain.
  static final List<MeasurementUnit> allUnits =
      List<MeasurementUnit>.unmodifiable(<MeasurementUnit>[
        ...medicineAmountUnits,
        millilitre,
        kilogram,
        bodyGram,
        minute,
        hour,
        ...concentrationUnits,
        ...flowRateUnits,
        ...administrationRateUnits,
        ...weightNormalizedDoseUnits,
      ]);

  static final Map<String, MeasurementUnit> _unitsByCode =
      Map<String, MeasurementUnit>.unmodifiable(<String, MeasurementUnit>{
        for (final MeasurementUnit unit in allUnits) unit.code: unit,
      });

  /// Finds a unit by its stable code or a supported textual alias.
  ///
  /// Both `mcg` and the two common Unicode micro symbols normalize to `ug`.
  /// Matching is case-insensitive for IU and ml.
  static MeasurementUnit? tryFind(String source) =>
      _unitsByCode[_normalizeCode(source)];

  /// Finds a unit or throws when [source] is not in the approved catalog.
  static MeasurementUnit find(String source) {
    final MeasurementUnit? result = tryFind(source);
    if (result == null) {
      throw ArgumentError.value(
        source,
        'source',
        'Unknown or unsupported unit.',
      );
    }
    return result;
  }

  static CompoundUnitDefinition _ratio({
    required UnitDefinition numerator,
    required List<UnitDefinition> denominators,
  }) => CompoundUnitDefinition(
    code:
        '${numerator.code}/${denominators.map((UnitDefinition unit) => unit.code).join('/')}',
    symbol:
        '${numerator.symbol}/${denominators.map((UnitDefinition unit) => unit.symbol).join('/')}',
    numeratorUnits: <UnitDefinition>[numerator],
    denominatorUnits: denominators,
  );

  static String _normalizeCode(String source) {
    String normalized = source.trim().replaceAll(' ', '').toLowerCase();
    normalized = normalized
        .replaceAll('mcg', 'ug')
        .replaceAll('µ', 'u')
        .replaceAll('μ', 'u')
        .replaceAll('iu', 'IU')
        .replaceAll('ml', 'mL');
    return normalized;
  }
}
