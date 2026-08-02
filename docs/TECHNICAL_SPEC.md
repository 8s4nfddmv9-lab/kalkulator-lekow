
# Specyfikacja techniczna domeny

**Wersja dokumentu:** 0.0.2  
**Stan:** przyjęta jako kontrakt implementacyjny dla MVP  
**Data:** 2 sierpnia 2026

## 1. Cel

Dokument zamienia wizję produktu w jednoznaczne zasady dla silnika obliczeniowego. Warstwa interfejsu nie może samodzielnie interpretować jednostek, wybierać wzorów ani rozstrzygać konfliktów.

Silnik ma być:

- niezależny od Fluttera;
- deterministyczny;
- dwukierunkowy;
- wymiarowo bezpieczny;
- oparty na dokładnej arytmetyce dziesiętnej lub wymiernej;
- audytowalny przez jawny tok obliczenia.

## 2. Wielkości domenowe

| Kod | Wielkość | Dozwolone role | Uwagi |
|---|---|---|---|
| `bodyMass` | masa pacjenta | wyłącznie wejście | nigdy nie jest celem równania |
| `drugAmount` | ilość leku | wejście lub wynik | masa substancji albo IU |
| `solutionVolume` | objętość roztworu | wejście lub wynik | w MVP ml |
| `concentration` | ilość leku / objętość | wejście lub wynik | rodzina ilości musi się zgadzać |
| `flowRate` | objętość / czas | wejście lub wynik | w UI ml/h |
| `administrationRate` | ilość leku / czas | wejście lub wynik | bez `/kg` |
| `weightNormalizedDose` | ilość leku / masa pacjenta / czas | wejście lub wynik | z `/kg` |
| `infusionDuration` | czas | wyłącznie wynik w MVP | wyliczany z objętości i przepływu |

## 3. Rodziny jednostek

### 3.1. Masa substancji leczniczej

Dozwolone jednostki:

- `ng`;
- `ug` — kod wewnętrzny, etykieta `µg`, akceptowany alias tekstowy `mcg`;
- `mg`;
- `g`.

Kanoniczną jednostką dla dokładnych współczynników konwersji jest `ng`:

```text
1 µg = 1 000 ng
1 mg = 1 000 000 ng
1 g  = 1 000 000 000 ng
```

### 3.2. Aktywność biologiczna

Dozwolona jednostka: `IU`.

`IU` stanowi odrębną rodzinę. Silnik nie ma ogólnej ścieżki konwersji między `IU` a `ng`, `µg`, `mg` lub `g`.

### 3.3. Objętość

MVP używa `ml` jako jednostki wejściowej, wyjściowej i kanonicznej.

### 3.4. Masa pacjenta

Dozwolone wejścia:

- `kg` — jednostka kanoniczna równań dawkowania;
- `g` — wygodne wejście dla małych mas, konwertowane dokładnie do kg.

Masa nie może zostać oznaczona jako wartość wyliczona.

### 3.5. Czas

Dozwolone jednostki:

- `min` — jednostka kanoniczna szybkości podaży;
- `h`, gdzie `1 h = 60 min`.

### 3.6. Jednostki złożone

Jednostka złożona jest strukturą, a nie dowolnym tekstem. Składa się z:

- rodziny ilości leku: masa substancji albo IU;
- opcjonalnego mianownika objętości `ml`;
- opcjonalnego mianownika masy pacjenta `kg`;
- mianownika czasu `min` albo `h`.

Przykłady poprawnych struktur:

```text
µg/ml
IU/ml
mg/h
IU/h
ng/kg/min
mg/kg/h
```

Przykłady zabronione:

```text
IU/mg
mg/IU/h
ml/kg
kg/h jako dawka leku
```

## 4. Reprezentacja liczb

### 4.1. Zakaz użycia `double` jako źródła prawdy

Wartości wpisane przez użytkownika są parsowane jako dokładna liczba dziesiętna. Silnik przechowuje je jako:

