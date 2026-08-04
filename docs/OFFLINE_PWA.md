# Pełny tryb offline PWA — InfusionCalc

## Cel

Publiczna wersja InfusionCalc może działać bez internetu po co najmniej jednym pełnym uruchomieniu online. Tryb offline obejmuje cały techniczny kalkulator: pola, jednostki, solver, walidację, szczegóły obliczeń, ustawienia prezentacji, ostrzeżenie i lokalne okno prywatności.

Pierwsze pobranie aplikacji oraz pobranie każdej nowej wersji wymagają połączenia z internetem.

## Samowystarczalny runtime Fluttera

Produkcyjny build jest wykonywany z opcją `--no-web-resources-cdn`. Kod uruchamiający Fluttera, `main.dart.js`, lokalny CanvasKit, pliki WebAssembly, fonty, ikony i pozostałe assety pochodzą z tego samego originu `infusioncalc.eu`.

Domyślna konfiguracja Flutter Web może używać zewnętrznego CDN dla renderera. Taki build może pozornie przejść test offline w przeglądarce, jeżeli renderer pozostaje w zwykłym HTTP cache po uruchomieniu online, ale zawiedzie na czystej instalacji lub w Home Screen PWA bez internetu. Finalizer i test przeglądarkowy jawnie odrzucają tę zależność.

Umami Cloud pozostaje jedynym opcjonalnym skryptem zewnętrznym. Jego brak, blokada lub niedostępność nie wpływają na uruchomienie Fluttera ani obliczenia.

## Jak przygotowywana jest wersja offline

Po produkcyjnym buildzie Flutter Web skrypt `tool/finalize_web_pwa.py`:

1. zbiera wszystkie publiczne pliki znajdujące się w `build/web`;
2. uwzględnia kod aplikacji, bootstrap Fluttera, assety, fonty, ikony i pliki renderera obecne w danym buildzie;
3. pomija ukryte techniczne metadane buildu, takie jak `.last_build_id`, które nie są potrzebne aplikacji i mogą nie być publikowane przez statyczny hosting;
4. zapisuje audytowalny `offline-manifest.json`;
5. wstrzykuje tę samą, dokładną listę do `pwa_service_worker.js`;
6. tworzy osobny cache o nazwie zawierającej identyfikator buildu;
7. sprawdza, czy manifest odpowiada dokładnie publicznej zawartości produkcyjnego artefaktu.

Service worker nie przechowuje własnego skryptu w cache. Przeglądarka pobiera go niezależnie podczas sprawdzania aktualizacji.

## Instalacja atomowa

Podczas instalacji nowej wersji service worker pobiera wszystkie pliki z wymuszeniem odświeżenia pamięci HTTP. Nowa wersja może zostać aktywowana dopiero po pomyślnym zapisaniu całego zestawu.

Jeżeli choć jeden wymagany plik jest niedostępny:

- instalacja nowej wersji kończy się niepowodzeniem;
- niekompletny cache jest usuwany;
- poprzednia kompletna wersja pozostaje dostępna;
- bieżące obliczenia nie są przerywane.

Po poprawnym zapisaniu pełnego zestawu worker wywołuje `skipWaiting()`. Zapobiega to sytuacji, w której kompletna aktualizacja pozostaje bezterminowo w stanie `waiting`, ponieważ starszy worker nadal kontroluje kartę Safari albo aplikację z ekranu głównego.

## Aktywacja i istniejące okna

Podczas aktywacji worker:

1. usuwa cache poprzednich wersji InfusionCalc oraz historyczny cache sprzed migracji;
2. wywołuje `clients.claim()`;
3. przejmuje obsługę kolejnych żądań z już otwartych okien bez automatycznego przeładowania interfejsu.

Przejęcie kontroli nie czyści formularza i nie przeładowuje bieżącej strony. Nowy worker rozpoczyna działanie dopiero po pełnym, atomowym precache, dlatego nie powstaje okno z niekompletnym zestawem plików.

## Strategia odczytu

Nawigacja i lokalne zasoby korzystają ze strategii `versioned-cache-first`:

- dokument główny jest odczytywany z `index.html` zapisanej dla tej samej wersji;
- skrypt `main.dart.js`, lokalny CanvasKit, WebAssembly, assety i fonty są odczytywane z tego samego cache;
- aplikacja nie łączy dokumentu jednej wersji z kodem albo assetami innego wydania;
- uruchomienie kalkulatora nie wymaga połączenia z CDN Fluttera, Google Fonts ani innym zewnętrznym originem;
- zapytania i nagłówki `Vary` nie powodują przypadkowego pominięcia poprawnie zapisanego zasobu;
- gdy cache nie zawiera żądanego pliku i internet jest dostępny, przeglądarka może użyć odpowiedzi sieciowej.

