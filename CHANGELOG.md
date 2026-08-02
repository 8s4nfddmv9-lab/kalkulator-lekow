# Changelog

Wszystkie istotne zmiany projektu są dokumentowane w tym pliku.

## [0.1.0-dev.2] — w przygotowaniu

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