```text
znak × współczynnik całkowity × 10^skala
```

albo równoważną liczbę wymierną z licznikiem i mianownikiem `BigInt`.

`double` może być użyte wyłącznie w niekrytycznej warstwie prezentacyjnej, nigdy do obliczenia wyniku klinicznego ani sprawdzenia konfliktu.

### 4.2. Separator dziesiętny

Parser akceptuje:

```text
0,05
0.05
```

Zabronione są mieszane separatory, wielokrotne separatory i notacje niejawne.

### 4.3. Zaokrąglanie

- brak zaokrągleń pośrednich;
- pełna precyzja jest przenoszona przez cały graf obliczeń;
- zaokrąglanie następuje wyłącznie podczas formatowania do wyświetlenia;
- ponowne formatowanie jednostki korzysta z wartości kanonicznej, nie z już zaokrąglonego tekstu.

## 5. Pochodzenie i stan wartości

Każde pole ma jawny stan:

```text
empty
userInput
calculated
conflict
invalid
```

Dodatkowe metadane:

- znacznik kolejności ostatniej edycji użytkownika;
- jednostka wybrana w UI;
- wartość kanoniczna;
- identyfikator równania będącego źródłem wyniku;
- identyfikatory pól źródłowych;
- pełny ślad konwersji jednostek.

Wartość `userInput` ma pierwszeństwo przed `calculated`. Silnik nie nadpisuje jawnego wejścia bez nowej akcji użytkownika.

## 6. Graf zależności

### 6.1. Przygotowanie roztworu

```text
concentration = drugAmount / solutionVolume
drugAmount = concentration × solutionVolume
solutionVolume = drugAmount / concentration
```

### 6.2. Szybkość podaży

```text
administrationRate = concentration × flowRate
flowRate = administrationRate / concentration
concentration = administrationRate / flowRate
```

Czas jest normalizowany jawnie. `ml/h` oraz dawka `/min` wymagają dokładnego współczynnika 60.

### 6.3. Dawka zależna od masy

```text
weightNormalizedDose = administrationRate / bodyMass
administrationRate = weightNormalizedDose × bodyMass
```

Równanie odwrotne wyliczające `bodyMass` nie istnieje w rejestrze równań.

### 6.4. Czas infuzji

```text
infusionDuration = solutionVolume / flowRate
```

W MVP czas infuzji jest wyłącznie wynikiem dodatkowym.

## 7. Algorytm solvera

1. Parser waliduje pojedyncze wartości i jednostki.
2. Wszystkie poprawne wejścia są normalizowane do typów kanonicznych.
3. Solver buduje zbiór dostępnych faktów.
4. Równania są wykonywane iteracyjnie tylko wtedy, gdy:
   - wszystkie wymagane wejścia są znane;
   - cel nie jest jawnym wejściem użytkownika;
   - rodziny jednostek są zgodne;
   - dzielnik jest różny od zera.
5. Każdy nowy fakt otrzymuje pochodzenie i ślad obliczenia.
6. Iteracja kończy się, gdy nie pojawiają się nowe fakty.
7. Jeżeli dwie niezależne ścieżki wyznaczają ten sam cel, wyniki są porównywane.
8. Niezgodność prowadzi do stanu `conflict`; żadna ścieżka nie wygrywa automatycznie.

Solver musi mieć stałą, testowaną kolejność równań. Kolejność nie może zależeć od platformy ani kolejności elementów w `Map`.

## 8. Wybór wejść i wyników

- ostatnia świadoma edycja użytkownika staje się wejściem;
- edycja pola wyliczonego zmienia jego pochodzenie na `userInput`;
- w grupie ilość–objętość–stężenie maksymalnie dwa najnowsze zgodne wejścia wyznaczają trzeci parametr;
- przy nadmiarowych, zgodnych wejściach wartości pozostają wejściami, a solver może pokazać potwierdzenie zgodności;
- przy nadmiarowych, niezgodnych wejściach pojawia się konflikt;
- wyczyszczenie wejścia usuwa wszystkie wyniki zależne i ponownie uruchamia solver.

