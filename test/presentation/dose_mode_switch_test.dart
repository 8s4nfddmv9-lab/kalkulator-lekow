import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/app.dart';

void main() {
  testWidgets('transfers an explicit per-kilogram dose to an absolute rate', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-bodyMass', '70');
    await _enter(tester, 'value-concentration', '80');
    await _enter(tester, 'dose-value-field', '0,1');

    expect(await _fieldText(tester, 'value-flowRate'), '5,25');

    await _toggleDoseMode(tester);

    expect(await _fieldText(tester, 'dose-value-field'), '7');

    await _enter(tester, 'value-bodyMass', '80');

    expect(await _fieldText(tester, 'dose-value-field'), '7');
    expect(await _fieldText(tester, 'value-flowRate'), '5,25');
  });

  testWidgets('transfers an explicit absolute rate to a per-kilogram dose', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-bodyMass', '70');
    await _enter(tester, 'value-concentration', '80');
    await _toggleDoseMode(tester);
    await _enter(tester, 'dose-value-field', '7');

    expect(await _fieldText(tester, 'value-flowRate'), '5,25');

    await _toggleDoseMode(tester);

    expect(await _fieldText(tester, 'dose-value-field'), '0,1');

    await _enter(tester, 'value-bodyMass', '80');

    expect(await _fieldText(tester, 'dose-value-field'), '0,1');
    expect(await _fieldText(tester, 'value-flowRate'), '6');
  });

  testWidgets('refuses to hide an explicit dose when body mass is missing', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'dose-value-field', '0,1');
    await _toggleDoseMode(tester);

    final FilterChip chip = tester.widget<FilterChip>(
      find.byKey(const Key('per-kilogram-toggle')),
    );
    expect(chip.selected, isTrue);
    expect(await _fieldText(tester, 'dose-value-field'), '0,1');

    final Finder message = find.textContaining(
      'Do przeliczenia wpisanej wartości potrzebna jest masa pacjenta',
    );
    await _reveal(tester, message);
    expect(message, findsOneWidget);
  });

  testWidgets('keeps the IU family when switching dose representation', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-bodyMass', '70');
    await _selectUnit(
      tester,
      selectorKey: 'unit-Dawka / szybkość podaży-µg/kg/min',
      option: 'IU/kg/h',
    );
    await _enter(tester, 'dose-value-field', '2');

    await _toggleDoseMode(tester);

    expect(
      find.byKey(
        const ValueKey<String>('unit-Dawka / szybkość podaży-IU/h'),
      ),
      findsOneWidget,
    );
    expect(await _fieldText(tester, 'dose-value-field'), '140');

    await _enter(tester, 'value-bodyMass', '80');
    expect(await _fieldText(tester, 'dose-value-field'), '140');
  });
}

Future<void> _toggleDoseMode(WidgetTester tester) async {
  final Finder toggle = find.byKey(const Key('per-kilogram-toggle'));
  await _reveal(tester, toggle);
  await tester.tap(toggle);
  await tester.pumpAndSettle();
}

Future<void> _selectUnit(
  WidgetTester tester, {
  required String selectorKey,
  required String option,
}) async {
  final Finder selector = find.byKey(ValueKey<String>(selectorKey));
  await _reveal(tester, selector);
  await tester.tap(selector);
  await tester.pumpAndSettle();
  await tester.tap(find.text(option).last);
  await tester.pumpAndSettle();
}

Future<void> _enter(WidgetTester tester, String key, String value) async {
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
