from __future__ import annotations

import re
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise SystemExit(
            f"Expected exactly one occurrence in {path}, found {count}: {old[:180]!r}",
        )
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


def replace_regex_once(path: Path, pattern: str, replacement: str) -> None:
    source = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, source, count=1, flags=re.DOTALL)
    if count != 1:
        raise SystemExit(f"Expected one regex match in {path}, found {count}: {pattern!r}")
    path.write_text(updated, encoding="utf-8")


# PWA installation analytics.
pwa_banner = Path("lib/presentation/pwa_install/pwa_install_banner.dart")
replace_once(
    pwa_banner,
    "import 'package:flutter/material.dart';\nimport 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';",
    "import 'package:flutter/material.dart';\nimport 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';\nimport 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';",
)
replace_once(
    pwa_banner,
    "  const PwaInstallBanner({\n    required this.promptStore,\n    this.bridge,",
    "  const PwaInstallBanner({\n    required this.promptStore,\n    this.analyticsTracker = const NoopAnalyticsTracker(),\n    this.bridge,",
)
replace_once(
    pwa_banner,
    "  final PwaInstallPromptStore promptStore;\n\n  /// Optional injected bridge used by tests.",
    "  final PwaInstallPromptStore promptStore;\n\n  /// Privacy-reviewed analytics sink isolated from calculator values.\n  final AnalyticsTracker analyticsTracker;\n\n  /// Optional injected bridge used by tests.",
)
replace_once(
    pwa_banner,
    "  bool _hiddenForSession = false;\n  bool _busy = false;",
    "  bool _hiddenForSession = false;\n  bool _busy = false;\n  bool _invitationTracked = false;\n  bool _installationTracked = false;",
)
replace_once(
    pwa_banner,
    """  void _handleSnapshot(PwaInstallSnapshot snapshot) {
    if (!mounted) {
      return;
    }
    setState(() {
      _snapshot = snapshot;
      if (snapshot.isStandalone) {
        _hiddenForSession = true;
      }
    });
  }
""",
    """  void _handleSnapshot(PwaInstallSnapshot snapshot) {
    if (!mounted) {
      return;
    }
    final bool becameStandalone =
        !_snapshot.isStandalone && snapshot.isStandalone;
    setState(() {
      _snapshot = snapshot;
      if (snapshot.isStandalone) {
        _hiddenForSession = true;
      }
    });
    if (becameStandalone && !_installationTracked) {
      _installationTracked = true;
      widget.analyticsTracker.track(AnalyticsEvent.pwaInstalled);
    }
  }
""",
)
replace_once(
    pwa_banner,
    """    if (!_shouldShow) {
      return const SizedBox.shrink();
    }

    final ThemeData theme = Theme.of(context);
""",
    """    if (!_shouldShow) {
      return const SizedBox.shrink();
    }

    _trackInvitationOpened();
    final ThemeData theme = Theme.of(context);
""",
)
replace_once(
    pwa_banner,
    """  Future<void> _startInstallation() async {
    if (_snapshot.platform == PwaInstallPlatform.ios) {
""",
    """  void _trackInvitationOpened() {
    if (_invitationTracked) {
      return;
    }
    _invitationTracked = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        widget.analyticsTracker.track(AnalyticsEvent.installPromptOpened);
      }
    });
  }

  String? get _installMethod => switch (_snapshot.platform) {
    PwaInstallPlatform.ios
        when _snapshot.browser == PwaInstallBrowser.safari =>
      'ios_safari_instructions',
    PwaInstallPlatform.ios => 'ios_open_safari',
    PwaInstallPlatform.android when _snapshot.canPrompt =>
      'android_native_prompt',
    PwaInstallPlatform.android => 'android_manual_instructions',
    PwaInstallPlatform.other => null,
  };

  Future<void> _startInstallation() async {
    final String? installMethod = _installMethod;
    if (installMethod != null) {
      widget.analyticsTracker.track(
        AnalyticsEvent.installButtonClicked,
        dimensions: <AnalyticsDimension, String>{
          AnalyticsDimension.installMethod: installMethod,
        },
      );
    }
    if (_snapshot.platform == PwaInstallPlatform.ios) {
""",
)

