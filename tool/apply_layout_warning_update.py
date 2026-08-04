from __future__ import annotations

import re
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    source = path.read_text(encoding="utf-8")
    if source.count(old) != 1:
        raise SystemExit(
            f"Expected exactly one occurrence in {path}, found {source.count(old)}: {old[:160]!r}",
        )
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


def replace_regex_once(path: Path, pattern: str, replacement: str) -> None:
    source = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, source, count=1, flags=re.DOTALL)
    if count != 1:
        raise SystemExit(f"Expected one regex match in {path}, found {count}: {pattern!r}")
    path.write_text(updated, encoding="utf-8")


calculator = Path("lib/presentation/calculator/calculator_screen.dart")
replace_once(
    calculator,
    "import 'package:kalkulator_lekow/presentation/calculator/widgets/calculation_field.dart';\n"
    "import 'package:kalkulator_lekow/presentation/formatting/rational_decimal_formatter.dart';",
    "import 'package:kalkulator_lekow/presentation/calculator/widgets/calculation_field.dart';\n"
    "import 'package:kalkulator_lekow/presentation/common/app_footer.dart';\n"
    "import 'package:kalkulator_lekow/presentation/formatting/rational_decimal_formatter.dart';",
)
replace_once(
    calculator,
    "        title: const Text('Kalkulator leków'),",
    "        title: const Text('InfusionCalc'),",
)
replace_once(
    calculator,
    "            PwaInstallBanner(promptStore: widget.pwaInstallPromptStore),\n"
    "            const _TechnicalCalculatorWarning(),",
    "            const _TopUtilityRow(),\n"
    "            PwaInstallBanner(promptStore: widget.pwaInstallPromptStore),",
)
replace_once(
    calculator,
    "            Text(\n"
    "              'Wyniki są aktualizowane bez przycisku „Oblicz”. '\n"
    "              'Zaokrąglanie dotyczy wyłącznie prezentacji.',\n"
    "              style: Theme.of(context).textTheme.bodySmall,\n"
    "              textAlign: TextAlign.center,\n"
    "            ),\n"
    "          ],",
    "            Text(\n"
    "              'Wyniki są aktualizowane bez przycisku „Oblicz”. '\n"
    "              'Zaokrąglanie dotyczy wyłącznie prezentacji.',\n"
    "              style: Theme.of(context).textTheme.bodySmall,\n"
    "              textAlign: TextAlign.center,\n"
    "            ),\n"
    "            const SizedBox(height: 24),\n"
    "            const AppFooter(key: Key('app-footer')),\n"
    "          ],",
)
replace_regex_once(
    calculator,
    r"class _TechnicalCalculatorWarning extends StatelessWidget \{.*?\n\}\n\nclass _ProblemSummary",
    """class _TopUtilityRow extends StatelessWidget {
  const _TopUtilityRow();

  static const String _warningText =
      'Techniczny kalkulator — nie jest przeznaczony do podejmowania '
      'decyzji klinicznych.';

  @override
  Widget build(BuildContext context) => Row(
    key: const Key('top-utility-row'),
    children: <Widget>[
      IconButton(
        key: const Key('technical-warning-button'),
        tooltip: 'Informacja o przeznaczeniu kalkulatora',
        onPressed: () => _showWarning(context),
        color: Theme.of(context).colorScheme.error,
        icon: const Icon(Icons.warning_amber_rounded),
      ),
      const Spacer(),
      // The right side is intentionally reserved for future language controls.
    ],
  );

  Future<void> _showWarning(BuildContext context) => showDialog<void>(
    context: context,
    builder: (BuildContext dialogContext) => AlertDialog(
      key: const Key('technical-warning-dialog'),
      title: const Text('Ważna informacja'),
      content: const Text(_warningText),
      actions: <Widget>[
        FilledButton(
          key: const Key('technical-warning-acknowledge-button'),
          onPressed: () => Navigator.of(dialogContext).pop(),
          child: const Text('Rozumiem'),
        ),
      ],
    ),
  );
}

class _ProblemSummary""",
)

