# Pełny tryb offline PWA — InfusionCalc

## Cel

Publiczna wersja InfusionCalc może działać bez internetu po co najmniej jednym pełnym uruchomieniu online. Tryb offline obejmuje cały techniczny kalkulator: pola, jednostki, solver, walidację, szczegóły obliczeń, ustawienia prezentacji, ostrzeżenie i lokalne okno prywatności.

Pierwsze pobranie aplikacji oraz pobranie każdej nowej wersji wymagają połączenia z internetem.

## Jak przygotowywana jest wersja offline

Po produkcyjnym buildzie Flutter Web skrypt `tool/finalize_web_pwa.py`:

1. zbiera wszystkie lokalne pliki znajdujące się w `build/web`;
2. uwzględnia kod aplikacji, bootstrap Fluttera, assety, fonty, ikony i pliki renderera obecne w danym buildzie;
3. zapisuje audytowalny `offline-manifest.json`;
4. wstrzykuje tę samą, dokładną listę do `pwa_service_worker.js`;
5. tworzy osobny cache o nazwie zawierającej identyfikator buildu;
6. sprawdza, czy manifest odpowiada dokładnie zawartości produkcyjnego artefaktu.

Service worker nie przechowuje własnego skryptu w cache. Przeglądarka pobiera go niezależnie podczas sprawdzania aktualizacji.

## Instalacja atomowa

Podczas instalacji nowej wersji service worker pobiera wszystkie pliki z wymuszeniem odświeżenia pamięci HTTP. Nowa wersja zostaje aktywowana dopiero po pomyślnym zapisaniu całego zestawu.

Jeżeli choć jeden wymagany plik jest niedostępny:

- instalacja nowej wersji kończy się niepowodzeniem;
- niekompletny cache jest usuwany;
- poprzednia kompletna wersja pozostaje dostępna;
- bieżące obliczenia nie są przerywane.

## Strategia odczytu

Nawigacja i lokalne zasoby korzystają ze strategii `versioned-cache-first`:

- dokument główny jest odczytywany z `index.html` zapisanej dla tej samej wersji;
- skrypt `main.dart.js`, assety, fonty i renderer są odczytywane z tego samego cache;
- aplikacja nie łączy dokumentu jednej wersji z kodem albo assetami innego wydania;
- gdy cache nie zawiera żądanego pliku i internet jest dostępny, przeglądarka może użyć odpowiedzi sieciowej.

## Aktualizacje

Rejestracja service workera używa `updateViaCache: none`. Po pełnym uruchomieniu online oraz po odzyskaniu połączenia aplikacja prosi przeglądarkę o sprawdzenie aktualizacji.

Nowa paczka jest pobierana w tle. Bieżąca sesja formularza nie jest automatycznie przeładowywana. Nowy service worker czeka, aż wszystkie otwarte okna i karty InfusionCalc zostaną zamknięte; dopiero później aktywuje nową, kompletną wersję. Zapobiega to przejęciu aktywnego formularza w trakcie obliczeń.

## Analityka offline

Umami Cloud nie jest potrzebne do działania kalkulatora. Zewnętrzny skrypt Umami nie jest częścią lokalnej paczki aplikacji.

W trybie offline:

- kalkulator działa normalnie;
- nie są wysyłane odsłony ani zdarzenia;
- zdarzenia nie są utrwalane na później;
- ograniczona kolejka analityki istnieje tylko w pamięci bieżącej strony i jest porzucana, jeżeli tracker pozostaje niedostępny.

## Dane lokalne

Cache offline zawiera wyłącznie publiczny kod i statyczne zasoby aplikacji. Nie zawiera:

- masy pacjenta;
- ilości leku;
- objętości;
- stężenia;
- przepływu;
- dawki;
- wyników;
- wzorów z bieżącego obliczenia;
- historii obliczeń;
- danych identyfikujących pacjenta.

Niezależnie od cache aplikacja zapisuje lokalnie tylko wybrane jednostki, tryb `/kg` i datę odroczenia zachęty do instalacji PWA.

