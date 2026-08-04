# Roadmapa — InfusionCalc

**Stan na:** 4 sierpnia 2026  
**Aktualny etap:** `0.1.3-beta.5 — poprawka startu offline na iOS`

Roadmapa opisuje plan produktu od specyfikacji do stabilnej wersji 1.0. Numery i zakresy kolejnych wydań mogą być korygowane w miarę wyników testów, oceny regulacyjnej i informacji od użytkowników, ale zasady bezpieczeństwa domenowego pozostają obowiązujące od początku.

## Zasady prowadzenia projektu

- najpierw poprawność modelu i jednostek, później wygoda oraz dodatkowe funkcje;
- silnik obliczeniowy pozostaje niezależny od interfejsu;
- techniczne MVP nie zawiera rekomendacji dawkowania ani interpretacji klinicznej;
- brak cichego nadpisywania danych i ukrytych założeń;
- każda zmiana wpływająca na matematykę wymaga nowych lub zaktualizowanych testów;
- biblioteka leków oraz rekomendacje dawkowania nie wchodzą do MVP;
- publiczna dystrybucja kliniczna jest osobną bramką decyzyjną, a nie automatycznym następstwem ukończenia kodu.

---

## 0.0.x — Fundament projektu

### 0.0.1 — Wizja, zakres i roadmapa **✓ ukończono**

**Cel:** utrwalić decyzje produktowe przed rozpoczęciem implementacji.

Zakres:

- [x] definicja głównej idei aplikacji;
- [x] zatwierdzenie dynamicznego, dwukierunkowego modelu obliczeń;
- [x] zatwierdzenie opcjonalnego członu `/kg`;
- [x] ustalenie, że masa pacjenta jest wyłącznie wejściem;
- [x] rozdzielenie IU i jednostek masy;
- [x] określenie zakresu MVP;
- [x] wybór Fluttera i Darta jako planowanego stosu;
- [x] przygotowanie `README.md`;
- [x] przygotowanie `docs/VISION.md`;
- [x] przygotowanie `ROADMAP.md`.

**Kryterium ukończenia:** dokumentacja znajduje się w repozytorium i stanowi punkt odniesienia dla pierwszych decyzji architektonicznych.

### 0.0.2 — Specyfikacja techniczna domeny **✓ ukończono**

**Cel:** zamienić wizję w jednoznaczny kontrakt implementacyjny.

Zakres:

- [x] katalog wszystkich typów wielkości i jednostek;
- [x] kanoniczne jednostki wewnętrzne;
- [x] zasady konwersji i kontroli wymiarowej;
- [x] formalny graf zależności między polami;
- [x] algorytm wyboru wejść i wyników;
- [x] model pochodzenia wartości;
- [x] model konfliktów i danych nadmiarowych;
- [x] polityka precyzji obliczeń;
- [x] polityka formatowania wyników;
- [x] tolerancje porównań;
- [x] katalog błędów oraz komunikatów użytkownika;
- [x] zestaw pierwszych przypadków referencyjnych.

**Kryterium ukończenia:** każda relacja matematyczna i każda zmiana stanu pola są opisane bez pozostawiania decyzji warstwie UI.

### 0.0.3 — Projekt UX i prototyp ekranu **✓ ukończono**

**Cel:** zweryfikować obsługę kalkulatora przed implementacją pełnej logiki.

Zakres:

- [x] makieta jednego głównego ekranu;
- [x] sposób odróżniania wejścia od wyniku;
- [x] selektory jednostek;
- [x] włącznik `/kg`;
- [x] wybór `/min` lub `/h`;
- [x] sposób przejęcia pola wynikowego do edycji;
- [x] komunikaty o brakujących danych;
- [x] widok konfliktu wartości;
- [x] rozwijany tok obliczenia;
- [x] zachowanie klawiatury numerycznej;
- [x] sprawdzenie małych ekranów, dużego tekstu i trybu ciemnego.