# Calculator screen integration.
calculator = Path("lib/presentation/calculator/calculator_screen.dart")
replace_once(
    calculator,
    "import 'package:flutter/services.dart';\nimport 'package:kalkulator_lekow/application/calculator_session.dart';",
    "import 'package:flutter/services.dart';\nimport 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';\nimport 'package:kalkulator_lekow/application/calculator_session.dart';",
)
replace_once(
    calculator,
    """  const CalculatorScreen({
    this.preferencesStore = const VolatileCalculatorPreferencesStore(),
    this.pwaInstallPromptStore = const EphemeralPwaInstallPromptStore(),
    super.key,
  });
""",
    """  const CalculatorScreen({
    this.preferencesStore = const VolatileCalculatorPreferencesStore(),
    this.pwaInstallPromptStore = const EphemeralPwaInstallPromptStore(),
    this.analyticsTracker = const NoopAnalyticsTracker(),
    super.key,
  });
""",
)
replace_once(
    calculator,
    """  /// Store used for the optional PWA installation reminder postponement.
  final PwaInstallPromptStore pwaInstallPromptStore;

  @override
""",
    """  /// Store used for the optional PWA installation reminder postponement.
  final PwaInstallPromptStore pwaInstallPromptStore;

  /// Privacy-reviewed analytics sink isolated from calculator values.
  final AnalyticsTracker analyticsTracker;

  @override
""",
)
replace_once(
    calculator,
    """            const _TopUtilityRow(),
            PwaInstallBanner(promptStore: widget.pwaInstallPromptStore),
""",
    """            _TopUtilityRow(analyticsTracker: widget.analyticsTracker),
            PwaInstallBanner(
              promptStore: widget.pwaInstallPromptStore,
              analyticsTracker: widget.analyticsTracker,
            ),
""",
)
replace_once(
    calculator,
    "            const AppFooter(key: Key('app-footer')),",
    "            AppFooter(\n              key: const Key('app-footer'),\n              analyticsTracker: widget.analyticsTracker,\n            ),",
)
replace_once(
    calculator,
    """class _TopUtilityRow extends StatelessWidget {
  const _TopUtilityRow();

  static const String _warningText =
""",
    """class _TopUtilityRow extends StatelessWidget {
  const _TopUtilityRow({required this.analyticsTracker});

  final AnalyticsTracker analyticsTracker;

  static const String _warningText =
""",
)
replace_once(
    calculator,
    """  Future<void> _showWarning(BuildContext context) => showDialog<void>(
    context: context,
""",
    """  Future<void> _showWarning(BuildContext context) {
    analyticsTracker.track(AnalyticsEvent.warningOpened);
    return showDialog<void>(
      context: context,
""",
)
replace_once(
    calculator,
    """      ],
    ),
  );
}

class _ProblemSummary extends StatelessWidget {
""",
    """        ],
      ),
    );
  }
}

class _ProblemSummary extends StatelessWidget {
""",
)

# Web tracker bootstrap and offline shell.
index = Path("web/index.html")
replace_once(
    index,
    "  <script src=\"pwa_install.js\"></script>",
    """  <script src="analytics.js"></script>
  <script
    defer
    src="https://cloud.umami.is/script.js"
    data-website-id="a75601c3-4636-4210-b309-c54736e06843"
    data-domains="infusioncalc.eu"></script>
  <script src="pwa_install.js"></script>""",
)

worker = Path("web/pwa_service_worker.js")
replace_once(
    worker,
    "  './flutter_bootstrap.js',\n  './pwa_install.js',",
    "  './flutter_bootstrap.js',\n  './analytics.js',\n  './pwa_install.js',",
)