calculator_test = Path("test/presentation/calculator_screen_test.dart")
replace_once(
    calculator_test,
    "  testWidgets('shows the calculator sections and safety warning', (\n"
    "    WidgetTester tester,\n"
    "  ) async {\n"
    "    await tester.pumpWidget(const KalkulatorLekowApp());\n\n"
    "    expect(find.text('Kalkulator leków'), findsOneWidget);\n"
    "    expect(\n"
    "      find.text(\n"
    "        'Techniczny kalkulator — nie jest przeznaczony do podejmowania '\n"
    "        'decyzji klinicznych.',\n"
    "      ),\n"
    "      findsOneWidget,\n"
    "    );\n"
    "    expect(find.text('Masa pacjenta'), findsOneWidget);\n"
    "    expect(find.text('Ilość leku'), findsOneWidget);\n\n"
    "    await _reveal(tester, find.text('Dawka / szybkość podaży'));\n\n"
    "    expect(find.text('Przepływ'), findsOneWidget);\n"
    "    expect(find.text('Dawka / szybkość podaży'), findsOneWidget);\n"
    "    expect(find.textContaining('bez przycisku'), findsOneWidget);\n"
    "  });",
    "  testWidgets('shows the InfusionCalc header and compact utility row', (\n"
    "    WidgetTester tester,\n"
    "  ) async {\n"
    "    await tester.pumpWidget(const KalkulatorLekowApp());\n\n"
    "    expect(find.text('InfusionCalc'), findsOneWidget);\n"
    "    expect(find.byKey(const Key('technical-warning-button')), findsOneWidget);\n"
    "    expect(\n"
    "      find.text(\n"
    "        'Techniczny kalkulator — nie jest przeznaczony do podejmowania '\n"
    "        'decyzji klinicznych.',\n"
    "      ),\n"
    "      findsNothing,\n"
    "    );\n"
    "    final Rect utilityRow = tester.getRect(\n"
    "      find.byKey(const Key('top-utility-row')),\n"
    "    );\n"
    "    final Rect warningButton = tester.getRect(\n"
    "      find.byKey(const Key('technical-warning-button')),\n"
    "    );\n"
    "    expect(warningButton.center.dx, lessThan(utilityRow.center.dx));\n"
    "    expect(find.text('Masa pacjenta'), findsOneWidget);\n"
    "    expect(find.text('Ilość leku'), findsOneWidget);\n\n"
    "    await _reveal(tester, find.text('Dawka / szybkość podaży'));\n\n"
    "    expect(find.text('Przepływ'), findsOneWidget);\n"
    "    expect(find.text('Dawka / szybkość podaży'), findsOneWidget);\n"
    "    expect(find.textContaining('bez przycisku'), findsOneWidget);\n"
    "  });\n\n"
    "  testWidgets('opens and acknowledges the technical warning dialog', (\n"
    "    WidgetTester tester,\n"
    "  ) async {\n"
    "    await tester.pumpWidget(const KalkulatorLekowApp());\n\n"
    "    const String warningText =\n"
    "        'Techniczny kalkulator — nie jest przeznaczony do podejmowania '\n"
    "        'decyzji klinicznych.';\n"
    "    expect(find.text(warningText), findsNothing);\n\n"
    "    await tester.tap(find.byKey(const Key('technical-warning-button')));\n"
    "    await tester.pumpAndSettle();\n\n"
    "    expect(find.byKey(const Key('technical-warning-dialog')), findsOneWidget);\n"
    "    expect(find.text(warningText), findsOneWidget);\n"
    "    expect(find.text('Rozumiem'), findsOneWidget);\n\n"
    "    await tester.tap(\n"
    "      find.byKey(const Key('technical-warning-acknowledge-button')),\n"
    "    );\n"
    "    await tester.pumpAndSettle();\n\n"
    "    expect(find.byKey(const Key('technical-warning-dialog')), findsNothing);\n"
    "  });",
)
replace_once(
    calculator_test,
    "  testWidgets('supports a small dark screen with enlarged text', (",
    "  testWidgets('renders the footer inside the scrollable page end', (\n"
    "    WidgetTester tester,\n"
    "  ) async {\n"
    "    await tester.pumpWidget(const KalkulatorLekowApp());\n\n"
    "    expect(\n"
    "      find.text('InfusionCalc · Technical infusion calculator'),\n"
    "      findsNothing,\n"
    "    );\n\n"
    "    final Finder footer = find.byKey(const Key('app-footer'));\n"
    "    await _reveal(tester, footer);\n\n"
    "    expect(footer, findsOneWidget);\n"
    "    expect(\n"
    "      find.ancestor(of: footer, matching: find.byType(ListView)),\n"
    "      findsOneWidget,\n"
    "    );\n"
    "    expect(\n"
    "      find.text('InfusionCalc · Technical infusion calculator'),\n"
    "      findsOneWidget,\n"
    "    );\n"
    "  });\n\n"
    "  testWidgets('supports a small dark screen with enlarged text', (",
)

