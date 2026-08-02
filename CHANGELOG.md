# Changelog

Wszystkie istotne zmiany projektu są dokumentowane w tym pliku.

## [0.1.0-dev.4] — w przygotowaniu

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

### Ograniczenia etapu

- solver nie jest jeszcze podłączony do kontrolerów tekstowych ekranu Flutter;
- formatowanie i prezentacja wyników oraz konfliktów należą do `0.1.0-dev.5`.

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

### Ograniczenia etapu

- równania nie są jeszcze automatycznie wybierane przez dynamiczny solver;
- formularz nie jest jeszcze połączony z silnikiem obliczeniowym;
- wykrywanie konfliktów nadmiarowych wejść zostanie dodane w `0.1.0-dev.4`.

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

### Ograniczenia etapu

- dynamiczny solver nie jest jeszcze podłączony;
- formularz nie wykonuje jeszcze obliczeń dawki, przepływu ani stężenia;
- formatowanie wyników klinicznych zostanie dodane wraz z równaniami i solverem.

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

- dynamicznego solvera;
- obliczeń dawek i przepływów;
- obsługi konfliktów danych;
- utrwalania ustawień;
- walidacji klinicznej i regulacyjnej.
