from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    if old not in source:
        raise SystemExit(f"Expected block not found in {path}: {old[:180]!r}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


readme = Path("README.md")
replace_once(
    readme,
    "# Kalkulator leków\n\nMobilna aplikacja na iOS i Android służąca do szybkiego, dwukierunkowego przeliczania parametrów podaży leków we wlewie ciągłym.\n",
    "# InfusionCalc\n\nPublicznie dostępna aplikacja PWA do szybkiego, dwukierunkowego przeliczania parametrów podaży leków we wlewie ciągłym. Działa w przeglądarce na telefonie, tablecie i komputerze oraz może zostać dodana do ekranu początkowego.\n\n**Wersja publiczna:** [https://infusioncalc.eu/](https://infusioncalc.eu/)\n",
)
replace_once(
    readme,
    "## Pierwsza wewnętrzna beta na iPhone\n\nWersja `0.1.2-beta.1+13` jest pierwszym wydaniem przeznaczonym do testów na fizycznym iPhonie. Nie dodaje nowych funkcji kalkulatora — zamraża sprawdzony zakres i przygotowuje powtarzalny proces instalacji.\n\nGitHub Actions na runnerze macOS buduje aplikację urządzeniową w trybie `release` z wyłączonym code signing i publikuje niepodpisane IPA jako artifact. Podpis darmowym Apple ID oraz instalacja odbywają się lokalnie na Windowsie przez Sideloadly. Żadne hasło Apple ID, kod 2FA, certyfikat ani profil provisioning nie trafiają do repozytorium lub GitHub Secrets.\n\nDarmowy profil Apple wygasa po 7 dniach, dlatego aplikację trzeba okresowo podpisać ponownie albo odświeżać przez Sideloadly Daemon. Nie jest to TestFlight ani publikacja w App Store.\n\nDystrybucję instalacyjną Androida odłożono. Istniejący build kontrolny Androida może pozostać w CI jako zabezpieczenie wieloplatformowości, ale ten etap nie tworzy wydania APK.\n\n",
    "## Publiczna wersja PWA\n\nInfusionCalc jest publikowany automatycznie z gałęzi `main` przez GitHub Pages pod adresem [https://infusioncalc.eu/](https://infusioncalc.eu/). Jest to główna i wspierana ścieżka dystrybucji.\n\nAplikacja nie ma własnego backendu. Serwer dostarcza wyłącznie statyczne pliki, a obliczenia wykonują się lokalnie w przeglądarce. Manifest PWA i service worker umożliwiają dodanie aplikacji do ekranu początkowego oraz korzystanie z wcześniej załadowanej wersji bez aktywnego połączenia.\n\nHistoryczne warianty instalacji niepodpisanego IPA oraz hostowania na mini-PC pozostają w repozytorium jako ręczne, archiwalne ścieżki techniczne. Nie uruchamiają się automatycznie i nie są domyślną metodą korzystania z aplikacji. Szczegóły opisuje [`DEPLOYMENT.md`](DEPLOYMENT.md).\n\n",
)
replace_once(
    readme,
    "- **Flutter + Dart** — wspólna aplikacja na iOS i Android;",
    "- **Flutter + Dart** — jedna baza kodu dla publicznego PWA oraz kontrolnych targetów iOS i Android;",
)
replace_once(
    readme,
    "- [Instalacja na iPhonie darmowym Apple ID](docs/IOS_FREE_APPLE_ID_INSTALL.md)\n- [Zakres pierwszej wewnętrznej bety iOS](docs/IOS_INTERNAL_BETA_0.1.2.md)",
    "- [Wdrożenie i ścieżki dystrybucji](DEPLOYMENT.md)\n- [Prywatność](docs/PRIVACY.md)\n- [Feedback po pierwszych testach](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18)\n- [Archiwalna instalacja na iPhonie darmowym Apple ID](docs/IOS_FREE_APPLE_ID_INSTALL.md)\n- [Archiwalny zakres pierwszej bety iOS](docs/IOS_INTERNAL_BETA_0.1.2.md)\n- [Archiwalne wdrożenie mini-PC i Tailscale](docs/WEB_PWA_MINI_PC.md)",
)
replace_once(
    readme,
    "**Wersja testowa:** `0.1.2-beta.1+13` — pierwsza wewnętrzna beta na iPhone  \n**Ostatnie stabilne MVP:** `0.1.0+8`  \n**Charakter produktu:** techniczny kalkulator, bez zaleceń klinicznych  \n**Platformy docelowe:** iOS i Android  \n**Bieżąca dystrybucja:** niepodpisane IPA z GitHub Actions, podpis lokalny darmowym Apple ID  \n**Android:** wydanie instalacyjne odłożone  \n**Model działania:** offline-first",
    "**Wersja publiczna:** `0.1.2-beta.2+14` — publiczne PWA  \n**Adres:** [https://infusioncalc.eu/](https://infusioncalc.eu/)  \n**Ostatnie stabilne MVP:** `0.1.0+8`  \n**Charakter produktu:** techniczny kalkulator, bez zaleceń klinicznych  \n**Główna dystrybucja:** GitHub Pages / PWA  \n**Platformy:** Safari, Chrome i inne współczesne przeglądarki; kontrolne buildy iOS i Android  \n**Model działania:** offline-first, bez własnego backendu",
)

roadmap = Path("ROADMAP.md")
replace_once(roadmap, "# Roadmapa — Kalkulator leków", "# Roadmapa — InfusionCalc")
replace_once(
    roadmap,
    "**Aktualny etap:** `0.1.2-beta.1 — pierwsze testy na fizycznym iPhonie`",
    "**Aktualny etap:** `0.1.2-beta.2 — publiczne PWA i pierwsze testy użytkowe`",
)
replace_once(
    roadmap,
    "### 0.1.2-beta.1 — Pierwsza wewnętrzna beta iOS **← obecnie**",
    "### 0.1.2-beta.1 — Pierwsza wewnętrzna beta iOS **✓ ukończono i zarchiwizowano**",
)
replace_once(
    roadmap,
    "**Dokumentacja:** [`docs/IOS_FREE_APPLE_ID_INSTALL.md`](docs/IOS_FREE_APPLE_ID_INSTALL.md) i [`docs/IOS_INTERNAL_BETA_0.1.2.md`](docs/IOS_INTERNAL_BETA_0.1.2.md).\n\n### 0.1.3 — Dostępność i ergonomia",
    """**Dokumentacja archiwalna:** [`docs/IOS_FREE_APPLE_ID_INSTALL.md`](docs/IOS_FREE_APPLE_ID_INSTALL.md) i [`docs/IOS_INTERNAL_BETA_0.1.2.md`](docs/IOS_INTERNAL_BETA_0.1.2.md).

### 0.1.2-beta.2 — Publiczne PWA **← obecnie**

- [x] produkcyjny build Flutter Web;
- [x] manifest PWA, ikona i tryb `standalone`;
- [x] service worker i wersjonowany cache offline;
- [x] automatyczne wdrożenie przez GitHub Pages;
- [x] własna domena `https://infusioncalc.eu/`;
- [x] wymuszony HTTPS;
- [x] stopka `Changelog`, `Privacy`, `GitHub`, `Contact`;
- [x] centralne issue #18 do zbierania feedbacku;
- [x] archiwizacja automatycznych workflow mini-PC i niepodpisanego IPA;
- [ ] zebranie oraz klasyfikacja pierwszych uwag użytkowych;
- [ ] ręczny przegląd formularza na różnych modelach iPhone'a i iPada;
- [ ] decyzja o zakresie kolejnego wydania na podstawie feedbacku.

**Główna dystrybucja:** GitHub Pages jako publiczne PWA. Mini-PC/Tailscale oraz niepodpisane IPA pozostają wyłącznie ręcznymi ścieżkami archiwalnymi.

**Dokumentacja:** [`DEPLOYMENT.md`](DEPLOYMENT.md), [`docs/PRIVACY.md`](docs/PRIVACY.md) i [issue #18](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18).

### 0.1.3 — Dostępność i ergonomia""",
)

changelog = Path("CHANGELOG.md")
replace_once(
    changelog,
    "## [0.1.2-beta.1] — w przygotowaniu",
    """## [Unreleased]

### Dodano

- stopkę InfusionCalc z sekcjami `Changelog`, `Privacy`, `GitHub` i `Contact`;
- lokalny komunikat prywatności i dokument `docs/PRIVACY.md`;
- centralne issue #18 do zbierania feedbacku z pierwszych testów;
- dokument `DEPLOYMENT.md` opisujący wspieraną i archiwalne ścieżki wdrożenia.

### Zmieniono

- GitHub Pages i `https://infusioncalc.eu/` są główną ścieżką publicznej dystrybucji;
- workflow niepodpisanego IPA oraz mini-PC/Docker/Tailscale są oznaczone jako archiwalne i uruchamiane wyłącznie ręcznie.

### Jakość

- cały projekt: `151/151` testów;
- pokrycie liniowe `lib/domain/`: `93,99%` (`720/766` linii);
- poprawne buildy kontrolne Androida i iOS.

## [0.1.2-beta.2] — 2026-08-03

### Wydano

- publiczną wersję Flutter PWA;
- automatyczny deploy przez GitHub Pages;
- własną domenę `https://infusioncalc.eu/` z HTTPS;
- manifest instalacyjny, ikony i service worker z wersjonowanym cache offline.

## [0.1.2-beta.1] — 2026-08-03""",
)
