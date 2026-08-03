# Raport wydania 0.1.0 — techniczny MVP

**Data:** 3 sierpnia 2026  
**Wersja aplikacji:** `0.1.0+8`  
**Status:** techniczny kalkulator przeliczeń, działający offline  
**Platformy objęte buildem kontrolnym:** Android i iOS Simulator

## 1. Deklarowane przeznaczenie

Wersja `0.1.0` jest technicznym kalkulatorem matematycznym i jednostkowym. Na podstawie wartości wpisanych przez użytkownika wykonuje jawne, dwukierunkowe przeliczenia pomiędzy:

- ilością leku;
- objętością roztworu;
- stężeniem;
- przepływem objętościowym;
- bezwzględną szybkością podaży;
- dawką odniesioną do masy ciała;
- czasem opróżnienia roztworu.

Aplikacja nie dobiera terapii, nie ocenia poprawności klinicznej danych wejściowych, nie interpretuje wyniku i nie jest przeznaczona do podejmowania decyzji klinicznych.

## 2. Zakres funkcjonalny

Wydanie obejmuje:

- jeden dynamiczny ekran bez przycisku „Oblicz”;
- obliczenia aktualizowane po każdej zmianie wartości lub jednostki;
- dwukierunkowe równania ilość–objętość–stężenie;
- dwukierunkowe równania stężenie–przepływ–szybkość podaży;
- dawkę z opcjonalnym członem `/kg` i czasem `/min` albo `/h`;
- dokładną arytmetykę wymierną bez binarnego `double` w domenie;
- rozdzielenie IU i jednostek masy;
- zachowanie fizycznej wartości przy zmianie jednostki;
- wykrywanie sprzecznych danych bez cichego nadpisywania;
- widoczny tok obliczenia i kopiowanie wyniku wraz z jednostką;
- lokalne zapamiętywanie wyłącznie jednostek prezentacyjnych i trybu `/kg`;
- puste pola liczbowe po każdym ponownym uruchomieniu;
- działanie bez konta, backendu, synchronizacji, reklam i zewnętrznej analityki.

## 3. Funkcje świadomie wyłączone

Wersja `0.1.0` nie zawiera:

- nazw leków ani biblioteki preparatów;
- dawek domyślnych, zakresów terapeutycznych lub zaleceń dawkowania;
- interpretacji klinicznej wyniku;
- alertów zależnych od substancji;
- bezpośredniego sterowania pompą infuzyjną;
- dokumentacji medycznej lub identyfikacji pacjenta;
- historii obliczeń i przywracania wartości klinicznych po restarcie;
- kalkulatora bolusa;
- kont użytkowników, chmury i synchronizacji.

## 4. Wyniki automatycznej walidacji

Końcowy pipeline jakości dla `0.1.0-dev.7`, stanowiącego podstawę wydania, zakończył się powodzeniem:

- `127/127` testów automatycznych;
- `93,47%` pokrycia liniowego katalogu `lib/domain/` (`716/766` linii);
- formatowanie Darta bez różnic;
- analiza statyczna Fluttera bez ostrzeżeń;
- poprawny build kontrolny Android debug APK;
- poprawny build kontrolny iOS Simulator debug.

Dodatkowe testy utwardzające obejmują:

- `3000` deterministycznych prób dokładnej odwracalności podstawowych równań;
- `4000` porównań solvera po zmianie kolejności wejść;
- pełną macierz zgodnych konwersji jednostek MVP;
- granice wektorów wymiarów i konstrukcji jednostek złożonych;
- blokadę mieszania IU z jednostkami masy;
- konflikty, obliczenia kaskadowe, kolejność edycji i separatory dziesiętne;
- scenariusze widgetowe głównego ekranu.

## 5. Zasady bezpieczeństwa technicznego

W warstwie domenowej obowiązują:

- brak zaokrągleń pośrednich;
- blokada wartości ujemnych;
- kontrola dzielenia przez zero;
- jawna kontrola wymiarów;
- brak uniwersalnej konwersji IU na jednostki masy;
- masa pacjenta wyłącznie jako wejście;
- brak cichego korygowania sprzecznych danych;
- deterministyczne wyniki niezależne od kolejności równoważnych wejść;
- formatowanie wyświetlania oddzielone od wartości używanej w obliczeniach.

## 6. Prywatność i dane trwałe

Aplikacja przechowuje lokalnie wyłącznie:

- stabilne kody ostatnio wybranych jednostek;
- ustawienie trybu dawki z `/kg` albo bez `/kg`.

Nie przechowuje:

- masy pacjenta;
- ilości leku;
- objętości;
- stężenia;
- przepływu;
- dawki;
- wyników ani historii obliczeń.

## 7. Znane ograniczenia

- Jest to techniczny kalkulator, a nie narzędzie dostarczające wiedzę kliniczną.
- Automatyczne testy potwierdzają zaimplementowaną matematykę i zachowanie kodu, ale nie stanowią walidacji zastosowania klinicznego.
- Ręczny, niezależny przegląd wzorów przez drugą osobę pozostaje wymogiem przed ewentualną przyszłą zmianą deklarowanego przeznaczenia w kierunku zastosowania klinicznego.
- Wersja nie zawiera instytucjonalnych procedur zarządzania konfiguracją, ryzykiem i zmianą właściwych dla produktu medycznego.
- Publiczna dystrybucja i sposób komunikowania zastosowania produktu wymagają osobnej decyzji.

## 8. Odtworzenie kontroli jakości

```bash
flutter pub get --enforce-lockfile
dart format --output=none --set-exit-if-changed lib test
flutter analyze --fatal-warnings
flutter test --coverage
python3 tool/check_coverage.py coverage/lcov.info --prefix lib/domain/ --minimum 90
flutter build apk --debug
flutter build ios --simulator --debug
```

Ostatnie polecenie wymaga macOS i Xcode.

## 9. Następne planowane etapy

- `0.1.1` — poprawki po testach wewnętrznych;
- `0.1.2` — dostępność i ergonomia;
- `0.1.3` — ponowny audyt domeny oraz precyzji;
- dalsze funkcje dopiero po osobnych decyzjach produktowych.

Dokument należy czytać łącznie z:

- [`README.md`](../README.md);
- [`ROADMAP.md`](../ROADMAP.md);
- [`VISION.md`](VISION.md);
- [`TECHNICAL_SPEC.md`](TECHNICAL_SPEC.md);
- [`UX_SPEC.md`](UX_SPEC.md).
