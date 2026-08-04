import 'package:flutter/material.dart';
import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';
import 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';
import 'package:kalkulator_lekow/presentation/calculator/calculator_screen.dart';
import 'package:kalkulator_lekow/presentation/common/app_footer.dart';

/// Root widget of the application.
class KalkulatorLekowApp extends StatelessWidget {
  /// Creates the application root.
  ///
  /// Tests and previews default to volatile stores. Production injects the
  /// platform-backed implementations from `main.dart`.
  const KalkulatorLekowApp({
    this.preferencesStore = const VolatileCalculatorPreferencesStore(),
    this.pwaInstallPromptStore = const EphemeralPwaInstallPromptStore(),
    super.key,
  });

  /// Store used exclusively for non-clinical presentation preferences.
  final CalculatorPreferencesStore preferencesStore;

  /// Store used for the optional PWA installation reminder postponement.
  final PwaInstallPromptStore pwaInstallPromptStore;

  @override
  Widget build(BuildContext context) => MaterialApp(
    debugShowCheckedModeBanner: false,
    title: 'InfusionCalc',
    theme: _buildTheme(Brightness.light),
    darkTheme: _buildTheme(Brightness.dark),
    themeMode: ThemeMode.system,
    home: _ApplicationShell(
      preferencesStore: preferencesStore,
      pwaInstallPromptStore: pwaInstallPromptStore,
    ),
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

class _ApplicationShell extends StatelessWidget {
  const _ApplicationShell({
    required this.preferencesStore,
    required this.pwaInstallPromptStore,
  });

  final CalculatorPreferencesStore preferencesStore;
  final PwaInstallPromptStore pwaInstallPromptStore;

  @override
  Widget build(BuildContext context) => Column(
    children: <Widget>[
      Expanded(
        child: CalculatorScreen(
          preferencesStore: preferencesStore,
          pwaInstallPromptStore: pwaInstallPromptStore,
        ),
      ),
      const AppFooter(),
    ],
  );
}
