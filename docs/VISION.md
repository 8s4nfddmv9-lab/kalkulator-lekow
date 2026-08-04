# Wizja projektu — Kalkulator leków

**Status dokumentu:** zatwierdzona wizja początkowa  
**Data:** 2 sierpnia 2026  
**Repozytorium:** `kalkulator-lekow`

## 1. Streszczenie

Kalkulator leków ma być prostą, szybką i przejrzystą aplikacją mobilną do dwukierunkowego przeliczania parametrów podaży leków we wlewie ciągłym.

Najważniejsza idea produktu brzmi:

> Użytkownik wpisuje dowolne znane parametry, a aplikacja natychmiast pokazuje wszystkie wartości, które można z nich jednoznacznie obliczyć.

**Obecne deklarowane przeznaczenie:** techniczny kalkulator przeliczeń matematycznych i jednostkowych. Aplikacja nie dobiera terapii, nie interpretuje klinicznie wyniku i nie jest przeznaczona do podejmowania decyzji klinicznych.

Aplikacja nie narzuca osobnego trybu pracy, nie wymaga wybierania rodzaju wzoru i nie korzysta z przycisku „Oblicz”. Formularz oraz wyniki reagują w czasie rzeczywistym na każdą zmianę wartości albo jednostki.

## 2. Problem

W praktyce klinicznej parametry wlewu bywają przedstawiane w różnych formach:

- ilość leku w strzykawce lub worku;
- objętość końcowa roztworu;
- stężenie;
- przepływ pompy w ml/h;
- szybkość podaży w jednostce czasu;
- dawka odniesiona do masy pacjenta.

Przeliczanie pomiędzy tymi zapisami jest matematycznie proste, ale powtarzalne, podatne na błędy jednostek i wykonywane często w warunkach presji czasu. Typowe kalkulatory wymagają wybrania jednego konkretnego kierunku obliczenia albo ponownego wpisania tych samych danych w innym formularzu.

Projekt ma ograniczyć ten problem przez zastosowanie jednego spójnego modelu wielkości fizycznych i dynamicznego silnika zależności.

## 3. Wizja produktu

Docelowo aplikacja powinna być podręcznym narzędziem, które:

- działa szybko i całkowicie offline;
- pozwala rozpocząć od dowolnego zestawu znanych danych;
- rozumie zależności między ilością, objętością, stężeniem, przepływem i dawką;
- przelicza wartości w obu kierunkach;
- zachowuje poprawność wymiarową jednostek;
- jasno odróżnia dane wpisane od wyników;
- pokazuje sposób uzyskania wyniku;
- wykrywa konflikty zamiast je ukrywać;
- nie zawiera ukrytych założeń klinicznych;
- pozostaje użyteczna zarówno dla dawek zależnych, jak i niezależnych od masy ciała.

## 4. Główne cele

### 4.1. Dowolny punkt wejścia

Użytkownik nie musi znać „właściwej kolejności” pól. Może rozpocząć np. od:

- ilości leku i objętości;
- stężenia i przepływu;
- pożądanej dawki i stężenia;
- dawki, masy oraz przepływu;
- ilości leku i stężenia;
- objętości, przepływu i czasu.

Silnik oblicza tylko te wartości, które są jednoznacznie określone przez aktualny zestaw danych.

### 4.2. Dwukierunkowość

Każda zależność, poza celowo wyłączonym wyliczaniem masy pacjenta, powinna działać w obu kierunkach.

Przykładowo:

- przepływ może być wejściem, a dawka wynikiem;
- dawka może być wejściem, a przepływ wynikiem;
- stężenie może być wynikiem przygotowania roztworu albo wejściem służącym do wyliczenia ilości leku;
- objętość może być wpisana albo wyliczona z ilości i stężenia.

### 4.3. Przejrzystość

Każdy wynik powinien mieć dostępny opis:

- użyte dane;
- użyte jednostki;
- wykonane konwersje;
- wzór;
- podstawienie;
- wynik przed formatowaniem do wyświetlenia.

### 4.4. Poprawność jednostek

