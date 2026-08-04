# Analityka — InfusionCalc

## Cel

InfusionCalc korzysta z minimalnej analityki Umami Cloud, aby oceniać liczbę odwiedzin, używane platformy oraz skuteczność instalacji PWA. Analityka nie służy do profilowania klinicznego, reklamy ani oceny sposobu dawkowania.

## Konfiguracja

- dostawca: Umami Cloud;
- domena produkcyjna: `infusioncalc.eu`;
- website ID: `a75601c3-4636-4210-b309-c54736e06843`;
- automatyczne odsłony są ograniczone atrybutem `data-domains` do domeny produkcyjnej;
- tracker respektuje ustawienie przeglądarki „Do Not Track”;
- parametry wyszukiwania i fragment adresu URL są wyłączone z automatycznego śledzenia;
- lokalny development, testy widgetowe i natywne buildy nie wysyłają zdarzeń do projektu produkcyjnego.

Website ID identyfikuje publiczną stronę w skrypcie trackera i nie jest sekretem uwierzytelniającym do panelu Umami.

## Automatyczne statystyki odwiedzin

Skrypt Umami rejestruje odsłony publicznej strony. Panel usługi może na tej podstawie prezentować standardowe statystyki techniczne, takie jak odwiedzana ścieżka, źródło wejścia, typ urządzenia, przeglądarka, system operacyjny oraz przybliżony kraj.

InfusionCalc nie przekazuje do automatycznych odsłon parametrów kalkulatora ani treści pól formularza. Query string i hash adresu URL są odrzucane przez konfigurację trackera.

## Własne zdarzenia

Lista nazw jest zamknięta w kodzie i obejmuje wyłącznie:

| Zdarzenie | Znaczenie |
|---|---|
| `app_open` | uruchomienie aplikacji w przeglądarce albo jako PWA |
| `install_prompt_opened` | wyświetlenie zachęty do instalacji |
| `install_button_clicked` | wybranie przycisku instalacji |
| `pwa_installed` | potwierdzenie instalacji przez przeglądarkę w bieżącej sesji |
| `warning_opened` | otwarcie informacji o technicznym przeznaczeniu |
| `privacy_opened` | otwarcie informacji o prywatności |
| `github_clicked` | przejście do publicznego repozytorium |
| `contact_clicked` | przejście do zgłoszenia kontaktowego / feedbacku |

Do zdarzeń mogą zostać dołączone wyłącznie następujące, niekliniczne wymiary:

- `app_version` — publiczna wersja aplikacji;
- `platform` — `ios`, `android` albo `other`;
- `display_mode` — `browser` albo `standalone`;
- `install_method` — jedna z czterech stałych ścieżek instalacji.

## Dane wykluczone

Kod analityczny nie ma dostępu do modelu obliczeniowego i nie może wysyłać:

- masy pacjenta;
- ilości leku;
- objętości;
- stężenia;
- przepływu;
- dawki;
- wyniku lub wzoru;
- historii obliczeń;
- nazw leków ani danych pacjenta;
- tekstu wpisanego do któregokolwiek pola;
- własnego identyfikatora użytkownika.

InfusionCalc nie wywołuje funkcji `umami.identify`. Nazwy zdarzeń i dopuszczalne pola są kontrolowane jednocześnie przez typowany adapter Dart oraz lokalny skrypt JavaScript z listą dozwolonych wartości.

## Odporność

Umami jest funkcją opcjonalną. Brak internetu, blokada skryptów analitycznych, rozszerzenie typu ad blocker albo awaria usługi nie mogą zatrzymać uruchomienia aplikacji ani obliczeń. Zdarzenia są przechowywane wyłącznie w krótkiej, ograniczonej kolejce pamięci bieżącej strony i są porzucane, gdy tracker pozostaje niedostępny.

## Dostęp do wyników

Właściciel projektu loguje się do panelu Umami Cloud i wybiera stronę `InfusionCalc`. Odsłony są widoczne w głównym dashboardzie, a osiem własnych zdarzeń w widoku zdarzeń. Właściwości zdarzeń można analizować według wersji, platformy, trybu uruchomienia i metody instalacji. Dostęp do panelu wymaga konta Umami i nie wynika z publicznego website ID.

Dokument opisuje konfigurację kodu InfusionCalc; zasady przetwarzania po stronie dostawcy są dodatkowo regulowane przez aktualne warunki i politykę prywatności Umami Cloud.
