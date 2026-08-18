# Monitor dostępności hAP be³ Media

Ten katalog zawiera operacyjny monitor sprzętowy projektu Home Zone. Jest
umieszczony pod `.github/`, dlatego pozostaje poza aplikacją InfusionCalc, jej
artefaktami wydaniowymi i kodem wykonywanym u użytkownika.

Workflow codziennie o 09:00 `Europe/Warsaw` sprawdza wybrane sklepy w Polsce
i Europie. Potwierdzona dostępność aktualizuje jedno zgłoszenie z etykietą
`hardware-watch` i oznacza właściciela repozytorium przez GitHub Notifications.
Przedsprzedaż, planowana dostawa, niejednoznaczna strona i błąd żądania nie
wywołują alertu o dostępności.

Walidacja:

```bash
python3 -m unittest discover -s .github/hardware-watch/hap-be3-media/tests -v
```

Kod aplikacji, logika medyczna, PWA i wydania nie importują tego katalogu.
Po utworzeniu osobnego publicznego repo infrastrukturalnego monitor może zostać
przeniesiony bez zmiany kontraktu detekcji.
