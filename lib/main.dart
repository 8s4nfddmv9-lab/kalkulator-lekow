import 'package:flutter/widgets.dart';
import 'package:kalkulator_lekow/app.dart';
import 'package:kalkulator_lekow/application/preferences/app_language.dart';
import 'package:kalkulator_lekow/infrastructure/analytics/analytics_factory.dart';
import 'package:kalkulator_lekow/infrastructure/preferences/shared_preferences_app_language_store.dart';
import 'package:kalkulator_lekow/infrastructure/preferences/shared_preferences_calculator_preferences_store.dart';
import 'package:kalkulator_lekow/infrastructure/pwa_install/shared_preferences_pwa_install_prompt_store.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final SharedPreferencesAppLanguageStore languageStore =
      SharedPreferencesAppLanguageStore();
  AppLanguage initialLanguage = AppLanguage.polish;
  try {
    initialLanguage = await languageStore.load();
  } on Object {
    // Existing installations remain usable with the Polish default.
  }
  runApp(
    KalkulatorLekowApp(
      initialLanguage: initialLanguage,
      languageStore: languageStore,
      preferencesStore: SharedPreferencesCalculatorPreferencesStore(),
      pwaInstallPromptStore: SharedPreferencesPwaInstallPromptStore(),
      analyticsTracker: createAnalyticsTracker(),
    ),
  );
}
