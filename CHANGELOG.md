# Changelog

Wszystkie istotne zmiany projektu są dokumentowane w tym pliku.

## [0.1.0-dev.1] — w przygotowaniu

### Dodano

- szkielet aplikacji Flutter z oddzielonymi warstwami domeny i prezentacji;
- pierwszy, nieobliczający jeszcze ekran kalkulatora;
- selektory jednostek ilości, stężenia, dawki i masy;
- opcjonalny człon `/kg` oraz wybór `/min` lub `/h`;
- dokładny typ `Rational` oparty na `BigInt` dla współczynników konwersji;
- pierwszy zamknięty katalog jednostek pierwotnych;
- blokadę konwersji `IU` do jednostek masy;
- testy typu wymiernego, konwersji jednostek i ekranu;
- specyfikację techniczną domeny i specyfikację UX;
- GitHub Actions dla formatowania, analizy statycznej i testów.

### Jeszcze nie dodano

- dynamicznego solvera;
- obliczeń dawek i przepływów;
- obsługi konfliktów danych;
- utrwalania ustawień;
- walidacji klinicznej i regulacyjnej.
