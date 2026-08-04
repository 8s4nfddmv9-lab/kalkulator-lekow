# Prywatność — InfusionCalc

## Zakres aplikacji

InfusionCalc jest statycznym technicznym kalkulatorem działającym jako Progressive Web App. Aplikacja nie ma kont użytkowników, własnego backendu, bazy danych ani wbudowanej analityki.

## Dane wpisywane do kalkulatora

Masa, ilość leku, objętość, stężenie, przepływ, dawka i wyniki są przetwarzane lokalnie w przeglądarce użytkownika. Kod aplikacji nie wysyła treści tych pól do serwera i nie zapisuje ich po stronie hostingu.

Nie należy wpisywać danych identyfikujących pacjenta.

## Dane zapisywane lokalnie

Aplikacja zapisuje lokalnie wyłącznie niekliniczne ustawienia:

- wybrane jednostki;
- tryb dawki z `/kg` lub bez `/kg`;
- datę, do której komunikat „Dodaj do ekranu głównego” ma pozostać ukryty po wybraniu „Nie teraz”.

Odroczenie komunikatu instalacji jest przechowywane jako lokalny znacznik czasu i nie jest wysyłane do serwera. Pola liczbowe, wyniki i historia obliczeń nie są utrwalane przez obecną wersję.

## Instalacja PWA

W zwykłym trybie przeglądarki aplikacja lokalnie sprawdza typ urządzenia, rodzinę przeglądarki, dostępność systemowego promptu instalacji oraz tryb wyświetlania `standalone`. Informacje te służą wyłącznie do pokazania właściwej instrukcji instalacji i nie są przesyłane ani zapisywane po stronie projektu.

## Hosting

Publiczna wersja jest dostarczana przez GitHub Pages. Dostawca hostingu może przetwarzać standardowe dane techniczne żądań HTTP, takie jak adres IP, informacje o przeglądarce lub czas żądania, zgodnie z własnymi zasadami i obowiązującym prawem. InfusionCalc nie wykorzystuje tych danych do profilowania ani analityki aplikacji.

## Kontakt i zgłoszenia

Uwagi do prywatności i działania aplikacji można zgłaszać w repozytorium projektu. Nie należy dołączać danych pacjentów ani innych informacji poufnych:

```text
https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18
```