# Production build validation.
finalizer = Path("tool/finalize_web_pwa.py")
replace_once(
    finalizer,
    '    "manifest.json",\n    "pwa_install.js",',
    '    "manifest.json",\n    "analytics.js",\n    "pwa_install.js",',
)
replace_once(
    finalizer,
    """    index_source = (build_dir / "index.html").read_text(encoding="utf-8")
    if 'src="pwa_install.js"' not in index_source:
        raise SystemExit("PWA install bridge is not loaded by index.html.")

    bridge_source = (build_dir / "pwa_install.js").read_text(encoding="utf-8")
""",
    """    index_source = (build_dir / "index.html").read_text(encoding="utf-8")
    if 'src="pwa_install.js"' not in index_source:
        raise SystemExit("PWA install bridge is not loaded by index.html.")
    for required_analytics_markup in (
        'src="analytics.js"',
        'src="https://cloud.umami.is/script.js"',
        'data-website-id="a75601c3-4636-4210-b309-c54736e06843"',
        'data-domains="infusioncalc.eu"',
    ):
        if required_analytics_markup not in index_source:
            raise SystemExit(
                f"Umami analytics markup is missing: {required_analytics_markup}",
            )

    analytics_source = (build_dir / "analytics.js").read_text(encoding="utf-8")
    for required_symbol in (
        "infusionCalcAnalyticsTrack",
        "app_open",
        "install_prompt_opened",
        "install_button_clicked",
        "pwa_installed",
        "warning_opened",
        "privacy_opened",
        "github_clicked",
        "contact_clicked",
    ):
        if required_symbol not in analytics_source:
            raise SystemExit(
                f"Analytics bridge is missing symbol: {required_symbol}",
            )
    if "umami.identify" in analytics_source or "umami.identify" in index_source:
        raise SystemExit("InfusionCalc must not identify analytics users.")
    if "./analytics.js" not in source:
        raise SystemExit("Analytics bridge is missing from the offline app shell.")

    bridge_source = (build_dir / "pwa_install.js").read_text(encoding="utf-8")
""",
)
replace_once(
    finalizer,
    '        "install_bridge": "pwa_install.js",\n',
    '        "install_bridge": "pwa_install.js",\n        "analytics_bridge": "analytics.js",\n        "analytics_provider": "Umami Cloud",\n        "analytics_domain": "infusioncalc.eu",\n',
)

# CI validates both browser bridges.
ci = Path(".github/workflows/ci.yml")
replace_once(
    ci,
    """      - name: Validate browser bridge syntax
        run: node --check web/pwa_install.js
""",
    """      - name: Validate browser bridge syntax
        run: |
          node --check web/analytics.js
          node --check web/pwa_install.js
""",
)

pages = Path(".github/workflows/github-pages.yml")
replace_once(
    pages,
    """      - name: Generate deterministic PWA icons
        run: python3 tool/prepare_web_pwa.py --web-dir web
""",
    """      - name: Validate browser bridge syntax
        run: |
          node --check web/analytics.js
          node --check web/pwa_install.js

      - name: Generate deterministic PWA icons
        run: python3 tool/prepare_web_pwa.py --web-dir web
""",
)

# Version.
pubspec = Path("pubspec.yaml")
replace_once(pubspec, "version: 0.1.3-beta.2+17", "version: 0.1.3-beta.3+18")