replace_once(
    Path("pubspec.yaml"),
    "version: 0.1.3-beta.1+16",
    "version: 0.1.3-beta.2+17",
)

replace_once(
    Path("README.md"),
    "**Wersja publiczna:** `0.1.3-beta.1+16` — kontekstowa instalacja PWA na iOS i Androidzie  ",
    "**Wersja publiczna:** `0.1.3-beta.2+17` — uporządkowany nagłówek, kompaktowe ostrzeżenie i przewijana stopka  ",
)

roadmap = Path("ROADMAP.md")
replace_once(
    roadmap,
    "**Aktualny etap:** `0.1.3-beta.1 — kontekstowa instalacja PWA`",
    "**Aktualny etap:** `0.1.3-beta.2 — porządek nagłówka i układu strony`",
)
replace_once(
    roadmap,
    "### 0.1.3-beta.1 — Kontekstowa instalacja PWA **← obecnie**",
    "### 0.1.3-beta.1 — Kontekstowa instalacja PWA **✓ ukończono**",
)
replace_once(
    roadmap,
    "**Zgłoszenie:** [issue #32](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/32).\n\n"
    "### 0.1.3 — Dostępność i ergonomia",
    """**Zgłoszenie:** [issue #32](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/32).

### 0.1.3-beta.2 — Porządek nagłówka i układu strony **← obecnie**

- [x] nazwa `InfusionCalc` w nagłówku aplikacji;
- [x] stopka przeniesiona do końca przewijanej zawartości;
- [x] pełny komunikat ostrzegawczy ukryty z głównego ekranu;
- [x] pojedyncza ikona ostrzeżenia wyrównana do lewej;
- [x] prawa część wiersza zarezerwowana pod przyszły wybór języka;
- [x] okno ostrzeżenia z pełną treścią i przyciskiem `Rozumiem`;
- [x] testy nagłówka, okna ostrzeżenia i położenia stopki;
- [ ] potwierdzenie układu na fizycznym iPhonie oraz Androidzie po wdrożeniu.

**Zgłoszenie:** [issue #34](https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/34).

### 0.1.3 — Dostępność i ergonomia""",
)

replace_once(
    Path("CHANGELOG.md"),
    "## [Unreleased]\n\n## [0.1.3-beta.1] — 2026-08-04",
    """## [Unreleased]

## [0.1.3-beta.2] — 2026-08-04

### Zmieniono

- tytuł głównego nagłówka z `Kalkulator leków` na `InfusionCalc`;
- stopkę z elementu stale widocznego na element umieszczony na końcu przewijanej strony;
- pełną kartę ostrzegawczą na kompaktową ikonę wyrównaną do lewej strony wiersza narzędziowego.

### Dodano

- okno z pełną treścią ostrzeżenia otwierane po kliknięciu ikony;
- przycisk `Rozumiem` zamykający okno ostrzeżenia;
- wolne miejsce po prawej stronie górnego wiersza pod przyszły wybór języka;
- testy regresji nagłówka, widoczności ostrzeżenia i położenia stopki w przewijanej zawartości.

### Granice

- brak zmian w solverze, równaniach, jednostkach, precyzji i danych użytkownika.

## [0.1.3-beta.1] — 2026-08-04""",
)
