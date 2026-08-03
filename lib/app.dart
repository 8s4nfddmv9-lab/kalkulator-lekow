import 'package:flutter/material.dart';
import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';
import 'package:kalkulator_lekow/presentation/calculator/calculator_screen.dart';

/// Root widget of the application.
class KalkulatorLekowApp extends StatelessWidget {
  /// Creates the application root.
  ///
  /// Tests and previews default to a volatile store. Production injects the
  /// platform-backed implementation from `main.dart`.
  const KalkulatorLekowApp({
    this.preferencesStore = const VolatileCalculatorPreferencesStore(),
    super.key,
  });

  /// Store used exclusively for non-clinical presentation preferences.
  final CalculatorPreferencesStore preferencesStore;

  @override
  Widget build(BuildContext context) => MaterialApp(
    debugShowCheckedModeBanner: false,
    title: 'Kalkulator leków',
    theme: _buildTheme(Brightness.light),
    darkTheme: _buildTheme(Brightness.dark),
    themeMode: ThemeMode.system,
    home: CalculatorScreen(preferencesStore: preferencesStore),
  );

  ThemeData _buildTheme(Brightness brightness) {
    final ColorScheme colorScheme = ColorScheme.fromSeed(
      seedColor: const Color(0xFF285A8E),
      brightness: brightness,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: colorScheme.surface,
      inputDecorationTheme: const InputDecorationTheme(
        border: OutlineInputBorder(),
      ),
    );
  }
}