System jednostek ma być elementem domeny, a nie wyłącznie etykietą przy polu tekstowym. Silnik musi rozpoznawać rodzaj wielkości oraz blokować działania wymiarowo niepoprawne.

### 4.5. Bezpieczne zachowanie przy niepełnych danych

Brak danych nie jest błędem. Aplikacja powinna spokojnie wskazać, czego brakuje, bez wyświetlania mylącego zera ani wyniku pochodzącego z ukrytej wartości domyślnej.

## 5. Zatwierdzone decyzje produktowe

### 5.1. `/kg` jest opcjonalne

Dawka może być przedstawiana:

- z odniesieniem do masy pacjenta;
- bez odniesienia do masy pacjenta.

Obsługiwane rodzaje zapisu obejmują m.in.:

- ng/min;
- µg/min;
- mg/h;
- IU/h;
- ng/kg/min;
- µg/kg/min;
- mg/kg/h;
- IU/kg/h.

Jeżeli `/kg` jest wyłączone, masa pacjenta nie jest potrzebna do obliczenia szybkości podaży lub przepływu.

### 5.2. Masa pacjenta nigdy nie jest wynikiem

Masa pacjenta jest wyłącznie daną wejściową. Aplikacja nie może jej:

- wyliczać z innych parametrów;
- sugerować;
- uzupełniać domyślnie;
- odzyskiwać z poprzedniej sesji bez jednoznacznej decyzji użytkownika.

Jest to celowe ograniczenie produktu, nawet jeśli matematycznie masa byłaby możliwa do wyznaczenia.

### 5.3. IU stanowi osobną rodzinę jednostek

IU nie jest jednostką masy. W ogólnym kalkulatorze nie istnieje bezpieczny, uniwersalny przelicznik pomiędzy IU i ng, µg, mg lub g.

Silnik utrzymuje dwa rozłączne rodzaje ilości leku:

1. ilość wyrażoną masą;
2. aktywność biologiczną wyrażoną w IU.

Konwersja między nimi nie będzie dostępna bez osobnego, jawnego i specyficznego dla substancji modelu, który pozostaje poza zakresem MVP.

### 5.4. Brak rekomendacji dawkowania w MVP

Pierwsza wersja nie zawiera:

- sugerowanych dawek;
- zakresów terapeutycznych;
- automatycznego doboru przygotowania;
- alarmów opartych na nazwie leku;
- biblioteki leków;
- interpretacji klinicznej wyniku.

Aplikacja przelicza dane podane przez użytkownika, ale nie odpowiada na pytanie, jaka dawka jest właściwa.

### 5.5. Zmiana jednostki zachowuje wielkość fizyczną

Zmiana `mg` na `µg` przelicza liczbę. Nie może prowadzić do zachowania liczby i tysiąckrotnej zmiany ilości substancji.

### 5.6. Konflikty są jawne

Jeżeli użytkownik poda zestaw danych, który jest nadmiarowy i niespójny, system:

- nie wybiera arbitralnie „ważniejszego” pola;
- nie nadpisuje danych w tle;
- wskazuje konflikt;
- pokazuje wartość wynikającą z pozostałych danych;
- pozwala użytkownikowi zdecydować, które pole zmienić.

## 6. Zakres domeny

### 6.1. Wielkości

- masa pacjenta;
- ilość leku;
- objętość roztworu;
- stężenie;
- przepływ objętościowy;
- bezwzględna szybkość podaży;
- dawka odniesiona do masy;
- czas infuzji.

### 6.2. Jednostki początkowe

**Ilość leku wyrażona masą:**

- ng;
- µg / mcg;
- mg;
- g.

**Aktywność biologiczna:**

- IU.

**Objętość:**

- ml.

**Przepływ:**

- ml/h.

**Czas w mianowniku dawki:**

- min;
- h.

**Odniesienie do masy pacjenta:**

- brak;
- `/kg`.

Rozszerzenia jednostek mogą zostać dodane później, ale nie mogą osłabić kontroli wymiarowej.

## 7. Model zależności

### 7.1. Przygotowanie roztworu

$$
C = \frac{A}{V}
$$

