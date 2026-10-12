# Diagnostyka mobilnego przewijania — 2026-10-12

## Zakres i status

Baza: `main` / `c6de6947aad7d4cd6a05a68d142004c735d261e8` (v0.1.7).
Gałąź poprawki: `fix/mobile-scroll-smoothness`. Zmiana przeznaczona do osobnego PR,
bez automatycznego scalania i bez publikowania na produkcji.

Odtworzono skoki pozycji oraz dodatkową pracę podczas przewijania w Chromium
z emulacją mobilną. Poprawka usuwa odtwarzanie elementów formularza podczas
przewijania i stabilizuje jego geometrię w wykonanych testach. **Nie wykonano
testu na fizycznym iPhonie. Nie jest to potwierdzenie rozwiązania wszystkich
przycięć Safari ani zainstalowanego PWA na iOS.**

## Potwierdzone ustalenia

1. Mobilny ekran używał `ListView` z elementami o różnych wysokościach.
   Pola i `PwaInstallBanner` były usuwane poza obszarem cache i tworzone ponownie
   podczas powrotu. Test zachowania tożsamości pola na bazowym kodzie nie przeszedł:
   element pola masy był odmontowany po przewinięciu. Ten sam test przechodzi po zmianie.
2. Odtworzony baner ponownie wywoływał `_loadSnooze()`. Do zakończenia odczytu
   `_preferencesLoaded == false` powoduje `SizedBox.shrink()`, po czym baner
   odzyskuje wysokość. W każdym z 12 bazowych przebiegów nastąpiła jedna nowa
   subskrypcja mostka PWA podczas samych gestów; po zmianie: zero.
3. Przy niezmiennych danych szacowane `maxScrollExtent` zmieniało się 28–38 razy
   na przebieg. W wypełnionym formularzu każdy z trzech przebiegów zawierał krok
   pozycji 182 px przy regularnych krokach dotyku 16 px. W pierwszym przebiegu
   `filled` po odtworzeniu banera pozycja przeszła z 432 do 250 px, a estymata
   końca listy z 2560 do 2364 px. Jest to korekta geometrii listy, nie zmiana
   żądanej bezwładności. Surowe próbki i zdarzenia subskrypcji zachowano w artefaktach.
4. Produkcyjna konfiguracja to Flutter **3.44.8**, `dart2js`, **CanvasKit** z lokalnymi
   zasobami (`useLocalCanvasKit: true`). Nie jest używany build `--wasm`/Skwasm.
   Pomiar wykonano na tej samej wersji SDK i tym samym rendererze przed i po.
5. Kod aplikacji nie wywołuje solvera z listenera przewijania. Aktualizacja
   obliczeń zachodzi przy zmianie danych/jednostek/trybu, a finalizacja wpisu
   roboczego przy utracie fokusu. `web/index.html` nie instaluje własnych
   listenerów `touchmove`, `scroll`, `resize` ani pętli `requestAnimationFrame`.
   Mostek PWA reaguje na instalację i zmianę trybu wyświetlania, nie na ruch palca.