**Kryterium ukończenia:** na prototypie da się przejść przez główne scenariusze bez dodatkowego ekranu i bez osobnego trybu obliczenia.

---

## 0.1.x — MVP silnika i kalkulatora

### 0.1.0-dev.1 — Szkielet aplikacji **✓ ukończono**

**Cel:** uruchomić projekt Flutter i podstawowy pipeline jakości.

Zakres:

- [x] utworzenie aplikacji Flutter;
- [x] konfiguracja Androida i iOS;
- [x] struktura warstw `domain`, `application`, `presentation`;
- [x] analiza statyczna i linting;
- [x] podstawowy GitHub Actions;
- [x] test uruchomieniowy na obu platformach;
- [x] brak zależności silnika domenowego od Flutter UI.

### 0.1.0-dev.2 — Typy wielkości i jednostek **✓ ukończono**

**Cel:** stworzyć bezpieczny fundament obliczeń.

Zakres:

- [x] ilość leku wyrażona masą: ng, µg, mg, g;
- [x] aktywność biologiczna: IU;
- [x] objętość: ml;
- [x] masa pacjenta: g i kg;
- [x] czas: min i h;
- [x] przepływ: ml/h;
- [x] dawka z opcjonalnym `/kg`;
- [x] jawne rodziny wymiarów;
- [x] konwersje zachowujące wielkość fizyczną;
- [x] arytmetyka dziesiętna;
- [x] blokada konwersji IU ↔ jednostki masy.

**Kryteria akceptacji:**

- wszystkie konwersje przechodzą testy;
- niedozwolona konwersja kończy się kontrolowanym błędem domenowym;
- zmiana jednostki i powrót do poprzedniej odtwarzają tę samą wielkość;
- masa pacjenta nie ma ścieżki obliczeniowej jako wynik.

### 0.1.0-dev.3 — Równania podstawowe **✓ ukończono**

**Cel:** zaimplementować komplet dwukierunkowych zależności.

Zakres:

- [x] ilość + objętość ↔ stężenie;
- [x] stężenie + przepływ ↔ szybkość podaży;
- [x] dawka + masa ↔ szybkość podaży, z wyłączeniem wyliczania masy;
- [x] konwersja czasu `/min` ↔ `/h`;
- [x] czas infuzji z objętości i przepływu;
- [x] obliczenia kaskadowe;
- [x] rejestrowanie toku i źródeł wyniku.

**Kryteria akceptacji:**

- każdy wzór ma testy bezpośrednie i odwrotne;
- brak zaokrągleń pośrednich;
- wynik kaskadowy jest zgodny z wynikiem bezpośrednim;
- obliczenia bez `/kg` nie wymagają masy;
- obliczenia z `/kg` bez masy pozostają niedookreślone.

### 0.1.0-dev.4 — Dynamiczny solver formularza **✓ ukończono**

**Cel:** pozwolić użytkownikowi zaczynać od dowolnego zestawu danych.

Zakres:

- [x] źródło wartości: użytkownik lub obliczenie;
- [x] kolejność ostatniej edycji;
- [x] automatyczny wybór wartości wynikowych;
- [x] ponowne rozwiązanie po zmianie jednostki;
- [x] przejmowanie pola wynikowego przez użytkownika;
- [x] obsługa układu niedookreślonego;
- [x] obsługa danych nadmiarowych;
- [x] wykrywanie konfliktów;
- [x] brak pętli i oscylacji stanu;
- [x] deterministyczne zachowanie niezależnie od platformy.

**Kryteria akceptacji:**

- każda wspierana sekwencja edycji ma test stanu;
- aplikacja nigdy nie nadpisuje jawnego wejścia bez działania użytkownika;
- sprzeczne dane generują konflikt zamiast wyniku udającego poprawny;
- masa pozostaje tylko wejściem w każdym scenariuszu.

### 0.1.0-dev.5 — Interfejs MVP **✓ ukończono**

**Cel:** połączyć silnik z jednym, szybkim ekranem.

Zakres:

