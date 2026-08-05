# InfusionCalc 0.1.4 — audyt bazowy indeksowania i widoczności

**Data audytu:** 4 sierpnia 2026  
**Audytowana wersja aplikacji:** `0.1.3+22`  
**Repozytorium:** `8s4nfddmv9-lab/kalkulator-lekow`  
**Główna domena:** `https://infusioncalc.eu/`  
**Charakter audytu:** stan przed wdrożeniem projektu `0.1.4 — indeksowanie i widoczność wyszukiwarkowa`

## 1. Wniosek wykonawczy

Warstwa aplikacyjna InfusionCalc jest dojrzała jak na pierwsze stabilne wydanie: build webowy jest samowystarczalny, uruchomienie offline jest wersjonowane i testowane, a kalkulator otwiera się bez ekranu marketingowego. Największy problem nie dotyczy jakości PWA, lecz tego, że wyszukiwarka ma obecnie bardzo mało sygnałów umożliwiających odkrycie i opisanie witryny.

### Ocena obszarów

| Obszar | Stan | Najważniejszy wniosek |
|---|---|---|
| Dostępność publicznej aplikacji i HTTPS | **zielony na podstawie konfiguracji projektu** | GitHub Pages jest wspieraną ścieżką produkcyjną; dokładne nagłówki live wymagają późniejszego pomiaru zewnętrznego |
| Brak blokady `noindex` w kodzie strony | **zielony** | źródłowy HTML nie zawiera `noindex` |
| Odkrywanie adresów przez crawler | **czerwony** | brak `sitemap.xml`, brak statycznych podstron i brak crawlable linków w początkowym HTML |
| `robots.txt` | **brak** | nie blokuje to samo w sobie indeksowania, ale nie ma deklaracji mapy witryny ani jawnej polityki crawl |
| Metadane strony głównej | **częściowe** | istnieją title, description, lang, ikony i manifest; brak canonical, Open Graph, social image i JSON-LD |
| Treść widoczna bez renderowania Fluttera | **czerwony** | początkowy HTML zawiera zasadniczo wyłącznie ekran „Uruchamianie InfusionCalc…” |
| `/about/`, `/privacy/`, `/changelog/` | **brak** | nie istnieją jako statyczne, bezpośrednio adresowalne strony HTML |
| Obsługa nieistniejących URL | **ryzyko** | brak własnego `404.html`; worker PWA może po przejęciu klienta zwracać app shell dla nawigacji |
| PWA i pełny offline | **zielony** | 43 pliki w wersjonowanym cache; test online→offline przechodzi z wyłączonym zwykłym cache HTTP |
| Walidacja SEO w CI | **czerwony** | obecne CI nie wymaga robots, sitemap, canonical, unikalnych tytułów, JSON-LD ani statycznych podstron |
| Widoczność w wyszukiwarce | **brak wykrytych wyników** | zapytania `site:infusioncalc.eu`, dokładna domena i dokładna nazwa nie zwróciły wyniku z domeny w dniu audytu |
| Lighthouse — wynik liczbowy live | **niezarejestrowany** | środowisko audytu nie mogło pobrać produkcyjnej domeny ani wywołać zewnętrznego Lighthouse; poniżej zapisano pełny audyt statyczny i obowiązkową procedurę pomiaru live |

**Decyzja:** Etap A jest wystarczająco rozpoznany, aby rozpocząć `0.1.4-dev.1`. Nie należy zmieniać strony głównej w landing page. Należy dodać brakujące sygnały techniczne i statyczne strony obok kalkulatora.

---

## 2. Zakres i metodyka

Audyt objął:

1. źródłowy `web/index.html`;
2. manifest PWA;
3. strukturę aplikacji Flutter oraz sposób routingu;
4. stopkę i obecne odnośniki informacyjne;
5. service worker i zachowanie nawigacji;
6. finalizer produkcyjnego artefaktu;
7. workflow CI i GitHub Pages;
8. wynik ostatniego testu samowystarczalnego PWA;
9. obecność planowanych plików i podstron w repozytorium;
10. testy wyszukiwarkowe dokładnej domeny i operatora `site:`;
11. zgodność planu z aktualną dokumentacją Google Search Central, PageSpeed Insights i GitHub Pages.

### Ograniczenie pomiarowe

W bieżącym środowisku wykonawczym nie było możliwe bezpośrednie połączenie sieciowe z `infusioncalc.eu` ani uruchomienie PageSpeed Insights API dla domeny. Nie należy interpretować tego jako awarii strony — jest to ograniczenie środowiska audytu. Z tego powodu:

