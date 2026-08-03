from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding='utf-8')
    if old not in source:
        raise SystemExit(f'Expected block not found in {path}: {old[:180]!r}')
    path.write_text(source.replace(old, new, 1), encoding='utf-8')


readme = Path('README.md')
replace_once(
    readme,
    "Aplikacja zapisuje lokalnie wyłącznie niekliniczne preferencje prezentacji: kody wybranych jednostek i tryb `/kg`. Nie zapisuje żadnych liczb z formularza, masy pacjenta, danych o leku, historii ani wyników. Po ponownym uruchomieniu wszystkie pola liczbowe są puste.\n\n## Uruchomienie projektu",
    "Aplikacja zapisuje lokalnie wyłącznie niekliniczne preferencje prezentacji: kody wybranych jednostek i tryb `/kg`. Nie zapisuje żadnych liczb z formularza, masy pacjenta, danych o leku, historii ani wyników. Po ponownym uruchomieniu wszystkie pola liczbowe są puste.\n\n## Niezależny techniczny zestaw referencyjny\n\nEtap `0.1.2-dev.1` dodaje wersjonowaną macierz 480 przypadków, rozwijaną do 600 dokładnych porównań wartości wynikowych. Oczekiwane wartości powstają w osobnym, testowym modelu ułamków opartym na `BigInt` i niezależnej tabeli współczynników jednostek. Oracle nie używa produkcyjnych równań do wyznaczania wyników oczekiwanych.\n\nZestaw obejmuje równania bezpośrednie, odwrotne i pełne łańcuchy dla `ng`, `µg`, `mg`, `g` oraz odrębnie `IU`, z czasem `/min` i `/h`, z `/kg` i bez `/kg`. Porównywane są dokładne liczniki i mianowniki, bez tolerancji oraz bez zaokrąglania.\n\nJest to automatyczny audyt techniczny, a nie walidacja kliniczna. Ręczny przegląd przez drugą osobę pozostaje oznaczony jako oczekujący.\n\n## Uruchomienie projektu",
)
replace_once(
    readme,
    "- [Raport wydania technicznego MVP 0.1.0](docs/RELEASE_0.1.0.md)",
    "- [Raport wydania technicznego MVP 0.1.0](docs/RELEASE_0.1.0.md)\n- [Techniczny zestaw referencyjny 0.1.2](docs/TECHNICAL_REFERENCE_ORACLE.md)",
)
replace_once(
    readme,
    "**Wersja rozwojowa:** `0.1.1-dev.2+10` — bezpieczne przywracanie preferencji  ",
    "**Wersja rozwojowa:** `0.1.2-dev.1+11` — niezależny techniczny zestaw referencyjny  ",
)

changelog = Path('CHANGELOG.md')
replace_once(
    changelog,
    "Wszystkie istotne zmiany projektu są dokumentowane w tym pliku.\n\n## [0.1.1-dev.2] — w przygotowaniu",
    "Wszystkie istotne zmiany projektu są dokumentowane w tym pliku.\n\n## [0.1.2-dev.1] — w przygotowaniu\n\n### Dodano\n\n- wersjonowaną macierz 480 technicznych przypadków referencyjnych;\n- osobny oracle dokładnej arytmetyki oparty na `BigInt`, niezależny od produkcyjnych równań;\n- 600 porównań dokładnych liczników i mianowników bez tolerancji i bez zaokrągleń;\n- równania bezpośrednie, odwrotne i pełne łańcuchy obliczeń;\n- pokrycie `ng`, `µg`, `mg`, `g` oraz osobno `IU`, czasu `/min` i `/h`, dawek z `/kg` i bez `/kg`, a także masy w `kg` i `g`;\n- wersjonowany manifest wejść z jawnym statusem ręcznego przeglądu;\n- dokument `docs/TECHNICAL_REFERENCE_ORACLE.md` opisujący konstrukcję, warunki zaliczenia i ograniczenia zestawu.\n\n### Wyniki automatycznego audytu\n\n- wszystkie 480 przypadków i 600 porównań zakończyło się pełną zgodnością;\n- cały projekt: `143/143` testy zakończone powodzeniem;\n- pokrycie liniowe `lib/domain/`: `93,99%` (`720/766` linii);\n- pokrycie `calculator_solver.dart`: `92,73%`;\n- formatowanie i analiza statyczna bez problemów.\n\n### Granice\n\n- zestaw nie zawiera rekomendacji dawkowania ani interpretacji klinicznej;\n- nie stanowi walidacji klinicznej;\n- ręczny przegląd przez drugą osobę pozostaje oczekującą bramką.\n\n## [0.1.1-dev.2] — 2026-08-03",
)

