# Prywatność — InfusionCalc

**Publiczna wersja:** https://infusioncalc.eu/privacy/

## Zakres aplikacji

InfusionCalc jest statycznym technicznym kalkulatorem działającym jako Progressive Web App. Aplikacja nie ma kont użytkowników, własnego backendu ani bazy danych pacjentów. Korzysta z ograniczonej analityki Umami Cloud opisanej poniżej.

## Dane wpisywane do kalkulatora

Masa, ilość leku, objętość, stężenie, przepływ, dawka, wyniki oraz wzory są przetwarzane lokalnie w przeglądarce użytkownika. Kod aplikacji nie wysyła treści tych pól do Umami, GitHub Pages ani innego serwera aplikacji i nie zapisuje ich po stronie hostingu.

Nie należy wpisywać danych identyfikujących pacjenta.

## Dane zapisywane lokalnie

Aplikacja zapisuje lokalnie wyłącznie niekliniczne ustawienia:

- wybrane jednostki;
- tryb dawki z `/kg` lub bez `/kg`;
- język interfejsu;
- datę, do której komunikat „Dodaj do ekranu głównego” ma pozostać ukryty po wybraniu „Nie teraz”.

Odroczenie komunikatu instalacji jest przechowywane jako lokalny znacznik czasu i nie jest wysyłane do serwera. Pola liczbowe, wyniki i historia obliczeń nie są utrwalane przez obecną wersję.

## Cache pełnego trybu offline

Po uruchomieniu online service worker zapisuje lokalnie publiczny kod i statyczne zasoby konkretnej wersji InfusionCalc. Cache może obejmować między innymi `index.html`, `main.dart.js`, bootstrap Fluttera, manifest PWA, ikony, fonty, assety, pliki renderera oraz statyczne strony informacyjne `/about/`, `/privacy/` i `/changelog/`. Pozwala to uruchamiać zainstalowaną aplikację bez internetu.

Cache offline nie zawiera masy, ilości leku, objętości, stężenia, przepływu, dawki, wyników, wzorów bieżącego obliczenia ani historii. Nie jest bazą danych użytkownika. Przeglądarka lub system może usunąć cache po wyczyszczeniu danych strony, usunięciu PWA, długim nieużywaniu lub przy presji na pamięć urządzenia.

Szczegóły techniczne i procedura testowa znajdują się w [`docs/OFFLINE_PWA.md`](OFFLINE_PWA.md).

## Analityka Umami Cloud

Publiczna wersja korzysta z Umami Cloud do podstawowych statystyk produktu. Skrypt jest ograniczony do domeny `infusioncalc.eu`. Rejestrowane są odsłony strony oraz zamknięta lista ośmiu zdarzeń interfejsu:

- uruchomienie aplikacji;
- wyświetlenie zachęty do instalacji;
- kliknięcie przycisku instalacji;
- potwierdzenie instalacji przez obsługiwaną przeglądarkę;
- otwarcie ostrzeżenia;
- otwarcie informacji o prywatności;
- kliknięcie odnośnika GitHub;
- kliknięcie odnośnika kontaktowego.

Do własnych zdarzeń mogą być dołączone wyłącznie: publiczna wersja aplikacji, platforma (`ios`, `android`, `other`), tryb uruchomienia (`browser`, `standalone`) oraz stała nazwa metody instalacji. Aplikacja nie ustawia własnego identyfikatora użytkownika i nie korzysta z `umami.identify`.

Analityka nie otrzymuje masy, ilości leku, objętości, stężenia, przepływu, dawki, wyników, wzorów, nazw leków, historii ani tekstu z pól formularza. Szczegółowy, wersjonowany kontrakt znajduje się w [`docs/ANALYTICS.md`](ANALYTICS.md).

Blokada trackera, brak internetu lub awaria Umami nie wpływają na obliczenia. Krótka kolejka zdarzeń istnieje wyłącznie w pamięci bieżącej strony i jest porzucana, gdy tracker pozostaje niedostępny. Zdarzenia nie są trwale kolejkowane do późniejszego wysłania po pracy offline.

## Instalacja PWA

W zwykłym trybie przeglądarki aplikacja sprawdza typ urządzenia, rodzinę przeglądarki, dostępność systemowego promptu instalacji oraz tryb wyświetlania `standalone`. Informacje te służą do pokazania właściwej instrukcji. Do Umami trafia jedynie znormalizowana platforma, tryb uruchomienia i — przy zdarzeniu instalacyjnym — jedna ze stałych nazw metody instalacji.

## Hosting

Publiczna wersja jest dostarczana przez GitHub Pages. Dostawca hostingu może przetwarzać standardowe dane techniczne żądań HTTP zgodnie z własnymi zasadami i obowiązującym prawem. Usługa analityczna jest dostarczana przez Umami Cloud zgodnie z aktualnymi warunkami i polityką prywatności dostawcy.

## Kontakt i zgłoszenia

Uwagi do prywatności i działania aplikacji można zgłaszać w repozytorium projektu. Nie należy dołączać danych pacjentów ani innych informacji poufnych:

```text
https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18
```