## 9. Konflikty

Konflikt zawiera:

- pole docelowe;
- wartość wpisaną przez użytkownika;
- wartość oczekiwaną z pozostałych danych;
- jednostki obu wartości;
- równanie i źródła;
- względną różnicę;
- komunikat możliwy do przedstawienia użytkownikowi.

Porównanie odbywa się na wartościach kanonicznych. Domyślna tolerancja implementacyjna dla redundantnych ścieżek wynosi `1 × 10⁻¹²` względnie; tolerancja nie może maskować różnicy wynikającej z błędnej jednostki. Polityka zostanie potwierdzona zestawem przypadków referencyjnych przed MVP.

## 10. Formatowanie wyników

Domyślna polityka prezentacji:

- 4 cyfry znaczące dla głównego wyniku;
- możliwość pokazania większej precyzji w szczegółach;
- zero przed separatorem;
- usuwanie niepotrzebnych zer końcowych;
- unikanie notacji naukowej w typowym zakresie klinicznym;
- notacja naukowa dla wartości ekstremalnych, z jawnym wykładnikiem;
- jednostka zawsze widoczna obok liczby;
- wynik kopiowany razem z jednostką.

## 11. Katalog błędów domenowych

| Kod | Znaczenie |
|---|---|
| `invalidNumber` | nie można sparsować liczby |
| `negativeValue` | wartość ujemna jest niedozwolona |
| `zeroDenominator` | objętość, stężenie, masa lub przepływ powodują dzielenie przez zero |
| `incompatibleUnitFamily` | próba połączenia IU z masą substancji albo inna niezgodność wymiarów |
| `missingBodyMass` | wybrano dawkę `/kg`, ale nie podano masy |
| `insufficientData` | brak jednoznacznego zestawu danych |
| `conflictingInputs` | redundantne wejścia dają różne wyniki |
| `outOfTechnicalRange` | wartość przekracza bezpieczny zakres reprezentacji lub UI |
| `cyclicDerivation` | ochrona przed błędną pętlą grafu |

## 12. Pierwsze przypadki referencyjne

1. `4 mg / 50 ml = 80 µg/ml`.
2. `80 µg/ml × 5 ml/h = 400 µg/h`.
3. `400 µg/h / 70 kg / 60 = 0,095238… µg/kg/min`.
4. `0,1 µg/kg/min × 70 kg × 60 / 80 µg/ml = 5,25 ml/h`.
5. `50 ml / 5 ml/h = 10 h`.
6. `1 mg = 1000 µg = 1 000 000 ng`.
7. `1 h = 60 min`.
8. `IU` do `mg` kończy się błędem zgodności wymiarowej.
9. Dawka bez `/kg` nie wymaga masy.
10. Dawka z `/kg` bez masy pozostaje niewyznaczalna.
11. Masa nigdy nie pojawia się jako wynik.
12. `4 mg + 50 ml + 100 µg/ml` daje konflikt z wartością referencyjną `80 µg/ml`.

## 13. Granica warstw

Warstwa `domain`:

- nie importuje Fluttera;
- nie przechowuje `TextEditingController` ani `BuildContext`;
- nie formatuje komunikatów zależnych od języka;
- nie zapisuje ustawień urządzenia;
- udostępnia typowane wyniki, błędy i ślad obliczenia.

Warstwa `application` zarządza stanem formularza i kolejnością edycji. Warstwa `presentation` odpowiada za widoki, dostępność, lokalizację i formatowanie końcowe.

## 14. Kryterium ukończenia specyfikacji

Specyfikacja 0.0.2 jest kompletna, gdy każdy nowy wzór, typ jednostki lub wyjątek można jednoznacznie przypisać do powyższych reguł. Zmiana kontraktu wymaga aktualizacji dokumentu i testów.
