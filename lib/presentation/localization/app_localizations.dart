import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:kalkulator_lekow/application/preferences/app_language.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';

/// Complete Polish and English copy for the interactive InfusionCalc UI.
final class AppLocalizations {
  /// Creates localized copy for [language].
  const AppLocalizations(this.language);

  /// Finds the current copy, using Polish for isolated widget previews.
  static AppLocalizations of(BuildContext context) =>
      Localizations.of<AppLocalizations>(context, AppLocalizations) ??
      const AppLocalizations(AppLanguage.polish);

  /// Delegate registered by the application root.
  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// App copy plus official Material, Widgets and Cupertino translations.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ];

  /// Languages supported by the two-state interface switch.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('pl'),
    Locale('en'),
  ];

  /// Active application language.
  final AppLanguage language;

  bool get _english => language == AppLanguage.english;

  String _text(String polish, String english) => _english ? english : polish;

  /// Text displayed inside the language switch.
  String get languageSwitchLabel => _english ? 'PL' : 'EN';

  /// Accessible description of the language switch action.
  String get languageSwitchTooltip =>
      _text('Przełącz na język angielski', 'Switch to Polish');

  String get clearAllTooltip =>
      _text('Wyczyść wszystkie pola', 'Clear all fields');

  String get patientSectionTitle => _text('Pacjent', 'Patient');

  String get patientSectionSubtitle => _text(
    'Masa jest wyłącznie daną wejściową i nigdy nie jest wyliczana.',
    'Body weight is an input only and is never calculated.',
  );

  String get bodyMassHelper => _text(
    'Wymagana tylko dla dawek zawierających /kg.',
    'Required only for doses that include /kg.',
  );

  String get solutionSectionTitle => _text('Roztwór', 'Solution');

  String get solutionSectionSubtitle => _text(
    'Dowolne dwa z trzech parametrów wyznaczają trzeci.',
    'Any two of the three parameters determine the third.',
  );

  String get administrationSectionTitle => _text('Podawanie', 'Administration');

  String get administrationSectionSubtitle => _text(
    'Zmiana przepływu lub dawki natychmiast przelicza pozostałe wartości.',
    'Changing the flow rate or dose immediately recalculates the remaining values.',
  );

  String get weightBasedDoseLabel =>
      _text('Dawka zależna od masy:', 'Weight-based dose:');

  String get bodyMassIncluded => _text(
    'masa pacjenta jest uwzględniana',
    'patient body weight is included',
  );

  String get administrationRateWithoutKilogram =>
      _text('szybkość podaży bez /kg', 'administration rate without /kg');

  String get doseFieldLabel =>
      _text('Dawka / szybkość podaży', 'Dose / administration rate');

  String get weightBasedDoseHelper => _text(
    'Masa jest potrzebna do przeliczenia dawki /kg na szybkość podaży lub przepływ.',
    'Body weight is required to convert a /kg dose into an administration rate or flow rate.',
  );

  String get nonWeightBasedDoseHelper => _text(
    'Ta wartość nie zależy od masy pacjenta.',
    'This value does not depend on patient body weight.',
  );

  String get liveCalculationNote => _text(
    'Wyniki są aktualizowane bez przycisku „Oblicz”. Zaokrąglanie dotyczy wyłącznie prezentacji.',
    'Results update without a “Calculate” button. Rounding affects presentation only.',
  );

  String conflictingFieldExpected(String value, String unit) => _text(
    'Z pozostałych danych wynika $value $unit.',
    'The remaining data imply $value $unit.',
  );

  String get invalidValue => _text('Nieprawidłowa wartość.', 'Invalid value.');

  String get valueMustBePositive => _text(
    'Wartość musi być większa od zera.',
    'The value must be greater than zero.',
  );

  String get incompatibleUnitCleared => _text(
    'Jednostek IU nie można automatycznie przeliczać na jednostki masy. Wartość pola została wyczyszczona.',
    'IU cannot be converted automatically to mass units. The field value has been cleared.',
  );

  String get calculatedUnitFamilyUnavailable => _text(
    'Wyliczonej wartości nie można pokazać w wybranej rodzinie jednostek. Najpierw zmień lub wyczyść dane źródłowe.',
    'The calculated value cannot be shown in the selected unit family. Change or clear the source data first.',
  );

  String get doseModeNeedsBodyMass => _text(
    'Do przeliczenia wpisanej wartości potrzebna jest masa pacjenta i spójne dane. Wpisz masę albo usuń konflikt przed zmianą trybu.',
    'Patient body weight and consistent data are required to convert the entered value. Enter the body weight or resolve the conflict before changing mode.',
  );

  String get preferencesReadFailed => _text(
    'Nie udało się odczytać ustawień jednostek. Użyto wartości domyślnych.',
    'Unit settings could not be loaded. Default values are being used.',
  );

  String get preferencesSaveFailed => _text(
    'Nie udało się zapisać ustawień jednostek. Obliczenia pozostają dostępne.',
    'Unit settings could not be saved. Calculations remain available.',
  );

  String conflictingInputSummary(String label, String value, String unit) =>
      _text(
        '$label jest niespójne. Z pozostałych danych wynika $value $unit.',
        '$label is inconsistent. The remaining data imply $value $unit.',
      );

  String copiedResult(String text) =>
      _text('Skopiowano: $text', 'Copied: $text');

  String domainError(DomainErrorCode code) => switch (code) {
    DomainErrorCode.invalidNumber => _text(
      'Wpisz liczbę z przecinkiem albo kropką, np. 0,05.',
      'Enter a number using a comma or decimal point, e.g. 0.05.',
    ),
    DomainErrorCode.negativeValue => _text(
      'Wartość nie może być ujemna.',
      'The value cannot be negative.',
    ),
    DomainErrorCode.zeroDenominator => _text(
      'Ta wartość musi być większa od zera, aby wykonać obliczenie.',
      'This value must be greater than zero to perform the calculation.',
    ),
    DomainErrorCode.incompatibleUnitFamily => _text(
      'Jednostki są niezgodne. IU nie można automatycznie przeliczyć na ng, µg, mg ani g.',
      'The units are incompatible. IU cannot be converted automatically to ng, µg, mg, or g.',
    ),
    DomainErrorCode.missingBodyMass => _text(
      'Do obliczenia dawki zawierającej /kg potrzebna jest masa pacjenta.',
      'Patient body weight is required to calculate a dose that includes /kg.',
    ),
    DomainErrorCode.insufficientData => _text(
      'Brakuje danych do jednoznacznego obliczenia.',
      'There is not enough data for an unambiguous calculation.',
    ),
    DomainErrorCode.conflictingInputs => _text(
      'Podane wartości są wzajemnie niespójne.',
      'The entered values are mutually inconsistent.',
    ),
    DomainErrorCode.outOfTechnicalRange => _text(
      'Wartość przekracza obsługiwany zakres techniczny.',
      'The value exceeds the supported technical range.',
    ),
    DomainErrorCode.cyclicDerivation => _text(
      'Nie można bezpiecznie ustalić kolejności obliczeń.',
      'A safe calculation order could not be determined.',
    ),
  };

  String quantityLabel(QuantityKind kind) => switch (kind) {
    QuantityKind.bodyMass => _text('Masa pacjenta', 'Patient body weight'),
    QuantityKind.drugAmount => _text('Ilość leku', 'Drug amount'),
    QuantityKind.solutionVolume => _text(
      'Objętość roztworu',
      'Solution volume',
    ),
    QuantityKind.concentration => _text('Stężenie', 'Concentration'),
    QuantityKind.flowRate => _text('Przepływ', 'Flow rate'),
    QuantityKind.administrationRate => _text(
      'Szybkość podaży',
      'Administration rate',
    ),
    QuantityKind.weightNormalizedDose => _text('Dawka /kg', 'Dose /kg'),
    QuantityKind.infusionDuration => _text('Czas infuzji', 'Infusion duration'),
    QuantityKind.time => _text('Czas', 'Time'),
  };

  String get technicalWarningTooltip => _text(
    'Informacja o przeznaczeniu kalkulatora',
    'Calculator purpose information',
  );

  String get technicalWarningTitle =>
      _text('Ważna informacja', 'Important information');

  String get technicalWarningText => _text(
    'Techniczny kalkulator — nie jest przeznaczony do podejmowania decyzji klinicznych.',
    'Technical calculator — not intended for clinical decision-making.',
  );

  String get acknowledge => _text('Rozumiem', 'I understand');

  String get checkData => _text('Sprawdź dane', 'Check the data');

  String get infusionDurationTitle =>
      _text('Czas opróżnienia roztworu', 'Time to empty the solution');

  String get infusionDurationSubtitle => _text(
    'Wyliczony z objętości i przepływu',
    'Calculated from volume and flow rate',
  );

  String get calculationDetailsTitle =>
      _text('Szczegóły obliczenia', 'Calculation details');

  String calculationResult(String result) =>
      _text('Wynik: $result', 'Result: $result');

  String get copyResult => _text('Kopiuj wynik', 'Copy result');

  String get enterValue => _text('Wpisz wartość', 'Enter a value');

  String get unitLabel => _text('Jednostka', 'Unit');

  String fieldStateLabel(String state) => switch (state) {
    'userInput' => _text('Wpisane', 'Entered'),
    'calculated' => _text('Wyliczone', 'Calculated'),
    'conflict' => _text('Konflikt', 'Conflict'),
    'invalid' => _text('Błąd', 'Error'),
    _ => '',
  };

  String get footerTagline => _text(
    'InfusionCalc · Technical infusion calculator',
    'InfusionCalc · Technical infusion calculator',
  );

  String get aboutLink => _text('About', 'About');

  String get changelogLink => _text('Changelog', 'Changelog');

  String get privacyLink => _text('Privacy', 'Privacy');

  String get contactLink => _text('Contact', 'Contact');

  String get close => _text('Zamknij', 'Close');

  String get copyAddress => _text('Kopiuj adres', 'Copy address');

  String get addressCopied => _text('Adres skopiowany.', 'Address copied.');

  String get privacyTitle => _text('Privacy', 'Privacy');

  String get privacyBody => _text(
    'Obliczenia wykonują się lokalnie na urządzeniu. InfusionCalc nie wysyła masy, ilości leku, stężenia, dawki, przepływu ani wyników do analityki. Nie wpisuj danych identyfikujących pacjenta.\n\n'
        'Aplikacja korzysta z minimalnej analityki Umami Cloud. Rejestrowane są odsłony strony oraz stała lista zdarzeń interfejsu, takich jak uruchomienie aplikacji, otwarcie informacji i działania związane z instalacją PWA. Zdarzenia mogą zawierać wyłącznie wersję aplikacji, platformę, tryb przeglądarki/PWA i metodę instalacji. Nie tworzymy własnego identyfikatora użytkownika.\n\n'
        'Pełny tryb offline zapisuje lokalnie publiczny kod i statyczne zasoby aplikacji, takie jak skrypty, fonty, ikony oraz strony informacyjne. Cache offline nie zawiera wartości formularza, wyników ani historii obliczeń.\n\n'
        'Lokalnie zapisywane są wyłącznie niekliniczne ustawienia: wybrane jednostki, tryb /kg, język interfejsu oraz data odroczenia komunikatu instalacji PWA po wybraniu „Nie teraz”. Pola liczbowe, wyniki i historia obliczeń nie są utrwalane.',
    'Calculations are performed locally on your device. InfusionCalc does not send patient body weight, drug amount, concentration, dose, flow rate, or results to analytics. Do not enter information that identifies a patient.\n\n'
        'The app uses minimal Umami Cloud analytics. It records page views and a fixed list of interface events, such as opening the app, viewing information, and actions related to PWA installation. Events may contain only the app version, platform, browser/PWA mode, and installation method. We do not create our own user identifier.\n\n'
        'Full offline mode stores the app’s public code and static assets locally, including scripts, fonts, icons, and informational pages. The offline cache does not contain form values, results, or calculation history.\n\n'
        'Only non-clinical settings are stored locally: selected units, /kg mode, interface language, and the date until which the PWA installation message is postponed after choosing “Not now”. Numeric fields, results, and calculation history are not persisted.',
  );

  String pwaDescriptionIosOtherBrowser() => _text(
    'Na iPhonie i iPadzie instalacja odbywa się przez Safari.',
    'On iPhone and iPad, installation is performed through Safari.',
  );

  String pwaDescriptionIosSafari() => _text(
    'Uruchamiaj InfusionCalc jak osobną aplikację z ekranu głównego.',
    'Launch InfusionCalc as a standalone app from your Home Screen.',
  );

  String pwaDescriptionAndroidPrompt() => _text(
    'Zainstaluj aplikację przez systemowe okno przeglądarki.',
    'Install the app using the browser’s system prompt.',
  );

  String pwaDescriptionAndroidManual() => _text(
    'Pokażemy, gdzie znaleźć instalację w menu przeglądarki.',
    'We will show you where to find installation in the browser menu.',
  );

  String get pwaSemanticsLabel => _text(
    'Instalacja InfusionCalc na ekranie głównym',
    'Install InfusionCalc on the Home Screen',
  );

  String get pwaBannerTitle => _text(
    'Dodaj InfusionCalc do ekranu głównego',
    'Add InfusionCalc to the Home Screen',
  );

  String get notNow => _text('Nie teraz', 'Not now');

  String get addToHomeScreen =>
      _text('Dodaj do ekranu głównego', 'Add to Home Screen');

  String get iosShareIconLabel =>
      _text('Ikona Udostępnij w Safari', 'Safari Share icon');

  String get iosOpenSafariNotice => _text(
    'Otwórz adres infusioncalc.eu w Safari. Instalacja z ekranu głównego na iPhonie i iPadzie jest dostępna z menu Safari.',
    'Open infusioncalc.eu in Safari. Home Screen installation on iPhone and iPad is available from the Safari menu.',
  );

  String iosInstruction(int step) => switch (step) {
    1 => _text(
      'W Safari dotknij przycisku Udostępnij — ikony strzałki wychodzącej z kwadratu.',
      'In Safari, tap the Share button — the arrow pointing out of a square.',
    ),
    2 => _text(
      'Przewiń listę czynności i wybierz „Dodaj do ekranu głównego”.',
      'Scroll through the actions and choose “Add to Home Screen”.',
    ),
    _ => _text(
      'Włącz „Otwórz jako aplikację”, jeśli ta opcja jest widoczna, a następnie dotknij „Dodaj”.',
      'Turn on “Open as Web App” if this option is shown, then tap “Add”.',
    ),
  };

  String get androidInstallTitle =>
      _text('Zainstaluj InfusionCalc', 'Install InfusionCalc');

  String get browserMenuLabel => _text('Menu przeglądarki', 'Browser menu');

  String androidInstruction(int step) => switch (step) {
    1 => _text(
      'Otwórz menu przeglądarki oznaczone trzema kropkami.',
      'Open the browser menu marked with three dots.',
    ),
    2 => _text(
      'Wybierz „Zainstaluj aplikację” albo „Dodaj do ekranu głównego”.',
      'Choose “Install app” or “Add to Home Screen”.',
    ),
    _ => _text(
      'Potwierdź instalację w oknie systemowym.',
      'Confirm installation in the system prompt.',
    ),
  };
}

final class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) => AppLocalizations.supportedLocales.any(
    (Locale supported) => supported.languageCode == locale.languageCode,
  );

  @override
  Future<AppLocalizations> load(Locale locale) => SynchronousFuture(
    AppLocalizations(AppLanguage.fromCode(locale.languageCode)),
  );

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}