- [x] pole masy pacjenta;
- [x] pola ilości, objętości i stężenia;
- [x] pola przepływu i dawki;
- [x] opcjonalne `/kg`;
- [x] wybór `/min` lub `/h`;
- [x] wyróżnienie wartości wyliczonych;
- [x] wskazanie brakujących danych;
- [x] prezentacja konfliktu;
- [x] szczegóły wzoru i podstawienia;
- [x] przycisk „Wyczyść”;
- [x] kopiowanie wyniku razem z jednostką;
- [x] przecinek i kropka jako separator;
- [x] działanie w trybie jasnym i ciemnym.

### 0.1.0-dev.6 — Utrwalanie ustawień i obsługa błędów **✓ ukończono**

**Cel:** dopracować codzienną użyteczność bez przechowywania danych pacjenta.

Zakres:

- [x] zapamiętywanie ostatnio wybranych jednostek;
- [x] jawna decyzja dotycząca przywracania wartości po restarcie;
- [x] walidacja zakresów technicznych;
- [x] ochrona przed zerem w dzielniku;
- [x] ochrona przed wartościami ujemnymi;
- [x] bezpieczne zachowanie przy bardzo małych i bardzo dużych liczbach;
- [x] czytelne komunikaty domenowe;
- [x] brak zewnętrznej analityki i transmisji danych.

**Decyzja o restarcie:** przywracane są wyłącznie jednostki i tryb `/kg`; wszystkie wartości liczbowe zawsze pozostają puste.

### 0.1.0-dev.7 — Testy referencyjne i utwardzenie **✓ ukończono**

**Cel:** zakończyć MVP dopiero po pokryciu pełnego modelu testami.

Zakres:

- [x] przypadki referencyjne dla każdej jednostki;
- [x] testy odwracalności;
- [x] testy właściwości;
- [x] testy konfliktów;
- [x] testy kolejności edycji;
- [x] testy obliczeń kaskadowych;
- [x] testy lokalizacji separatora dziesiętnego;
- [x] testy widgetów;
- [x] testy integracyjne głównych scenariuszy;
- [x] minimalny próg pokrycia kodu domenowego;
**Stan automatycznej walidacji:** `127/127` testów, `93,47%` pokrycia warstwy domenowej oraz poprawne buildy Androida i iOS.

**Pozycjonowanie produktu:** obecna wersja jest technicznym kalkulatorem przeliczeń. Nie zawiera zaleceń ani interpretacji klinicznej i nie jest przeznaczona do podejmowania decyzji klinicznych.

**Przyszła bramka kliniczna:** ręczny przegląd wzorów przez drugą osobę pozostaje wymagany przed ewentualną zmianą deklarowanego przeznaczenia w kierunku zastosowania klinicznego; nie blokuje wydania technicznego kalkulatora.

### 0.1.0 — Pierwsze kompletne MVP **✓ ukończono**

**Zakres wydania:**

- jeden ekran;
- pełny dynamiczny kalkulator;
- działanie offline;
- jednostki ng, µg, mg, g i IU;
- przepływ ml/h;
- dawki na minutę lub godzinę, z `/kg` albo bez `/kg`;
- brak biblioteki leków i rekomendacji;
- pełny tok obliczenia;
- testy automatyczne i zestaw referencyjny.

**Bramka wydania:** wersja `0.1.0` została oznaczona wyłącznie jako techniczny kalkulator bez zaleceń klinicznych. Ewentualne przyszłe przeznaczenie kliniczne wymaga osobnej decyzji, niezależnej walidacji i oceny sposobu dystrybucji.

**Raport wydania:** [`docs/RELEASE_0.1.0.md`](docs/RELEASE_0.1.0.md).

---

## 0.1.x — Stabilizacja MVP

### 0.1.1 — Poprawki po testach wewnętrznych **✓ ukończono**

- [x] poprawki błędów obliczeń i stanu;
- [x] doprecyzowanie komunikatów;
- [ ] korekty formatowania;
- [x] testy regresji dla każdego znalezionego błędu;
- [x] dokumentacja znanych ograniczeń.