Mechanizm usuwania i odtwarzania dzieci jest opisany również w
[dokumentacji cyklu życia ListView](https://api.flutter.dev/flutter/widgets/ListView-class.html).
Profilowanie Web przez oś czasu przeglądarki jest zgodne z
[zalecanym sposobem profilowania Flutter Web](https://docs.flutter.dev/perf/web-performance).

## Poprawka

Wyłącznie w mobilnej gałęzi ekranu zastąpiono `ListView` przez
`SingleChildScrollView` z rozciągniętą `Column` i `RepaintBoundary`.
Formularz ma stałą, niewielką liczbę pól, więc może utrzymywać wszystkie elementy
w pamięci. Wysokość jest wyznaczana dla całego formularza, a warstwa malowania
może być zachowana podczas przesuwania. Koszt utworzenia wszystkich pól przechodzi
na początek; nie jest to wzorzec dla nieograniczonej listy danych.

Nie zmieniono fizyki przewijania, obsługi gestów, viewport HTML, renderera,
solvera, walidacji, kontrolerów tekstu ani zarządzania fokusem. `Scaffold` nadal
reaguje na klawiaturę. Desktopowy dashboard korzysta z dotychczasowej gałęzi.

## Pomiar przed i po

Środowisko: Linux, Chromium **151.0.7922.34**, Playwright **1.62.1**, okno
390 × 844, DPR 1, dotyk i mobilny UA Android, spowolnienie CPU ×4. Jest to
kontrolowany test emulowany, a nie model wydajności konkretnego telefonu.
GPU przeglądarki: ANGLE/Vulkan **SwiftShader** (renderowanie programowe).
Budowy pomiarowe: `--release --no-web-resources-cdn`, z osobnym testowym
entry pointem używającym produkcyjnego `main()`. Kod sondy nie trafia do normalnego buildu.
Sonda ustawia dane przez kontrolery i istniejące `onChanged` przed rejestracją;
sam ruch pochodzi ze zdarzeń dotykowych CDP, a pozycja z `ScrollPosition` Fluttera.

Każdy stan: trzy świeże konteksty, po trzy przeciągnięcia w dół i w górę;
każde przeciągnięcie ma 30 kroków po 16 px. Rejestrowanie następuje po
uruchomieniu aplikacji i przygotowaniu cache offline. W czasie pomiarów
nie wykonywano kompilacji ani testów Fluttera. Szczegółowe trace'y są zbierane
osobno w `--profile`, ponieważ instrumentacja wpływa na czasy.

W tabelach podano **medianę z trzech przebiegów**, a nie najlepszy wynik.
Przed → po:

| Stan | Odstęp klatek p99 (ms) | Klatki >25 ms | Długie zadania >50 ms | Łączny czas długich zadań (ms) | Największy krok pozycji podczas przeciągania (px) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pusty | 50,1 → 33,4 | 29 → 20 | 6 → 3 | 530 → 308 | 16 → 16 |
| Wypełniony | 49,9 → 33,4 | 20 → 7 | 4 → 3 | 353 → 273 | 182 → 16 |
| Błędna masa | 49,9 → 33,3 | 20 → 6 | 5 → 3 | 405 → 277 | 182 → 16 |
| Edycja stężenia | 50,0 → 33,3 | 21 → 7 | 5 → 3 | 410 → 283 | 182 → 16 |

| Stan | Zmiany estymaty końca listy | Odtworzenia banera | Reakcja na gest p50 (ms) | Reakcja na gest p95 (ms) |
| --- | ---: | ---: | ---: | ---: |
| Pusty | 28 → 0 | 1 → 0 | 66,6 → 67,0 | 88,4 → 127,8 |
| Wypełniony | 32 → 0 | 1 → 0 | 134,2 → 79,1 | 150,2 → 150,1 |
| Błędna masa | 38 → 0 | 1 → 0 | 67,2 → 80,7 | 150,4 → 150,4 |
| Edycja stężenia | 32 → 0 | 1 → 0 | 149,6 → 81,2 | 150,6 → 150,0 |

Odstępy klatek to odstępy `requestAnimationFrame`, nie pomiar czasu rastra GPU.
Mediana odstępu pozostała 16,7 ms. Najdłuższe odstępy nadal wynoszą około
100–117 ms po poprawce. Reakcja oznacza czas od wysłania początku gestu do
pierwszej zaobserwowanej zmiany pozycji, z progiem rozpoznania gestu i narzutem
automatyzacji; nie jest INP. W pustym/błędnym formularzu nie uzyskano poprawy tej
metryki. Wyniki potwierdzają stabilniejszy układ i mniej kosztownych klatek,
ale **nie dowodzą stałych 60 FPS ani usunięcia wszystkich opóźnień**.

Stany formularza:

- pusty, z widocznym zaproszeniem do instalacji PWA;
- masa 70 kg, lek 4 mg, roztwór 50 ml, przepływ 5 ml/h;
- te same dane z niepoprawnym tekstem masy (`bad`) i komunikatami walidacji;
- zmiana stężenia na 100 µg/ml po wypełnieniu danych (edycja odwrotna, nie wymuszony konflikt).

Surowe próbki, zdarzenia dotykowe i wyniki każdego przebiegu:
[`artifacts/mobile-scroll`](../artifacts/mobile-scroll/).

## Szczegółowy profil Fluttera

Osobny przebieg `filled` w trybie `--profile`, z włączonymi
`debugProfileBuildsEnabled`, `debugProfileLayoutsEnabled` i
`debugProfilePaintsEnabled`, zapisano przez Chrome DevTools Protocol `Tracing`.
Wszystkie poniższe czasy mają narzut instrumentacji; nie są dodatkowymi
wynikami release i nie należy sumować zagnieżdżonych kategorii.

| Zdarzenie Fluttera | Liczba przed → po | Łączny czas przed → po (ms) |
| --- | ---: | ---: |
| Budowanie `CalculationField` | 6 → 0 | 85,23 → 0 |
| Budowanie `PwaInstallBanner` | 2 → 0 | 21,89 → 0 |
| Budowanie `CalculatorScreen` | 0 → 0 | 0 → 0 |
| Faza `BUILD` | 86 → 19 | 475,30 → 15,92 |
| Faza `LAYOUT` | 190 → 189 | 893,08 → 3,61 |
| Faza `PAINT` | 190 → 189 | 401,21 → 170,59 |

Profil wskazuje koszt odtwarzanych poddrzew i layoutu listy. Nie potwierdza
hipotezy o ciągłym przebudowywaniu całego `CalculatorScreen` ani liczeniu solvera
podczas samego gestu. Spadek czasu `PAINT` oznacza mniej pracy frameworka;
nie jest pomiarem kosztu rastra CanvasKit na GPU iPhone'a.

Ślady: [przed](../artifacts/mobile-scroll/before/flutter-profile-trace.json.gz),
[po](../artifacts/mobile-scroll/after/flutter-profile-trace.json.gz),
[zestawienie](../artifacts/mobile-scroll/flutter-trace-summary.json).
Zrzut wypełnionego widoku po sekwencji gestów był identyczny pikselowo przed
i po (SHA-256 `c87826590e3d7f65dd974d33ff97b606354751efced2777f7ff4978b50816e0a`):
[zrzut](../artifacts/mobile-scroll/filled-mobile.png).

Dodatkowo wykonano po jednym przebiegu przed/po z UA iOS Safari w Chromium:
z widocznym banerem największy krok wynosił 166 → 16 px, liczba zmian końca
listy 35 → 0, odtworzenia banera 1 → 0. Z tym samym UA i symulowanym
`navigator.standalone=true` (baner ukryty) krok wynosił 16 → 16 px, zmiany
końca listy 25 → 0. Ta kontrola potwierdza udział widocznego, odtwarzanego banera
w dużym skoku; dodatkowy koszt listy występuje również bez widocznego banera.
Są to testy gałęzi logiki PWA, **nie testy silnika Safari**. W pojedynczym
przebiegu z UA iOS najdłuższy odstęp po poprawce wyniósł 183 ms; nadal
pozostają opóźnienia, których ta poprawka nie eliminuje.

## Regresje i ograniczenia urządzeń

- `flutter analyze`: bez problemów.
- `flutter test`: **197 testów przeszło**, w tym sześć nowych testów mobilnych.
- Dwa istniejące testy sprawdzają teraz widoczność stopki i właściwy obszar
  przewijania zamiast wymagać konkretnego typu `ListView`.
- Nowe testy obejmują zachowanie elementów/PWA, stałą geometrię przy dotyku dla
  danych wypełnionych, błędnych i edycji odwrotnej, wąski ekran 320 × 568 z tekstem
  ×2, fokus i wpis ułamkowy przy symulowanej klawiaturze 300 px.
- Obliczenia referencyjne: 4 mg / 50 ml = 80 µg/ml; przy 70 kg i 5 ml/h
  dawka 0,095238095 µg/kg/min i czas 10 h. Test klawiatury potwierdza także
  natychmiastowy wynik 52,5 ml/h po wpisaniu 1,0 µg/kg/min.
- Testy narzędzi PWA/SEO/routingu: **25 przeszło**.
- Zwykły produkcyjny build `lib/main.dart` uruchomił się offline po wyczyszczeniu
  i wyłączeniu cache HTTP oraz całkowitym odcięciu sieci. Zweryfikowany pakiet
  obejmuje 53 pliki, lokalny CanvasKit i fonty. Testy kanonicznych tras,
  przekierowań i odrębnego 404 przeszły online i offline.
- Testy desktopowego dashboardu, języków, jednostek, walidacji, precyzji i PWA
  są częścią pełnej regresji.

**Realne urządzenia: nie wykonano żadnego testu.** W sesji nie ma podłączonego
fizycznego iPhone'a ani Androida. Nie wykonano Safari na iOS, systemowej
klawiatury iOS, animacji paska adresu Safari ani rzeczywistego uruchomienia
zainstalowanego standalone PWA. Symulacja insets w Flutterze weryfikuje logikę
układu i fokusu, lecz nie zastępuje tych testów.

Nadal wymagają weryfikacji na urządzeniu: wydajność CanvasKit/GPU przy wysokim
DPR, częstotliwość zmian viewport podczas zwijania paska Safari, klawiatura
i bezwładność w Safari i standalone. W kodzie aplikacji nie potwierdzono
osobnego błędu obsługi tych zdarzeń, dlatego nie wprowadzono obejść dla iOS.

## Zmienione pliki

- `lib/presentation/calculator/calculator_screen.dart` — stabilny kontener mobilnego formularza i granica malowania.
- `test/presentation/mobile_scroll_test.dart` — regresje przewijania, geometrii, fokusu i danych.
- `test/presentation/calculator_screen_test.dart` — asercje zachowania stopki i kontenera.
- `tool/mobile_scroll_probe.dart` — sonda tylko dla lokalnego buildu pomiarowego.
- `tool/profile_mobile_scroll.cjs` — powtarzalne gesty, metryki i zapis Chrome trace.
- `docs/MOBILE_SCROLL_DIAGNOSTICS.md` i `artifacts/mobile-scroll/` — raport i dowody pomiarowe.

`calculation_field.dart`, `pwa_install_banner.dart`, `web/index.html`, bootstrap
i workflowy zostały przeanalizowane; poprawka nie wymaga zmiany tych plików.

## Odtworzenie pomiaru

Wymagane: przypięty Flutter 3.44.8, Node, Playwright 1.62.1 i jego Chromium.
Używać oddzielnych katalogów wyjściowych dla bazowego commita i poprawki.
Sonda musi być obecna również w kopii bazowego kodu.

```sh
flutter pub get --enforce-lockfile
python3 tool/prepare_web_pwa.py --web-dir web
python3 tool/prepare_web_fallback_fonts.py --web-dir web
flutter build web --release --no-web-resources-cdn \
  --target tool/mobile_scroll_probe.dart --output /tmp/scroll-build
python3 tool/finalize_web_pwa.py /tmp/scroll-build local-scroll-probe
node tool/profile_mobile_scroll.cjs /tmp/scroll-build /tmp/scroll-results 3
```

Dla diagnostyki operacji Fluttera zamienić `--release` na
`--profile --dart-define=SCROLL_TRACE=true` i uruchomić skrypt z
`PROFILE_TRACE=1 SCROLL_STATES=filled` oraz jednym powtórzeniem. Plik
`filled-trace.json.gz` można rozpakować i otworzyć w Chrome DevTools Performance.
Nie mieszać wyników z instrumentacją z tabelą release.

`SCROLL_PLATFORM=ios` zmienia wyłącznie UA dla logiki zaproszenia PWA;
`SCROLL_STANDALONE=1` symuluje flagę `navigator.standalone`. Żadna z tych opcji
nie uruchamia Safari ani prawdziwego systemowego PWA.
