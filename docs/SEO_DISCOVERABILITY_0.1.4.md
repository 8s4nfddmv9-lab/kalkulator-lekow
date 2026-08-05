# InfusionCalc 0.1.4 — indeksowanie i widoczność wyszukiwarkowa

**Status:** w realizacji — `0.1.4-dev.1` i `0.1.4-dev.2` scalone; `0.1.4-beta.1` w toku
**Priorytet:** bieżący
**Charakter zmiany:** infrastruktura publikacji, statyczne treści informacyjne i walidacja SEO; bez zmian w solverze, równaniach, jednostkach i danych formularza

## Stan realizacji — 5 sierpnia 2026

- [x] ukończono i zapisano audyt bazowy;
- [x] scalono `0.1.4-dev.1` z fundamentami metadanych, robots, sitemap i walidatora;
- [x] przygotowano statyczne `/about/`, `/privacy/` i `/changelog/` z osobnymi metadanymi;
- [x] rozszerzono routing service workera i pakiet offline o strony informacyjne;
- [x] dodano dyskretne odnośniki informacyjne do stopki kalkulatora;
- [x] scalono `0.1.4-dev.2` i poprawnie wdrożono statyczne strony przez GitHub Pages;
- [x] przygotowano twardy kontrakt 404, przekierowania z końcowym ukośnikiem i testy online/offline;
- [ ] zakończyć Lighthouse, pełne CI i automatyczną walidację wdrożonej domeny.

## 1. Cel projektu

Celem wersji `0.1.4` jest umożliwienie wyszukiwarkom poprawnego odkrywania, indeksowania i opisywania InfusionCalc bez pogarszania podstawowej zalety produktu: po otwarciu `https://infusioncalc.eu/` użytkownik ma od razu otrzymać kalkulator.

Projekt nie tworzy ekranu powitalnego przed aplikacją. Strona główna pozostaje narzędziem, a treści promocyjne i objaśniające otrzymują osobny, indeksowalny adres.

## 2. Nienaruszalne decyzje produktowe

1. `https://infusioncalc.eu/` otwiera bezpośrednio kalkulator.
2. Nie dodajemy przekierowania na landing page, ekranu wejściowego, obowiązkowego przycisku „Otwórz kalkulator”, pop-upu marketingowego ani dodatkowego kroku przed formularzem.
3. Osobna strona informacyjno-promocyjna powstaje pod adresem `https://infusioncalc.eu/about/` i jest dostępna z dyskretnego odnośnika `About` w stopce kalkulatora.
4. Strona `/about/` opisuje funkcje techniczne aplikacji, działanie offline, obsługiwane wielkości i ograniczenia. Nie zawiera rekomendacji dawkowania ani twierdzeń o walidacji klinicznej.
5. Zmiana nie może wpływać na obliczenia, precyzję, solver, kolejność rozwiązywania pól ani model przechowywania danych.
6. Nie dodajemy nowych trackerów, reklam, cookies marketingowych ani identyfikatorów użytkownika.
7. Pełny tryb offline PWA musi pozostać sprawny po wdrożeniu zmian.

## 3. Docelowa architektura adresów

| Adres | Rola | Oczekiwane zachowanie |
|---|---|---|
| `/` | główna aplikacja | kalkulator widoczny od razu, bez dodatkowego kliknięcia |
| `/about/` | statyczna strona informacyjno-promocyjna | opis produktu, funkcji, działania offline, ograniczeń i FAQ |
| `/privacy/` | publiczna polityka prywatności | indeksowalna, czytelna bez uruchamiania Fluttera |
| `/changelog/` | publiczny changelog | krótka, aktualizowana historia wydań |
| `/robots.txt` | reguły indeksowania | dostępny publicznie, bez blokady właściwych stron |
| `/sitemap.xml` | mapa witryny | zawiera wyłącznie kanoniczne, publiczne adresy |

Strony informacyjne powinny być dostarczane jako statyczny HTML lub prerenderowany artefakt, a nie wyłącznie jako widok renderowany po uruchomieniu Fluttera. Pozwala to robotom odczytać treść, tytuł, opis i linki bez zależności od pełnego uruchomienia CanvasKit.

## 4. Zakres wykonawczy

### Etap A — audyt stanu wyjściowego