- nie zapisano liczbowych wyników Performance, Accessibility, Best Practices i SEO;
- nie potwierdzono bezpośrednio nagłówków HTTP produkcji, `X-Robots-Tag`, przekierowania HTTP→HTTPS ani polityki `www`;
- nie sprawdzono wyrenderowanego DOM produkcji narzędziem URL Inspection.

Te cztery pomiary są obowiązkową bramką wersji beta po wdrożeniu zmian. Pozostałe ustalenia wynikają bezpośrednio z kodu, procesu buildu i testów CI.

---

## 3. Stan strony głównej `/`

### 3.1. Elementy istniejące i poprawne

Źródłowy HTML zawiera:

- `<!DOCTYPE html>`;
- język dokumentu `lang="pl"`;
- tytuł `InfusionCalc`;
- polski meta description;
- viewport mobilny;
- `theme-color`;
- znaczniki Apple PWA;
- favicon i apple-touch-icon;
- odnośnik do `manifest.json`;
- ekran startowy z komunikatem o uruchamianiu;
- diagnostykę błędu i timeoutu startu;
- rejestrację wersjonowanego service workera;
- opcjonalny skrypt Umami, który nie jest wymagany do uruchomienia kalkulatora.

Manifest PWA zawiera:

- `id`, `start_url` i `scope` ustawione na `/`;
- `display: standalone`;
- orientację pionową;
- język `pl`;
- kategorie `medical` i `utilities`;
- ikony 192 i 512 px, także w wariancie maskable.

### 3.2. Braki techniczne

W `web/index.html` nie ma:

- `rel="canonical"`;
- Open Graph (`og:title`, `og:description`, `og:url`, `og:image`, `og:type`);
- Twitter/X card;
- lokalnego obrazu social preview;
- JSON-LD;
- klasycznego nagłówka `<h1>` w początkowym HTML;
- statycznego opisu funkcji aplikacji;
- klasycznych linków `<a href>` do stron informacyjnych.

Nie ma również `meta name="robots"`. Sam brak tej deklaracji nie jest błędem blokującym, ponieważ domyślnym zachowaniem Google jest indeksowanie i śledzenie linków, o ile strona nie jest blokowana innym mechanizmem. W projekcie warto jednak ustalić świadomą, testowalną politykę i odrzucać `noindex` w CI.

### 3.3. Tytuł i język

Obecny `<title>InfusionCalc</title>` jest poprawny technicznie, ale zbyt mało opisowy. Nie mówi, że chodzi o dwukierunkowy kalkulator infuzji.

Ważna korekta względem wstępnego planu: strona główna ma `lang="pl"`, a cały interfejs kalkulatora jest po polsku. Dlatego tytuł i opis strony głównej powinny na tym etapie pozostać po polsku. Google zaleca zgodność języka title z głównym językiem treści. Angielski opis należy umieścić na osobnej stronie `/about/` z `lang="en"`. Nie należy mieszać angielskiego title z polską zawartością strony głównej przed wdrożeniem pełnej wielojęzyczności.

Proponowany kierunek, do finalnej redakcji w implementacji:

```html
<title>InfusionCalc — techniczny kalkulator infuzji</title>
<meta
  name="description"
  content="Dwukierunkowy kalkulator stężenia, przepływu i dawki we wlewie, działający także offline. Bez zaleceń dawkowania."
>
<link rel="canonical" href="https://infusioncalc.eu/">
```

---

## 4. Indeksowalność i odkrywanie

### 4.1. Brak jawnej blokady

W źródłowym HTML nie znaleziono `noindex`. Nie znaleziono też reguł `Disallow`, ponieważ `robots.txt` w ogóle nie istnieje w źródłach produkcyjnych.

Wymóg minimalny Google obejmuje: brak blokady Googlebota, odpowiedź HTTP 200 i indeksowalną treść. Na podstawie kodu można potwierdzić brak blokady w HTML, lecz odpowiedź live 200 oraz ewentualny nagłówek `X-Robots-Tag` trzeba potwierdzić po wdrożeniu narzędziem URL Inspection lub zewnętrznym `curl -I`.

### 4.2. `robots.txt`

Plik `web/robots.txt` nie istnieje i nie jest tworzony przez finalizer. Brak robots.txt sam w sobie nie wyłącza indeksowania. W tej witrynie plik jest jednak potrzebny jako:

