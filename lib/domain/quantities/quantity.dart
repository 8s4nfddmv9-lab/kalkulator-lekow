import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';
import 'package:kalkulator_lekow/domain/validation/technical_input_policy.dart';

/// Exact, non-negative physical value with an explicit semantic kind and unit.
final class Quantity {
  Quantity._({required this.kind, required this.value, required this.unit});

  /// Creates a validated quantity.
  factory Quantity({
    required QuantityKind kind,
    required Rational value,
    required MeasurementUnit unit,
  }) {
    _validateUnit(kind, unit);
    if (value.isNegative) {
      throw NegativeValueException(value: value.toString());
    }
    return Quantity._(kind: kind, value: value, unit: unit);
  }

  /// Parses and validates an exact decimal quantity.
  factory Quantity.parse({
    required QuantityKind kind,
    required String source,
    required MeasurementUnit unit,
  }) {
    TechnicalInputPolicy.validate(source);
    return Quantity(
      kind: kind,
      value: Rational.parseDecimal(source),
      unit: unit,
    );
  }

  /// Semantic role of the value.
  final QuantityKind kind;

  /// Exact numeric value expressed in [unit].
  final Rational value;

  /// Selected presentation unit.
  final MeasurementUnit unit;

  /// Exact value expressed in the canonical unit of [unit.dimension].
  Rational get canonicalValue => value * unit.toCanonical;

  /// Whether this quantity is exactly zero.
  bool get isZero => value.isZero;

  /// Converts this value to [target] while preserving physical magnitude.
  Quantity convertTo(MeasurementUnit target) {
    _validateUnit(kind, target);
    return Quantity(
      kind: kind,
      value: value * unit.conversionFactorTo(target),
      unit: target,
    );
  }

  /// Whether two quantities describe exactly the same physical magnitude.
  bool isPhysicallyEquivalentTo(Quantity other) =>
      kind == other.kind &&
      unit.isCompatibleWith(other.unit) &&
      canonicalValue == other.canonicalValue;

  static void _validateUnit(QuantityKind kind, MeasurementUnit unit) {
    if (!kind.accepts(unit)) {
      throw QuantityUnitException(
        quantityKind: kind.name,
        unitCode: unit.code,
        unitDimension: unit.dimension.toString(),
      );
    }
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Quantity &&
          kind == other.kind &&
          value == other.value &&
          unit == other.unit;

  @override
  int get hashCode => Object.hash(kind, value, unit);

  @override
  String toString() => '$value ${unit.symbol}';
}