- [ ] zapisać aktualne odpowiedzi HTTP i kod źródłowy dla `/`;
- [ ] sprawdzić aktualne wartości `title`, `description`, `canonical`, `robots`, Open Graph i manifestu PWA;
- [ ] sprawdzić, czy `robots.txt` oraz `sitemap.xml` już istnieją;
- [ ] ustalić aktualne zachowanie bezpośrednich wejść na podstrony w GitHub Pages;
- [ ] zapisać bazowe wyniki Lighthouse i testu Rich Results / Schema Markup;
- [ ] potwierdzić, że źródłowy HTML nie zawiera `noindex` ani przypadkowej blokady crawlerów.

**Wynik etapu:** krótki raport bazowy, który pozwala wykazać brak regresji po wdrożeniu.

### Etap B — techniczne fundamenty SEO strony głównej

- [ ] ustawić jednoznaczny tytuł strony, np. `InfusionCalc — technical infusion calculator`;
- [ ] dodać zwięzły meta description zgodny z deklarowanym przeznaczeniem technicznym;
- [ ] dodać kanoniczny adres `https://infusioncalc.eu/` bez polegania na zmianie wykonywanej dopiero przez JavaScript;
- [ ] ustawić `robots` na indeksowanie i śledzenie linków;
- [ ] uzupełnić Open Graph i metadane udostępniania linku;
- [ ] dodać lokalny obraz podglądu społecznościowego bez zależności od zewnętrznego CDN;
- [ ] dodać JSON-LD typu `WebApplication` / `SoftwareApplication` z ostrożnym, technicznym opisem;
- [ ] ujednolicić nazwę, opis, `start_url`, `scope`, ikony i identyfikator w manifeście PWA;
- [ ] zachować istniejący szybki ekran startowy i natychmiastowe uruchomienie kalkulatora.

**Wynik etapu:** wyszukiwarka i serwisy udostępniania linków otrzymują poprawny opis strony głównej, mimo że jej podstawową treścią nadal jest aplikacja.

### Etap C — statyczna strona `/about/`

- [ ] przygotować responsywną stronę w języku angielskim, ponieważ jest to podstawowy język publicznego pozycjonowania domeny;
- [ ] dodać wyraźny przycisk prowadzący bezpośrednio do `/`, bez automatycznego przekierowania;
- [ ] opisać dwukierunkowe obliczenia ilości, objętości, stężenia, przepływu i dawki;
- [ ] opisać obsługę jednostek masy oraz oddzielnej rodziny `IU`;
- [ ] opisać dawki z `/kg` i bez `/kg`, na minutę i godzinę;
- [ ] opisać lokalne wykonywanie obliczeń i tryb offline PWA;
- [ ] dodać krótkie FAQ dotyczące instalacji, prywatności, działania offline i ograniczeń;
- [ ] powtórzyć deklarowane przeznaczenie techniczne i wymóg niezależnej weryfikacji wyniku;
- [ ] nie dodawać nazw leków, typowych przygotowań, zakresów dawek ani słów sugerujących dobór terapii;
- [ ] dodać unikalny `title`, opis, canonical, Open Graph i dane strukturalne;
- [ ] dodać odnośniki do kalkulatora, polityki prywatności, changelogu i GitHuba.

**Wynik etapu:** wyszukiwarki otrzymują rzeczywistą, użyteczną treść opisową, a użytkownik kalkulatora nie musi jej oglądać przed rozpoczęciem pracy.

### Etap D — pozostałe strony i nawigacja

- [ ] udostępnić politykę prywatności pod `/privacy/` jako czytelny statyczny HTML;
- [ ] udostępnić changelog pod `/changelog/` jako czytelny statyczny HTML;
- [ ] dodać `About` do obecnej stopki obok `Changelog`, `Privacy`, `GitHub` i `Contact`;
- [ ] zachować stopkę na końcu przewijanej zawartości kalkulatora;
- [ ] upewnić się, że wszystkie linki są zwykłymi, indeksowalnymi odnośnikami z poprawnym adresem docelowym;
- [ ] zapewnić sensowne zachowanie stron informacyjnych bez JavaScriptu.

### Etap E — `robots.txt`, `sitemap.xml` i kanonikalizacja