roadmap = Path('ROADMAP.md')
replace_once(
    roadmap,
    "**Aktualny etap:** `0.1.1-dev.2 — bezpieczne przywracanie preferencji`",
    "**Aktualny etap:** `0.1.2-dev.1 — niezależny techniczny zestaw referencyjny`",
)
replace_once(
    roadmap,
    "### 0.1.1 — Poprawki po testach wewnętrznych **← obecnie**",
    "### 0.1.1 — Poprawki po testach wewnętrznych **✓ ukończono**",
)
replace_once(
    roadmap,
    "### 0.1.2 — Dostępność i ergonomia\n\n- [ ] duże rozmiary tekstu;\n- [ ] czytniki ekranowe;\n- [ ] kontrast i tryb ciemny;\n- [ ] ergonomia obsługi jedną ręką;\n- [ ] obsługa różnych rozmiarów ekranów;\n- [ ] ograniczenie przypadkowych zmian jednostki;\n- [ ] haptyczne lub wizualne potwierdzenie konfliktu bez polegania wyłącznie na kolorze.\n\n### 0.1.3 — Audyt domeny i precyzji\n\n- [ ] ponowny przegląd wszystkich konwersji;\n- [ ] audyt polityki zaokrągleń;\n- [ ] testy graniczne;\n- [ ] porównanie z niezależnym zestawem obliczeń;\n- [ ] raport walidacji wersji MVP.",
    "### 0.1.2 — Audyt domeny i precyzji **← obecnie**\n\n- [x] wersjonowana macierz 480 przypadków referencyjnych;\n- [x] niezależny oracle dokładnej arytmetyki oparty na `BigInt`;\n- [x] 600 porównań liczników i mianowników bez tolerancji;\n- [x] równania bezpośrednie, odwrotne i pełne łańcuchy;\n- [x] rodziny jednostek masy oraz odrębnie IU;\n- [x] czas `/min` i `/h`, dawki z `/kg` i bez `/kg`;\n- [x] automatyczny raport konstrukcji i ograniczeń zestawu;\n- [ ] ręczny przegląd macierzy i wzorów przez drugą osobę;\n- [ ] osobny audyt polityki zaokrągleń warstwy prezentacji;\n- [ ] dodatkowy zestaw przypadków zgłoszonych w testach wewnętrznych.\n\n**Stan automatyczny:** 480/480 przypadków, 600/600 dokładnych porównań, 143/143 testy oraz 93,99% pokrycia domeny.\n\n**Dokumentacja:** [`docs/TECHNICAL_REFERENCE_ORACLE.md`](docs/TECHNICAL_REFERENCE_ORACLE.md).\n\n### 0.1.3 — Dostępność i ergonomia\n\n- [ ] duże rozmiary tekstu;\n- [ ] czytniki ekranowe;\n- [ ] kontrast i tryb ciemny;\n- [ ] ergonomia obsługi jedną ręką;\n- [ ] obsługa różnych rozmiarów ekranów;\n- [ ] ograniczenie przypadkowych zmian jednostki;\n- [ ] haptyczne lub wizualne potwierdzenie konfliktu bez polegania wyłącznie na kolorze.",
)
