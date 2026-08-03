# Changelog

Wszystkie istotne zmiany projektu są dokumentowane w tym pliku.

## [0.1.0-dev.7] — w przygotowaniu

### Dodano

- 3000 deterministycznych prób dokładnej odwracalności podstawowych równań;
- 4000 porównań solvera po kontrolowanym przetasowaniu kolejności wejść;
- pełną macierz zgodnych konwersji jednostek MVP w obie strony;
- testy rozdzielenia IU i jednostek masy we wszystkich rodzinach wielkości;
- testy graniczne wektorów wymiarów, jednostek prostych i jednostek złożonych;
- przypięty graf zależności w `pubspec.lock` oraz jego egzekwowanie w CI;
- obowiązkowy próg co najmniej 90% pokrycia liniowego kodu `lib/domain/`;
- jednoznaczne oznaczenie produktu jako technicznego kalkulatora bez zaleceń i interpretacji klinicznej.

### Wyniki automatycznej walidacji

- `127/127` testów zakończonych powodzeniem;
- `93,47%` pokrycia liniowego warstwy domenowej (`716/766` linii);
- poprawne buildy kontrolne Androida i iOS;
- zielone formatowanie i analiza statyczna bez ostrzeżeń.

### Deklarowane przeznaczenie

- aplikacja wykonuje techniczne przeliczenia matematyczne i jednostkowe na podstawie danych użytkownika;
- nie zawiera biblioteki leków, zaleceń dawkowania ani interpretacji klinicznej;
- nie jest przeznaczona do podejmowania decyzji klinicznych.

## [0.1.0-dev.6] — 2026-08-03

### Dodano

- lokalne zapamiętywanie ostatnio wybranych jednostek prezentacyjnych;
- zapamiętywanie trybu dawki z `/kg` albo bez `/kg`;
- asynchroniczny magazyn preferencji oparty na stabilnych kodach jednostek;
- bezpieczne wartości domyślne dla nieznanych, usuniętych lub niezgodnych kodów;
- ochronę przed nadpisaniem szybkiej zmiany użytkownika przez opóźniony odczyt ustawień;
- niekrytyczną obsługę błędów odczytu i zapisu preferencji;
- centralny katalog jednostek dostępnych w formularzu;
- techniczne limity długości i precyzji tekstowego wejścia liczbowego;
- osobny błąd domenowy `outOfTechnicalRange`;
- testy modelu preferencji, fallbacków, zakresów technicznych i integracji z ekranem.

### Polityka danych trwałych

- zapis obejmuje wyłącznie kody jednostek oraz wartość logiczną trybu `/kg`;
- aplikacja nie zapisuje masy pacjenta, ilości leku, objętości, stężenia, przepływu, dawki, historii ani wyników;
- po restarcie wszystkie pola liczbowe pozostają puste.

### Nadal obowiązuje

- aplikacja działa bez konta, backendu, analityki i transmisji danych kalkulatora;
- wersja pozostaje prototypem nieprzeznaczonym do podejmowania decyzji klinicznych.

## [0.1.0-dev.5] — 2026-08-03

### Dodano

- pełne połączenie jednego ekranu Flutter z sesją i dynamicznym solverem;
- natychmiastowe przeliczanie stężenia, przepływu, szybkości podaży, dawki `/kg` i czasu infuzji bez przycisku „Oblicz”;
- edycję wartości wyliczonej jako nowe wejście wraz z automatycznym ponownym rozwiązaniem formularza;
- wizualne rozróżnienie pól pustych, wpisanych, wyliczonych, błędnych i skonfliktowanych;
- selektory wszystkich jednostek dawki i stężenia oraz przełącznik `/kg`;
- zmianę jednostki zachowującą fizyczną wartość, np. `1 mg → 1000 µg`;
- bezpieczne rozdzielenie jednostek masy i IU także podczas interakcji w UI;
- adaptacyjne formatowanie wyników z przecinkiem, bez zaokrągleń pośrednich i z zapisem naukowym dla bardzo małych wartości;
- kontrolowane diagnostyki solvera zamiast przerwania działania formularza;
- komunikaty walidacji dla wartości ujemnych, zerowych dzielników, nieprawidłowych liczb i niezgodnych jednostek;
- kartę czasu opróżnienia roztworu;
- rozwijany tok obliczenia z wzorem, wejściami i wynikiem;
- kopiowanie głównego wyniku razem z jednostką;
- rozszerzone testy widgetowe prawdziwych scenariuszy obliczeniowych, dostępności i małego ekranu.

### Przypadki potwierdzone w interfejsie

- `4 mg + 50 ml → 80 µg/ml`;
- `4 mg + 50 ml + 5 ml/h + 70 kg → 0,095238095 µg/kg/min`;
- `0,1 µg/kg/min + 70 kg + 80 µg/ml → 5,25 ml/h`;
- wyłączenie `/kg` pokazuje bezwzględną szybkość podaży;
- `1 mg → 1000 µg` po zmianie jednostki;
- `50 ml / 5 ml/h → 10 h`.