## Funkcje wymagające internetu

Bez połączenia mogą nie otworzyć się odnośniki prowadzące poza aplikację:

- Changelog w GitHub;
- repozytorium GitHub;
- Contact / issue feedbackowe;
- internetowy plik licencji MIT.

Brak dostępu do tych stron nie wpływa na kalkulator. Ostrzeżenie techniczne i skrócona informacja Privacy są częścią lokalnego interfejsu.

## Test ręczny — iPhone lub iPad

1. Po wdrożeniu nowej wersji połącz urządzenie z internetem.
2. Otwórz `https://infusioncalc.eu/` bezpośrednio w Safari.
3. Poczekaj, aż formularz w pełni się uruchomi, a następnie pozostaw stronę otwartą jeszcze przez kilkanaście sekund.
4. Dodaj InfusionCalc do ekranu głównego albo — jeżeli ikona już istnieje — uruchom ją raz online i ponownie zamknij.
5. Zamknij aplikację z widoku ostatnio używanych aplikacji oraz zamknij inne karty Safari otwarte na `infusioncalc.eu`, aby oczekująca kompletna wersja mogła się aktywować.
6. Włącz tryb samolotowy i wyłącz Wi‑Fi.
7. Uruchom InfusionCalc z ikony na ekranie głównym.
8. Wykonaj kontrolne obliczenie, np. `4 mg + 50 ml → 80 µg/ml`.
9. Sprawdź zmianę jednostki, przełącznik `/kg`, ostrzeżenie i lokalne Privacy.
10. Przywróć internet i uruchom aplikację ponownie, aby umożliwić sprawdzenie aktualizacji.

## Test ręczny — Android

1. Otwórz `https://infusioncalc.eu/` w Chrome lub innej obsługiwanej przeglądarce.
2. Poczekaj na pełne uruchomienie i zakończenie przygotowywania cache.
3. Zainstaluj PWA przez systemowy prompt lub menu przeglądarki.
4. Uruchom aplikację raz online i zamknij ją oraz inne otwarte karty `infusioncalc.eu`.
5. Włącz tryb samolotowy oraz wyłącz Wi‑Fi.
6. Uruchom InfusionCalc z ikony i wykonaj kontrolne obliczenie.
7. Przywróć internet i ponownie uruchom aplikację.

## Ograniczenia systemowe

Przeglądarka lub system operacyjny może usunąć dane strony, szczególnie po:

- ręcznym wyczyszczeniu danych Safari lub Chrome;
- usunięciu PWA z ekranu głównego;
- dużej presji na pamięć urządzenia;
- długim okresie nieużywania aplikacji.

Po usunięciu danych potrzebne jest ponowne pełne uruchomienie online. Projekt nie może zagwarantować bezterminowego przechowywania cache przez system operacyjny.

## Automatyczna walidacja

CI uruchamia `tool/test_offline_pwa.py`, buduje produkcyjne Flutter Web i odrzuca artefakt, gdy:

- brakuje pliku krytycznego, w tym `main.dart.js`;
- dowolny plik z `build/web` nie znajduje się w manifeście;
- manifest zawiera plik nieistniejący lub zewnętrzny URL;
- lista nie jest unikalna i posortowana;
- build ID albo nazwa cache są niespójne;
- service worker nadal zawiera placeholder;
- worker nie używa atomowej instalacji i wersjonowanej strategii cache-first;
- konfiguracja aktualizacji service workera jest niekompletna.

Dodatkowo `tool/smoke_test_offline_pwa.py` uruchamia produkcyjny build w prawdziwym profilu Google Chrome przez ChromeDriver, czeka na zweryfikowanie wszystkich plików w cache, zamyka lokalny serwer, włącza ścisły tryb offline i potwierdza ponowne wyrenderowanie tej samej wersji aplikacji wyłącznie z service workera.

Dokument opisuje zachowanie techniczne. Nie zmienia deklarowanego przeznaczenia InfusionCalc jako technicznego kalkulatora bez zaleceń dawkowania i bez podejmowania decyzji klinicznych.
