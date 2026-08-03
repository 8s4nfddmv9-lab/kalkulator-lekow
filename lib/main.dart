import 'package:flutter/widgets.dart';
import 'package:kalkulator_lekow/app.dart';
import 'package:kalkulator_lekow/infrastructure/preferences/shared_preferences_calculator_preferences_store.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(
    KalkulatorLekowApp(
      preferencesStore: SharedPreferencesCalculatorPreferencesStore(),
    ),
  );
}
