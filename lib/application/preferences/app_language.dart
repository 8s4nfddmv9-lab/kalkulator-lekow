/// Language used by the InfusionCalc presentation layer.
enum AppLanguage {
  /// Polish, the default language for existing installations.
  polish('pl'),

  /// English.
  english('en');

  const AppLanguage(this.code);

  /// Stable ISO 639-1 language code used for persistence and Flutter locales.
  final String code;

  /// Resolves a persisted language code, preserving Polish as the fallback.
  static AppLanguage fromCode(String? code) => switch (code) {
    'en' => AppLanguage.english,
    _ => AppLanguage.polish,
  };

  /// The other language exposed by the two-state switch.
  AppLanguage get toggled => switch (this) {
    AppLanguage.polish => AppLanguage.english,
    AppLanguage.english => AppLanguage.polish,
  };
}

/// Asynchronous boundary for the non-clinical language preference.
abstract interface class AppLanguageStore {
  /// Loads the selected language, falling back to Polish when absent.
  Future<AppLanguage> load();

  /// Persists the selected language.
  Future<void> save(AppLanguage language);
}

/// Test-safe store that keeps the application in Polish and discards writes.
final class VolatileAppLanguageStore implements AppLanguageStore {
  /// Creates the volatile language store.
  const VolatileAppLanguageStore();

  @override
  Future<AppLanguage> load() async => AppLanguage.polish;

  @override
  Future<void> save(AppLanguage language) async {}
}
