import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';

/// Single source of truth for units exposed by the MVP calculator form.
abstract final class CalculatorUnitOptions {
  /// Returns the ordered units selectable for [kind].
  static List<MeasurementUnit> forKind(QuantityKind kind) =>
      List<MeasurementUnit>.unmodifiable(switch (kind) {
        QuantityKind.bodyMass => <MeasurementUnit>[
          ...UnitCatalog.bodyMassUnits,
        ],
        QuantityKind.drugAmount => <MeasurementUnit>[
          ...UnitCatalog.medicineAmountUnits,
        ],
        QuantityKind.solutionVolume => <MeasurementUnit>[
          UnitCatalog.millilitre,
        ],
        QuantityKind.concentration => <MeasurementUnit>[
          ...UnitCatalog.concentrationUnits,
        ],
        QuantityKind.flowRate => <MeasurementUnit>[
          UnitCatalog.millilitresPerHour,
        ],
        QuantityKind.administrationRate => <MeasurementUnit>[
          ...UnitCatalog.administrationRateUnits,
        ],
        QuantityKind.weightNormalizedDose => <MeasurementUnit>[
          ...UnitCatalog.weightNormalizedDoseUnits,
        ],
        QuantityKind.infusionDuration || QuantityKind.time =>
          <MeasurementUnit>[UnitCatalog.minute, UnitCatalog.hour],
      });

  /// Default presentation unit used when no valid preference is available.
  static MeasurementUnit defaultFor(QuantityKind kind) => switch (kind) {
    QuantityKind.bodyMass => UnitCatalog.kilogram,
    QuantityKind.drugAmount => UnitCatalog.milligram,
    QuantityKind.solutionVolume => UnitCatalog.millilitre,
    QuantityKind.concentration => UnitCatalog.find('ug/mL'),
    QuantityKind.flowRate => UnitCatalog.millilitresPerHour,
    QuantityKind.administrationRate => UnitCatalog.find('ug/min'),
    QuantityKind.weightNormalizedDose => UnitCatalog.find('ug/kg/min'),
    QuantityKind.infusionDuration => UnitCatalog.hour,
    QuantityKind.time => UnitCatalog.minute,
  };

  /// Whether [unit] is explicitly exposed for [kind] in the MVP form.
  static bool supports(QuantityKind kind, MeasurementUnit unit) => forKind(
    kind,
  ).any((MeasurementUnit candidate) => candidate.code == unit.code);

  /// Resolves a stable unit [code], falling back safely when it is unknown,
  /// incompatible, or no longer exposed by the current application version.
  static MeasurementUnit resolveOrDefault(QuantityKind kind, String? code) {
    if (code == null) {
      return defaultFor(kind);
    }
    final MeasurementUnit? unit = UnitCatalog.tryFind(code);
    if (unit == null || !supports(kind, unit)) {
      return defaultFor(kind);
    }
    return unit;
  }
}
