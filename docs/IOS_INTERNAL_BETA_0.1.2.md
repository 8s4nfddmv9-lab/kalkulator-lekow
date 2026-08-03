# Pierwsza wewnętrzna beta iOS — 0.1.2-beta.1

## Cel

Udostępnić bieżący techniczny kalkulator do pierwszych testów na fizycznym iPhonie, bez dodawania nowych funkcji produktowych i bez rozpoczynania dystrybucji w App Store.

## Zakres wydania

Wydanie zawiera stan aplikacji po:

- wdrożeniu dynamicznego, dwukierunkowego solvera;
- utwardzeniu jednostek oraz rozdzieleniu IU i jednostek masy;
- dodaniu dokładnej arytmetyki opartej na ułamkach;
- wykonaniu niezależnego technicznego zestawu referencyjnego;
- audycie polityki precyzji wyświetlania;
- poprawkach stanu formularza i przywracania preferencji.

Nie dodaje:

- biblioteki leków;
- nazw leków;
- sugerowanych dawek;
- interpretacji wyniku;
- historii obliczeń;
- zapisanych przygotowań;
- nowych kalkulatorów;
- dystrybucji Androida.

## Sposób dystrybucji

GitHub Actions tworzy niepodpisane IPA dla fizycznego urządzenia iOS. Plik jest następnie lokalnie podpisywany darmowym Apple ID oraz instalowany przez Sideloadly na Windowsie.

To nie jest TestFlight, App Store, Ad Hoc Distribution ani publiczne wydanie.

Instrukcja:

- [`IOS_FREE_APPLE_ID_INSTALL.md`](IOS_FREE_APPLE_ID_INSTALL.md)

## Numer wersji

```text
0.1.2-beta.1+13
```

Stały identyfikator buildu przed ewentualną modyfikacją przez narzędzie podpisujące:

```text
pl.kalkulatorlekow.technicalcalculator
```

## Kryteria techniczne przed rozpoczęciem testów

- [ ] standardowe CI zakończone powodzeniem;
- [ ] build urządzeniowy iOS w trybie release zakończony powodzeniem;
- [ ] artifact zawiera niepodpisane IPA;
- [ ] IPA ma architekturę arm64;
- [ ] suma SHA-256 została wygenerowana;
- [ ] aplikacja została podpisana lokalnie darmowym Apple ID;
- [ ] aplikacja została uruchomiona na fizycznym iPhonie;
- [ ] podstawowy scenariusz `4 mg / 50 ml / 70 kg / 0,1 µg/kg/min` został sprawdzony na urządzeniu;
- [ ] przycisk czyszczenia, zmiana jednostek i tryb `/kg` zostały sprawdzone na urządzeniu;
- [ ] wygląd w jasnym i ciemnym motywie został sprawdzony na urządzeniu.

## Lista obserwacji podczas testów

Podczas pierwszych testów należy zwracać uwagę przede wszystkim na:

- wygodę wpisywania liczb z przecinkiem;
- zachowanie klawiatury i przewijania;
- szybkość zmiany jednostek;
- czytelność pól wpisanych i wyliczonych;
- widoczność komunikatów konfliktu;
- czytelność toku obliczenia;
- zachowanie przy dużym rozmiarze tekstu;
- układ na rzeczywistym ekranie iPhone'a;
- działanie po ponownym uruchomieniu aplikacji;
- ponowną instalację przed wygaśnięciem 7-dniowego profilu.

## Granice

Wydanie pozostaje technicznym kalkulatorem matematycznym i jednostkowym. Nie zawiera zaleceń dawkowania, nie ocenia danych użytkownika klinicznie i nie jest przeznaczone do podejmowania decyzji klinicznych.
