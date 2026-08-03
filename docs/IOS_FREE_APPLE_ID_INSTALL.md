# Instalacja na iPhonie bez płatnego Apple Developer Program

Ten dokument opisuje wewnętrzne testowanie aplikacji na własnym iPhonie bez członkostwa w Apple Developer Program i bez posiadania komputera Mac.

## Wybrany model

Proces jest podzielony na dwa etapy:

1. **GitHub Actions na macOS** buduje aplikację Flutter dla fizycznego iPhone'a i tworzy niepodpisany plik `.ipa`.
2. **Sideloadly na Windowsie** podpisuje plik lokalnie darmowym Apple ID i instaluje go na podłączonym iPhonie.

GitHub nie otrzymuje hasła Apple ID, kodu 2FA, certyfikatu ani profilu provisioning. W repozytorium i GitHub Secrets nie należy umieszczać żadnych danych logowania Apple.

## Dlaczego podpis nie odbywa się w GitHub Actions

Darmowe konto Apple jest w Xcode oznaczane jako **Personal Team**. Apple zarządza jego App ID, urządzeniami, certyfikatami i profilami bezpośrednio w Xcode. Nie jest to standardowy kanał automatycznej dystrybucji ani TestFlight.

GitHub Actions może bezpiecznie i powtarzalnie utworzyć aplikację dla urządzenia z wyłączonym code signing. Podpis Personal Team jest następnie tworzony lokalnie w czasie instalacji.

Oficjalne informacje Apple:

- https://developer.apple.com/help/account/basics/about-your-developer-account
- https://developer.apple.com/support/compare-memberships/

## Ograniczenia darmowego Apple ID

Według Apple dla Personal Team obowiązują między innymi:

- profil instalacyjny wygasa po **7 dniach**;
- po wygaśnięciu aplikację trzeba ponownie podpisać i zainstalować;
- maksymalnie 3 takie aplikacje na jednym urządzeniu;
- maksymalnie 10 aktywnych App ID;
- maksymalnie 3 zarejestrowane urządzenia w tym trybie;
- brak TestFlight i publikacji w App Store.

Ponowne podpisanie tym samym Apple ID i z tym samym bundle ID może nadpisać istniejącą instalację. Aplikacja nie zapisuje wartości formularza ani historii, więc wygaśnięcie nie powoduje utraty danych klinicznych.

## 1. Zbudowanie IPA w GitHub Actions

1. Otwórz repozytorium `kalkulator-lekow` na GitHubie.
2. Wejdź w zakładkę **Actions**.
3. Wybierz workflow **iOS unsigned device build**.
4. Kliknij **Run workflow** i wybierz gałąź `main`.
5. Po zakończeniu otwórz wykonanie zakończone zielonym statusem.
6. W sekcji **Artifacts** pobierz plik o nazwie podobnej do:

   ```text
   kalkulator-lekow-ios-unsigned-123
   ```

7. Rozpakuj pobrane archiwum ZIP. W środku znajdują się:

   ```text
   Kalkulator-Lekow-<wersja>-unsigned.ipa
   Kalkulator-Lekow-<wersja>-unsigned.ipa.sha256
   ios-build-info.txt
   ```

Plik `.sha256` pozwala sprawdzić integralność IPA, a `ios-build-info.txt` zawiera wersję, commit, bundle ID i architekturę.

### Opcjonalne sprawdzenie sumy SHA-256 w PowerShell

W katalogu z plikiem IPA uruchom:

```powershell
Get-FileHash .\Kalkulator-Lekow-*-unsigned.ipa -Algorithm SHA256
Get-Content .\Kalkulator-Lekow-*-unsigned.ipa.sha256
```

Obie wartości SHA-256 powinny być identyczne.

## 2. Przygotowanie Windowsa

Sideloadly jest narzędziem zewnętrznym, nie jest produktem Apple ani częścią projektu. Przed użyciem należy samodzielnie zaakceptować jego model działania i politykę prywatności.

Oficjalna strona projektu:

- https://sideloadly.io/
- https://sideloadly.io/faq.html
- https://sideloadly.io/privacy

Na Windowsie Sideloadly wymaga internetowych wersji iTunes i iCloud ze strony Apple, a nie wydań z Microsoft Store.

1. Jeżeli masz wersje iTunes lub iCloud z Microsoft Store, odinstaluj je.
2. Zainstaluj wersje wskazane na stronie Sideloadly:
   - Web iTunes 64-bit;
   - Web iCloud.
3. Zainstaluj najnowszą wersję Sideloadly.
4. Uruchom ponownie komputer, jeżeli instalator lub sterowniki Apple tego wymagają.

## 3. Podłączenie iPhone'a

1. Podłącz iPhone do komputera przewodem USB.
2. Odblokuj telefon.
3. Na iPhonie wybierz **Zaufaj temu komputerowi**.
4. W razie potrzeby otwórz iTunes i potwierdź, że urządzenie jest widoczne.
5. Uruchom Sideloadly i upewnij się, że właściwy iPhone jest wybrany na liście urządzeń.

