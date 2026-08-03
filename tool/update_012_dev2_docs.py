from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding='utf-8')
    if old not in source:
        raise SystemExit(f'Expected block not found in {path}: {old[:200]!r}')
    path.write_text(source.replace(old, new, 1), encoding='utf-8')


readme = Path('README.md')
replace_once(
    readme,
    "Jest to automatyczny audyt techniczny, a nie walidacja kliniczna. Ręczny przegląd przez drugą osobę pozostaje oznaczony jako oczekujący.\n\n## Uruchomienie projektu",
    "Jest to automatyczny audyt techniczny, a nie walidacja kliniczna. Ręczny przegląd przez drugą osobę pozostaje oznaczony jako oczekujący.\n\n## Polityka precyzji wyświetlania\n\nEtap `0.1.2-dev.2` formalizuje oddzielenie dokładnej wartości domenowej od tekstu prezentowanego użytkownikowi. Obliczenia pozostają ułamkami dokładnymi; dopiero formatter tworzy tekst z przecinkiem dziesiętnym, zaokrągleniem `half-up`, maksymalnie 12 miejscami po przecinku oraz adaptacyjną liczbą cyfr znaczących.\n\nWersjonowana macierz 31 przypadków granicznych sprawdza m.in. progi zaokrąglenia, ułamki okresowe, bardzo małe wartości dodatnie i ujemne, brak mylącego `0`, zero przed przecinkiem oraz znormalizowany zapis naukowy. Audyt wykrył i poprawił możliwość pokazania zapisu `10e-20`; ta sama wartość jest teraz prezentowana kanonicznie jako `1e-19`.\n\nZmiana dotyczy wyłącznie prezentacji i nie wpływa na dokładne wartości używane przez solver.\n\n## Uruchomienie projektu",
)
replace_once(
    readme,
    "- [Techniczny zestaw referencyjny 0.1.2](docs/TECHNICAL_REFERENCE_ORACLE.md)",
    "- [Techniczny zestaw referencyjny 0.1.2](docs/TECHNICAL_REFERENCE_ORACLE.md)\n- [Polityka precyzji i formatowania wyniku](docs/DISPLAY_PRECISION_POLICY.md)",
)
replace_once(
    readme,
    "**Wersja rozwojowa:** `0.1.2-dev.1+11` — niezależny techniczny zestaw referencyjny  ",
    "**Wersja rozwojowa:** `0.1.2-dev.2+12` — audyt precyzji warstwy prezentacji  ",
)

changelog = Path('CHANGELOG.md')
replace_once(
    changelog,
    "Wszystkie istotne zmiany projektu są dokumentowane w tym pliku.\n\n## [0.1.2-dev.1] — w przygotowaniu",
    "Wszystkie istotne zmiany projektu są dokumentowane w tym pliku.\n\n## [0.1.2-dev.2] — w przygotowaniu\n\n### Poprawiono\n\n- zapis naukowy jest normalizowany po przeniesieniu wynikającym z zaokrąglenia, np. `10e-20` → `1e-19`;\n- formatter zachowuje rozdzielenie dokładnej wartości domenowej i tekstu wyświetlanego użytkownikowi.\n\n### Dodano\n\n- wersjonowaną macierz 31 przypadków granicznych polityki prezentacji;\n- testy zaokrąglania `half-up`, przecinka dziesiętnego i usuwania niepotrzebnych zer końcowych;\n- testy wartości okresowych, dodatnich, ujemnych, dużych i bardzo małych;\n- testy granicy między zapisem stałopozycyjnym i naukowym;\n- niezmienniki blokujące wyświetlenie wartości niezerowej jako `0` lub `-0`;\n- dokument `docs/DISPLAY_PRECISION_POLICY.md`.\n\n### Wyniki automatycznego audytu\n\n- 31/31 przypadków polityki prezentacji zakończonych powodzeniem;\n- cały projekt: `148/148` testów;\n- pokrycie liniowe `lib/domain/`: `93,99%` (`720/766` linii);\n- formatowanie i analiza statyczna bez problemów.\n\n### Granice\n\n- zmiana nie modyfikuje obliczeń domenowych ani tolerancji solvera;\n- nie stanowi walidacji klinicznej;\n- ręczny przegląd przypadków przez drugą osobę pozostaje oczekujący.\n\n## [0.1.2-dev.1] — 2026-08-03",
)

roadmap = Path('ROADMAP.md')
replace_once(
    roadmap,
    "**Aktualny etap:** `0.1.2-dev.1 — niezależny techniczny zestaw referencyjny`",
    "**Aktualny etap:** `0.1.2-dev.2 — audyt precyzji warstwy prezentacji`",
)
replace_once(
    roadmap,
    "- [ ] osobny audyt polityki zaokrągleń warstwy prezentacji;",
    "- [x] osobny audyt polityki zaokrągleń warstwy prezentacji;",
)
replace_once(
    roadmap,
    "**Stan automatyczny:** 480/480 przypadków, 600/600 dokładnych porównań, 143/143 testy oraz 93,99% pokrycia domeny.\n\n**Dokumentacja:** [`docs/TECHNICAL_REFERENCE_ORACLE.md`](docs/TECHNICAL_REFERENCE_ORACLE.md).",
    "**Stan automatyczny:** 480/480 przypadków domenowych, 600/600 dokładnych porównań, 31/31 przypadków precyzji prezentacji, 148/148 testów oraz 93,99% pokrycia domeny.\n\n**Wykryta poprawka:** normalizacja przeniesienia w zapisie naukowym (`10e-20` → `1e-19`) bez zmiany dokładnej wartości.\n\n**Dokumentacja:** [`docs/TECHNICAL_REFERENCE_ORACLE.md`](docs/TECHNICAL_REFERENCE_ORACLE.md) i [`docs/DISPLAY_PRECISION_POLICY.md`](docs/DISPLAY_PRECISION_POLICY.md).",
)
