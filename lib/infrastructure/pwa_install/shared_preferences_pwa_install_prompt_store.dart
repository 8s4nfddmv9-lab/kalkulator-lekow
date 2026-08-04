import 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Persists the non-clinical PWA installation reminder preference locally.
final class SharedPreferencesPwaInstallPromptStore
    implements PwaInstallPromptStore {
  /// Creates the store, optionally with an injected preferences client.
  SharedPreferencesPwaInstallPromptStore({SharedPreferencesAsync? preferences})
    : _preferences = preferences ?? SharedPreferencesAsync();

  final SharedPreferencesAsync _preferences;

  static const String _snoozedUntilKey =
      'infusioncalc.pwa_install.v1.snoozed_until_epoch_ms';

  @override
  Future<DateTime?> loadSnoozedUntil() async {
    final int? epochMilliseconds = await _preferences.getInt(_snoozedUntilKey);
    if (epochMilliseconds == null) {
      return null;
    }
    return DateTime.fromMillisecondsSinceEpoch(epochMilliseconds, isUtc: true);
  }

  @override
  Future<void> saveSnoozedUntil(DateTime value) => _preferences.setInt(
    _snoozedUntilKey,
    value.toUtc().millisecondsSinceEpoch,
  );

  @override
  Future<void> clearSnooze() => _preferences.remove(_snoozedUntilKey);
}