- jawna deklaracja, że publiczne strony można crawlowć;
- miejsce wskazania pełnego adresu `sitemap.xml`;
- element deterministycznie sprawdzany w artefakcie i CI.

Docelowo:

```text
User-agent: *
Allow: /

Sitemap: https://infusioncalc.eu/sitemap.xml
```

### 4.3. `sitemap.xml`

Plik `web/sitemap.xml` nie istnieje i nie jest generowany. Witryna jest mała, więc mapa nie jest bezwzględnie konieczna technicznie, ale jest szczególnie wskazana, ponieważ domena jest nowa i ma obecnie niewiele zewnętrznych linków. Mapa ma obejmować wyłącznie kanoniczne adresy zwracające 200:

- `/`;
- `/about/`;
- `/privacy/`;
- `/changelog/`.

Nie należy umieszczać w niej:

- plików Fluttera;
- manifestu PWA;
- service workera;
- manifestu offline;
- parametrów analitycznych;
- zasobów graficznych i fontów.

### 4.4. Wynik testu wyszukiwarkowego

W dniu 4 sierpnia 2026 wykonano zapytania:

```text
site:infusioncalc.eu
"infusioncalc.eu"
"InfusionCalc" "infusioncalc.eu"
site:infusioncalc.eu InfusionCalc technical infusion calculator
```

Żadne z nich nie zwróciło wyniku należącego do domeny `infusioncalc.eu` w użytym indeksie wyszukiwarki. Oznacza to, że publiczna widoczność nie została wykryta w tym teście. Nie jest to stuprocentowy dowód braku domeny we wszystkich centrach danych Google, ale jest wystarczającym sygnałem, że należy wdrożyć mapę, Search Console i jawne treści opisowe.

---

## 5. Renderowanie JavaScript i treść widoczna dla robota

InfusionCalc korzysta z modelu app shell. Początkowa odpowiedź HTML nie zawiera formularza, opisów sekcji ani stopki kalkulatora. Widoczna zawartość powstaje dopiero po uruchomieniu Fluttera i CanvasKit.

Google potrafi wykonywać JavaScript, ale proces odbywa się w kolejnych etapach: crawl, render, index. Strona może oczekiwać w kolejce renderowania, a inne roboty i serwisy podglądu linków mogą JavaScriptu nie uruchamiać. Google nadal zaleca prerendering lub statyczny HTML, gdy jest to możliwe.

### Konsekwencje obecnego modelu

- robot po pierwszym pobraniu widzi głównie komunikat startowy;
- właściwy opis funkcji nie istnieje w HTML odpowiedzi;
- crawler nie ma prostego statycznego linku do strony opisowej;
- podgląd linku nie ma Open Graph i może użyć przypadkowego tekstu lub nie pokazać obrazu;
- awaria lub opóźnienie JS zmniejsza ilość treści dostępnej do indeksowania.

### Rekomendowana architektura

- `/` pozostaje bezpośrednim kalkulatorem;
- `/about/`, `/privacy/` i `/changelog/` są statycznym HTML-em;
- `/about/` zawiera pełną, uczciwą treść opisową i klasyczne `<a href>`;
- link `About` w stopce kalkulatora powinien prowadzić do zwykłego adresu URL i, na webie, być możliwie zrealizowany jako rzeczywisty link, nie tylko handler kliknięcia;
- strony informacyjne powinny działać i być czytelne bez JavaScriptu.

---

## 6. Audyt podstron i routingu

### 6.1. Stan obecny

Nie istnieją statyczne pliki ani katalogi dla:

- `/about/`;
- `/privacy/`;
- `/changelog/`.

Aplikacja Flutter nie definiuje routingu dla tych ścieżek. `MaterialApp` używa wyłącznie `home: CalculatorScreen`.

Obecna stopka:

- otwiera `CHANGELOG.md` na GitHubie;
- pokazuje politykę prywatności jako okno dialogowe Fluttera;
- prowadzi do repozytorium GitHub;
- prowadzi do formularza kontaktowego/issue;
- nie ma linku `About`.

### 6.2. Bezpośrednie wejścia

Brak statycznych plików oznacza, że pierwsze bezpośrednie wejście online na planowane podstrony nie ma obecnie treści do obsłużenia przez GitHub Pages. Nie należy polegać na client-side routingu ani na service workerze jako sposobie tworzenia publicznych stron SEO.

### 6.3. Service worker i ryzyko soft 404

Obecny worker przechwytuje nawigacje same-origin i potrafi zwrócić cache `index.html`. Jest to właściwe dla uruchamiania jednego ekranu PWA offline, ale po dodaniu statycznych podstron wymaga korekty. W przeciwnym razie:

