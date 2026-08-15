import 'package:flutter/material.dart';
import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';
import 'package:kalkulator_lekow/application/preferences/app_language.dart';
import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';
import 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';
import 'package:kalkulator_lekow/presentation/calculator/calculator_screen.dart';
import 'package:kalkulator_lekow/presentation/localization/app_localizations.dart';
import 'package:kalkulator_lekow/presentation/localization/document_language_bridge.dart';

/// Root widget of the application.
class KalkulatorLekowApp extends StatefulWidget {
  /// Creates the application root.
  ///
  /// Tests and previews default to volatile stores and disabled analytics.
  /// Production injects platform-backed implementations from `main.dart`.
  const KalkulatorLekowApp({
    this.initialLanguage = AppLanguage.polish,
    this.languageStore = const VolatileAppLanguageStore(),
    this.preferencesStore = const VolatileCalculatorPreferencesStore(),
    this.pwaInstallPromptStore = const EphemeralPwaInstallPromptStore(),
    this.analyticsTracker = const NoopAnalyticsTracker(),
    super.key,
  });

  /// Language resolved before the first application frame.
  final AppLanguage initialLanguage;

  /// Store used exclusively for the non-clinical interface language.
  final AppLanguageStore languageStore;

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
  late AppLanguage _language;
  Future<void> _languageWriteQueue = Future<void>.value();

  @override
  void initState() {
    super.initState();
    _language = widget.initialLanguage;
    updateDocumentLanguage(_language);
    widget.analyticsTracker.track(AnalyticsEvent.appOpen);
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    debugShowCheckedModeBanner: false,
    title: 'InfusionCalc',
    theme: _buildTheme(Brightness.light),
    darkTheme: _buildTheme(Brightness.dark),
    themeMode: ThemeMode.system,
    locale: Locale(_language.code),
    supportedLocales: AppLocalizations.supportedLocales,
    localizationsDelegates: AppLocalizations.localizationsDelegates,
    home: CalculatorScreen(
      preferencesStore: widget.preferencesStore,
      pwaInstallPromptStore: widget.pwaInstallPromptStore,
      analyticsTracker: widget.analyticsTracker,
      onLanguageToggle: _toggleLanguage,
    ),
  );

  void _toggleLanguage() {
    final AppLanguage selected = _language.toggled;
    setState(() => _language = selected);
    updateDocumentLanguage(selected);

    _languageWriteQueue = _languageWriteQueue.then((_) async {
      try {
        await widget.languageStore.save(selected);
      } on Object {
        // The in-memory selection remains usable when persistence is blocked.
      }
    });
  }

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
