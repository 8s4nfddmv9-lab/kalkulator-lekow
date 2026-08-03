# Wdrożenie InfusionCalc

## Główna ścieżka — GitHub Pages

Publiczna wersja InfusionCalc jest wdrażana automatycznie z gałęzi `main` przez workflow:

```text
.github/workflows/github-pages.yml
```

Adres produkcyjny:

```text
https://infusioncalc.eu/
```

Każda zmiana aplikacji scalona do `main`, która spełnia filtry workflow, uruchamia produkcyjny build Flutter Web i wdrożenie na GitHub Pages. Ta ścieżka jest domyślną oraz wspieraną metodą publikacji.

Aplikacja jest statycznym PWA. Obliczenia wykonują się lokalnie w przeglądarce; GitHub Pages dostarcza wyłącznie pliki aplikacji.

## Archiwalne ścieżki alternatywne

Poniższe warianty pozostają w repozytorium wyłącznie do ręcznych testów lub awaryjnego użycia. Nie uruchamiają się automatycznie po zmianach w `main`.

### Mini-PC, Docker, Caddy i Tailscale

Workflow:

```text
.github/workflows/web-pwa.yml
```

Instrukcja historyczna:

```text
docs/WEB_PWA_MINI_PC.md
```

Ten wariant buduje kontener PWA przeznaczony do ręcznego uruchomienia na mini-PC. Nie jest główną metodą hostowania publicznej aplikacji.

### Niepodpisane IPA dla iPhone'a

Workflow:

```text
.github/workflows/ios-unsigned-device-build.yml
```

Instrukcje historyczne:

```text
docs/IOS_FREE_APPLE_ID_INSTALL.md
docs/IOS_INTERNAL_BETA_0.1.2.md
```

Ten wariant pozostaje ręcznym narzędziem technicznym. Publiczna wersja InfusionCalc jest dystrybuowana jako PWA i nie wymaga podpisywania aplikacji Apple ID.

## Zasada utrzymania

- GitHub Pages jest jedyną automatyczną ścieżką wdrożenia publicznego.
- Alternatywne workflow uruchamia się wyłącznie ręcznie przez `workflow_dispatch`.
- Zmiany w silniku kalkulatora przechodzą standardowe testy niezależnie od sposobu dystrybucji.
- Przywrócenie którejkolwiek archiwalnej ścieżki jako automatycznej wymaga osobnej decyzji i osobnego PR.
