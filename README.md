# Kalkulator leków

Mobilna aplikacja na iOS i Android służąca do szybkiego, dwukierunkowego przeliczania parametrów podaży leków we wlewie ciągłym.

> [!WARNING]
> Projekt znajduje się na etapie projektowania i prototypowania. Nie jest obecnie zwalidowany, certyfikowany ani przeznaczony do podejmowania decyzji klinicznych. Przed zastosowaniem klinicznym lub publiczną dystrybucją konieczne są niezależna weryfikacja obliczeń, walidacja produktu oraz ocena wymagań prawnych i regulacyjnych.

## Idea

Użytkownik może wpisać dowolny zestaw znanych parametrów, a aplikacja natychmiast oblicza wszystkie wartości, które w danej chwili są jednoznacznie wyznaczalne.

Nie ma osobnego trybu „oblicz dawkę” i „oblicz przepływ” ani przycisku „Oblicz”. Każda zmiana wartości lub jednostki powoduje przeliczenie wyników w czasie rzeczywistym.

Przykładowe kierunki obliczeń:

- ilość leku + objętość → stężenie;
- stężenie + przepływ → szybkość podaży;
- stężenie + przepływ + masa → dawka na kilogram;
- pożądana dawka + masa + stężenie → wymagany przepływ;
- pożądana dawka + masa + przepływ → wymagane stężenie;
- wymagane stężenie + objętość → ilość leku do przygotowania.

Jeżeli danych jest za mało, aplikacja pokazuje wartości nadal potrzebne do wykonania obliczenia. Jeżeli użytkownik poda nadmiarowe, sprzeczne dane, aplikacja zgłasza konflikt zamiast arbitralnie nadpisywać wartości.

## Zakres parametrów

| Parametr | Jednostki / warianty | Rola |
|---|---|---|
| Masa pacjenta | kg | wyłącznie dane wejściowe |
| Ilość leku | ng, µg (mcg), mg, g, IU | wejście lub wynik |
| Objętość roztworu | ml | wejście lub wynik |
| Stężenie | ng/ml, µg/ml, mg/ml, g/ml, IU/ml | wejście lub wynik |
| Przepływ | ml/h | wejście lub wynik |
| Szybkość podaży / dawka | ng, µg, mg, g lub IU; opcjonalnie `/kg`; `/min` albo `/h` | wejście lub wynik |

Człon `/kg` jest opcjonalny. Pozwala to obsługiwać zarówno dawki zależne od masy, jak i szybkości podaży niezależne od masy, np.:

- IU/h;
- mg/h;
- µg/min;
- mg/kg/h;
- IU/kg/h.

### Masa pacjenta jest wyjątkiem

Aplikacja nigdy nie wylicza ani nie sugeruje masy pacjenta na podstawie dawki, przepływu lub stężenia. Masa może zostać wyłącznie wpisana przez użytkownika.

## Model obliczeniowy

Oznaczenia:

- `W` — masa pacjenta w kg;
- `A` — ilość leku;
- `V` — objętość roztworu w ml;
- `C` — stężenie leku;
- `R` — przepływ w ml/h;
- `P` — bezwzględna szybkość podaży leku;
- `D` — dawka odniesiona do masy pacjenta.

### Stężenie

$$
C = \frac{A}{V}
$$

Równania odwrotne:

$$
A = C \times V
$$

$$
V = \frac{A}{C}
$$

### Szybkość podaży bez odniesienia do masy

Na godzinę:

$$
P_h = C \times R
$$

Na minutę:

$$
P_{min} = \frac{C \times R}{60}
$$

### Dawka odniesiona do masy

Na kilogram na godzinę:

$$
D_h = \frac{C \times R}{W}
$$

Na kilogram na minutę:

$$
D_{min} = \frac{C \times R}{W \times 60}
$$

### Przepływ wynikający z pożądanej dawki

Dla dawki na kilogram na minutę:

$$
R = \frac{D_{min} \times W \times 60}{C}
$$

Dla dawki na kilogram na godzinę:

$$
R = \frac{D_h \times W}{C}
$$