Pierwsza instalacja powinna zostać wykonana przez USB. Później można skonfigurować odświeżanie przez Wi-Fi.

## 4. Podpisanie i instalacja

1. Przeciągnij plik `Kalkulator-Lekow-...-unsigned.ipa` do okna Sideloadly.
2. Wybierz podłączony iPhone.
3. Wprowadź Apple ID używane do darmowego podpisu.
4. Kliknij **Start**.
5. Potwierdź logowanie i kod uwierzytelniania dwuskładnikowego, gdy zostanie wyświetlony.
6. Poczekaj na komunikat o zakończonej instalacji.

Nie zapisuj Apple ID ani hasła w repozytorium, pliku konfiguracyjnym projektu, GitHub Secrets ani zgłoszeniu błędu. Opcjonalnie można używać osobnego Apple ID przeznaczonego wyłącznie do prywatnego sideloadingu.

## 5. Ustawienia na iPhonie

### Developer Mode

Od iOS 16 aplikacje instalowane poza App Store wymagają Developer Mode:

```text
Ustawienia
→ Prywatność i ochrona
→ Tryb deweloperski
→ Włącz
```

Telefon poprosi o ponowne uruchomienie i potwierdzenie.

### Zaufanie profilowi

Jeżeli iOS pokaże komunikat o niezaufanym deweloperze:

```text
Ustawienia
→ Ogólne
→ VPN i zarządzanie urządzeniem
→ profil z użytym Apple ID
→ Zaufaj
```

Nazwy pozycji mogą nieznacznie różnić się zależnie od wersji iOS i języka systemu.

## 6. Odświeżanie co 7 dni

Darmowy profil wygasa po 7 dniach. Dostępne są dwa sposoby:

### Ręczne

Ponownie przeciągnij tę samą IPA do Sideloadly, użyj tego samego Apple ID i tego samego bundle ID, a następnie zainstaluj aplikację ponownie.

### Automatyczne

Sideloadly Daemon może odnawiać podpis przed wygaśnięciem, gdy:

- komputer jest uruchomiony;
- iPhone jest podłączony przez USB albo poprawnie sparowany przez Wi-Fi;
- komputer i telefon znajdują się w tej samej sieci przy odświeżaniu bezprzewodowym.

Instrukcja Wi-Fi znajduje się w FAQ Sideloadly. Pierwsze sparowanie nadal wymaga przewodu USB.

## 7. Aktualizacja aplikacji

Po każdej nowej wersji:

1. uruchom workflow ponownie;
2. pobierz nowy artifact;
3. sprawdź sumę SHA-256;
4. zainstaluj nową IPA przez Sideloadly tym samym Apple ID.

Użycie tego samego Apple ID i niezmienionego bundle ID powinno zastąpić poprzednią instalację zamiast tworzyć drugą ikonę.

Stały bundle ID przygotowanego buildu:

```text
pl.kalkulatorlekow.technicalcalculator
```

Sideloadly może zmodyfikować bundle ID zgodnie z ograniczeniami darmowego konta. Przy kolejnych instalacjach należy zachować ten sam identyfikator wygenerowany przez narzędzie.

## 8. Co workflow rzeczywiście gwarantuje

Workflow:

- buduje tryb `release` dla fizycznego urządzenia i architektury arm64;
- nie podpisuje aplikacji;
- nie przechowuje żadnych danych Apple;
- tworzy poprawną strukturę IPA z `Payload/Runner.app`;
- sprawdza integralność archiwum;
- zapisuje sumę SHA-256 i metadane buildu;
- przechowuje artifact przez 30 dni.

Nie gwarantuje działania po podpisaniu na każdym urządzeniu i każdej wersji iOS. Ostateczny test odbywa się na fizycznym iPhonie.

## 9. Najczęstsze problemy

### Sideloadly nie widzi iPhone'a

- odblokuj telefon i zaakceptuj zaufanie;
- otwórz iTunes;
- zmień przewód lub port USB;
- sprawdź, czy zainstalowano internetowe wersje iTunes oraz iCloud;
- uruchom ponownie komputer i telefon.

### Developer Mode Required

Włącz Tryb deweloperski w `Ustawienia → Prywatność i ochrona` i uruchom ponownie iPhone.

### Untrusted Developer

Zaufaj profilowi w `Ustawienia → Ogólne → VPN i zarządzanie urządzeniem`.

### Aplikacja przestała się uruchamiać po kilku dniach

Najprawdopodobniej wygasł 7-dniowy profil. Podpisz i zainstaluj aplikację ponownie albo skonfiguruj automatyczne odświeżanie.

### Limit App ID lub limit trzech aplikacji

To ograniczenie darmowego konta Apple. Usuń niepotrzebne aplikacje sideloadowane lub poczekaj na wygaśnięcie tygodniowego limitu App ID.

## Granica bezpieczeństwa

Ta instalacja jest przeznaczona wyłącznie do wewnętrznych testów technicznych. Aplikacja pozostaje kalkulatorem matematycznym i jednostkowym bez biblioteki leków, zaleceń dawkowania i interpretacji klinicznej. Wynik powinien być niezależnie weryfikowany podczas testów.