- [ ] dodać `robots.txt` zezwalający na indeksowanie publicznych stron;
- [ ] wskazać w `robots.txt` pełny adres mapy witryny;
- [ ] dodać `sitemap.xml` z `/`, `/about/`, `/privacy/` i `/changelog/`;
- [ ] umieszczać w mapie wyłącznie adresy kanoniczne zwracające `200`;
- [ ] nie wpisywać do mapy zasobów technicznych PWA, manifestów cache ani parametrów analitycznych;
- [ ] ustalić spójną politykę końcowego ukośnika i przekierowań;
- [ ] sprawdzić, że GitHub Pages nie zwraca pozornego `200` z aplikacją dla nieistniejących stron, które miałyby zostać zaindeksowane.

### Etap F — integracja z buildem, wdrożeniem i offline

- [ ] generować lub kopiować strony statyczne oraz pliki SEO w deterministycznym kroku produkcyjnego buildu;
- [ ] objąć je walidacją przed wdrożeniem GitHub Pages;
- [ ] dodać strony informacyjne i ich lokalne zasoby do wersjonowanego pakietu offline, o ile nie zwiększa to ryzyka niepełnej instalacji;
- [ ] zachować atomową instalację cache i brak mieszania plików różnych wersji;
- [ ] nie dodawać obowiązkowych zasobów zewnętrznych;
- [ ] zachować opcjonalność i izolację Umami;
- [ ] sprawdzić bezpośrednie wejście online na każdy adres oraz ponowne uruchomienie zainstalowanej aplikacji offline.

### Etap G — automatyczne testy i bramki CI

- [ ] walidator produkcyjnego artefaktu wymaga `robots.txt`, `sitemap.xml` i wszystkich stron publicznych;
- [ ] test sprawdza unikalne tytuły, opisy i kanoniczne adresy;
- [ ] test parsuje XML mapy witryny i potwierdza zgodność adresów z rzeczywistymi plikami;
- [ ] test parsuje JSON-LD i odrzuca niepoprawny JSON;
- [ ] test odrzuca `noindex` na stronach przeznaczonych do indeksowania;
- [ ] test sprawdza brak obowiązkowych zasobów zewnętrznych na starcie;
- [ ] browser smoke test otwiera `/`, `/about/`, `/privacy/` i `/changelog/`;
- [ ] test potwierdza, że `/` nadal udostępnia kalkulator bez kliknięcia w przycisk marketingowy;
- [ ] pełna dotychczasowa regresja solvera i PWA pozostaje zielona.

### Etap H — rejestracja w wyszukiwarkach

Część tego etapu wymaga ręcznego dostępu właściciela domeny.

- [ ] dodać domenę `infusioncalc.eu` jako usługę domenową w Google Search Console;
- [ ] zweryfikować własność domeny rekordem DNS;
- [ ] przesłać `https://infusioncalc.eu/sitemap.xml`;
- [ ] sprawdzić `/` i `/about/` narzędziem kontroli adresu URL oraz poprosić o indeksowanie;
- [ ] dodać i zweryfikować witrynę w Bing Webmaster Tools, ewentualnie importując weryfikację z Google Search Console;
- [ ] przesłać sitemapę do Bing;
- [ ] po pierwszym crawl sprawdzić błędy indeksowania, canonical, renderowanie i dane strukturalne;
- [ ] nie traktować samego przesłania mapy jako gwarancji pozycji w wynikach.

IndexNow pozostaje opcją przyszłą. Przy kilku rzadko zmienianych stronach nie jest wymagany do wydania `0.1.4`.

### Etap I — publikacja i obserwacja

- [ ] wykonać produkcyjny deploy na osobnej wersji kandydującej;
- [ ] przeprowadzić kontrolę na fizycznym iPhonie i co najmniej jednej przeglądarce desktopowej;
- [ ] potwierdzić uruchomienie kalkulatora offline po aktualizacji;
- [ ] potwierdzić poprawny podgląd linku w co najmniej jednym komunikatorze;
- [ ] zapisać stan indeksacji po wdrożeniu, bez deklarowania gwarantowanego terminu pojawienia się w wynikach;
- [ ] wydać stabilne `v0.1.4` po zielonym CI i ręcznej kontroli produkcji.

## 5. Proponowane wydania robocze

### `0.1.4-dev.1` — fundamenty i walidator

- audyt bazowy;
- metadane strony głównej;
- canonical, Open Graph i JSON-LD;
- `robots.txt` i `sitemap.xml`;
- pierwsze testy artefaktu.

### `0.1.4-dev.2` — strony statyczne