# Privacy policy.
Path("docs/PRIVACY.md").write_text(
    """# Prywatność — InfusionCalc

## Zakres aplikacji

InfusionCalc jest statycznym technicznym kalkulatorem działającym jako Progressive Web App. Aplikacja nie ma kont użytkowników, własnego backendu ani bazy danych pacjentów. Korzysta z ograniczonej analityki Umami Cloud opisanej poniżej.

## Dane wpisywane do kalkulatora

Masa, ilość leku, objętość, stężenie, przepływ, dawka, wyniki oraz wzory są przetwarzane lokalnie w przeglądarce użytkownika. Kod aplikacji nie wysyła treści tych pól do Umami, GitHub Pages ani innego serwera aplikacji i nie zapisuje ich po stronie hostingu.

Nie należy wpisywać danych identyfikujących pacjenta.

## Dane zapisywane lokalnie

Aplikacja zapisuje lokalnie wyłącznie niekliniczne ustawienia:

- wybrane jednostki;
- tryb dawki z `/kg` lub bez `/kg`;
- datę, do której komunikat „Dodaj do ekranu głównego” ma pozostać ukryty po wybraniu „Nie teraz”.

Odroczenie komunikatu instalacji jest przechowywane jako lokalny znacznik czasu i nie jest wysyłane do serwera. Pola liczbowe, wyniki i historia obliczeń nie są utrwalane przez obecną wersję.

## Analityka Umami Cloud

Publiczna wersja korzysta z Umami Cloud do podstawowych statystyk produktu. Skrypt jest ograniczony do domeny `infusioncalc.eu`. Rejestrowane są odsłony strony oraz zamknięta lista ośmiu zdarzeń interfejsu:

- uruchomienie aplikacji;
- wyświetlenie zachęty do instalacji;
- kliknięcie przycisku instalacji;
- potwierdzenie instalacji przez obsługiwaną przeglądarkę;
- otwarcie ostrzeżenia;
- otwarcie informacji o prywatności;
- kliknięcie odnośnika GitHub;
- kliknięcie odnośnika kontaktowego.

Do własnych zdarzeń mogą być dołączone wyłącznie: publiczna wersja aplikacji, platforma (`ios`, `android`, `other`), tryb uruchomienia (`browser`, `standalone`) oraz stała nazwa metody instalacji. Aplikacja nie ustawia własnego identyfikatora użytkownika i nie korzysta z `umami.identify`.

Analityka nie otrzymuje masy, ilości leku, objętości, stężenia, przepływu, dawki, wyników, wzorów, nazw leków, historii ani tekstu z pól formularza. Szczegółowy, wersjonowany kontrakt znajduje się w [`docs/ANALYTICS.md`](ANALYTICS.md).

Blokada trackera, brak internetu lub awaria Umami nie wpływają na obliczenia. Krótka kolejka zdarzeń istnieje wyłącznie w pamięci bieżącej strony i jest porzucana, gdy tracker pozostaje niedostępny.

## Instalacja PWA

W zwykłym trybie przeglądarki aplikacja sprawdza typ urządzenia, rodzinę przeglądarki, dostępność systemowego promptu instalacji oraz tryb wyświetlania `standalone`. Informacje te służą do pokazania właściwej instrukcji. Do Umami trafia jedynie znormalizowana platforma, tryb uruchomienia i — przy zdarzeniu instalacyjnym — jedna ze stałych nazw metody instalacji.

## Hosting

Publiczna wersja jest dostarczana przez GitHub Pages. Dostawca hostingu może przetwarzać standardowe dane techniczne żądań HTTP zgodnie z własnymi zasadami i obowiązującym prawem. Usługa analityczna jest dostarczana przez Umami Cloud zgodnie z aktualnymi warunkami i polityką prywatności dostawcy.

## Kontakt i zgłoszenia

Uwagi do prywatności i działania aplikacji można zgłaszać w repozytorium projektu. Nie należy dołączać danych pacjentów ani innych informacji poufnych:

```text
https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18
```
""",
    encoding="utf-8",
)