Znajomość dowolnych dwóch spośród `A`, `V` i `C` umożliwia wyliczenie trzeciej.

### 7.2. Podaż leku

$$
P = C \times R
$$

gdzie jednostka czasu jest normalizowana i odpowiednio przeliczana między godziną a minutą.

### 7.3. Dawka zależna od masy

$$
D = \frac{P}{W}
$$

Masa może być użyta jako wejście do równania, ale nie może być jego wynikiem w interfejsie ani API domenowym.

### 7.4. Czas infuzji

$$
T = \frac{V}{R}
$$

### 7.5. Obliczenia kaskadowe

Silnik powinien wykonywać serię bezpiecznych kroków. Przykład:

1. użytkownik podaje masę, dawkę, przepływ i objętość;
2. silnik wylicza wymagane stężenie;
3. z wymaganego stężenia i objętości wylicza ilość leku;
4. interfejs pokazuje oba wyniki i pełny tok obliczenia.

Każdy krok musi zachowywać informację o pochodzeniu wartości.

## 8. Model stanu pól

Każde pole ma jawne metadane:

- wartość;
- jednostkę;
- źródło: użytkownik albo obliczenie;
- czas lub kolejność ostatniej edycji;
- status walidacji;
- zależności, z których powstał wynik.

Silnik nie powinien jedynie „wypełniać pustych pól”. Musi rozumieć, które wartości są źródłami prawdy, a które wynikami możliwymi do ponownego obliczenia.

### 8.1. Przejęcie pola przez użytkownika

Kiedy użytkownik zaczyna edytować pole wyliczone:

1. pole staje się wejściem;
2. jego poprzednia zależność zostaje odłączona;
3. silnik ponownie rozwiązuje układ;
4. inne pole może stać się wynikiem.

### 8.2. Układ niedookreślony

Jeżeli nie istnieje jednoznaczne rozwiązanie, pole pozostaje puste. Interfejs może pokazać krótką podpowiedź, np.:

> Dodaj stężenie albo ilość leku i objętość, aby obliczyć przepływ.

### 8.3. Układ nadokreślony

Jeżeli wszystkie wartości są spójne, aplikacja może potwierdzić ich zgodność. Jeżeli nie są spójne, zgłasza konflikt wraz z tolerancją numeryczną ustaloną w specyfikacji technicznej.

## 9. Interfejs docelowy

Podstawowy ekran powinien być możliwy do obsługi jedną ręką i bez przechodzenia między wieloma podstronami.

Proponowany układ:

```text
Masa pacjenta
[ 70 ] kg

Przygotowanie roztworu
Ilość leku   [ 4 ] [mg]
Objętość     [50 ] [ml]
Stężenie     [80 ] [µg/ml]   ← wyliczone

Podaż
Przepływ     [5,25] [ml/h]    ← wyliczone
Dawka        [0,1 ] [µg] [/kg: tak] [/min]

Szczegóły obliczenia
(0,1 × 70 × 60) / 80 = 5,25 ml/h
```

Wyniki powinny być łatwe do skopiowania, ale kopiowana wartość musi obejmować jednostkę lub wyraźnie ostrzegać przed jej pominięciem.

## 10. Zasady UX

- brak przycisku „Oblicz”;
- natychmiastowa aktualizacja po zmianie danych;
- czytelne odróżnienie wejścia od wyniku;
- brak ukrytych wartości domyślnych;
- przecinek i kropka akceptowane jako separator;
- brak mylącego wyniku `0` przy braku danych;
- minimalna liczba dotknięć potrzebna do zmiany jednostki;
- widoczna jednostka przy każdym wyniku;
- odpowiednia wielkość elementów dotykowych;
- tryb jasny i ciemny;
- dostępność dla większych rozmiarów tekstu;
- poprawna obsługa orientacji i małych ekranów.

## 11. Architektura

### 11.1. Aplikacja

Planowana technologia: Flutter i Dart, jedna baza kodu dla iOS i Androida.

### 11.2. Warstwy

**Domena**

- typy wielkości;
- jednostki i konwersje;
- równania;
- silnik rozwiązywania zależności;
- walidacja;
- diagnostyka konfliktów;
- formatowanie wyników niezależne od UI.