### Ograniczenia etapu

- ustawienia jednostek nie są jeszcze utrwalane między uruchomieniami;
- nie ma jeszcze osobnej polityki zakresów technicznych ani pełnej lokalizacji komunikatów;
- aplikacja pozostaje technicznym kalkulatorem nieprzeznaczonym do podejmowania decyzji klinicznych.

## [0.1.0-dev.4] — 2026-08-02

### Dodano

- deterministyczny solver stałopunktowy wybierający wszystkie osiągalne równania;
- obliczenia kaskadowe od dowolnego wystarczającego zestawu wejść;
- jawne pochodzenie każdej wartości: wejście użytkownika albo wynik obliczenia;
- kolejność edycji oraz śledzenie źródłowych i pośrednich zależności;
- exact-relative tolerance dla porównywania redundantnych wartości;
- wykrywanie konfliktów wejście–wynik i wynik–wynik;
- blokowanie niejednoznacznego parametru oraz unieważnianie zależnych wyników;
- zachowanie wszystkich jawnych wejść bez cichego nadpisywania;
- sesję aplikacyjną obsługującą edycję, czyszczenie, reset i przejmowanie pola wyliczonego;
- automatyczne zastępowanie najstarszego odpowiedniego wejścia po edycji wartości wyliczonej;
- ochronę masy pacjenta przed automatycznym i ręcznym zastąpieniem;
- testy deterministyczności, konfliktów, tolerancji, kolejności edycji i przejmowania wyniku.

### Przykładowe zachowanie

- po wpisaniu `4 mg`, `50 ml`, `5 ml/h` i `70 kg` solver wylicza stężenie, szybkość podaży, dawkę `/kg` i czas wlewu;
- po edycji wyliczonej dawki na `0,1 µg/kg/min` przepływ `5 ml/h` zostaje zwolniony i ponownie wyliczony jako `5,25 ml/h`;
- zestaw `4 mg + 50 ml + 100 µg/ml` powoduje konflikt zamiast nadpisania któregokolwiek wejścia.

## [0.1.0-dev.3] — 2026-08-02

### Dodano

- dziewięć dokładnych, dwukierunkowych równań domenowych dla przygotowania roztworu, szybkości podaży, dawki zależnej od masy i czasu infuzji;
- jawne identyfikatory oraz symboliczne wzory wszystkich równań;
- niezmienny ślad obliczenia zawierający wejścia, jednostki, wartości kanoniczne i wynik;
- kontrolowane błędy nieprawidłowego rodzaju wejścia i dzielenia przez zero;
- dokładną normalizację `/min` i `/h` bez zaokrągleń pośrednich;
- zachowanie rodziny masy leku albo IU przez cały łańcuch obliczeń;
- przypadki referencyjne `4 mg/50 ml`, `400 µg/h`, `0,1 µg/kg/min → 5,25 ml/h` i `50 ml/5 ml/h → 10 h`;
- testy bezpośrednie, odwrotne, kaskadowe i odwracalności dla równań.

### Zasada bezpieczeństwa

- masa pacjenta pozostaje wyłącznie wejściem; rejestr równań nie zawiera żadnej ścieżki wyliczającej masę.

## [0.1.0-dev.2] — 2026-08-02

### Dodano

- dokładny parser liczb dziesiętnych akceptujący przecinek i kropkę;
- stabilne, maszynowo odczytywalne kody błędów domenowych;
- jawny wektor wymiarów jednostek;
- strukturalne jednostki złożone, m.in. `µg/ml`, `ml/h`, `mg/h` i `IU/kg/h`;
- zamknięty katalog wszystkich jednostek MVP i obsługę aliasu `mcg`;
- typ `Quantity`, łączący rodzaj wielkości, dokładną wartość i jednostkę;
- dokładne konwersje zachowujące fizyczną wartość;
- walidację niedozwolonych jednostek i wartości ujemnych;
- testy parsera, jednostek złożonych, aliasów, odwracalności i typowanych wielkości.

## [0.1.0-dev.1] — 2026-08-02

### Dodano

- szkielet aplikacji Flutter z oddzielonymi warstwami domeny i prezentacji;
- pierwszy, nieobliczający jeszcze ekran kalkulatora;
- selektory jednostek ilości, stężenia, dawki i masy;
- opcjonalny człon `/kg` oraz wybór `/min` lub `/h`;
- dokładny typ `Rational` oparty na `BigInt` dla współczynników konwersji;
- pierwszy zamknięty katalog jednostek pierwotnych;
- blokadę konwersji `IU` do jednostek masy;
- testy typu wymiernego, konwersji jednostek i ekranu;
- specyfikację techniczną domeny i specyfikację UX;
- GitHub Actions dla formatowania, analizy statycznej, testów oraz kontrolnych buildów Androida i iOS.

### Jeszcze nie dodano

- utrwalania ustawień;
- walidacji klinicznej i regulacyjnej.