# README.
readme = Path("README.md")
replace_once(
    readme,
    "- brak kont, serwera, analityki i danych identyfikujących pacjenta;",
    "- brak kont, backendu i danych identyfikujących pacjenta; minimalna analityka Umami nie otrzymuje wartości z formularza;",
)
replace_once(
    readme,
    """Aplikacja zapisuje lokalnie wyłącznie niekliniczne preferencje: kody wybranych jednostek, tryb `/kg` oraz datę odroczenia komunikatu instalacji PWA po wybraniu „Nie teraz”. Nie zapisuje żadnych liczb z formularza, masy pacjenta, danych o leku, historii ani wyników. Po ponownym uruchomieniu wszystkie pola liczbowe są puste.
""",
    """Aplikacja zapisuje lokalnie wyłącznie niekliniczne preferencje: kody wybranych jednostek, tryb `/kg` oraz datę odroczenia komunikatu instalacji PWA po wybraniu „Nie teraz”. Nie zapisuje żadnych liczb z formularza, masy pacjenta, danych o leku, historii ani wyników. Po ponownym uruchomieniu wszystkie pola liczbowe są puste.

Publiczna wersja korzysta z minimalnej analityki Umami Cloud dla odsłon i ośmiu stałych zdarzeń interfejsu. Analityka nie ma dostępu do parametrów ani wyników kalkulatora, nie ustawia własnego identyfikatora użytkownika i jest opcjonalna dla działania aplikacji.
""",
)
replace_once(
    readme,
    """W zwykłym trybie mobilnej przeglądarki pod nagłówkiem pojawia się przycisk „Dodaj do ekranu głównego”. Na Androidzie uruchamia natywny prompt instalacji, gdy przeglądarka go udostępnia, a w pozostałych przypadkach pokazuje instrukcję ręczną. Na iPhonie i iPadzie wyświetla instrukcję Safari z ikoną „Udostępnij”. Komunikat nie jest renderowany w trybie `standalone`; opcja „Nie teraz” odracza go lokalnie na 30 dni.
""",
    """W zwykłym trybie mobilnej przeglądarki pod nagłówkiem pojawia się przycisk „Dodaj do ekranu głównego”. Na Androidzie uruchamia natywny prompt instalacji, gdy przeglądarka go udostępnia, a w pozostałych przypadkach pokazuje instrukcję ręczną. Na iPhonie i iPadzie wyświetla instrukcję Safari z ikoną „Udostępnij”. Komunikat nie jest renderowany w trybie `standalone`; opcja „Nie teraz” odracza go lokalnie na 30 dni.

Umami Cloud rejestruje podstawowe odsłony i stałe zdarzenia użyteczności, takie jak otwarcie informacji czy kroki instalacji PWA. Zakres danych, twarde wyłączenia oraz sposób dostępu do panelu opisuje [`docs/ANALYTICS.md`](docs/ANALYTICS.md).
""",
)
replace_once(
    readme,
    "- [Prywatność](docs/PRIVACY.md)\n- [Feedback po pierwszych testach]",
    "- [Prywatność](docs/PRIVACY.md)\n- [Analityka](docs/ANALYTICS.md)\n- [Feedback po pierwszych testach]",
)
replace_once(
    readme,
    "**Wersja publiczna:** `0.1.3-beta.2+17` — uporządkowany nagłówek, kompaktowe ostrzeżenie i przewijana stopka",
    "**Wersja publiczna:** `0.1.3-beta.3+18` — minimalna, prywatna analityka Umami Cloud",
)

# Changelog.
changelog = Path("CHANGELOG.md")
replace_once(
    changelog,
    "## [Unreleased]\n\n",
    """## [Unreleased]

## [0.1.3-beta.3] — 2026-08-04

### Dodano

- minimalną analitykę Umami Cloud ograniczoną do domeny `infusioncalc.eu`;
- automatyczne statystyki odsłon oraz osiem stałych zdarzeń produktu;
- typowany adapter Dart i lokalny bridge JavaScript z listą dozwolonych zdarzeń i pól;
- wersję aplikacji, platformę i tryb `browser`/`standalone` jako niespersonalizowane wymiary zdarzeń;
- dokument `docs/ANALYTICS.md` oraz testy kontraktu analitycznego;
- walidację konfiguracji Umami i skryptu analitycznego w produkcyjnym buildzie PWA.

### Zmieniono

- komunikat i dokumentację prywatności, aby jawnie opisywały Umami Cloud;
- lejek instalacji PWA, ostrzeżenie, prywatność oraz linki GitHub/Contact o wyłącznie stałe zdarzenia użyteczności.

### Prywatność

- analityka nie odczytuje ani nie wysyła żadnej wartości formularza, masy, dawki, przepływu, stężenia, wyniku lub wzoru;
- aplikacja nie korzysta z `umami.identify` i nie ustawia własnego identyfikatora użytkownika;
- tracker jest opcjonalny — blokada, brak internetu lub awaria nie wpływają na kalkulator.

### Granice

- brak zmian w solverze, równaniach, jednostkach i polityce precyzji.

""",
)