**Pierwsza poprawka:** bezpieczne, transakcyjne przełączanie dawki `/kg` i szybkości podaży bez pozostawiania niewidocznych wejść.

**Druga poprawka:** opóźniony odczyt preferencji nie może zmienić jednostki prezentacji po rozpoczęciu wpisywania danych; zapobiega to rozbieżności między widoczną liczbą a wartością solvera.

### 0.1.2 — Audyt domeny i precyzji **✓ audyt automatyczny ukończony**

- [x] wersjonowana macierz 480 przypadków referencyjnych;
- [x] niezależny oracle dokładnej arytmetyki oparty na `BigInt`;
- [x] 600 porównań liczników i mianowników bez tolerancji;
- [x] równania bezpośrednie, odwrotne i pełne łańcuchy;
- [x] rodziny jednostek masy oraz odrębnie IU;
- [x] czas `/min` i `/h`, dawki z `/kg` i bez `/kg`;
- [x] automatyczny raport konstrukcji i ograniczeń zestawu;
- [ ] ręczny przegląd macierzy i wzorów przez drugą osobę;
- [x] osobny audyt polityki zaokrągleń warstwy prezentacji;
- [ ] dodatkowy zestaw przypadków zgłoszonych w testach wewnętrznych.

**Stan automatyczny:** 480/480 przypadków domenowych, 600/600 dokładnych porównań, 31/31 przypadków precyzji prezentacji, 148/148 testów oraz 93,99% pokrycia domeny.

**Wykryta poprawka:** normalizacja przeniesienia w zapisie naukowym (`10e-20` → `1e-19`) bez zmiany dokładnej wartości.

**Dokumentacja:** [`docs/TECHNICAL_REFERENCE_ORACLE.md`](docs/TECHNICAL_REFERENCE_ORACLE.md) i [`docs/DISPLAY_PRECISION_POLICY.md`](docs/DISPLAY_PRECISION_POLICY.md).

### 0.1.2-beta.1 — Pierwsza wewnętrzna beta iOS **✓ ukończono i zarchiwizowano**

- [x] wersja `0.1.2-beta.1+13`;
- [x] automatyczny build urządzeniowy iOS na runnerze macOS;
- [x] niepodpisane IPA publikowane jako GitHub Actions artifact;
- [x] suma SHA-256 i metadane buildu;
- [x] stały bazowy bundle ID;
- [x] brak danych Apple ID i materiałów podpisujących w GitHubie;
- [x] instrukcja lokalnego podpisania darmowym Apple ID na Windowsie;
- [x] dystrybucja instalacyjna Androida odłożona;
- [ ] poprawny przebieg workflow na `main`;
- [ ] podpisanie IPA i instalacja na fizycznym iPhonie;
- [ ] uruchomienie podstawowych scenariuszy testowych na urządzeniu;
- [ ] zebranie pierwszych uwag UX przed rozpoczęciem kolejnych funkcji.

**Model dystrybucji:** GitHub Actions tworzy niepodpisane IPA, a Sideloadly lokalnie tworzy 7-dniowy podpis Personal Team i instaluje aplikację.

**Dokumentacja archiwalna:** [`docs/IOS_FREE_APPLE_ID_INSTALL.md`](docs/IOS_FREE_APPLE_ID_INSTALL.md) i [`docs/IOS_INTERNAL_BETA_0.1.2.md`](docs/IOS_INTERNAL_BETA_0.1.2.md).

### 0.1.2-beta.2 — Publiczne PWA **✓ ukończono**