**Aplikacja / stan**

- źródła wartości;
- kolejność edycji;
- obsługa komend użytkownika;
- tworzenie listy wyników i ostrzeżeń.

**Prezentacja**

- formularz;
- selektory jednostek;
- karty wyników;
- szczegóły obliczenia;
- komunikaty o brakach i konfliktach.

**Infrastruktura lokalna**

- ustawienia użytkownika;
- ostatnio wybrane jednostki;
- w przyszłości: zapisane własne przygotowania i historia.

### 11.3. Brak backendu w pierwszych wersjach

MVP nie wymaga:

- konta;
- logowania;
- synchronizacji;
- serwera;
- bazy danych pacjentów;
- dostępu do Internetu.

## 12. Strategia jakości

### 12.1. Testy referencyjne

Każdy wzór i każda konwersja muszą mieć zestaw ręcznie zweryfikowanych przypadków referencyjnych.

### 12.2. Testy właściwości

Przykładowe niezmienniki:

- zmiana jednostki nie zmienia wielkości fizycznej;
- obliczenie dawki z przepływu i następnie przepływu z tej dawki odtwarza wartość początkową;
- przejście z `/min` na `/h` zachowuje współczynnik 60;
- IU nigdy nie przechodzi do rodziny jednostek masy;
- masa nigdy nie pojawia się jako wynik;
- kolejność wpisania równoważnych danych nie zmienia rezultatu końcowego;
- obliczenia kaskadowe dają wynik zgodny z obliczeniem bezpośrednim;
- wartości bardzo małe nie są obcinane do zera;
- formatowanie nie wpływa na wartość przechowywaną przez silnik.

### 12.3. Precyzja

- brak zaokrąglania pośredniego;
- jawna arytmetyka dziesiętna;
- odrębna polityka precyzji obliczeń i prezentacji;
- deterministyczne wyniki na obu platformach;
- testy wartości granicznych i ekstremalnych.

### 12.4. Niezależna weryfikacja

Przed jakąkolwiek przyszłą zmianą deklarowanego przeznaczenia w kierunku zastosowania klinicznego wszystkie krytyczne równania, przypadki referencyjne i zachowania interfejsu powinny zostać niezależnie zweryfikowane przez co najmniej jedną osobę inną niż autor implementacji.

## 13. Prywatność i bezpieczeństwo informacji

MVP nie potrzebuje danych identyfikujących pacjenta. Masa jest wartością chwilową używaną do obliczenia, a nie elementem profilu pacjenta.

Założenia:

- brak transmisji wartości formularza, danych pacjenta, wyników i wzorów;
- dopuszczalna jest wyłącznie minimalna analityka techniczna odsłon oraz stałych zdarzeń interfejsu;
- brak własnych identyfikatorów użytkownika i funkcji identyfikacji analitycznej;
- brak reklamowych SDK i profilowania marketingowego;
- brak nazwisk, numerów dokumentacji i innych identyfikatorów;
- ustawienia kalkulatora przechowywane wyłącznie lokalnie;
- jawna decyzja przed ewentualnym rozszerzeniem analityki lub dodaniem synchronizacji.

Obecna implementacja Umami Cloud jest odseparowana od modelu kalkulatora. Może otrzymać wyłącznie wersję aplikacji, znormalizowaną platformę, tryb `browser`/`standalone`, metodę instalacji i jedną z zatwierdzonych nazw zdarzeń. Szczegóły opisuje `docs/ANALYTICS.md`.

## 14. Granice produktu

### MVP nie jest:

- bazą wiedzy o lekach;
- systemem zleceń lekarskich;
- elementem sterującym pompą infuzyjną;
- zamiennikiem instrukcji produktu leczniczego;
- narzędziem automatycznie dobierającym dawkę;
- dokumentacją medyczną;
- systemem monitorującym pacjenta.

### Potencjalne przyszłe rozszerzenia