# Roadmap.
roadmap = Path("ROADMAP.md")
replace_once(
    roadmap,
    "**Aktualny etap:** `0.1.3-beta.2 — porządek nagłówka i układu strony`",
    "**Aktualny etap:** `0.1.3-beta.3 — prywatna analityka produktu`",
)
replace_once(
    roadmap,
    "### 0.1.3-beta.2 — Porządek nagłówka i układu strony **← obecnie**",
    "### 0.1.3-beta.2 — Porządek nagłówka i układu strony **✓ ukończono**",
)
replace_once(
    roadmap,
    """**Zgłoszenie:** [issue #34](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/34).

### 0.1.3 — Dostępność i ergonomia
""",
    """**Zgłoszenie:** [issue #34](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/34).

### 0.1.3-beta.3 — Prywatna analityka produktu **← obecnie**

- [x] Umami Cloud ograniczone do domeny `infusioncalc.eu`;
- [x] automatyczne statystyki odsłon;
- [x] zamknięta lista ośmiu zdarzeń użyteczności;
- [x] wersja, platforma, tryb PWA i metoda instalacji jako jedyne własne wymiary;
- [x] brak dostępu analityki do formularza i modelu obliczeniowego;
- [x] brak `umami.identify` i własnych identyfikatorów użytkownika;
- [x] bezpieczne działanie przy blokadzie trackera i offline;
- [x] zaktualizowana polityka prywatności i dokumentacja analityki;
- [x] walidacja produkcyjnego builda PWA i testy zdarzeń;
- [ ] potwierdzenie pierwszych odsłon i zdarzeń w panelu Umami Cloud po wdrożeniu.

**Zgłoszenie:** [issue #36](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/36).

### 0.1.3 — Dostępność i ergonomia
""",
)

# Product vision privacy decision.
vision = Path("docs/VISION.md")
replace_once(
    vision,
    """Założenia:

- brak transmisji danych;
- brak zewnętrznej analityki;
- brak reklamowych SDK;
- brak nazwisk, numerów dokumentacji i innych identyfikatorów;
- ustawienia przechowywane wyłącznie lokalnie;
- jawna decyzja przed ewentualnym dodaniem synchronizacji.
""",
    """Założenia:

- brak transmisji wartości formularza, danych pacjenta, wyników i wzorów;
- dopuszczalna jest wyłącznie minimalna analityka techniczna odsłon oraz stałych zdarzeń interfejsu;
- brak własnych identyfikatorów użytkownika i funkcji identyfikacji analitycznej;
- brak reklamowych SDK i profilowania marketingowego;
- brak nazwisk, numerów dokumentacji i innych identyfikatorów;
- ustawienia kalkulatora przechowywane wyłącznie lokalnie;
- jawna decyzja przed ewentualnym rozszerzeniem analityki lub dodaniem synchronizacji.

Obecna implementacja Umami Cloud jest odseparowana od modelu kalkulatora. Może otrzymać wyłącznie wersję aplikacji, znormalizowaną platformę, tryb `browser`/`standalone`, metodę instalacji i jedną z zatwierdzonych nazw zdarzeń. Szczegóły opisuje `docs/ANALYTICS.md`.
""",
)

# Widget tests for footer analytics and disclosure.
footer_test = Path("test/presentation/app_footer_test.dart")
replace_once(
    footer_test,
    "import 'package:kalkulator_lekow/presentation/common/app_footer.dart';\n",
    "import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';\nimport 'package:kalkulator_lekow/presentation/common/app_footer.dart';\n\nimport '../support/recording_analytics_tracker.dart';\n",
)
replace_once(
    footer_test,
    """  Widget subject() => const MaterialApp(
    home: Scaffold(body: SizedBox.expand(), bottomNavigationBar: AppFooter()),
  );
""",
    """  Widget subject({AnalyticsTracker? analyticsTracker}) => MaterialApp(
    home: Scaffold(
      body: const SizedBox.expand(),
      bottomNavigationBar: AppFooter(
        analyticsTracker: analyticsTracker ?? const NoopAnalyticsTracker(),
      ),
    ),
  );
""",
)
replace_once(
    footer_test,
    """  testWidgets('privacy dialog explains local processing', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(subject());
""",
    """  testWidgets('privacy dialog explains local processing and Umami', (
    WidgetTester tester,
  ) async {
    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();
    await tester.pumpWidget(subject(analyticsTracker: tracker));
""",
)
replace_once(
    footer_test,
    """    expect(
      find.textContaining('data odroczenia komunikatu instalacji PWA'),
      findsOneWidget,
    );
""",
    """    expect(find.textContaining('Umami Cloud'), findsOneWidget);
    expect(
      find.textContaining('Nie tworzymy własnego identyfikatora użytkownika'),
      findsOneWidget,
    );
    expect(tracker.count(AnalyticsEvent.privacyOpened), 1);
""",
)
replace_once(
    footer_test,
    """  testWidgets('native contact fallback exposes the feedback issue address', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(subject());
""",
    """  testWidgets('GitHub and contact links report fixed events', (
    WidgetTester tester,
  ) async {
    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();
    await tester.pumpWidget(subject(analyticsTracker: tracker));

    await tester.tap(find.text('GitHub'));
    await tester.pumpAndSettle();
    expect(tracker.count(AnalyticsEvent.githubClicked), 1);
    await tester.tap(find.text('Zamknij'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Contact'));
""",
)
replace_once(
    footer_test,
    """    expect(find.text('Kopiuj adres'), findsOneWidget);
  });
}
""",
    """    expect(find.text('Kopiuj adres'), findsOneWidget);
    expect(tracker.count(AnalyticsEvent.contactClicked), 1);
  });
}
""",
)

