from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    if old not in source:
        raise SystemExit(f"Expected block not found in {path}: {old[:180]!r}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


readme = Path("README.md")
replace_once(
    readme,
    "Zmiana dotyczy wyłącznie prezentacji i nie wpływa na dokładne wartości używane przez solver.\n\n## Uruchomienie projektu",
    """Zmiana dotyczy wyłącznie prezentacji i nie wpływa na dokładne wartości używane przez solver.

## Pierwsza wewnętrzna beta na iPhone

Wersja `0.1.2-beta.1+13` jest pierwszym wydaniem przeznaczonym do testów na fizycznym iPhonie. Nie dodaje nowych funkcji kalkulatora — zamraża sprawdzony zakres i przygotowuje powtarzalny proces instalacji.

GitHub Actions na runnerze macOS buduje aplikację urządzeniową w trybie `release` z wyłączonym code signing i publikuje niepodpisane IPA jako artifact. Podpis darmowym Apple ID oraz instalacja odbywają się lokalnie na Windowsie przez Sideloadly. Żadne hasło Apple ID, kod 2FA, certyfikat ani profil provisioning nie trafiają do repozytorium lub GitHub Secrets.

Darmowy profil Apple wygasa po 7 dniach, dlatego aplikację trzeba okresowo podpisać ponownie albo odświeżać przez Sideloadly Daemon. Nie jest to TestFlight ani publikacja w App Store.

Dystrybucję instalacyjną Androida odłożono. Istniejący build kontrolny Androida może pozostać w CI jako zabezpieczenie wieloplatformowości, ale ten etap nie tworzy wydania APK.

## Uruchomienie projektu""",
)
replace_once(
    readme,
    "- [Polityka precyzji i formatowania wyniku](docs/DISPLAY_PRECISION_POLICY.md)",
    """- [Polityka precyzji i formatowania wyniku](docs/DISPLAY_PRECISION_POLICY.md)
- [Instalacja na iPhonie darmowym Apple ID](docs/IOS_FREE_APPLE_ID_INSTALL.md)
- [Zakres pierwszej wewnętrznej bety iOS](docs/IOS_INTERNAL_BETA_0.1.2.md)""",
)
replace_once(
    readme,
    "**Wersja rozwojowa:** `0.1.2-dev.2+12` — audyt precyzji warstwy prezentacji  ",
    "**Wersja testowa:** `0.1.2-beta.1+13` — pierwsza wewnętrzna beta na iPhone  ",
)
replace_once(
    readme,
    "**Platformy docelowe:** iOS i Android  \n**Model działania:** offline-first",
    """**Platformy docelowe:** iOS i Android  
**Bieżąca dystrybucja:** niepodpisane IPA z GitHub Actions, podpis lokalny darmowym Apple ID  
**Android:** wydanie instalacyjne odłożone  
**Model działania:** offline-first""",
)

changelog = Path("CHANGELOG.md")
replace_once(
    changelog,
    "## [0.1.2-dev.2] — w przygotowaniu\n",
    """## [0.1.2-beta.1] — w przygotowaniu

### Dodano

- ręcznie uruchamiany workflow `iOS unsigned device build` na runnerze macOS;
- urządzeniowy build iOS `release` z wyłączonym code signing;
- pakowanie `Payload/Runner.app` do niepodpisanego IPA dla fizycznego iPhone'a;
- stały bazowy bundle ID `pl.kalkulatorlekow.technicalcalculator`;
- artifact z IPA, sumą SHA-256 i metadanymi wersji, commitu oraz architektury;
- instrukcję podpisania darmowym Apple ID i instalacji na iPhonie z Windowsa przez Sideloadly;
- dokument zakresu pierwszych testów na fizycznym urządzeniu.

### Bezpieczeństwo procesu

- workflow nie przyjmuje ani nie przechowuje danych Apple ID;
- w repozytorium i GitHub Secrets nie są wymagane certyfikaty ani profile provisioning;
- podpis następuje lokalnie na komputerze użytkownika;
- artifact jest jawnie opisany jako niepodpisany;
- wydanie pozostaje technicznym kalkulatorem bez rekomendacji i interpretacji klinicznej.

### Ograniczenia

- darmowy profil Apple wygasa po 7 dniach i wymaga ponownego podpisania lub odświeżenia;
- brak TestFlight i App Store;
- Sideloadly jest narzędziem zewnętrznym, niezależnym od Apple i projektu;
- dystrybucję instalacyjną Androida odłożono.

## [0.1.2-dev.2] — 2026-08-03
""",
)

roadmap = Path("ROADMAP.md")
replace_once(
    roadmap,
    "**Aktualny etap:** `0.1.2-dev.2 — audyt precyzji warstwy prezentacji`",
    "**Aktualny etap:** `0.1.2-beta.1 — pierwsze testy na fizycznym iPhonie`",
)
replace_once(
    roadmap,
    "### 0.1.2 — Audyt domeny i precyzji **← obecnie**",
    "### 0.1.2 — Audyt domeny i precyzji **✓ audyt automatyczny ukończony**",
)
replace_once(
    roadmap,
    "### 0.1.3 — Dostępność i ergonomia\n",
    """### 0.1.2-beta.1 — Pierwsza wewnętrzna beta iOS **← obecnie**

- [x] wersja `0.1.2-beta.1+13`;
- [x] automatyczny build urządzeniowy iOS na runnerze macOS;
- [x] niepodpisane IPA publikowane jako GitHub Actions artifact;
- [x] suma SHA-256 i metadane buildu;
- [x] stały bazowy bundle ID;
- [x] brak danych Apple ID i materiałów podpisujących w GitHubie;
- [x] instrukcja lokalnego podpisania darmowym Apple ID na Windowsie;
- [x] dystrybucja instalacyjna Androida odłożona;
- [ ] poprawny przebieg workflow na `main`;
- [ ] podpisanie IPA i instalacja na fizycznym iPhonie;
- [ ] uruchomienie podstawowych scenariuszy testowych na urządzeniu;
- [ ] zebranie pierwszych uwag UX przed rozpoczęciem kolejnych funkcji.

**Model dystrybucji:** GitHub Actions tworzy niepodpisane IPA, a Sideloadly lokalnie tworzy 7-dniowy podpis Personal Team i instaluje aplikację.

**Dokumentacja:** [`docs/IOS_FREE_APPLE_ID_INSTALL.md`](docs/IOS_FREE_APPLE_ID_INSTALL.md) i [`docs/IOS_INTERNAL_BETA_0.1.2.md`](docs/IOS_INTERNAL_BETA_0.1.2.md).

### 0.1.3 — Dostępność i ergonomia
""",
)
