import 'package:kalkulator_lekow/application/calculator_unit_options.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_definition.dart';

/// Persistable, non-clinical presentation preferences.
///
/// This model deliberately contains no numeric values, patient mass, drug
/// amount, concentration, flow, dose, history, or calculation result.
final class CalculatorPreferences {
  /// Creates a preference snapshot from stable unit codes.
  CalculatorPreferences({
    required Map<QuantityKind, String> unitCodes,
    required this.dosePerKilogram,
  }) : unitCodes = Map<QuantityKind, String>.unmodifiable(unitCodes);

  /// Creates the built-in defaults used for a fresh installation.
  factory CalculatorPreferences.defaults() => CalculatorPreferences(
    unitCodes: <QuantityKind, String>{
      for (final QuantityKind kind in persistedKinds)
        kind: CalculatorUnitOptions.defaultFor(kind).code,
    },
    dosePerKilogram: true,
  );

  /// Quantity kinds whose presentation units may be persisted.
  static const List<QuantityKind> persistedKinds = <QuantityKind>[
    QuantityKind.bodyMass,
    QuantityKind.drugAmount,
    QuantityKind.solutionVolume,
    QuantityKind.concentration,
    QuantityKind.flowRate,
    QuantityKind.administrationRate,
    QuantityKind.weightNormalizedDose,
    QuantityKind.infusionDuration,
  ];

  /// Stable unit codes keyed by semantic quantity kind.
  final Map<QuantityKind, String> unitCodes;

  /// Whether the dose field opens in the weight-normalized `/kg` mode.
  final bool dosePerKilogram;

  /// Returns a validated unit, falling back when stored data is obsolete or
  /// malformed.
  MeasurementUnit unitFor(QuantityKind kind) =>
      CalculatorUnitOptions.resolveOrDefault(kind, unitCodes[kind]);

  /// Creates a new snapshot while preserving unspecified settings.
  CalculatorPreferences copyWith({
    Map<QuantityKind, String>? unitCodes,
    bool? dosePerKilogram,
  }) => CalculatorPreferences(
    unitCodes: unitCodes ?? this.unitCodes,
    dosePerKilogram: dosePerKilogram ?? this.dosePerKilogram,
  );
}

/// Asynchronous boundary for loading and saving non-clinical preferences.
abstract interface class CalculatorPreferencesStore {
  /// Loads the latest available preference snapshot.
  Future<CalculatorPreferences> load();

  /// Persists one complete preference snapshot.
  Future<void> save(CalculatorPreferences preferences);
}

/// Test-safe and fallback store that always returns built-in defaults.
///
/// Production injects the platform-backed implementation explicitly.
final class VolatileCalculatorPreferencesStore
    implements CalculatorPreferencesStore {
  /// Creates a store that never writes to disk.
  const VolatileCalculatorPreferencesStore();

  @override
  Future<CalculatorPreferences> load() async => CalculatorPreferences.defaults();

  @override
  Future<void> save(CalculatorPreferences preferences) async {}
}