Dla szybkości podaży bez odniesienia do masy:

$$
R = \frac{P_h}{C}
$$

lub dla wartości podanej na minutę:

$$
R = \frac{P_{min} \times 60}{C}
$$

### Czas opróżnienia roztworu

Jeżeli znane są objętość i przepływ:

$$
T = \frac{V}{R}
$$

## Przykład

Dane:

- masa pacjenta: `70 kg`;
- ilość leku: `4 mg`;
- objętość: `50 ml`.

Stężenie:

$$
4\ mg = 4000\ \mu g
$$

$$
C = \frac{4000\ \mu g}{50\ ml} = 80\ \mu g/ml
$$

Po wpisaniu przepływu `5 ml/h`:

$$
D = \frac{80\ \mu g/ml \times 5\ ml/h}{70\ kg \times 60} = 0{,}095238\ \mu g/kg/min
$$

Po wpisaniu zamiast przepływu pożądanej dawki `0,1 µg/kg/min`:

$$
R = \frac{0{,}1\ \mu g/kg/min \times 70\ kg \times 60}{80\ \mu g/ml} = 5{,}25\ ml/h
$$

## Reguły jednostek

### Jednostki masy leku

Konwersje są dozwolone wewnątrz jednej rodziny jednostek:

```text
g ↔ mg ↔ µg ↔ ng
```

### IU

IU jest osobnym rodzajem wielkości i nie może być traktowane jak jednostka masy.

Aplikacja nie wykonuje ogólnych konwersji:

```text
IU ↔ g
IU ↔ mg
IU ↔ µg
IU ↔ ng
```

Jeżeli ilość lub stężenie zostały podane w IU, wszystkie zależne wyniki pozostają w rodzinie IU. Jeżeli zostały podane w jednostce masy, wyniki pozostają w rodzinie jednostek masy.

### Zmiana jednostki zachowuje wartość fizyczną

Zmiana jednostki w formularzu przelicza liczbę, zamiast zmieniać fizyczną ilość:

```text
1 mg → 1000 µg
```

Nigdy:

```text
1 mg → 1 µg
```

## Zachowanie interfejsu

Każde pole ma jeden z trzech stanów:

1. puste;
2. wpisane lub zmienione przez użytkownika;
3. wyliczone przez aplikację.

Wartości wyliczone są wizualnie odróżnione od danych wejściowych. Dotknięcie wyniku i rozpoczęcie edycji zmienia go w dane wejściowe, a silnik ponownie ustala, które pozostałe pole powinno być wynikiem.

### Priorytet ostatniej edycji

W grupie `ilość–objętość–stężenie` aplikacja pamięta pola ostatnio świadomie podane przez użytkownika. Trzecia wartość jest obliczana. Analogiczna zasada obowiązuje dla zależności między stężeniem, przepływem i dawką.

### Sprzeczne dane

Przykład konfliktu:

```text
4 mg + 50 ml + 100 µg/ml
```

Ponieważ `4 mg / 50 ml = 80 µg/ml`, aplikacja pokazuje komunikat o niespójności i wyliczoną wartość referencyjną. Nie wybiera samodzielnie, którą wartość nadpisać.

## Zasady bezpieczeństwa

Od pierwszej wersji obowiązują następujące zasady:

- brak zaokrąglania obliczeń pośrednich;
- arytmetyka dziesiętna zamiast polegania wyłącznie na binarnym `double`;
- akceptowanie przecinka i kropki jako separatora dziesiętnego;
- wyświetlanie zera przed separatorem, np. `0,05`, nigdy `.05`;
- blokada wartości ujemnych;
- blokada dzielenia przez zero;
- ścisła kontrola zgodności wymiarów i jednostek;
- brak automatycznej konwersji IU na jednostki masy;
- brak wyliczania masy pacjenta;
- widoczny tok obliczenia i podstawienie do wzoru;
- brak domyślnych dawek, zakresów terapeutycznych i rekomendacji lekowych w MVP;
- brak cichego korygowania sprzecznych danych;
- komplet testów referencyjnych i testów odwracalności równań.

