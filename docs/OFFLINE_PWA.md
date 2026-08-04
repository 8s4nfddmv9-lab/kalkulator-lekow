# Tryb offline PWA — InfusionCalc

## Cel

Publiczna wersja InfusionCalc ma działać jako zainstalowana aplikacja PWA również bez połączenia z internetem. Pełny tryb offline jest przygotowywany automatycznie po co najmniej jednym kompletnym uruchomieniu aktualnej wersji online.

## Jak przygotowywany jest tryb offline

Po produkcyjnym buildzie Flutter Web skrypt `tool/finalize_web_pwa.py`:

1. skanuje cały katalog `build/web`;
2. tworzy uporządkowaną listę wszystkich lokalnych plików aplikacji;
3. zapisuje listę w `offline-assets.json` wraz z liczbą plików i sumą SHA-256 listy;
4. zapisuje metadane w `pwa-build-info.json`;
5. wstrzykuje kompletną listę oraz identyfikator buildu do `pwa_service_worker.js`;
6. sprawdza, czy zestaw zawiera wymagane pliki Fluttera i zasoby PWA.

W zestawie znajdują się między innymi:

- `index.html`;
- `main.dart.js`;
- `flutter.js` i `flutter_bootstrap.js`;
- pliki z katalogów `assets/` oraz `canvaskit/`;
- fonty, manifest, ikony i lokalne skrypty PWA;
- metadane i manifest zasobów offline.

Zewnętrzny skrypt Umami Cloud nie jest zapisywany jako część aplikacji offline i nie jest wymagany do działania kalkulatora.

## Instalacja service workera

Service worker otwiera cache nazwany identyfikatorem konkretnego buildu i wykonuje `cache.addAll()` dla całego manifestu. Nowa wersja nie przechodzi do aktywnego stanu, dopóki nie uda się pobrać pełnego zestawu lokalnych plików.

Po aktywacji:

- stary cache poprzedniej wersji jest usuwany;
- nowy service worker przejmuje kontrolę nad aplikacją;
- lokalne zasoby są obsługiwane strategią cache-first;
- nawigacja próbuje najpierw pobrać aktualny dokument z sieci, a bez internetu używa lokalnego `index.html`.

## Zachowanie użytkowe

### Pierwsze przygotowanie

1. Otwórz `https://infusioncalc.eu/` z dostępem do internetu.
2. Poczekaj na pełne uruchomienie kalkulatora.
3. Pozostaw aplikację otwartą przez kilka sekund, aby service worker zakończył instalację.
4. Dodaj aplikację do ekranu głównego albo uruchom istniejącą ikonę ponownie online po wdrożeniu nowej wersji.

### Test na iPhonie lub iPadzie

1. Uruchom InfusionCalc z ikony przy aktywnym internecie.
2. Zamknij aplikację z widoku ostatnich aplikacji.
3. Włącz tryb samolotowy i wyłącz Wi‑Fi.
4. Uruchom InfusionCalc ponownie z ikony.
5. Wykonaj przykładowe obliczenie, np. `4 mg`, `50 ml`, `5 ml/h` i `70 kg`.

### Test na Androidzie

1. Uruchom zainstalowane PWA online.
2. Zamknij aplikację.
3. Wyłącz transmisję danych i Wi‑Fi.
4. Uruchom aplikację z ikony i wykonaj obliczenie.

## Co działa offline

- cały formularz i silnik obliczeniowy;
- wszystkie jednostki i konwersje;
- walidacja, konflikty i szczegóły wzoru;
- lokalne ustawienia jednostek i trybu `/kg`;
- ostrzeżenie techniczne oraz lokalna treść informacji o prywatności;
- wyczyszczenie formularza i kopiowanie wyniku.

## Co wymaga internetu

- odnośniki do Changelog, GitHub, Contact i internetowej wersji licencji;
- pobranie nowej wersji aplikacji;
- wysłanie odsłon i zdarzeń do Umami Cloud.

Brak internetu albo blokada Umami nie wpływają na obliczenia. Zdarzenia analityczne nie są przechowywane jako trwała historia offline.

## Prywatność cache

Cache PWA przechowuje wyłącznie statyczny kod i zasoby aplikacji, takie jak JavaScript, fonty, CanvasKit, ikony, manifest i metadane buildu. Nie zawiera:

- masy pacjenta;
- ilości leku, objętości, stężenia, przepływu lub dawki;
- wyników i wzorów;
- treści pól formularza;
- historii obliczeń;
- danych identyfikujących pacjenta.

## Aktualizacje

Każdy deploy otrzymuje nową nazwę cache opartą na SHA commitu. Po uruchomieniu aplikacji online nowy service worker pobiera kompletną wersję w tle. Po aktywacji usuwa cache poprzedniego buildu. Użytkownik może potrzebować zamknąć i ponownie otworzyć PWA, aby zobaczyć nową wersję interfejsu.

## Ograniczenia platformowe

Pierwsze pełne uruchomienie danej instalacji wymaga internetu. System operacyjny lub przeglądarka mogą w przyszłości usunąć dane strony, na przykład po ręcznym wyczyszczeniu danych Safari/Chrome, usunięciu PWA albo przy presji na pamięć urządzenia. W takim przypadku należy ponownie uruchomić InfusionCalc online.

## Automatyczna walidacja

`tool/validate_offline_pwa.py` niezależnie sprawdza po buildzie:

- zgodność `offline-assets.json`, `pwa-build-info.json` i listy w service workerze;
- istnienie każdego pliku manifestu;
- brak zewnętrznych URL w precache;
- obecność wymaganych plików Fluttera, `assets/` i `canvaskit/`;
- brak niewypełnionych placeholderów;
- strategię pełnego precache, fallback nawigacji i cache-first dla zasobów.

Walidator jest uruchamiany zarówno w CI pull requestu, jak i przed publikacją GitHub Pages.
