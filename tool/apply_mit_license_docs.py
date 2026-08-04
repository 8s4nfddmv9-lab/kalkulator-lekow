from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    if old not in source:
        raise SystemExit(f"Expected block not found in {path}: {old!r}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


replace_once(
    Path("README.md"),
    "## Licencja\n\nLicencja projektu nie została jeszcze wybrana. Do czasu dodania pliku `LICENSE` wszystkie prawa pozostają zastrzeżone.",
    """## Licencja

Projekt jest udostępniany na licencji [MIT](LICENSE). Licencja pozwala używać, kopiować, modyfikować, publikować i rozpowszechniać kod, również komercyjnie, pod warunkiem zachowania informacji o prawach autorskich i treści licencji.

Copyright © 2026 M W. Oprogramowanie jest udostępniane bez gwarancji, zgodnie z warunkami pliku [`LICENSE`](LICENSE).""",
)

replace_once(
    Path("CHANGELOG.md"),
    "## [Unreleased]\n\n",
    """## [Unreleased]

### Dodano

- licencję MIT z oznaczeniem praw autorskich `Copyright (c) 2026 M W`;
- odnośnik do licencji i informację `© 2026 M W · MIT License` w stopce aplikacji;
- test regresji odnośnika licencyjnego w stopce.

### Zmieniono

- sekcję licencyjną README, która teraz opisuje warunki używania projektu i odsyła do pliku `LICENSE`.

""",
)