- `/about/` może po przejęciu klienta dostać app shell zamiast statycznej treści;
- nieistniejące ścieżki mogą zachowywać się jak pozorne 200;
- robot lub użytkownik może otrzymać kalkulator dla adresu, który powinien być 404.

Google ostrzega przed soft 404 w aplikacjach SPA. Docelowo należy:

1. obsługiwać `/`, `/about/`, `/privacy/` i `/changelog/` jako konkretne zasoby;
2. dodać kontrolowany `404.html`;
3. nie zamieniać każdej nieznanej nawigacji w `index.html`;
4. przetestować status i treść nieistniejącego URL;
5. zachować uruchomienie kalkulatora offline dla `/`.

---

## 7. Stopka i crawlable links

Stopka jest renderowana przez Fluttera i korzysta z `InkWell` oraz kodu uruchamiającego zewnętrzny URL. Nie ma gwarancji, że początkowy HTML prezentuje te elementy jako klasyczne linki `<a href>`.

Google odkrywa adresy przede wszystkim w atrybutach `href` elementów `<a>`. Przy wdrażaniu `About`, `Privacy` i `Changelog` należy sprawdzić wyrenderowany DOM, a nie tylko to, czy kliknięcie działa dla użytkownika.

**Kryterium akceptacji:** narzędzie testowe ma znaleźć w wyrenderowanej stronie normalne adresy docelowe oraz bezpośrednio otworzyć każdą podstronę w nowej, czystej sesji przeglądarki.

---

## 8. Dane strukturalne i Rich Results

W kodzie nie ma JSON-LD ani innych danych strukturalnych. Obecny wynik audytu Rich Results brzmi więc:

> brak danych do walidacji, a nie „niepoprawny JSON-LD”.

Można dodać `SoftwareApplication` lub `WebApplication`, aby jawnie opisać aplikację. Należy jednak zachować ostrożność:

- nie wolno tworzyć fikcyjnego `aggregateRating` lub `review`;
- nie wolno deklarować walidacji klinicznej;
- aplikacja jest bezpłatna, więc ewentualna oferta może mieć cenę `0`;
- samo poprawne JSON-LD nie gwarantuje rich result;
- według aktualnej dokumentacji Google specjalny rich result Software App wymaga również ratingu lub recenzji, więc początkowy JSON-LD może służyć głównie jednoznacznemu opisowi encji, bez obietnicy rozszerzonego wyniku.

Zalecany rdzeń semantyczny:

- nazwa `InfusionCalc`;
- typ `WebApplication` lub `SoftwareApplication`;
- system operacyjny `Web`;
- kategoria zgodna z technicznym charakterem narzędzia;
- adres kanoniczny;
- opis zgodny z deklarowanym przeznaczeniem;
- oferta bezpłatna, tylko jeśli struktura zostanie zaimplementowana zgodnie z wytycznymi;
- brak danych, których projekt faktycznie nie posiada.

---

## 9. PWA, offline i prywatność

To najmocniejsza część obecnego wdrożenia.

### Potwierdzone elementy

- build Flutter Web używa `--no-web-resources-cdn`;
- CanvasKit, WebAssembly i fallback fontu są lokalne;
- finalizer wymaga kompletu plików startowych;
- powstaje wersjonowany manifest offline;
- nowa paczka jest instalowana atomowo;
- zwykły cache HTTP jest czyszczony i wyłączany w teście;
- serwer i sieć są odcinane przed ponownym uruchomieniem;
- test online→offline przeszedł poprawnie;
- ostatni sprawdzony build miał 43 pliki offline;
- Umami jest opcjonalne i nie jest zależnością startową kalkulatora.

### Wpływ projektu SEO na offline

Nowe strony i pliki muszą wejść do deterministycznego procesu buildu. Należy zdecydować:

- czy strony informacyjne są dostępne offline;
- jak worker rozróżnia root aplikacji od statycznych podstron;
- czy `robots.txt` i `sitemap.xml` są w cache — nie jest to wymagane dla działania PWA, ale ich obecność nie szkodzi;
- jak zachować atomowość cache po zwiększeniu liczby plików.

**Bramka:** żadna zmiana SEO nie może pogorszyć obecnego testu online→offline ani startu z ekranu głównego iPhone'a.

---

## 10. Audyt CI i artefaktu publikacyjnego

### 10.1. Obecne mocne bramki

CI obecnie sprawdza:

