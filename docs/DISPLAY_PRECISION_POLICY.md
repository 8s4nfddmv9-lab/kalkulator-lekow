# Polityka precyzji i formatowania wyniku

**Wersja:** `0.1.2-dev.2`  
**Zakres:** wyłącznie warstwa prezentacji  
**Status ręcznego przeglądu przez drugą osobę:** oczekuje

## Rozdzielenie obliczeń i prezentacji

Silnik kalkulatora przechowuje i przelicza wartości jako dokładne ułamki. Formatowanie tekstu odbywa się dopiero po zakończeniu obliczenia i nie zmienia wartości używanej przez solver.

Zasada ta oznacza, że:

- żaden wynik pośredni nie jest zaokrąglany;
- ponowne obliczenie nie używa tekstu wyświetlanego użytkownikowi;
- zmiana jednostki jest wykonywana na dokładnej wartości;
- kopiowany wynik zawiera tekst po formatowaniu oraz jednostkę, ale nie zastępuje stanu domenowego.

## Domyślna polityka

`RationalDecimalFormatter` używa domyślnie:

- 8 cyfr znaczących dla części ułamkowej;
- maksymalnie 12 miejsc po przecinku w zapisie stałopozycyjnym;
- przecinka jako separatora dziesiętnego;
- zaokrąglania `half-up`;
- usuwania niepotrzebnych zer końcowych;
- obowiązkowego zera przed przecinkiem;
- zapisu naukowego, gdy niezerowa wartość zostałaby w zapisie stałopozycyjnym pokazana jako zero.

Duże części całkowite są zachowywane w całości. Limit cyfr znaczących steruje doborem liczby miejsc po przecinku, a nie obcinaniem cyfr części całkowitej.

## Zapis naukowy

Zapis naukowy ma postać:

```text
1,2345678e-18
```

Obowiązują następujące reguły:

- mała litera `e`;
- mantysa w zakresie od 1 włącznie do 10 wyłącznie;
- brak zbędnych zer końcowych mantysy;
- jawny znak `+` dla wykładnika nieujemnego;
- brak postaci nieznormalizowanej, np. `10e-20`.

Audyt wykrył przypadek, w którym zaokrąglenie mantysy `9,99999995…` mogło dać tekst `10e-20`. Wartość była matematycznie poprawna, ale zapis nie był znormalizowany. Formatter przenosi teraz przeniesienie dziesiętne do wykładnika i pokazuje `1e-19`.

## Macierz audytowa

Plik `test/reference/display_precision_cases.json` zawiera 31 jawnych przypadków granicznych, w tym:

- zero, liczby całkowite i ułamki kończące się;
- ułamki okresowe;
- wartości dokładnie poniżej i na progu zaokrąglenia;
- przejście z wartości poniżej 1 do tekstu `1` po zaokrągleniu;
- granicę między zapisem stałopozycyjnym i naukowym;
- bardzo małe wartości dodatnie i ujemne;
- przeniesienie mantysy z `9,99…` do kolejnego wykładnika;
- niestandardową liczbę cyfr znaczących;
- niestandardowy limit miejsc po przecinku.

Testy sprawdzają również niezmienniki:

- niezerowa wartość nie może zostać pokazana jako `0` ani `-0`;
- część ułamkowa nie może zaczynać się bez zera przed przecinkiem;
- każdy zapis naukowy musi być znormalizowany;
- każda wartość musi dokładnie odpowiadać tekstowi zapisanemu w wersjonowanym manifeście.

## Uruchomienie

```bash
flutter test test/presentation/display_precision_policy_test.dart
```

## Granice

Jest to audyt techniczny warstwy prezentacji. Nie ocenia on poprawności terapii, nie definiuje dopuszczalnych dawek i nie zmienia deklarowanego przeznaczenia aplikacji. Ręczny przegląd przypadków przez drugą osobę pozostaje osobnym, niewykonanym etapem.
