import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/app.dart';
import 'package:kalkulator_lekow/presentation/calculator/calculator_screen.dart';

void main() {
  testWidgets('shows the calculator sections and safety warning', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    expect(find.text('Kalkulator leków'), findsOneWidget);
    expect(
      find.text('Prototyp — nie używać do podejmowania decyzji klinicznych.'),
      findsOneWidget,
    );
    expect(find.text('Masa pacjenta'), findsOneWidget);
    expect(find.text('Ilość leku'), findsOneWidget);

    await _reveal(tester, find.text('Dawka / szybkość podaży'));

    expect(find.text('Przepływ'), findsOneWidget);
    expect(find.text('Dawka / szybkość podaży'), findsOneWidget);
    expect(find.textContaining('bez przycisku'), findsOneWidget);
  });

  testWidgets('calculates concentration immediately from amount and volume', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-drugAmount', '4');
    await _enter(tester, 'value-solutionVolume', '50');

    expect(await _fieldText(tester, 'value-concentration'), '80');
    expect(find.text('Wyliczone'), findsWidgets);
  });

  testWidgets('calculates the full reference chain in real time', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-bodyMass', '70');
    await _enter(tester, 'value-drugAmount', '4');
    await _enter(tester, 'value-solutionVolume', '50');
    await _enter(tester, 'value-flowRate', '5');

    expect(await _fieldText(tester, 'value-concentration'), '80');
    expect(await _fieldText(tester, 'dose-value-field'), '0,095238095');

    await _reveal(tester, find.byKey(const Key('infusion-duration-value')));
    expect(find.text('10 h'), findsOneWidget);
    expect(find.byKey(const Key('calculation-details')), findsOneWidget);
  });

  testWidgets('calculates 5.25 ml/h from a desired weight-normalized dose', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-bodyMass', '70');
    await _enter(tester, 'value-drugAmount', '4');
    await _enter(tester, 'value-solutionVolume', '50');
    await _enter(tester, 'dose-value-field', '0,1');

    expect(await _fieldText(tester, 'value-flowRate'), '5,25');
  });

  testWidgets('allows disabling the per-kilogram component', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-concentration', '80');
    await _enter(tester, 'value-flowRate', '5');
    await _reveal(tester, find.byKey(const Key('per-kilogram-toggle')));

    expect(await _fieldText(tester, 'dose-value-field'), isEmpty);

    await tester.tap(find.byKey(const Key('per-kilogram-toggle')));
    await tester.pumpAndSettle();

    expect(await _fieldText(tester, 'dose-value-field'), '6,6666667');
    expect(find.text('szybkość podaży bez /kg'), findsOneWidget);
  });

  testWidgets('changing mg to micrograms preserves physical amount', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());
    await _enter(tester, 'value-drugAmount', '1');

    final Finder selector = find.byKey(
      const ValueKey<String>('unit-Ilość leku-mg'),
    );
    await _reveal(tester, selector);
    await tester.tap(selector);
    await tester.pumpAndSettle();
    await tester.tap(find.text('µg').last);
    await tester.pumpAndSettle();

    expect(await _fieldText(tester, 'value-drugAmount'), '1000');
  });

  testWidgets('shows an inline error for a zero body mass', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-bodyMass', '0');

    expect(find.text('Wartość musi być większa od zera.'), findsOneWidget);
    expect(find.text('Sprawdź dane'), findsOneWidget);
  });

  testWidgets('shows the auditable formula for a calculated result', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-drugAmount', '4');
    await _enter(tester, 'value-solutionVolume', '50');
    await _reveal(tester, find.byKey(const Key('calculation-details')));
    await tester.tap(find.byKey(const Key('calculation-details')));
    await tester.pumpAndSettle();

    expect(find.text('C = A / V'), findsOneWidget);
    expect(find.text('Wynik: 80 µg/ml'), findsOneWidget);
  });

  testWidgets('clear button removes all inputs and results', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-drugAmount', '4');
    await _enter(tester, 'value-solutionVolume', '50');
    expect(await _fieldText(tester, 'value-concentration'), '80');

    await tester.tap(find.byTooltip('Wyczyść wszystkie pola'));
    await tester.pumpAndSettle();

    expect(await _fieldText(tester, 'value-drugAmount'), isEmpty);
    expect(await _fieldText(tester, 'value-solutionVolume'), isEmpty);
    expect(await _fieldText(tester, 'value-concentration'), isEmpty);
  });

  testWidgets('supports a small dark screen with enlarged text', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(320, 568);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        theme: ThemeData.dark(useMaterial3: true),
        home: MediaQuery(
          data: const MediaQueryData(textScaler: TextScaler.linear(1.5)),
          child: const CalculatorScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.byType(ListView), findsOneWidget);

    await _reveal(tester, find.text('Dawka / szybkość podaży'));

    expect(tester.takeException(), isNull);
    expect(find.text('Dawka / szybkość podaży'), findsOneWidget);
  });
}

Future<void> _enter(
  WidgetTester tester,
  String key,
  String value,
) async {
  final Finder finder = find.byKey(Key(key));
  await _reveal(tester, finder);
  await tester.enterText(finder, value);
  await tester.pumpAndSettle();
}

Future<String> _fieldText(WidgetTester tester, String key) async {
  final Finder finder = find.byKey(Key(key));
  await _reveal(tester, finder);
  return tester.widget<TextField>(finder).controller!.text;
}

Future<void> _reveal(WidgetTester tester, Finder target) async {
  if (target.evaluate().isNotEmpty) {
    await tester.ensureVisible(target.first);
    await tester.pumpAndSettle();
    return;
  }

  final Finder listView = find.byType(ListView);
  for (int attempt = 0; attempt < 16; attempt++) {
    await tester.drag(listView, const Offset(0, -280));
    await tester.pumpAndSettle();
    if (target.evaluate().isNotEmpty) {
      await tester.ensureVisible(target.first);
      await tester.pumpAndSettle();
      return;
    }
  }
  for (int attempt = 0; attempt < 32; attempt++) {
    await tester.drag(listView, const Offset(0, 280));
    await tester.pumpAndSettle();
    if (target.evaluate().isNotEmpty) {
      await tester.ensureVisible(target.first);
      await tester.pumpAndSettle();
      return;
    }
  }
  fail('Could not reveal target: $target');
}
