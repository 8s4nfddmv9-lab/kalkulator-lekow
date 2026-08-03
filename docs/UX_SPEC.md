
# Specyfikacja UX głównego ekranu

**Wersja dokumentu:** 0.0.3  
**Stan:** zatwierdzony kierunek prototypu  
**Data:** 2 sierpnia 2026

## 1. Zasada interakcji

Kalkulator ma jeden główny ekran i nie posiada przycisku „Oblicz”. Użytkownik może zacząć od dowolnego wspieranego zestawu danych. Każda zmiana wartości lub jednostki uruchamia ponowne rozwiązanie formularza.

## 2. Układ

Ekran jest podzielony na trzy sekcje:

1. **Pacjent** — masa pacjenta;
2. **Roztwór** — ilość leku, objętość, stężenie;
3. **Podawanie** — przepływ, dawka/szybkość podaży.

Na górze stale widoczne jest oznaczenie, że aplikacja jest technicznym kalkulatorem nieprzeznaczonym do podejmowania decyzji klinicznych. W prawym górnym rogu znajduje się akcja „Wyczyść”.

## 3. Stany pola

Pole może być:

- puste;
- wpisane przez użytkownika;
- wyliczone;
- niepoprawne;
- w konflikcie.

Stan nie może być komunikowany wyłącznie kolorem. Wartość wyliczona otrzymuje ikonę kalkulatora i etykietę „Wyliczono”. Konflikt otrzymuje ikonę ostrzeżenia, opis tekstowy i możliwość rozwinięcia szczegółów.

## 4. Edycja wyniku

Dotknięcie pola wyliczonego i rozpoczęcie edycji:

1. zmienia jego pochodzenie na wejście użytkownika;
2. zachowuje wybraną jednostkę;
3. uruchamia ponownie solver;
4. może przekształcić inne pole w wynik;
5. nigdy nie zmienia masy pacjenta w wynik.

## 5. Jednostki

Jednostki ilości i stężenia są wybierane z zamkniętych list. Zmiana jednostki zachowuje wartość fizyczną i przelicza liczbę.

Dawka jest składana z trzech niezależnych elementów:

- `ng`, `µg`, `mg`, `g` albo `IU`;
- przełącznik `/kg`;
- `/min` albo `/h`.

Aktualna pełna jednostka jest zawsze pokazana obok etykiety pola, np. `µg/kg/min`.

## 6. Klawiatura i liczby

- klawiatura numeryczna z separatorem dziesiętnym;
- akceptowanie przecinka i kropki;
- brak automatycznego zerowania pustego pola;
- brak dopuszczenia liczb ujemnych;
- zero przed separatorem w wynikach;
- po zamknięciu klawiatury wynik pozostaje widoczny.

## 7. Brakujące dane

Aplikacja nie pokazuje błędu tylko dlatego, że formularz jest niepełny. Zamiast tego może wyświetlić neutralny komunikat, np.:

> Podaj stężenie albo ilość leku i objętość, aby wyliczyć dawkę.

Komunikat ma wskazywać minimalne brakujące zestawy, nie wszystkie teoretyczne możliwości.

## 8. Konflikt

Przykładowy komunikat:

> Podane wartości są niespójne. 4 mg w 50 ml odpowiada stężeniu 80 µg/ml, a nie 100 µg/ml.

Użytkownik może:

- edytować dowolne wejście;
- wyczyścić jedno pole;
- rozwinąć tok obliczenia.

Aplikacja nie wybiera automatycznie wartości do usunięcia.

## 9. Tok obliczenia

Każdy wynik ma rozwijane szczegóły zawierające:

- użyte wejścia;
- konwersje jednostek;
- wzór symboliczny;
- podstawienie liczb;
- pełny wynik przed formatowaniem;
- wynik wyświetlany.

Przykład:

```text
(80 µg/ml × 5 ml/h) ÷ 70 kg ÷ 60
= 0,095238095… µg/kg/min
Wyświetlono: 0,09524 µg/kg/min
```

## 10. Wyczyść

Akcja „Wyczyść” usuwa wartości pacjenta i roztworu, ale zachowuje ostatnio wybrane jednostki. Przed wdrożeniem zapamiętywania ustawień zostanie podjęta osobna decyzja, czy wartości mają być przywracane po restarcie — domyślnie nie.

## 11. Responsywność i dostępność

- minimalny cel dotykowy 48 × 48 dp;
- przewijanie zamiast ściskania pól;
- brak poziomego przewijania na typowym telefonie;
- obsługa powiększonego tekstu;
- etykiety semantyczne dla przełączników i ostrzeżeń;
- tryb jasny i ciemny;
- kontrast zgodny z Material 3;
- kolejność fokusu zgodna z układem od góry do dołu;
- interfejs nie polega wyłącznie na kolorze.

## 12. Zakres prototypu 0.0.3

Pierwszy kodowany prototyp zawiera:

- jeden przewijany ekran;
- wszystkie pola i selektory jednostek;
- przełącznik `/kg`;
- wybór `/min` lub `/h`;
- przycisk „Wyczyść”;
- tryb jasny i ciemny;
- ostrzeżenie o statusie prototypu;
- brak podłączonego solvera.

Celem prototypu jest sprawdzenie struktury i ergonomii, nie wykonywanie obliczeń.
