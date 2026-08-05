# InfusionCalc 0.1.4 — produkcyjna checklista SEO

**Stan na:** 5 sierpnia 2026  
**Etap:** `0.1.4-beta.1 — routing, 404 i walidacja produkcyjna`  
**Domena kanoniczna:** `https://infusioncalc.eu/`

## 1. Nienaruszalne zasady

- [x] wejście na domenę główną otwiera bezpośrednio kalkulator;
- [x] brak ekranu marketingowego, automatycznego przekierowania i dodatkowego kliknięcia;
- [x] strony opisowe pozostają zwykłymi dokumentami HTML;
- [x] brak zmian w solverze, równaniach, jednostkach, precyzji i danych formularza;
- [x] brak nowych trackerów, reklam, cookies marketingowych i identyfikatorów użytkownika;
- [x] treści nie zawierają rekomendacji dawkowania ani twierdzeń o walidacji klinicznej.

## 2. Kontrakt publicznych adresów

| Adres | Oczekiwany status | Indeksowanie | Rola |
|---|---:|---|---|
| `/` | `200` | `index,follow` | kalkulator |
| `/about/` | `200` | `index,follow` | opis techniczny i FAQ |
| `/privacy/` | `200` | `index,follow` | polityka prywatności |
| `/changelog/` | `200` | `index,follow` | historia wydań |
| `/about` | przekierowanie do `/about/` | adres pośredni | normalizacja URL |
| `/privacy` | przekierowanie do `/privacy/` | adres pośredni | normalizacja URL |
| `/changelog` | przekierowanie do `/changelog/` | adres pośredni | normalizacja URL |
| dowolny nieistniejący adres | `404` | `noindex,follow` | statyczna strona błędu |

`404.html` nie może zawierać canonical, JSON-LD ani Flutter runtime i nie może znajdować się w `sitemap.xml`.

## 3. Automatyczne bramy przed scaleniem

- [ ] formatowanie Darta;
- [ ] analiza statyczna Flutter;
- [ ] wszystkie testy Flutter;
- [ ] pokrycie warstwy domenowej co najmniej 90%;
- [ ] build Android debug APK;
- [ ] build iOS Simulator;
- [ ] produkcyjny build Flutter Web bez CDN runtime;
- [ ] walidacja canonical, Open Graph, Twitter Card, JSON-LD, robots i sitemap;
- [ ] walidacja statycznego `404.html` i jawnych tras service workera;
- [ ] test ChromeDriver: kalkulator uruchamia się online i offline;
- [ ] test ChromeDriver: `/about/`, `/privacy/` i `/changelog/` pozostają odrębnymi stronami online i offline;
- [ ] test ChromeDriver: nieistniejący URL nie staje się kalkulatorem;
- [ ] Lighthouse mobile dla czterech kanonicznych stron;
- [ ] Lighthouse desktop dla czterech kanonicznych stron.

Raporty Lighthouse są zapisywane jako artefakt CI. Początkowe progi dla Flutterowego kalkulatora są celowo łagodniejsze niż dla lekkich stron statycznych; wyniki tworzą wersjonowany punkt odniesienia do późniejszego zaostrzania.

## 4. Automatyczna kontrola po wdrożeniu

Workflow GitHub Pages po opublikowaniu wersji powinien potwierdzić:

- [ ] `pwa-build-info.json` zawiera SHA właśnie wdrożonego commitu;
- [ ] cztery adresy kanoniczne zwracają bezpośrednio `200`;
- [ ] tytuł i canonical każdego dokumentu są zgodne z kontraktem;
- [ ] warianty bez ukośnika przekierowują na adres kanoniczny;
- [ ] losowy nieistniejący adres zwraca HTTP `404` i własną stronę błędu;
- [ ] `robots.txt` wskazuje `https://infusioncalc.eu/sitemap.xml`;
- [ ] mapa zawiera dokładnie cztery kanoniczne adresy;
- [ ] obraz podglądu jest dostępny jako PNG;
- [ ] żądanie HTTP kończy się na kanonicznym adresie HTTPS;
- [ ] pełny pakiet PWA nadal przechodzi ścisłe uruchomienie bez sieci.

## 5. Google Search Console — czynności właściciela domeny

Po stabilnym wdrożeniu `0.1.4`:

- [ ] dodać usługę typu **Domena** dla `infusioncalc.eu`;
- [ ] dodać rekord TXT otrzymany od Google w panelu DNS;
- [ ] zakończyć weryfikację własności;
- [ ] przesłać `https://infusioncalc.eu/sitemap.xml`;
- [ ] sprawdzić inspekcją adresy `/` i `/about/`;
- [ ] zgłosić `/` i `/about/` do indeksacji;
- [ ] po kilku dniach skontrolować wybrany canonical, renderowanie i ewentualne błędy;
- [ ] zapisać datę pierwszego pojawienia się wyświetleń i zapytań.

Do repozytorium nie zapisujemy tokenu weryfikacyjnego DNS ani danych dostępowych do konta Google.

## 6. Bing Webmaster Tools — czynności właściciela domeny

- [ ] dodać lub zaimportować witrynę;
- [ ] zweryfikować własność domeny;
- [ ] przesłać `sitemap.xml`;
- [ ] sprawdzić `/` oraz `/about/`;
- [ ] skontrolować raport błędów indeksowania.

Do repozytorium nie zapisujemy sekretów ani danych konta Microsoft.

## 7. Kontrola podglądów i danych strukturalnych

- [ ] sprawdzić stronę główną oraz `/about/` w narzędziu podglądu Open Graph;
- [ ] potwierdzić obraz `1200 × 630`;
- [ ] zweryfikować JSON-LD strony głównej i `/about/`;
- [ ] potwierdzić brak pól sugerujących dobór terapii, dawkowanie albo walidację kliniczną;
- [ ] zapisać wynik kontroli w issue projektu bez danych uwierzytelniających.

## 8. Monitoring po wydaniu

W pierwszych czterech tygodniach po publikacji:

- [ ] raz w tygodniu sprawdzić liczbę zaindeksowanych adresów;
- [ ] sprawdzić błędy 404 i nietypowe ścieżki;
- [ ] sprawdzić, czy Google nie wybrał innego canonical;
- [ ] obserwować zapytania i współczynnik kliknięć bez sztucznego upychania słów kluczowych;
- [ ] potwierdzić, że kalkulator nadal otwiera się bezpośrednio i działa offline;
- [ ] zgłaszać regresje jako osobne issues.

## 9. Kryterium stabilnego `v0.1.4`

Wydanie jest gotowe dopiero, gdy:

1. wszystkie automatyczne bramy są zielone;
2. wdrożona domena przechodzi kontrolę statusów i metadanych;
3. fizyczny iPhone nadal uruchamia przygotowaną wersję offline;
4. mapa witryny została przesłana co najmniej do Google Search Console;
5. dokumentacja wersji i changelog są zgodne z wdrożonym kodem;
6. nie ma nierozwiązanych błędów wpływających na obliczenia, routing, prywatność albo indeksowanie.
