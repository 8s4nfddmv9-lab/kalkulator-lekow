# Changelog

Wszystkie istotne zmiany projektu są dokumentowane w tym pliku.

## [Unreleased]

## [0.1.3-beta.1] — 2026-08-04

### Dodano

- kontekstowy przycisk „Dodaj do ekranu głównego” pod nagłówkiem kalkulatora;
- wykrywanie iOS, iPadOS, Androida, rodziny przeglądarki oraz trybu `standalone`;
- obsługę zdarzeń `beforeinstallprompt` i `appinstalled` dla natywnej instalacji na Androidzie;
- instrukcję instalacji na iPhonie i iPadzie z graficzną ikoną „Udostępnij”;
- instrukcję ręczną na Androidzie, gdy systemowy prompt nie jest dostępny;
- lokalną opcję „Nie teraz”, która odracza zachętę na 30 dni;
- produkcyjny build i walidację Flutter Web jako osobny etap CI;
- testy widgetowe instalacji, odroczenia i ukrywania zachęty w trybie `standalone`;
- licencję MIT z oznaczeniem praw autorskich `Copyright (c) 2026 M W`;
- odnośnik do licencji i informację `© 2026 M W · MIT License` w stopce aplikacji.

### Zmieniono

- nazwę instalowanej aplikacji i metadane manifestu PWA na `InfusionCalc`;
- service worker, aby przechowywał skrypt obsługi instalacji w pamięci offline;
- sekcję prywatności o lokalne przechowywanie daty odroczenia komunikatu;
- sekcję licencyjną README, która opisuje warunki MIT i odsyła do pliku `LICENSE`.

### Granice

- brak zmian w solverze, równaniach, jednostkach i polityce precyzji;
- wykrywanie platformy służy wyłącznie lokalnemu dobraniu instrukcji instalacji;
- dane z formularza nadal nie są zapisywane ani wysyłane.

## [0.1.2-beta.3] — 2026-08-03

### Poprawiono

- wpisanie przecinka lub kropki jako pierwszego znaku automatycznie tworzy zapis `0,`;
- klawiatura numeryczna i fokus pozostają aktywne podczas wpisywania oraz kasowania ułamków przechodzących przez `0`, `0,` i kolejne zera;
- przejściowe, niedokończone prefiksy dziesiętne nie są zgłaszane jako błąd w trakcie edycji;
- zero i niedokończony separator nadal są walidowane po opuszczeniu pola.

### Dodano

- trwałe węzły fokusu dla wszystkich pól kalkulatora;
- testy regresji połączenia klawiatury, fokusu oraz automatycznego zera przed separatorem;
- stopkę InfusionCalc z sekcjami `Changelog`, `Privacy`, `GitHub` i `Contact`;
- lokalny komunikat prywatności i dokument `docs/PRIVACY.md`;
- centralne issue #18 do zbierania feedbacku z pierwszych testów;
- dokument `DEPLOYMENT.md` opisujący wspieraną i archiwalne ścieżki wdrożenia.

### Zmieniono

- GitHub Pages i `https://infusioncalc.eu/` są główną ścieżką publicznej dystrybucji;
- workflow niepodpisanego IPA oraz mini-PC/Docker/Tailscale są oznaczone jako archiwalne i uruchamiane wyłącznie ręcznie.

## [0.1.2-beta.2] — 2026-08-03

### Wydano

- publiczną wersję Flutter PWA;
- automatyczny deploy przez GitHub Pages;
- własną domenę `https://infusioncalc.eu/` z HTTPS;
- manifest instalacyjny, ikony i service worker z wersjonowanym cache offline.

## [0.1.2-beta.1] — 2026-08-03

### Dodano

- ręcznie uruchamiany workflow `iOS unsigned device build` na runnerze macOS;
- urządzeniowy build iOS `release` z wyłączonym code signing;
- pakowanie `Payload/Runner.app` do niepodpisanego IPA dla fizycznego iPhone'a;
- stały bazowy bundle ID `pl.kalkulatorlekow.technicalcalculator`;
- artifact z IPA, sumą SHA-256 i metadanymi wersji, commitu oraz architektury;
- instrukcję podpisania darmowym Apple ID i instalacji na iPhonie z Windowsa przez Sideloadly;
- dokument zakresu pierwszych testów na fizycznym urządzeniu.

### Bezpieczeństwo procesu

- workflow nie przyjmuje ani nie przechowuje danych Apple ID;
- w repozytorium i GitHub Secrets nie są wymagane certyfikaty ani profile provisioning;
- podpis następuje lokalnie na komputerze użytkownika;
- artifact jest jawnie opisany jako niepodpisany;
- wydanie pozostaje technicznym kalkulatorem bez rekomendacji i interpretacji klinicznej.

### Ograniczenia

- darmowy profil Apple wygasa po 7 dniach i wymaga ponownego podpisania lub odświeżenia;
- brak TestFlight i App Store;
- Sideloadly jest narzędziem zewnętrznym, niezależnym od Apple i projektu;
- dystrybucję instalacyjną Androida odłożono.

## [0.1.2-dev.2] — 2026-08-03

### Poprawiono

- zapis naukowy jest normalizowany po przeniesieniu wynikającym z zaokrąglenia, np. `10e-20` → `1e-19`;
- formatter zachowuje rozdzielenie dokładnej wartości domenowej i tekstu wyświetlanego użytkownikowi.

### Dodano

- wersjonowaną macierz 31 przypadków granicznych polityki prezentacji;
- testy zaokrąglania `half-up`, przecinka dziesiętnego i usuwania niepotrzebnych zer końcowych;
- testy wartości okresowych, dodatnich, ujemnych, dużych i bardzo małych;
- testy granicy między zapisem stałopozycyjnym i naukowym;
- niezmienniki blokujące wyświetlenie wartości niezerowej jako `0` lub `-0`;
- dokument `docs/DISPLAY_PRECISION_POLICY.md`.