- `/about/`;
- `/privacy/`;
- `/changelog/`;
- odnośnik `About` w stopce;
- unikalne metadane i linkowanie wewnętrzne.

### `0.1.4-beta.1` — integracja produkcyjna

- pełna integracja z GitHub Pages i cache offline;
- testy bezpośrednich wejść;
- testy na urządzeniach;
- poprawki wykryte przez Lighthouse i walidatory.

### `0.1.4` — wydanie stabilne

- publiczne pliki SEO i strony informacyjne;
- brak regresji kalkulatora i offline;
- zweryfikowana własność w Google Search Console i Bing Webmaster Tools lub jasno udokumentowany pozostały krok właściciela domeny;
- przesłana sitemap;
- dokumentacja wydania i aktualizacja changelogu.

## 6. Kryteria ukończenia projektu

Projekt jest ukończony dopiero, gdy łącznie spełnione są następujące warunki:

- wejście na `https://infusioncalc.eu/` nadal pokazuje kalkulator bez dodatkowego kroku;
- `/about/`, `/privacy/` i `/changelog/` działają jako odrębne, indeksowalne strony o unikalnych metadanych;
- `robots.txt` i `sitemap.xml` są publiczne, poprawne i objęte testami;
- canonical oraz linki wewnętrzne są spójne;
- dane strukturalne przechodzą walidację składni;
- nie dodano nowych trackerów ani danych formularza do analityki;
- pełny pakiet PWA pozostaje samowystarczalny i działa offline;
- dotychczasowe testy domeny, precyzji, UI i offline pozostają zielone;
- Search Console i Bing Webmaster Tools mają zweryfikowaną domenę oraz przesłaną sitemapę albo dokumentacja wskazuje jedyny pozostały ręczny krok;
- wydanie ma zapisany raport wdrożenia i ograniczeń.

## 7. Poza zakresem `0.1.4`

- ekran powitalny lub obowiązkowy landing page przed kalkulatorem;
- blog tworzony wyłącznie dla słów kluczowych;
- masowe strony pod nazwy leków, dawki lub konkretne terapie;
- płatne reklamy i kampanie marketingowe;
- nowe systemy analityczne, profile użytkowników i remarketing;
- obietnica konkretnej pozycji lub terminu indeksacji;
- zmiana deklarowanego przeznaczenia na kliniczne;
- biblioteka leków, rekomendacje dawkowania i interpretacja wyników;
- przebudowa interfejsu kalkulatora niezwiązana bezpośrednio z linkiem `About` i semantyką publikacji.

## 8. Ryzyka i sposoby ograniczenia

| Ryzyko | Ograniczenie |
|---|---|
| treść Flutter CanvasKit jest słabo dostępna w źródłowym HTML | kluczowa treść opisowa jako statyczne `/about/`, poprawne metadane w oryginalnym HTML |
| SEO zaczyna utrudniać szybkie użycie kalkulatora | brak landingu na `/`, brak przekierowania i brak dodatkowego kliknięcia |
| GitHub Pages błędnie obsługuje bezpośrednie wejścia | fizyczne katalogi z `index.html` oraz testy odpowiedzi dla każdego adresu |
| nowe pliki psują atomowy cache offline | włączenie do istniejącego manifestu, walidacja kompletności i test ponownego uruchomienia offline |
| opis produktu sugeruje zastosowanie kliniczne | zatwierdzony neutralny język techniczny i powtórzenie ograniczeń |
| mapa witryny zawiera niekanoniczne lub nieistniejące adresy | automatyczne parsowanie i porównanie z artefaktem produkcyjnym |
| zewnętrzny obraz lub skrypt blokuje start | wszystkie wymagane zasoby lokalne; Umami pozostaje opcjonalne |

## 9. Oficjalne materiały referencyjne

- Google Search Central — crawling and indexing: https://developers.google.com/search/docs/crawling-indexing
- Google Search Central — JavaScript SEO basics: https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics
- Google Search Central — sitemaps: https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
- Bing Webmaster Tools — sitemaps: https://www.bing.com/webmasters/help/sitemaps-3b5cf6ed
- Bing Webmaster Tools — URL inspection: https://www.bing.com/webmasters/help/URL-Inspection-55a30305
- Schema.org — WebApplication: https://schema.org/WebApplication
- Schema.org — SoftwareApplication: https://schema.org/SoftwareApplication