# PWA installation analytics tests.
pwa_test = Path("test/presentation/pwa_install_banner_test.dart")
replace_once(
    pwa_test,
    "import 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';\n",
    "import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';\nimport 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';\n",
)
replace_once(
    pwa_test,
    "import 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_bridge.dart';\n",
    "import 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_bridge.dart';\n\nimport '../support/recording_analytics_tracker.dart';\n",
)
replace_once(
    pwa_test,
    """  Widget subject({
    required PwaInstallBridge bridge,
    required PwaInstallPromptStore store,
  }) => MaterialApp(
""",
    """  Widget subject({
    required PwaInstallBridge bridge,
    required PwaInstallPromptStore store,
    AnalyticsTracker? analyticsTracker,
  }) => MaterialApp(
""",
)
replace_once(
    pwa_test,
    """          PwaInstallBanner(bridge: bridge, promptStore: store, now: () => now),
""",
    """          PwaInstallBanner(
            bridge: bridge,
            promptStore: store,
            analyticsTracker:
                analyticsTracker ?? const NoopAnalyticsTracker(),
            now: () => now,
          ),
""",
)
replace_once(
    pwa_test,
    """    await tester.pumpWidget(subject(bridge: bridge, store: _FakeStore()));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('pwa-install-banner')), findsOneWidget);
    await tester.tap(find.byKey(const Key('pwa-install-button')));
""",
    """    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();
    await tester.pumpWidget(
      subject(
        bridge: bridge,
        store: _FakeStore(),
        analyticsTracker: tracker,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('pwa-install-banner')), findsOneWidget);
    expect(tracker.count(AnalyticsEvent.installPromptOpened), 1);
    await tester.tap(find.byKey(const Key('pwa-install-button')));
""",
)
replace_once(
    pwa_test,
    """    expect(find.textContaining('Otwórz jako aplikację'), findsOneWidget);
  });
""",
    """    expect(find.textContaining('Otwórz jako aplikację'), findsOneWidget);
    expect(
      tracker.single(AnalyticsEvent.installButtonClicked).dimensions,
      <AnalyticsDimension, String>{
        AnalyticsDimension.installMethod: 'ios_safari_instructions',
      },
    );
  });
""",
)
replace_once(
    pwa_test,
    """    await tester.pumpWidget(subject(bridge: bridge, store: _FakeStore()));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('pwa-install-button')));
    await tester.pumpAndSettle();

    expect(
      find.textContaining('Otwórz adres infusioncalc.eu w Safari'),
      findsOneWidget,
    );
  });
""",
    """    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();
    await tester.pumpWidget(
      subject(
        bridge: bridge,
        store: _FakeStore(),
        analyticsTracker: tracker,
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('pwa-install-button')));
    await tester.pumpAndSettle();

    expect(
      find.textContaining('Otwórz adres infusioncalc.eu w Safari'),
      findsOneWidget,
    );
    expect(
      tracker.single(AnalyticsEvent.installButtonClicked).dimensions,
      <AnalyticsDimension, String>{
        AnalyticsDimension.installMethod: 'ios_open_safari',
      },
    );
  });
""",
)
replace_once(
    pwa_test,
    """    final _FakeStore store = _FakeStore();

    await tester.pumpWidget(subject(bridge: bridge, store: store));
""",
    """    final _FakeStore store = _FakeStore();
    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();

    await tester.pumpWidget(
      subject(bridge: bridge, store: store, analyticsTracker: tracker),
    );
""",
)
replace_once(
    pwa_test,
    """    expect(bridge.promptCalls, 1);
    expect(find.byKey(const Key('pwa-install-banner')), findsNothing);
    expect(store.clearCalls, 1);
  });
""",
    """    expect(bridge.promptCalls, 1);
    expect(find.byKey(const Key('pwa-install-banner')), findsNothing);
    expect(store.clearCalls, 1);
    expect(
      tracker.single(AnalyticsEvent.installButtonClicked).dimensions,
      <AnalyticsDimension, String>{
        AnalyticsDimension.installMethod: 'android_native_prompt',
      },
    );
    expect(tracker.count(AnalyticsEvent.pwaInstalled), 0);

    bridge.emit(
      const PwaInstallSnapshot(
        platform: PwaInstallPlatform.android,
        browser: PwaInstallBrowser.chromium,
        isStandalone: true,
        canPrompt: false,
      ),
    );
    await tester.pump();
    expect(tracker.count(AnalyticsEvent.pwaInstalled), 1);
  });
""",
)
replace_once(
    pwa_test,
    """    await tester.pumpWidget(subject(bridge: bridge, store: _FakeStore()));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('pwa-install-button')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('android-pwa-install-dialog')), findsOneWidget);
""",
    """    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();
    await tester.pumpWidget(
      subject(
        bridge: bridge,
        store: _FakeStore(),
        analyticsTracker: tracker,
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('pwa-install-button')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('android-pwa-install-dialog')), findsOneWidget);
""",
)
replace_once(
    pwa_test,
    """    expect(find.byKey(const Key('android-menu-icon')), findsOneWidget);
    expect(find.textContaining('Zainstaluj aplikację'), findsWidgets);
  });
""",
    """    expect(find.byKey(const Key('android-menu-icon')), findsOneWidget);
    expect(find.textContaining('Zainstaluj aplikację'), findsWidgets);
    expect(
      tracker.single(AnalyticsEvent.installButtonClicked).dimensions,
      <AnalyticsDimension, String>{
        AnalyticsDimension.installMethod: 'android_manual_instructions',
      },
    );
  });
""",
)
replace_once(
    pwa_test,
    """    await tester.pumpWidget(subject(bridge: bridge, store: _FakeStore()));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('pwa-install-banner')), findsNothing);
  });
""",
    """    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();
    await tester.pumpWidget(
      subject(
        bridge: bridge,
        store: _FakeStore(),
        analyticsTracker: tracker,
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('pwa-install-banner')), findsNothing);
    expect(tracker.count(AnalyticsEvent.installPromptOpened), 0);
  });
""",
)