- [x] produkcyjny build Flutter Web;
- [x] manifest PWA, ikona i tryb `standalone`;
- [x] service worker i wersjonowany cache offline;
- [x] automatyczne wdrożenie przez GitHub Pages;
- [x] własna domena `https://infusioncalc.eu/`;
- [x] wymuszony HTTPS;
- [x] stopka `Changelog`, `Privacy`, `GitHub`, `Contact`;
- [x] centralne issue #18 do zbierania feedbacku;
- [x] archiwizacja automatycznych workflow mini-PC i niepodpisanego IPA;
- [ ] zebranie oraz klasyfikacja pierwszych uwag użytkowych;
- [ ] ręczny przegląd formularza na różnych modelach iPhone'a i iPada;
- [ ] decyzja o zakresie kolejnego wydania na podstawie feedbacku.

**Główna dystrybucja:** GitHub Pages jako publiczne PWA. Mini-PC/Tailscale oraz niepodpisane IPA pozostają wyłącznie ręcznymi ścieżkami archiwalnymi.

**Dokumentacja:** [`DEPLOYMENT.md`](DEPLOYMENT.md), [`docs/PRIVACY.md`](docs/PRIVACY.md) i [issue #18](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18).

### 0.1.2-beta.3 — Pierwsze poprawki UX **✓ ukończono**

- [x] wpisanie `,` lub `.` w pustym polu tworzy `0,`;
- [x] przejściowe prefiksy `0`, `0,`, `0,0` nie zamykają klawiatury;
- [x] fokus pola jest stabilny podczas przebudowy interfejsu;
- [x] kasowanie ułamka nie przerywa edycji na iPhonie;
- [x] walidacja zera lub niedokończonego separatora następuje po opuszczeniu pola;
- [x] testy regresji fokusu, klawiatury i formatowania separatora;
- [x] potwierdzenie poprawki na fizycznym iPhonie w publicznym PWA.

**Zgłoszenie:** [issue #29](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/29).

### 0.1.3-beta.1 — Kontekstowa instalacja PWA **✓ ukończono**

- [x] przycisk „Dodaj do ekranu głównego” pod nagłówkiem na urządzeniach mobilnych;
- [x] wykrywanie iPhone'a, iPada, Androida i trybu `standalone`;
- [x] natywny prompt instalacji na obsługiwanych przeglądarkach Androida;
- [x] instrukcja ręczna na Androidzie, gdy prompt nie jest dostępny;
- [x] instrukcja Safari na iOS i iPadOS z czytelną ikoną „Udostępnij”;
- [x] informacja o konieczności użycia Safari w innych przeglądarkach iOS;
- [x] automatyczne ukrycie zachęty w zainstalowanej wersji PWA;
- [x] „Nie teraz” zapisujące lokalne odroczenie na 30 dni;
- [x] aktualizacja informacji o prywatności;
- [x] osobny produkcyjny build Flutter Web w CI;
- [x] testy widgetowe wszystkich ścieżek instalacji i ukrywania komunikatu;
- [ ] test instalacji natywnej na co najmniej jednym urządzeniu z Androidem;
- [ ] końcowe potwierdzenie instrukcji na fizycznym iPhonie po wdrożeniu.

**Zgłoszenie:** [issue #32](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/32).

### 0.1.3-beta.2 — Porządek nagłówka i układu strony **✓ ukończono**

- [x] nazwa `InfusionCalc` w nagłówku aplikacji;
- [x] stopka przeniesiona do końca przewijanej zawartości;
- [x] pełny komunikat ostrzegawczy ukryty z głównego ekranu;
- [x] pojedyncza ikona ostrzeżenia wyrównana do lewej;
- [x] prawa część wiersza zarezerwowana pod przyszły wybór języka;
- [x] okno ostrzeżenia z pełną treścią i przyciskiem `Rozumiem`;
- [x] testy nagłówka, okna ostrzeżenia i położenia stopki;
- [ ] potwierdzenie układu na fizycznym iPhonie oraz Androidzie po wdrożeniu.

**Zgłoszenie:** [issue #34](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/34).

### 0.1.3-beta.3 — Prywatna analityka produktu **✓ ukończono**

- [x] Umami Cloud ograniczone do domeny `infusioncalc.eu`;
- [x] automatyczne statystyki odsłon;
- [x] zamknięta lista ośmiu zdarzeń użyteczności;
- [x] wersja, platforma, tryb PWA i metoda instalacji jako jedyne własne wymiary;
- [x] brak dostępu analityki do formularza i modelu obliczeniowego;
- [x] brak `umami.identify` i własnych identyfikatorów użytkownika;
- [x] bezpieczne działanie przy blokadzie trackera i offline;
- [x] zaktualizowana polityka prywatności i dokumentacja analityki;
- [x] walidacja produkcyjnego builda PWA i testy zdarzeń;
- [ ] potwierdzenie pierwszych odsłon i zdarzeń w panelu Umami Cloud po wdrożeniu.

**Zgłoszenie:** [issue #36](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/36).

### 0.1.3-beta.4 — Pełny tryb offline PWA **✓ ukończono, wykryto regresję iOS**

- [x] automatyczny manifest wszystkich lokalnych plików produkcyjnego buildu;
- [x] wstępne zapisanie kodu Fluttera, assetów, fontów, ikon i rendererów;
- [x] atomowa instalacja kompletnej paczki wersji;
- [x] osobny cache dla każdego buildu;
- [x] strategia `cache-first` bez mieszania plików różnych wersji;
- [x] aktualizacja service workera po odzyskaniu internetu;
- [x] działanie kalkulatora niezależne od Umami;
- [x] polityka prywatności obejmująca code-only offline cache;
- [x] testy narzędzi i pełna walidacja artefaktu w CI;
- [x] dokumentowana procedura testu na iPhonie i Androidzie;
- [ ] potwierdzenie uruchomienia i obliczeń w trybie samolotowym na fizycznym iPhonie;
- [ ] potwierdzenie uruchomienia i obliczeń offline na fizycznym urządzeniu z Androidem.

**Zgłoszenie:** [issue #38](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/38).  
**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3-beta.5 — Poprawka startu offline na iOS **← obecnie**

- [x] potwierdzenie przyczyny: kompletny worker pozostawał w stanie `waiting` za starszą wersją;
- [x] `skipWaiting()` po pełnym, atomowym precache;
- [x] `clients.claim()` po aktywacji bez automatycznego przeładowania formularza;
- [x] wykluczenie `.last_build_id` i innych ukrytych metadanych z manifestu offline;
- [x] odporniejsze dopasowanie cache dla Safari;
- [x] test pierwszej kontroli strony bez opuszczania originu;
- [x] diagnostyczny ekran `BOOT_TIMEOUT` / `BOOT_RUNTIME_ERROR`;
- [x] pełna walidacja w CI i przed deployem GitHub Pages;
- [ ] potwierdzenie uruchomienia i obliczeń w trybie samolotowym na fizycznym iPhonie;
- [ ] potwierdzenie uruchomienia i obliczeń offline na fizycznym urządzeniu z Androidem.

**Zgłoszenie:** [issue #40](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/40).  
**Dokumentacja:** [`docs/OFFLINE_PWA.md`](docs/OFFLINE_PWA.md).

### 0.1.3 — Dostępność i ergonomia

- [ ] duże rozmiary tekstu;
- [ ] czytniki ekranowe;
- [ ] kontrast i tryb ciemny;
- [ ] ergonomia obsługi jedną ręką;
- [ ] obsługa różnych rozmiarów ekranów;
- [ ] ograniczenie przypadkowych zmian jednostki;
- [ ] haptyczne lub wizualne potwierdzenie konfliktu bez polegania wyłącznie na kolorze.

---

## 0.2.0 — Użyteczność codzienna

**Cel:** przyspieszyć powtarzalne obliczenia bez dodawania rekomendacji klinicznych.

Planowany zakres:

- [ ] własne zapisane przygotowania użytkownika;
- [ ] edycja, duplikowanie i usuwanie przygotowań;
- [ ] oznaczanie ulubionych;
- [ ] lokalna historia ostatnich obliczeń;
- [ ] szybkie odtworzenie obliczenia;
- [ ] eksport lub udostępnienie wyniku wraz z jednostkami i wzorem;
- [ ] wyraźne rozróżnienie danych zapisanych przez użytkownika od treści dostarczanych przez aplikację;
- [ ] możliwość całkowitego wyłączenia historii;
- [ ] brak danych identyfikujących pacjenta.

**Bramka:** zapisane przygotowania są wyłącznie wartościami użytkownika; aplikacja nie oznacza ich jako zalecane ani standardowe.

---

## 0.3.0 — Rozszerzone obliczenia infuzji

**Cel:** dodać powiązane kalkulatory bez zmiany neutralnego charakteru produktu.

Planowany zakres:

- [ ] ilość leku podana w zadanym czasie;
- [ ] objętość podana w zadanym czasie;
- [ ] pozostały czas wlewu;
- [ ] ilość leku pozostająca w roztworze;
- [ ] przygotowanie roztworu dla zadanej dawki i przepływu;
- [ ] porównanie dwóch wariantów przygotowania;
- [ ] opcjonalne `ml/min`;
- [ ] dodatkowe jednostki objętości po analizie potrzeb;
- [ ] osobny moduł bolusa, pod warunkiem przygotowania odrębnej specyfikacji i analizy ryzyka.

---

## 0.4.0 — Personalizacja i wielojęzyczność

**Cel:** przygotować aplikację do szerszych testów użytkowych.

Planowany zakres:

- [ ] język polski i angielski;
- [ ] spójny zapis `µg` oraz alternatywna etykieta `mcg`;
- [ ] ustawienia domyślnych jednostek;
- [ ] wybór sposobu formatowania liczb;
- [ ] opcjonalny tryb kompaktowy;
- [ ] lepsza obsługa tabletów;
- [ ] onboarding pokazujący model działania bez sugerowania dawek;
- [ ] sekcja ograniczeń i bezpieczeństwa dostępna z kalkulatora.

---

## 0.5.0 — Zamknięta beta i walidacja użytkowa

**Cel:** sprawdzić poprawność, zrozumiałość i odporność produktu w kontrolowanej grupie testowej.

Planowany zakres:

- [ ] formalny plan testów beta;
- [ ] zanonimizowany mechanizm zgłaszania błędów bez automatycznej analityki;
- [ ] scenariusze testowe dla różnych kolejności wpisywania danych;
- [ ] testy użyteczności z docelowymi użytkownikami;
- [ ] rejestr nieporozumień jednostek i błędów obsługi;
- [ ] korekty interfejsu wynikające z obserwacji;
- [ ] niezależna weryfikacja przypadków referencyjnych;
- [ ] raport z walidacji użyteczności;
- [ ] zamrożenie krytycznego API domeny przed kandydatem do wydania.

---

## 0.6.0 — Bramka regulacyjna i model dystrybucji

**Cel:** podjąć świadomą decyzję, czym produkt jest i w jaki sposób może być udostępniany.

Planowany zakres:

- [ ] ostateczne intended purpose;
- [ ] docelowi użytkownicy i środowisko użycia;
- [ ] analiza kwalifikacji jako oprogramowania medycznego;
- [ ] analiza klasyfikacji i wymaganej ścieżki zgodności;
- [ ] analiza ryzyka produktu;
- [ ] strategia cyklu życia, zmian i wersjonowania;
- [ ] wymagania dokumentacji technicznej;
- [ ] strategia nadzoru po wydaniu;
- [ ] wymagania App Store i Google Play;
- [ ] decyzja: prototyp prywatny, narzędzie edukacyjne, produkt profesjonalny lub inny model;
- [ ] konsultacja z kompetentnym specjalistą regulacyjnym.

**Bramka:** bez zakończenia tego etapu aplikacja nie jest przedstawiana jako zwalidowane narzędzie do zastosowania klinicznego.

---

## 0.7.0 — Przygotowanie produkcyjne

Zakres zależny od decyzji z wersji 0.6.0:

- [ ] finalizacja dokumentacji jakościowej;
- [ ] procedura zarządzania zmianą;
- [ ] rejestr zagrożeń i kontroli ryzyka;
- [ ] cyberbezpieczeństwo i zależności;
- [ ] polityka prywatności;
- [ ] obsługa zgłoszeń i incydentów;
- [ ] kopie materiałów sklepowych;
- [ ] podpisywanie i konfiguracja wydań;
- [ ] TestFlight i zamknięty kanał Android;
- [ ] odtwarzalne buildy;
- [ ] lista wspieranych wersji systemów.

---

## 0.8.0 — Release candidate

**Cel:** zamrozić zakres funkcjonalny i skupić się wyłącznie na jakości wydania.

- [ ] brak nowych funkcji;
- [ ] pełna regresja;
- [ ] testy na urządzeniach fizycznych;
- [ ] ponowna weryfikacja wszystkich wzorów;
- [ ] przegląd dostępności;
- [ ] przegląd komunikatów bezpieczeństwa;
- [ ] przegląd dokumentacji użytkownika;
- [ ] przegląd zależności i licencji;
- [ ] usunięcie lub jawne zaakceptowanie wszystkich błędów blokujących;
- [ ] finalna decyzja `go / no-go`.

---

## 0.9.0 — Kandydat do wersji 1.0

- [ ] wydanie do ograniczonej grupy docelowej;
- [ ] monitoring zgłoszeń zgodny z ustalonym modelem prywatności;
- [ ] wyłącznie poprawki błędów;
- [ ] finalne testy instalacji, aktualizacji i migracji ustawień;
- [ ] potwierdzenie gotowości obu sklepów lub wybranego kanału dystrybucji.

---

## 1.0.0 — Stabilna wersja

Wersja 1.0 oznacza produkt o ustalonym przeznaczeniu, zweryfikowanym modelu matematycznym, udokumentowanym procesie jakości i świadomie wybranym sposobie dystrybucji.

Minimalne warunki:

- [ ] pełny, stabilny kalkulator dwukierunkowy;
- [ ] komplet wspieranych jednostek i ich testów;
- [ ] opcjonalne `/kg`;
- [ ] masa wyłącznie jako wejście;
- [ ] IU całkowicie oddzielone od jednostek masy;
- [ ] brak niejawnych wartości i cichego nadpisywania;
- [ ] pełny tok obliczenia;
- [ ] udokumentowana precyzja i formatowanie;
- [ ] niezależnie zweryfikowane przypadki referencyjne;
- [ ] testy regresji i integracji;
- [ ] dostępność i obsługa wspieranych urządzeń;
- [ ] decyzja regulacyjna i spełnienie wynikających z niej wymagań;
- [ ] dokumentacja użytkownika;
- [ ] procedura zgłaszania błędów i utrzymania produktu.

---

## Pomysły po 1.0 — poza zatwierdzonym zakresem

Poniższe funkcje nie są obietnicą ani częścią aktualnego zakresu:

- biblioteka leków i standardowych przygotowań;
- instytucjonalne zestawy konfiguracji;
- zakresy dawek i ostrzeżenia kliniczne;
- integracja z pompami infuzyjnymi;
- integracja z systemami szpitalnymi;
- skanowanie etykiet lub kodów;
- profile specjalistyczne, np. anestezjologia, intensywna terapia, pediatria;
- synchronizacja między urządzeniami;
- zarządzanie treścią kliniczną i jej wersjonowaniem.

Każdy z tych kierunków wymaga osobnej analizy ryzyka, potrzeb użytkownika i konsekwencji regulacyjnych.

## Najbliższy krok

Po publikacji dokumentacji kolejnym etapem jest `0.0.2`: szczegółowa specyfikacja domeny, jednostek, precyzji oraz algorytmu dynamicznego solvera. Dopiero po jej zatwierdzeniu należy utworzyć szkielet aplikacji Flutter.
