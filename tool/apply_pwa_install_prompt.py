from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    if old not in source:
        raise SystemExit(f"Expected block not found in {path}: {old[:240]!r}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


calculator = Path("lib/presentation/calculator/calculator_screen.dart")
replace_once(
    calculator,
    "import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';\n",
    "import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';\n"
    "import 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';\n",
)
replace_once(
    calculator,
    "import 'package:kalkulator_lekow/presentation/formatting/rational_decimal_formatter.dart';\n",
    "import 'package:kalkulator_lekow/presentation/formatting/rational_decimal_formatter.dart';\n"
    "import 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_banner.dart';\n",
)
replace_once(
    calculator,
    """  const CalculatorScreen({
    this.preferencesStore = const VolatileCalculatorPreferencesStore(),
    super.key,
  });

  /// Store used only for non-clinical presentation preferences.
  final CalculatorPreferencesStore preferencesStore;
""",
    """  const CalculatorScreen({
    this.preferencesStore = const VolatileCalculatorPreferencesStore(),
    this.pwaInstallPromptStore = const EphemeralPwaInstallPromptStore(),
    super.key,
  });

  /// Store used only for non-clinical presentation preferences.
  final CalculatorPreferencesStore preferencesStore;

  /// Store used for the optional PWA installation reminder postponement.
  final PwaInstallPromptStore pwaInstallPromptStore;
""",
)
replace_once(
    calculator,
    """          children: <Widget>[
            const _TechnicalCalculatorWarning(),
""",
    """          children: <Widget>[
            PwaInstallBanner(promptStore: widget.pwaInstallPromptStore),
            const _TechnicalCalculatorWarning(),
""",
)

banner = Path("lib/presentation/pwa_install/pwa_install_banner.dart")
replace_once(
    banner,
    """  Future<void> _startInstallation() async {
    switch (_snapshot.platform) {
      case PwaInstallPlatform.ios:
        await _showIosInstructions();
      case PwaInstallPlatform.android:
        await _startAndroidInstallation();
      case PwaInstallPlatform.other:
        return;
    }
  }
""",
    """  Future<void> _startInstallation() async {
    if (_snapshot.platform == PwaInstallPlatform.ios) {
      await _showIosInstructions();
      return;
    }
    if (_snapshot.platform == PwaInstallPlatform.android) {
      await _startAndroidInstallation();
    }
  }
""",
)
replace_once(
    banner,
    """    switch (outcome) {
      case PwaInstallOutcome.accepted:
        setState(() {
          _hiddenForSession = true;
          _snoozedUntil = null;
        });
        unawaited(_clearStoredSnooze());
      case PwaInstallOutcome.dismissed:
        await _snooze();
      case PwaInstallOutcome.unavailable:
        await _showAndroidInstructions();
    }
""",
    """    if (outcome == PwaInstallOutcome.accepted) {
      setState(() {
        _hiddenForSession = true;
        _snoozedUntil = null;
      });
      unawaited(_clearStoredSnooze());
      return;
    }
    if (outcome == PwaInstallOutcome.dismissed) {
      await _snooze();
      return;
    }
    await _showAndroidInstructions();
""",
)

readme = Path("README.md")
replace_once(
    readme,
    "Aplikacja zapisuje lokalnie wyłącznie niekliniczne preferencje prezentacji: kody wybranych jednostek i tryb `/kg`. Nie zapisuje żadnych liczb z formularza, masy pacjenta, danych o leku, historii ani wyników. Po ponownym uruchomieniu wszystkie pola liczbowe są puste.",
    "Aplikacja zapisuje lokalnie wyłącznie niekliniczne preferencje: kody wybranych jednostek, tryb `/kg` oraz datę odroczenia komunikatu instalacji PWA po wybraniu „Nie teraz”. Nie zapisuje żadnych liczb z formularza, masy pacjenta, danych o leku, historii ani wyników. Po ponownym uruchomieniu wszystkie pola liczbowe są puste.",
)
replace_once(
    readme,
    "Aplikacja nie ma własnego backendu. Serwer dostarcza wyłącznie statyczne pliki, a obliczenia wykonują się lokalnie w przeglądarce. Manifest PWA i service worker umożliwiają dodanie aplikacji do ekranu początkowego oraz korzystanie z wcześniej załadowanej wersji bez aktywnego połączenia.\n\nHistoryczne warianty",
    "Aplikacja nie ma własnego backendu. Serwer dostarcza wyłącznie statyczne pliki, a obliczenia wykonują się lokalnie w przeglądarce. Manifest PWA i service worker umożliwiają dodanie aplikacji do ekranu początkowego oraz korzystanie z wcześniej załadowanej wersji bez aktywnego połączenia.\n\nW zwykłym trybie mobilnej przeglądarki pod nagłówkiem pojawia się przycisk „Dodaj do ekranu głównego”. Na Androidzie uruchamia natywny prompt instalacji, gdy przeglądarka go udostępnia, a w pozostałych przypadkach pokazuje instrukcję ręczną. Na iPhonie i iPadzie wyświetla instrukcję Safari z ikoną „Udostępnij”. Komunikat nie jest renderowany w trybie `standalone`; opcja „Nie teraz” odracza go lokalnie na 30 dni.\n\nHistoryczne warianty",
)
replace_once(
    readme,
    "**Wersja publiczna:** `0.1.2-beta.3+15` — pierwsze poprawki UX publicznego PWA",
    "**Wersja publiczna:** `0.1.3-beta.1+16` — kontekstowa instalacja PWA na iOS i Androidzie",
)

roadmap = Path("ROADMAP.md")
replace_once(
    roadmap,
    "**Stan na:** 3 sierpnia 2026  \n**Aktualny etap:** `0.1.2-beta.3 — pierwsze poprawki po testach użytkowych`",
    "**Stan na:** 4 sierpnia 2026  \n**Aktualny etap:** `0.1.3-beta.1 — kontekstowa instalacja PWA`",
)
replace_once(
    roadmap,
    "### 0.1.2-beta.3 — Pierwsze poprawki UX **← obecnie**",
    "### 0.1.2-beta.3 — Pierwsze poprawki UX **✓ ukończono**",
)
replace_once(
    roadmap,
    "- [ ] potwierdzenie poprawki na fizycznym iPhonie w publicznym PWA.",
    "- [x] potwierdzenie poprawki na fizycznym iPhonie w publicznym PWA.",
)
replace_once(
    roadmap,
    """**Zgłoszenie:** [issue #29](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/29).

### 0.1.3 — Dostępność i ergonomia
""",
    """**Zgłoszenie:** [issue #29](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/29).

### 0.1.3-beta.1 — Kontekstowa instalacja PWA **← obecnie**

- [x] przycisk „Dodaj do ekranu głównego” pod nagłówkiem na urządzeniach mobilnych;
- [x] wykrywanie iPhone'a, iPada, Androida i trybu `standalone`;
- [x] natywny prompt instalacji na obsługiwanych przeglądarkach Androida;
- [x] instrukcja ręczna na Androidzie, gdy prompt nie jest dostępny;
- [x] instrukcja Safari na iOS i iPadOS z czytelną ikoną „Udostępnij”;
- [x] informacja o konieczności użycia Safari w innych przeglądarkach iOS;
- [x] automatyczne ukrycie zachęty w zainstalowanej wersji PWA;
- [x] „Nie teraz” zapisujące lokalne odroczenie na 30 dni;
- [x] aktualizacja informacji o prywatności;
- [x] osobny produkcyjny build Flutter Web w CI;
- [x] testy widgetowe wszystkich ścieżek instalacji i ukrywania komunikatu;
- [ ] test instalacji natywnej na co najmniej jednym urządzeniu z Androidem;
- [ ] końcowe potwierdzenie instrukcji na fizycznym iPhonie po wdrożeniu.

**Zgłoszenie:** [issue #32](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/32).

### 0.1.3 — Dostępność i ergonomia
""",
)

changelog = Path("CHANGELOG.md")
old_unreleased = """## [Unreleased]

### Dodano

- licencję MIT z oznaczeniem praw autorskich `Copyright (c) 2026 M W`;
- odnośnik do licencji i informację `© 2026 M W · MIT License` w stopce aplikacji;
- test regresji odnośnika licencyjnego w stopce.

### Zmieniono

- sekcję licencyjną README, która teraz opisuje warunki używania projektu i odsyła do pliku `LICENSE`.

"""
new_unreleased = """## [Unreleased]

## [0.1.3-beta.1] — 2026-08-04

### Dodano

- kontekstowy przycisk „Dodaj do ekranu głównego” pod nagłówkiem kalkulatora;
- wykrywanie iOS, iPadOS, Androida, rodziny przeglądarki oraz trybu `standalone`;
- obsługę zdarzeń `beforeinstallprompt` i `appinstalled` dla natywnej instalacji na Androidzie;
- instrukcję instalacji na iPhonie i iPadzie z graficzną ikoną „Udostępnij”;
- instrukcję ręczną na Androidzie, gdy systemowy prompt nie jest dostępny;
- lokalną opcję „Nie teraz”, która odracza zachętę na 30 dni;
- produkcyjny build i walidację Flutter Web jako osobny etap CI;
- testy widgetowe instalacji, odroczenia i ukrywania zachęty w trybie `standalone`;
- licencję MIT z oznaczeniem praw autorskich `Copyright (c) 2026 M W`;
- odnośnik do licencji i informację `© 2026 M W · MIT License` w stopce aplikacji.

### Zmieniono

- nazwę instalowanej aplikacji i metadane manifestu PWA na `InfusionCalc`;
- service worker, aby przechowywał skrypt obsługi instalacji w pamięci offline;
- sekcję prywatności o lokalne przechowywanie daty odroczenia komunikatu;
- sekcję licencyjną README, która opisuje warunki MIT i odsyła do pliku `LICENSE`.

### Granice

- brak zmian w solverze, równaniach, jednostkach i polityce precyzji;
- wykrywanie platformy służy wyłącznie lokalnemu dobraniu instrukcji instalacji;
- dane z formularza nadal nie są zapisywane ani wysyłane.

"""
replace_once(changelog, old_unreleased, new_unreleased)
