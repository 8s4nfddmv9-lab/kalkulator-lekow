import 'package:flutter/material.dart';
import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';
import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';
import 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';
import 'package:kalkulator_lekow/presentation/calculator/calculator_screen.dart';

/// Root widget of the application.
class KalkulatorLekowApp extends StatefulWidget {
  /// Creates the application root.
  ///
  /// Tests and previews default to volatile stores and disabled analytics.
  /// Production injects platform-backed implementations from `main.dart`.
  const KalkulatorLekowApp({
    this.preferencesStore = const VolatileCalculatorPreferencesStore(),
    this.pwaInstallPromptStore = const EphemeralPwaInstallPromptStore(),
    this.analyticsTracker = const NoopAnalyticsTracker(),
    super.key,
  });

  /// Store used exclusively for non-clinical presentation preferences.
  final CalculatorPreferencesStore preferencesStore;

  /// Store used for the optional PWA installation reminder postponement.
  final PwaInstallPromptStore pwaInstallPromptStore;

  /// Privacy-reviewed analytics sink isolated from calculator values.
  final AnalyticsTracker analyticsTracker;

  @override
  State<KalkulatorLekowApp> createState() => _KalkulatorLekowAppState();
}

class _KalkulatorLekowAppState extends State<KalkulatorLekowApp> {
  @override
  void initState() {
    super.initState();
    widget.analyticsTracker.track(AnalyticsEvent.appOpen);
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    debugShowCheckedModeBanner: false,
    title: 'InfusionCalc',
    theme: _buildTheme(Brightness.light),
    darkTheme: _buildTheme(Brightness.dark),
    themeMode: ThemeMode.system,
    home: CalculatorScreen(
      preferencesStore: widget.preferencesStore,
      pwaInstallPromptStore: widget.pwaInstallPromptStore,
      analyticsTracker: widget.analyticsTracker,
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