- własne zapisane przygotowania;
- historia obliczeń bez danych identyfikujących pacjenta;
- kalkulator całkowitej podanej dawki w określonym czasie;
- kalkulator pozostałego czasu wlewu;
- kalkulator wymaganej ilości leku;
- kalkulator bolusa jako oddzielny moduł;
- jednostki dodatkowe, np. ml/min lub jednostki objętości dla małych objętości;
- eksport lub udostępnianie wyniku wraz z pełnym wzorem;
- lokalizacja językowa;
- tryb instytucjonalny;
- biblioteka leków dopiero po osobnej decyzji produktowej, klinicznej i regulacyjnej.

## 15. Aspekty regulacyjne

Sposób kwalifikacji produktu zależy od jego deklarowanego przeznaczenia oraz sposobu wprowadzenia do obrotu. Sama nazwa „kalkulator” lub obecność zastrzeżenia nie zastępują formalnej oceny.

Przed publiczną dystrybucją należy co najmniej:

1. jednoznacznie zdefiniować intended purpose;
2. określić docelowych użytkowników i środowisko użycia;
3. przeprowadzić analizę ryzyka błędnego wyniku i błędnej obsługi;
4. ocenić kwalifikację i klasyfikację oprogramowania;
5. ustalić wymagany poziom dokumentacji, walidacji i nadzoru zmian;
6. określić zasady publikacji w App Store i Google Play;
7. potwierdzić wymagania z kompetentnym specjalistą regulacyjnym.

Punkty odniesienia:

- [Rozporządzenie (UE) 2017/745](https://eur-lex.europa.eu/eli/reg/2017/745/oj/eng)
- [MDCG 2019-11 rev.1, czerwiec 2025](https://health.ec.europa.eu/latest-updates/update-mdcg-2019-11-rev1-qualification-and-classification-software-regulation-eu-2017745-and-2025-06-17_en)

Ten dokument nie stanowi opinii prawnej ani regulacyjnej.

## 16. Kryteria sukcesu

### Sukces techniczny

- wszystkie przypadki referencyjne przechodzą automatyczne testy;
- brak niejawnych konwersji między niezgodnymi rodzinami jednostek;
- identyczne wyniki domenowe na iOS i Androidzie;
- silnik działa niezależnie od interfejsu;
- każda wartość wynikowa ma możliwe do odtworzenia pochodzenie.

### Sukces użytkowy

- typowe obliczenie można wykonać bez przechodzenia między ekranami;
- użytkownik rozumie, które pola wpisał, a które wyliczono;
- zmiana kierunku obliczenia nie wymaga resetowania formularza;
- konflikt danych jest czytelny i możliwy do naprawienia;
- jednostka wyniku pozostaje zawsze widoczna.

### Sukces bezpieczeństwa

- brak masy wyliczonej lub domyślnej;
- brak konwersji IU do masy;
- brak cichego nadpisywania danych;
- brak rekomendacji dawkowania w MVP;
- brak utraty precyzji wskutek zaokrągleń pośrednich;
- udokumentowany proces weryfikacji przed publicznym użyciem.

## 17. Otwarte decyzje

Do jednoznacznego ustalenia podczas implementacji v0.1 pozostają:

- dokładna polityka liczby cyfr znaczących i formatowania wyników;
- tolerancja używana przy wykrywaniu sprzeczności wartości nadmiarowych;
- sposób wyboru nowego wyniku po przejęciu pola wyliczonego przez użytkownika;
- czy jednostka masy pacjenta ma w przyszłości obsługiwać gramy dla neonatologii;
- czy `ml/min` powinno trafić do pierwszego rozszerzenia jednostek;
- zakres zapamiętywania stanu po zamknięciu aplikacji;
- ostateczna nazwa produktu, identyfikator pakietu i oprawa wizualna;
- model dystrybucji prototypu oraz moment rozpoczęcia formalnej ścieżki regulacyjnej.

## 18. Jednozdaniowa definicja produktu

> Kalkulator leków to działająca offline aplikacja mobilna, która w czasie rzeczywistym i w obu kierunkach przelicza ilość leku, objętość, stężenie, przepływ oraz szybkość podaży z opcjonalnym odniesieniem do masy pacjenta, zachowując ścisłą kontrolę jednostek i pełną przejrzystość obliczeń.