- formatowanie i analizę Darta;
- testy oraz pokrycie domeny;
- build Androida i iOS;
- produkcyjny build webowy;
- lokalność runtime i fontów;
- składnię skryptów;
- kompletność manifestu offline;
- aktywację workera;
- uruchomienie online i późniejsze uruchomienie offline w ChromeDriver.

### 10.2. Brakujące bramki SEO

Finalizer i workflow nie wymagają obecnie:

- `robots.txt`;
- `sitemap.xml`;
- `/about/index.html`;
- `/privacy/index.html`;
- `/changelog/index.html`;
- canonical;
- unikalnych title i description;
- poprawnego Open Graph;
- poprawnego JSON-LD;
- braku `noindex`;
- zgodności sitemap z rzeczywistymi plikami;
- bezpośredniego wejścia na każdą stronę;
- prawidłowego 404;
- crawlable links;
- liczbowego raportu Lighthouse.

### 10.3. Docelowe testy automatyczne

Minimalny validator `0.1.4` powinien:

1. wymagać wszystkich czterech stron publicznych;
2. parsować każdy HTML;
3. wymagać dokładnie jednego canonical;
4. wymagać unikalnego title i description;
5. odrzucać `noindex`;
6. parsować JSON-LD jako JSON;
7. parsować `sitemap.xml` jako XML;
8. sprawdzać zgodność adresów mapy z plikami i canonical;
9. sprawdzać `Sitemap:` w robots.txt;
10. sprawdzać brak obowiązkowych zasobów zewnętrznych;
11. uruchamiać smoke test `/`, `/about/`, `/privacy/`, `/changelog/` i nieistniejącego URL;
12. ponownie wykonywać obecny test offline kalkulatora.

---

## 11. Audyt Lighthouse — stan bazowy

Lighthouse mierzy Performance, Accessibility, Best Practices i SEO. Dokładny raport liczbowy live nie został uzyskany z powodu ograniczenia sieciowego środowiska audytu. Nie wpisano wymyślonych wartości.

### 11.1. Statycznie potwierdzone zaliczenia

- poprawny doctype;
- ustawiony `lang`;
- title obecny;
- meta description obecny;
- viewport zawiera `width=device-width` i `initial-scale=1`;
- HTTPS jest deklarowaną i wspieraną ścieżką produkcyjną;
- manifest i ikony są obecne;
- aplikacja nie zależy od zewnętrznego CDN;
- start offline przechodzi test przeglądarkowy.

### 11.2. Statycznie potwierdzone problemy lub ryzyka

- title jest mało opisowy;
- brak canonical;
- brak crawlable treści i linków w początkowym HTML;
- brak statycznych podstron;
- brak robots i sitemap;
- brak danych strukturalnych;
- brak social preview;
- viewport zawiera `user-scalable=no`, co ogranicza zoom użytkownika i powinno zostać usunięte w ramach dostępności;
- nie ma własnej kontroli 404;
- ciężar Flutter/CanvasKit wymaga pomiaru, ale nie wolno z samej architektury wnioskować konkretnego wyniku Performance.

### 11.3. Obowiązkowa procedura pomiaru live

Po wdrożeniu `0.1.4-beta.1` należy uruchomić:

- PageSpeed Insights: mobile i desktop;
- wszystkie kategorie: Performance, Accessibility, Best Practices, SEO;
- Rich Results Test dla `/` i `/about/`;
- URL Inspection dla `/`, `/about/`, `/privacy/`, `/changelog/`;
- test HTML i nagłówków przez `curl -I`;
- bezpośrednie wejście w prywatnym oknie bez istniejącego service workera;
- powtórkę po zainstalowaniu i aktywacji service workera.

Raport powinien zapisać datę, wersję Lighthouse, final URL, urządzenie, wyniki kategorii, LCP, CLS, TBT, FCP, Speed Index oraz listę niezaliczonych audytów. Wynik Performance jest zmienny; ważniejsze od pojedynczej liczby jest porównywanie tej samej procedury przed i po zmianie.

---

## 12. Priorytety wdrożenia po audycie

### P0 — wymagane do `0.1.4-dev.1`

