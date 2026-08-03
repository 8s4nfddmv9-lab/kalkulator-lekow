# Prywatność — InfusionCalc

## Zakres aplikacji

InfusionCalc jest statycznym technicznym kalkulatorem działającym jako Progressive Web App. Aplikacja nie ma kont użytkowników, własnego backendu, bazy danych ani wbudowanej analityki.

## Dane wpisywane do kalkulatora

Masa, ilość leku, objętość, stężenie, przepływ, dawka i wyniki są przetwarzane lokalnie w przeglądarce użytkownika. Kod aplikacji nie wysyła treści tych pól do serwera i nie zapisuje ich po stronie hostingu.

Nie należy wpisywać danych identyfikujących pacjenta.

## Dane zapisywane lokalnie

Aplikacja zapisuje lokalnie wyłącznie niekliniczne ustawienia prezentacji:

- wybrane jednostki;
- tryb dawki z `/kg` lub bez `/kg`.

Pola liczbowe, wyniki i historia obliczeń nie są utrwalane przez obecną wersję.

## Hosting

Publiczna wersja jest dostarczana przez GitHub Pages. Dostawca hostingu może przetwarzać standardowe dane techniczne żądań HTTP, takie jak adres IP, informacje o przeglądarce lub czas żądania, zgodnie z własnymi zasadami i obowiązującym prawem. InfusionCalc nie wykorzystuje tych danych do profilowania ani analityki aplikacji.

## Kontakt i zgłoszenia

Uwagi do prywatności i działania aplikacji można zgłaszać w repozytorium projektu. Nie należy dołączać danych pacjentów ani innych informacji poufnych:

```text
https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18
```