## Zakres MVP — v0.1.0

Pierwsza działająca wersja obejmuje:

- jeden główny ekran kalkulatora;
- obliczenia w czasie rzeczywistym;
- wszystkie parametry i jednostki opisane wyżej;
- dawki z opcjonalnym `/kg` oraz czasem `/min` lub `/h`;
- dynamiczne obliczenia w obu kierunkach;
- wykrywanie brakujących, niezgodnych i sprzecznych danych;
- szczegóły wzoru i toku obliczenia;
- przycisk wyczyszczenia formularza;
- zapamiętywanie ostatnio wybranych jednostek;
- działanie całkowicie offline;
- brak kont, serwera, analityki i danych identyfikujących pacjenta;
- testy jednostkowe, właściwościowe i integracyjne silnika obliczeniowego.

Poza zakresem MVP pozostają m.in. biblioteka leków, sugerowane dawki, synchronizacja, konta użytkowników i przechowywanie danych pacjentów.

## Uruchomienie projektu

Wymagany jest Flutter 3.44.8 z Dartem 3.12.2. Po sklonowaniu repozytorium:

```bash
flutter pub get
flutter analyze --fatal-warnings
flutter test
flutter run
```

Projekt platformowy Android/iOS jest generowany z oficjalnego szablonu Fluttera przez `tool/bootstrap_platforms.sh`.

## Technologia

Stos technologiczny:

- **Flutter + Dart** — wspólna aplikacja na iOS i Android;
- niezależny od interfejsu silnik domenowy;
- lokalne, offline-first działanie bez backendu;
- arytmetyka dziesiętna i jawny system jednostek;
- GitHub Actions dla analizy statycznej i testów;
- testy jednostkowe, właściwościowe, widgetowe i integracyjne.

Proponowana struktura:

```text
lib/
  app/
  domain/
    calculations/
    quantities/
    units/
    validation/
  features/
    calculator/
  shared/

test/
  domain/
  features/
  reference_cases/

docs/
  VISION.md

README.md
ROADMAP.md
```

Silnik obliczeniowy ma pozostać niezależny od Fluttera i warstwy UI. Pozwoli to testować obliczenia bez uruchamiania aplikacji oraz ograniczy ryzyko, że zmiana interfejsu wpłynie na matematykę.

## Dokumentacja projektu

- [Wizja produktu](docs/VISION.md)
- [Specyfikacja techniczna domeny](docs/TECHNICAL_SPEC.md)
- [Specyfikacja UX](docs/UX_SPEC.md)
- [Roadmapa](ROADMAP.md)

## Aspekty regulacyjne

Przed określeniem sposobu dystrybucji i deklarowanego zastosowania należy przeprowadzić formalną ocenę kwalifikacji produktu oraz wymagań dotyczących oprogramowania medycznego. Zakres tej oceny zależy m.in. od deklarowanego przeznaczenia, grupy użytkowników, środowiska użycia i potencjalnych konsekwencji błędnego wyniku.

Materiały referencyjne:

- [Rozporządzenie (UE) 2017/745 — EUR-Lex](https://eur-lex.europa.eu/eli/reg/2017/745/oj/eng)
- [MDCG 2019-11 rev.1 — Qualification and classification of software](https://health.ec.europa.eu/latest-updates/update-mdcg-2019-11-rev1-qualification-and-classification-software-regulation-eu-2017745-and-2025-06-17_en)
- [Flutter — oficjalna dokumentacja](https://docs.flutter.dev/)

Dokumentacja repozytorium nie stanowi opinii prawnej ani regulacyjnej.

## Status

**Etap:** `0.1.0-dev.1` — szkielet aplikacji i pierwszy prototyp ekranu
**Planowana pierwsza wersja:** `0.1.0`  
**Platformy docelowe:** iOS i Android  
**Model działania:** offline-first

## Licencja

Licencja projektu nie została jeszcze wybrana. Do czasu dodania pliku `LICENSE` wszystkie prawa pozostają zastrzeżone.
