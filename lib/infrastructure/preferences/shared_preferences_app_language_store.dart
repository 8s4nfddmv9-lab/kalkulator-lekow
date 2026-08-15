import 'package:kalkulator_lekow/application/preferences/app_language.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Browser- and device-backed storage for the selected interface language.
final class SharedPreferencesAppLanguageStore implements AppLanguageStore {
  /// Creates the store, optionally with an injected preferences client.
  SharedPreferencesAppLanguageStore({SharedPreferencesAsync? preferences})
    : _preferences = preferences ?? SharedPreferencesAsync();

  final SharedPreferencesAsync _preferences;

  /// Public so the web bootstrap can read the same key before Flutter starts.
  static const String preferenceKey = 'infusioncalc.presentation.v1.language';

  @override
  Future<AppLanguage> load() async =>
      AppLanguage.fromCode(await _preferences.getString(preferenceKey));

  @override
  Future<void> save(AppLanguage language) =>
      _preferences.setString(preferenceKey, language.code);
}
