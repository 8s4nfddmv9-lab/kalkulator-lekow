from pathlib import Path

changelog = Path('CHANGELOG.md')
source = changelog.read_text()
marker = '## [0.1.0-dev.5] — w przygotowaniu\n'
section = '''## [0.1.0-dev.6] — w przygotowaniu

### Dodano

- lokalne zapamiętywanie ostatnio wybranych jednostek prezentacyjnych;
- zapamiętywanie trybu dawki z `/kg` albo bez `/kg`;
- asynchroniczny magazyn preferencji oparty na stabilnych kodach jednostek;
- bezpieczne wartości domyślne dla nieznanych, usuniętych lub niezgodnych kodów;
- ochronę przed nadpisaniem szybkiej zmiany użytkownika przez opóźniony odczyt ustawień;
- niekrytyczną obsługę błędów odczytu i zapisu preferencji;
- centralny katalog jednostek dostępnych w formularzu;
- techniczne limity długości i precyzji tekstowego wejścia liczbowego;
- osobny błąd domenowy `outOfTechnicalRange`;
- testy modelu preferencji, fallbacków, zakresów technicznych i integracji z ekranem.

### Polityka danych trwałych

- zapis obejmuje wyłącznie kody jednostek oraz wartość logiczną trybu `/kg`;
- aplikacja nie zapisuje masy pacjenta, ilości leku, objętości, stężenia, przepływu, dawki, historii ani wyników;
- po restarcie wszystkie pola liczbowe pozostają puste.

### Nadal obowiązuje

- aplikacja działa bez konta, backendu, analityki i transmisji danych kalkulatora;
- wersja pozostaje prototypem nieprzeznaczonym do podejmowania decyzji klinicznych.

## [0.1.0-dev.5] — 2026-08-03
'''
if marker not in source:
    raise SystemExit('CHANGELOG marker not found')
changelog.write_text(source.replace(marker, section, 1))

readme = Path('README.md')
source = readme.read_text()
source = source.replace(
    '- zapamiętywanie ostatnio wybranych jednostek;\n',
    '- zapamiętywanie ostatnio wybranych jednostek i trybu `/kg`;\n',
    1,
)
marker = (
    'Poza zakresem MVP pozostają m.in. biblioteka leków, sugerowane dawki, '
    'synchronizacja, konta użytkowników i przechowywanie danych pacjentów.\n'
)
addition = marker + '''
Aplikacja zapisuje lokalnie wyłącznie niekliniczne preferencje prezentacji: kody wybranych jednostek i tryb `/kg`. Nie zapisuje żadnych liczb z formularza, masy pacjenta, danych o leku, historii ani wyników. Po ponownym uruchomieniu wszystkie pola liczbowe są puste.
'''
if marker not in source:
    raise SystemExit('README privacy marker not found')
source = source.replace(marker, addition, 1)
source = source.replace(
    '**Etap:** `0.1.0-dev.1` — szkielet aplikacji i pierwszy prototyp ekranu\n',
    '**Etap:** `0.1.0-dev.6` — preferencje lokalne i utwardzenie walidacji  \n',
    1,
)
readme.write_text(source)

roadmap = Path('ROADMAP.md')
source = roadmap.read_text()
source = source.replace('**Stan na:** 2 sierpnia 2026  ', '**Stan na:** 3 sierpnia 2026  ', 1)
source = source.replace(
    '**Aktualny etap:** `0.1.0-dev.1 — szkielet aplikacji`',
    '**Aktualny etap:** `0.1.0-dev.6 — preferencje i utwardzenie`',
    1,
)
source = source.replace(
    '### 0.0.3 — Projekt UX i prototyp ekranu **w realizacji**',
    '### 0.0.3 — Projekt UX i prototyp ekranu **✓ ukończono**',
    1,
)
source = source.replace(
    '### 0.1.0-dev.1 — Szkielet aplikacji **← obecnie**',
    '### 0.1.0-dev.1 — Szkielet aplikacji **✓ ukończono**',
    1,
)
for version, title in [
    ('2', 'Typy wielkości i jednostek'),
    ('3', 'Równania podstawowe'),
    ('4', 'Dynamiczny solver formularza'),
    ('5', 'Interfejs MVP'),
]:
    plain = f'### 0.1.0-dev.{version} — {title}'
    source = source.replace(plain, f'{plain} **✓ ukończono**', 1)
source = source.replace(
    '### 0.1.0-dev.6 — Utrwalanie ustawień i obsługa błędów',
    '### 0.1.0-dev.6 — Utrwalanie ustawień i obsługa błędów **← obecnie**',
    1,
)
prefix, separator, suffix = source.partition('### 0.1.0-dev.7 — Testy referencyjne i utwardzenie')
if not separator:
    raise SystemExit('ROADMAP dev.7 marker not found')
prefix = prefix.replace('- [ ]', '- [x]')
decision = '''**Decyzja o restarcie:** przywracane są wyłącznie jednostki i tryb `/kg`; wszystkie wartości liczbowe zawsze pozostają puste.\n\n'''
source = prefix + decision + separator + suffix
roadmap.write_text(source)
