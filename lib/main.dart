import 'package:flutter/widgets.dart';
import 'package:kalkulator_lekow/app.dart';
import 'package:kalkulator_lekow/infrastructure/preferences/shared_preferences_calculator_preferences_store.dart';
import 'package:kalkulator_lekow/infrastructure/pwa_install/shared_preferences_pwa_install_prompt_store.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    KalkulatorLekowApp(
      preferencesStore: SharedPreferencesCalculatorPreferencesStore(),
      pwaInstallPromptStore: SharedPreferencesPwaInstallPromptStore(),
    ),
  );
}