### Wyniki automatycznego audytu

- 31/31 przypadków polityki prezentacji zakończonych powodzeniem;
- cały projekt: `148/148` testów;
- pokrycie liniowe `lib/domain/`: `93,99%` (`720/766` linii);
- formatowanie i analiza statyczna bez problemów.

### Granice

- zmiana nie modyfikuje obliczeń domenowych ani tolerancji solvera;
- nie stanowi walidacji klinicznej;
- ręczny przegląd przypadków przez drugą osobę pozostaje oczekujący.

## [0.1.2-dev.1] — 2026-08-03

### Dodano

- wersjonowaną macierz 480 technicznych przypadków referencyjnych;
- osobny oracle dokładnej arytmetyki oparty na `BigInt`, niezależny od produkcyjnych równań;
- 600 porównań dokładnych liczników i mianowników bez tolerancji i bez zaokrągleń;
- równania bezpośrednie, odwrotne i pełne łańcuchy obliczeń;
- pokrycie `ng`, `µg`, `mg`, `g` oraz osobno `IU`, czasu `/min` i `/h`, dawek z `/kg` i bez `/kg`, a także masy w `kg` i `g`;
- wersjonowany manifest wejść z jawnym statusem ręcznego przeglądu;
- dokument `docs/TECHNICAL_REFERENCE_ORACLE.md` opisujący konstrukcję, warunki zaliczenia i ograniczenia zestawu.

### Wyniki automatycznego audytu

- wszystkie 480 przypadków i 600 porównań zakończyło się pełną zgodnością;
- cały projekt: `143/143` testy zakończone powodzeniem;
- pokrycie liniowe `lib/domain/`: `93,99%` (`720/766` linii);
- pokrycie `calculator_solver.dart`: `92,73%`;
- formatowanie i analiza statyczna bez problemów.

### Granice

- zestaw nie zawiera rekomendacji dawkowania ani interpretacji klinicznej;
- nie stanowi walidacji klinicznej;
- ręczny przegląd przez drugą osobę pozostaje oczekującą bramką.

## [0.1.1-dev.2] — 2026-08-03

### Poprawiono

- opóźniony odczyt zapisanych jednostek nie może już zmienić etykiety jednostki po wpisaniu wartości podczas uruchamiania aplikacji;
- preferencje nie są nakładane, gdy formularz zawiera jawne wejście albo nieprawidłowy tekst;
- po całkowitym wyczyszczeniu przejściowych wartości oczekujące preferencje mogą zostać bezpiecznie zastosowane;
- liczba, widoczna jednostka i wartość używana przez solver pozostają zawsze zgodne.

### Testy regresji

- szybkie wpisanie `1 mg` przed zakończeniem odczytu preferencji nadal daje `1000 µg/ml` dla `1 ml` i pozostawia etykietę `mg`;
- zapisany tryb oraz jednostka mogą zostać przywrócone, gdy użytkownik przed zakończeniem odczytu wyczyści cały formularz.

## [0.1.1-dev.1] — 2026-08-03

### Poprawiono

- przełączanie dawki `/kg` i szybkości podaży przenosi jawne wejście zamiast pozostawiać niewidoczny warunek;
- zmiana trybu bez masy pacjenta jest odrzucana z czytelnym komunikatem, dzięki czemu wpisana wartość nie znika;
- przełączanie zachowuje rodzinę IU albo jednostek masy oraz bezpiecznie dobiera zgodną jednostkę prezentacji;
- zmiana masy po przełączeniu nie zmienia wartości, którą użytkownik świadomie ustawił jako nowe wejście;
- doprecyzowano opis roli masy przy dawce `/kg`;
- wewnętrzna polityka limitów liczbowych została nazwana techniczną, zgodnie z przeznaczeniem produktu.

### Testy regresji

- przeniesienie wejścia `/kg` → bez `/kg`;
- przeniesienie wejścia bez `/kg` → `/kg`;
- odmowa ukrycia wejścia bez dostępnej masy;
- zachowanie rodziny IU podczas przełączania.

## [0.1.0] — 2026-08-03

### Wydano

- pierwszy kompletny techniczny MVP dwukierunkowego kalkulatora podaży leków;
- jeden ekran obliczający w czasie rzeczywistym bez przycisku „Oblicz”;
- pełne zależności ilość–objętość–stężenie–przepływ–szybkość podaży–dawka;
- opcjonalne `/kg`, czas `/min` albo `/h` oraz odrębną rodzinę IU;
- dokładną arytmetykę, jawne konflikty, tok obliczenia i bezpieczną zmianę jednostek;
- lokalne utrwalanie wyłącznie nieklinicznych ustawień prezentacji;
- przypięte zależności oraz obowiązkową bramkę jakości domeny w CI;
- raport zakresu, walidacji i znanych ograniczeń w `docs/RELEASE_0.1.0.md`.

### Wyniki jakości

- `127/127` testów zakończonych powodzeniem;
- `93,47%` pokrycia liniowego warstwy domenowej (`716/766` linii);
- poprawne buildy Androida i iOS;
- formatowanie i analiza statyczna bez problemów.

### Deklarowane przeznaczenie

- wersja `0.1.0` jest technicznym kalkulatorem matematycznym i jednostkowym;
- nie zawiera biblioteki leków, zaleceń dawkowania ani interpretacji klinicznej;
- nie jest przeznaczona do podejmowania decyzji klinicznych.

## [0.1.0-dev.7] — 2026-08-03

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
- wersja pozostaje technicznym kalkulatorem nieprzeznaczonym do podejmowania decyzji klinicznych.

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