1. Ustalić kanoniczny host: apex `infusioncalc.eu` jako wersja główna; zweryfikować później przekierowanie `www`.
2. Dodać polski, opisowy title i description na `/`.
3. Dodać canonical w statycznym HTML.
4. Dodać Open Graph i lokalny obraz social preview.
5. Dodać ostrożne, zgodne z prawdą JSON-LD.
6. Dodać statyczne `/about/`, `/privacy/`, `/changelog/`.
7. Dodać `robots.txt` i `sitemap.xml`.
8. Dodać link `About` oraz zapewnić crawlable linki.
9. Zmienić service worker tak, aby poprawnie obsługiwał konkretne podstrony i nie tworzył soft 404.
10. Dodać `404.html`.
11. Rozszerzyć finalizer i CI o testy SEO.
12. Zachować wszystkie dotychczasowe testy PWA i solvera.

### P1 — wymagane przed stabilnym `0.1.4`

1. Usunąć `user-scalable=no`.
2. Uruchomić Lighthouse mobile i desktop.
3. Uruchomić Rich Results Test i poprawić błędy krytyczne.
4. Sprawdzić link preview.
5. Sprawdzić bezpośrednie wejścia przed i po aktywacji workera.
6. Zweryfikować przekierowania HTTP/HTTPS oraz apex/www.
7. Zarejestrować domenę w Google Search Console i Bing Webmaster Tools.
8. Przesłać sitemapę i poprosić o indeksację `/` oraz `/about/`.

### P2 — obserwacja po wydaniu

1. Monitorować Coverage/Pages w Search Console.
2. Monitorować wybrany canonical przez Google.
3. Monitorować zapytania, wyświetlenia i CTR bez dodawania marketingowego trackingu do aplikacji.
4. Sprawdzić ponownie operator `site:` po crawlu, pamiętając, że operator nie jest pełnym raportem indeksu.
5. Aktualizować changelog statyczny przy kolejnych wydaniach.

---

## 13. Elementy, których nie należy traktować jako błędu

- Brak `meta robots index,follow` nie blokuje strony; jest to ustawienie domyślne.
- Brak sitemap nie uniemożliwia indeksacji, ale utrudnia odkrywanie nowej witryny.
- Brak CNAME w repozytorium nie jest błędem przy publikacji przez custom GitHub Actions; domena może być skonfigurowana w ustawieniach Pages.
- Brak JSON-LD nie blokuje zwykłego wyniku wyszukiwania.
- Brak landing page na `/` jest świadomą i prawidłową decyzją produktową.
- Brak natychmiastowego wyniku po zgłoszeniu mapy nie oznacza awarii — indeksacja nie jest gwarantowana i może potrwać.

---

## 14. Kryterium zakończenia Etapu A

Etap A uznaje się za zakończony, ponieważ:

- zapisano aktualny stan źródłowego HTML i manifestu;
- zidentyfikowano istniejące oraz brakujące metadane;
- sprawdzono obecność robots, sitemap i podstron;
- przeanalizowano routing, stopkę i service worker;
- potwierdzono zielony stan testów PWA/offline;
- wykonano test widoczności domeny w wyszukiwarce;
- zdefiniowano braki CI;
- zdefiniowano procedurę liczbowego Lighthouse live;
- ustalono priorytety P0/P1/P2;
- nie znaleziono przesłanki do zmiany głównego założenia UX.

**Następny etap:** `0.1.4-dev.1 — fundamenty techniczne i statyczne strony informacyjne`.

---

## 15. Materiał dowodowy w repozytorium

- `web/index.html` — obecne metadane i app shell;
- `web/manifest.json` — konfiguracja PWA;
- `lib/app.dart` — brak routingu podstron, `home: CalculatorScreen`;
- `lib/presentation/calculator/calculator_screen.dart` — główny ekran i polska treść;
- `lib/presentation/common/app_footer.dart` — obecne linki/dialog prywatności;
- `web/pwa_service_worker.js` — przechwytywanie nawigacji;
- `tool/finalize_web_pwa.py` — lista wymaganych plików i walidacja artefaktu;
- `.github/workflows/ci.yml` — bramki CI;
- `.github/workflows/github-pages.yml` — build i publikacja;
- `DEPLOYMENT.md` — wspierana ścieżka GitHub Pages;
- `pubspec.yaml` — wersja `0.1.3+22`;
- `docs/SEO_DISCOVERABILITY_0.1.4.md` — zatwierdzony plan projektu;
- issue `#46` — główna checklista wykonawcza.

## 16. Źródła zewnętrzne wykorzystane do interpretacji

- Google Search Central — JavaScript SEO basics;
- Google Search Central — technical requirements;
- Google Search Central — sitemaps;
- Google Search Central — title links;
- Google Search Central — SoftwareApplication structured data;
- Chrome for Developers — Lighthouse;
- GitHub Docs — custom domains and GitHub Pages.
