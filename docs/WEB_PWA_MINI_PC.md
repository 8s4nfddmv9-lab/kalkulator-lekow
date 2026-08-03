# Kalkulator leków jako PWA na mini-PC

## Cel

Ta ścieżka uruchamia tę samą aplikację Flutter jako prywatną aplikację webową instalowaną na ekranie początkowym iPhone'a.

Architektura:

```text
GitHub main
  → Flutter web release
  → obraz Caddy w GitHub Container Registry
  → Docker na mini-PC, port 127.0.0.1:8080
  → Tailscale Serve z prywatnym HTTPS
  → Safari na iPhonie
  → Dodaj do ekranu początkowego
```

Aplikacja pozostaje technicznym kalkulatorem. Nie zawiera biblioteki leków, zaleceń dawkowania ani interpretacji klinicznej.

## Co działa lokalnie

Wszystkie obliczenia wykonuje kod uruchomiony w przeglądarce. Mini-PC serwuje wyłącznie statyczne pliki aplikacji. Dane wpisywane w formularzu nie są wysyłane do backendu, ponieważ backend nie istnieje.

Zapisywane są wyłącznie lokalne preferencje interfejsu obsługiwane przez przeglądarkę. Aplikacja nie zapisuje masy, dawek ani wyników.

## Wymagania mini-PC

- Linux;
- Docker Engine z pluginem Docker Compose;
- Tailscale zalogowany do tego samego tailnetu co iPhone;
- dostęp do GitHub Container Registry, jeżeli pakiet pozostaje prywatny.

## 1. Przygotowanie katalogu

```bash
sudo mkdir -p /opt/kalkulator-lekow
sudo chown "$USER":"$USER" /opt/kalkulator-lekow
cd /opt/kalkulator-lekow
```

Skopiuj do tego katalogu plik `deploy/web/compose.yaml` z repozytorium.

## 2. Dostęp do prywatnego obrazu GHCR

Repozytorium jest prywatne, więc obraz kontenera może również pozostać prywatny. Utwórz token GitHub z minimalnym uprawnieniem `read:packages`, a następnie na mini-PC wykonaj:

```bash
export GHCR_USER="8s4nfddmv9-lab"
read -s GHCR_TOKEN
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
unset GHCR_TOKEN
```

Alternatywnie pakiet `kalkulator-lekow-web` można później oznaczyć w GitHub Packages jako publiczny. Wtedy logowanie na mini-PC nie będzie potrzebne.

## 3. Uruchomienie kontenera

W katalogu zawierającym `compose.yaml`:

```bash
docker compose pull
docker compose up -d
docker compose ps
curl -I http://127.0.0.1:8080/
```

Kontener nasłuchuje wyłącznie na `127.0.0.1:8080`. Nie jest bezpośrednio wystawiony do sieci lokalnej ani internetu.

Aktualizacja po opublikowaniu nowej wersji:

```bash
cd /opt/kalkulator-lekow
docker compose pull
docker compose up -d
docker image prune -f
```

## 4. Prywatny HTTPS przez Tailscale Serve

W panelu administracyjnym Tailscale włącz certyfikaty HTTPS dla tailnetu. Następnie na mini-PC:

```bash
sudo tailscale serve --bg http://127.0.0.1:8080
tailscale serve status
```

Tailscale pokaże prywatny adres w domenie `*.ts.net`, na przykład:

```text
https://mini-pc.nazwa-tailnetu.ts.net/
```

Adres jest dostępny tylko dla urządzeń dopuszczonych do tailnetu. Nie używamy Tailscale Funnel, ponieważ aplikacja nie ma być publiczna.

Wyłączenie udostępnienia:

```bash
sudo tailscale serve reset
```

## 5. iPhone

1. Zainstaluj aplikację Tailscale z App Store i zaloguj iPhone do tego samego tailnetu.
2. Włącz połączenie Tailscale.
3. Otwórz w Safari adres `https://...ts.net/` pokazany przez `tailscale serve status`.
4. Sprawdź podstawowe obliczenie.
5. Dotknij przycisku udostępniania w Safari.
6. Wybierz **Dodaj do ekranu początkowego**.
7. Zatwierdź nazwę **Kalkulator leków**.

Ikona uruchamia aplikację w trybie `standalone`, bez typowego paska adresu Safari.

## 6. Pierwszy test offline

1. Otwórz aplikację przynajmniej raz przy aktywnym połączeniu.
2. Poczekaj kilka sekund, aby service worker zapisał zasoby.
3. Zamknij aplikację z przełącznika aplikacji.
4. Wyłącz Wi-Fi, internet komórkowy i Tailscale.
5. Uruchom ikonę ponownie.
6. Sprawdź scenariusz:

```text
masa: 70 kg
ilość: 4 mg
objętość: 50 ml
dawka: 0,1 µg/kg/min
oczekiwany przepływ: 5,25 ml/h
```

Pierwsze otwarcie zawsze wymaga połączenia z mini-PC. Dalsze uruchomienia powinny działać offline po zapisaniu zasobów.

## Aktualizacje i cache

Każdy build otrzymuje osobny identyfikator cache oparty na commicie Git. Nowy service worker usuwa poprzednie cache aplikacji po aktywacji.

Pliki startowe i service worker są serwowane z nagłówkami `no-cache`, aby Safari sprawdzało dostępność aktualizacji. Pozostałe zasoby są przechowywane lokalnie przez service worker na potrzeby pracy offline.

Po wdrożeniu nowej wersji:

1. odśwież aplikację przy aktywnym Tailscale;
2. zamknij ją całkowicie;
3. uruchom ponownie z ikony.

Jeżeli Safari zachowuje starszą wersję, usuń skrót z ekranu początkowego, wyczyść dane witryny dla domeny `ts.net`, otwórz stronę ponownie i dodaj skrót jeszcze raz.

## GitHub Actions

Workflow `.github/workflows/web-pwa.yml`:

- generuje deterministyczne ikony PWA;
- wykonuje `flutter build web --release`;
- wersjonuje service worker identyfikatorem commitu;
- waliduje wymagane pliki PWA;
- publikuje artifact `kalkulator-lekow-web-*`;
- buduje kontener Caddy;
- po zmianie na `main` publikuje obrazy:

```text
ghcr.io/8s4nfddmv9-lab/kalkulator-lekow-web:latest
ghcr.io/8s4nfddmv9-lab/kalkulator-lekow-web:sha-<commit>
```

Na pull requestach obraz jest tylko budowany kontrolnie i nie jest publikowany.

## Kopia zapasowa i wycofanie wersji

Aby wrócić do konkretnego obrazu:

```yaml
services:
  kalkulator-lekow-web:
    image: ghcr.io/8s4nfddmv9-lab/kalkulator-lekow-web:sha-PEŁNY_COMMIT
```

Następnie:

```bash
docker compose pull
docker compose up -d
```

## Ograniczenia

- instalacja PWA wymaga pierwszego otwarcia w Safari;
- zachowanie cache zależy od polityki iOS dotyczącej pamięci witryn;
- PWA nie korzysta z natywnych funkcji takich jak HealthKit;
- aktualizacja nie jest natychmiastowa, dopóki Safari nie pobierze nowego service workera;
- dostęp z zewnątrz wymaga aktywnego Tailscale, chyba że aplikacja została wcześniej zapisana i jest używana offline;
- ta dystrybucja nie zmienia przeznaczenia produktu ani zakresu walidacji.
