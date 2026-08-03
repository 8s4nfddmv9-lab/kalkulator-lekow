import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Platform-backed store for non-clinical calculator preferences.
///
/// Only stable unit codes and the `/kg` display mode are written. Numeric
/// calculator values and patient-related inputs are never persisted.
final class SharedPreferencesCalculatorPreferencesStore
    implements CalculatorPreferencesStore {
  /// Creates the store, optionally with an injected preferences client.
  SharedPreferencesCalculatorPreferencesStore({
    SharedPreferencesAsync? preferences,
  }) : _preferences = preferences ?? SharedPreferencesAsync();

  final SharedPreferencesAsync _preferences;

  static const String _prefix = 'kalkulator_lekow.presentation.v1.';
  static const String _dosePerKilogramKey = '${_prefix}dose_per_kilogram';

  @override
  Future<CalculatorPreferences> load() async {
    final CalculatorPreferences defaults = CalculatorPreferences.defaults();
    final Map<QuantityKind, String> unitCodes =
        Map<QuantityKind, String>.of(defaults.unitCodes);

    for (final QuantityKind kind in CalculatorPreferences.persistedKinds) {
      final String? storedCode = await _preferences.getString(_unitKey(kind));
      if (storedCode != null) {
        unitCodes[kind] = storedCode;
      }
    }

    return CalculatorPreferences(
      unitCodes: unitCodes,
      dosePerKilogram:
          await _preferences.getBool(_dosePerKilogramKey) ??
          defaults.dosePerKilogram,
    );
  }

  @override
  Future<void> save(CalculatorPreferences preferences) async {
    for (final QuantityKind kind in CalculatorPreferences.persistedKinds) {
      await _preferences.setString(
        _unitKey(kind),
        preferences.unitFor(kind).code,
      );
    }
    await _preferences.setBool(
      _dosePerKilogramKey,
      preferences.dosePerKilogram,
    );
  }

  static String _unitKey(QuantityKind kind) => '${_prefix}unit.${kind.name}';
}