# Warning analytics test.
calculator_test = Path("test/presentation/calculator_screen_test.dart")
replace_once(
    calculator_test,
    "import 'package:kalkulator_lekow/app.dart';\n",
    "import 'package:kalkulator_lekow/app.dart';\nimport 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';\n",
)
replace_once(
    calculator_test,
    "import 'package:kalkulator_lekow/presentation/calculator/calculator_screen.dart';\n",
    "import 'package:kalkulator_lekow/presentation/calculator/calculator_screen.dart';\n\nimport '../support/recording_analytics_tracker.dart';\n",
)
replace_once(
    calculator_test,
    """  testWidgets('opens and acknowledges the technical warning dialog', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());
""",
    """  testWidgets('opens, tracks and acknowledges the technical warning', (
    WidgetTester tester,
  ) async {
    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();
    await tester.pumpWidget(KalkulatorLekowApp(analyticsTracker: tracker));
""",
)
replace_once(
    calculator_test,
    """    expect(find.byKey(const Key('technical-warning-dialog')), findsOneWidget);
    expect(find.text(warningText), findsOneWidget);
""",
    """    expect(find.byKey(const Key('technical-warning-dialog')), findsOneWidget);
    expect(find.text(warningText), findsOneWidget);
    expect(tracker.count(AnalyticsEvent.warningOpened), 1);
""",
)

print("Applied Umami analytics integration updates.")