## Aktualizacje

Rejestracja service workera używa `updateViaCache: none`. Po pełnym uruchomieniu online oraz po odzyskaniu połączenia aplikacja prosi przeglądarkę o sprawdzenie aktualizacji.

Nowa paczka jest pobierana w tle. Po pełnym zapisaniu zostaje aktywowana i przejmuje obsługę żądań, ale aplikacja nie przeładowuje automatycznie bieżącego formularza. Pełny interfejs nowego wydania jest widoczny po następnym uruchomieniu albo ręcznym przeładowaniu.

## Diagnostyka ekranu startowego

Jeżeli Flutter nie wyrenderuje pierwszej klatki w ciągu 20 sekund, ekran startowy nie pozostaje już bez końca na napisie „Uruchamianie InfusionCalc…”. Zamiast tego wyświetla instrukcję ponowienia oraz jeden z kodów:

- `BOOT_TIMEOUT` — nie zakończono uruchamiania w oczekiwanym czasie;
- `BOOT_RUNTIME_ERROR` — podczas ładowania wystąpił błąd JavaScript lub odrzucona obietnica.

Kod nie zawiera wartości formularza ani innych danych użytkownika. Służy wyłącznie do rozróżnienia rodzaju awarii startu.

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
2. Jeżeli ikona InfusionCalc już istnieje, uruchom aplikację bezpośrednio z ekranu głównego. Jeżeli jej nie ma, otwórz `https://infusioncalc.eu/` w Safari, dodaj aplikację do ekranu głównego i uruchom ją z ikony.
3. Poczekaj, aż formularz w pełni się uruchomi, a następnie pozostaw aplikację otwartą jeszcze przez kilkanaście sekund.
4. Zamknij aplikację z widoku ostatnio używanych aplikacji.
5. Włącz tryb samolotowy i wyłącz Wi‑Fi.
6. Uruchom InfusionCalc z ikony na ekranie głównym.
7. Wykonaj kontrolne obliczenie, np. `4 mg + 50 ml → 80 µg/ml`.
8. Sprawdź zmianę jednostki, przełącznik `/kg`, ostrzeżenie i lokalne Privacy.
9. Przywróć internet i uruchom aplikację ponownie, aby umożliwić sprawdzenie kolejnych aktualizacji.

Nie trzeba zamykać wszystkich kart Safari z domeną `infusioncalc.eu`; kompletna wersja po instalacji sama opuszcza stan `waiting`.

## Test ręczny — Android

1. Otwórz `https://infusioncalc.eu/` w Chrome lub innej obsługiwanej przeglądarce.
2. Poczekaj na pełne uruchomienie i zakończenie przygotowywania cache.
3. Zainstaluj PWA przez systemowy prompt lub menu przeglądarki.
4. Uruchom aplikację raz online i zamknij ją.
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
- dowolny publiczny plik z `build/web` nie znajduje się w manifeście;
- manifest zawiera ukryty plik techniczny, plik nieistniejący lub zewnętrzny URL;
- lista nie jest unikalna i posortowana;
- build ID albo nazwa cache są niespójne;
- service worker nadal zawiera placeholder;
- worker nie używa atomowej instalacji i wersjonowanej strategii cache-first;
- worker nie aktywuje się po kompletnym precache albo nie przejmuje klientów;
- konfiguracja aktualizacji service workera jest niekompletna;
- wygenerowany runtime zawiera znany adres CDN renderera lub fontów;
- brakuje lokalnego JavaScript albo WebAssembly CanvasKit.

Dodatkowo `tool/smoke_test_offline_pwa.py` uruchamia produkcyjny build w prawdziwym profilu Google Chrome przez ChromeDriver. Test wymaga, aby worker kontrolował już pierwsze uruchomienie bez przechodzenia na `about:blank`, oraz odrzuca wszystkie zewnętrzne zasoby startowe poza opcjonalnym Umami. Następnie czyści i wyłącza zwykły HTTP cache, zachowując CacheStorage service workera, zamyka lokalny serwer, odcina sieć i potwierdza ponowne wyrenderowanie tej samej wersji wyłącznie z lokalnej paczki PWA.

Dokument opisuje zachowanie techniczne. Nie zmienia deklarowanego przeznaczenia InfusionCalc jako technicznego kalkulatora bez zaleceń dawkowania i bez podejmowania decyzji klinicznych.
