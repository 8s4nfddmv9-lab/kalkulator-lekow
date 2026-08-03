# Techniczny zestaw referencyjny obliczeń

**Wersja zestawu:** `0.1.2-dev.1`  
**Zakres:** techniczne przeliczenia matematyczne i jednostkowe  
**Status ręcznego przeglądu przez drugą osobę:** oczekuje

## Cel

Zestaw ma wykrywać regresje silnika niezależnie od testów poszczególnych metod produkcyjnych. Nie zawiera nazw leków, zalecanych dawek, zakresów terapeutycznych ani interpretacji wyniku.

Nie jest to walidacja kliniczna ani dowód dopuszczenia produktu do podejmowania decyzji klinicznych.

## Konstrukcja

Plik `test/reference/technical_reference_matrix.json` zawiera wersjonowaną macierz wejść. Test `test/reference/technical_reference_oracle_test.dart` rozwija ją do dokładnie 480 przypadków.

Wartości oczekiwane oblicza osobny, testowy model:

- korzysta z własnego typu ułamka opartego na `BigInt`;
- ma własną tabelę współczynników jednostek;
- nie importuje `InfusionEquations`;
- nie korzysta z produkcyjnego solvera do obliczania wartości oczekiwanych;
- porównuje z wynikiem solvera dokładne liczniki i mianowniki, bez tolerancji i bez zaokrąglania.

Produkcja i oracle współdzielą jedynie publiczny katalog kodów jednostek potrzebny do utworzenia danych wejściowych oraz konwersji uzyskanego wyniku do jednostki wskazanej przez przypadek referencyjny.

## Zakres 480 przypadków

| Kategoria | Liczba |
|---|---:|
| ilość + objętość → stężenie | 80 |
| stężenie + objętość → ilość | 40 |
| ilość + stężenie → objętość | 40 |
| stężenie + przepływ → szybkość podaży | 80 |
| szybkość podaży + stężenie → przepływ | 40 |
| szybkość podaży + przepływ → stężenie | 40 |
| szybkość podaży + masa → dawka `/kg` | 80 |
| dawka `/kg` + masa → szybkość podaży | 40 |
| pełny łańcuch ilość–objętość–przepływ–masa | 40 |
| **Razem** | **480** |

Pełne łańcuchy sprawdzają po cztery wyniki, dlatego zestaw wykonuje łącznie 600 dokładnych porównań wartości wynikowych.

## Jednostki i wartości graniczne

Macierz obejmuje:

- `ng`, `µg`, `mg`, `g` oraz osobno `IU`;
- stężenia na `ml`;
- przepływy `ml/h` oraz wewnętrznie obsługiwane `ml/min`;
- szybkości podaży na minutę i godzinę;
- dawki z `/kg` na minutę i godzinę;
- masę pacjenta w `kg` i `g`;
- małe wartości dziesiętne, liczby całkowite i wartości z wieloma cyframi znaczącymi;
- konwersje wyniku do innej zgodnej jednostki niż jednostka danych wejściowych.

Rodzina IU nigdy nie jest łączona z rodziną jednostek masy.

## Warunki zaliczenia

Każdy przypadek wymaga jednocześnie:

1. braku konfliktów solvera;
2. braku diagnostyk domenowych;
3. obecności wszystkich oczekiwanych wyników;
4. pochodzenia wyniku z obliczenia, a nie z wejścia;
5. identycznego licznika i mianownika względem niezależnego oracle;
6. zgodności łącznej liczby przypadków z wartością zapisaną w manifeście.

## Uruchomienie

```bash
flutter test test/reference/technical_reference_oracle_test.dart
```

Pełne CI uruchamia zestaw razem z pozostałymi testami i nadal egzekwuje minimalne 90% pokrycia liniowego katalogu `lib/domain/`.

## Ograniczenia

Zestaw jest automatycznie rozwijaną macierzą techniczną. Na obecnym etapie:

- nie został jeszcze ręcznie podpisany przez drugą osobę;
- nie ocenia poprawności dawek ani terapii;
- nie zawiera danych specyficznych dla konkretnych leków;
- nie zastępuje przeglądu interfejsu ani testów na rzeczywistych urządzeniach;
- nie zmienia deklarowanego przeznaczenia aplikacji.

Przed ewentualną przyszłą zmianą przeznaczenia produktu należy wykonać osobny, udokumentowany przegląd ręczny i niezależną ocenę adekwatną do nowego zastosowania.
