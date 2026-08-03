import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/app.dart';
import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  testWidgets('restores units and dose mode without restoring numeric values', (
    WidgetTester tester,
  ) async {
    final _FakePreferencesStore store = _FakePreferencesStore(
      CalculatorPreferences(
        unitCodes: <QuantityKind, String>{
          QuantityKind.drugAmount: UnitCatalog.microgram.code,
          QuantityKind.concentration: UnitCatalog.find('mg/mL').code,
          QuantityKind.weightNormalizedDose: UnitCatalog.find('mg/kg/h').code,
        },
        dosePerKilogram: false,
      ),
    );

    await tester.pumpWidget(KalkulatorLekowApp(preferencesStore: store));
    await tester.pumpAndSettle();

    expect(
      find.byKey(const ValueKey<String>('unit-Ilość leku-µg')),
      findsOneWidget,
    );
    expect(await _fieldText(tester, 'value-bodyMass'), isEmpty);
    expect(await _fieldText(tester, 'value-drugAmount'), isEmpty);
    expect(await _fieldText(tester, 'value-concentration'), isEmpty);
    expect(await _fieldText(tester, 'value-flowRate'), isEmpty);
    expect(await _fieldText(tester, 'dose-value-field'), isEmpty);

    await _reveal(tester, find.text('szybkość podaży bez /kg'));
    expect(find.text('szybkość podaży bez /kg'), findsOneWidget);
  });

  testWidgets('changing a unit persists a presentation-only snapshot', (
    WidgetTester tester,
  ) async {
    final _FakePreferencesStore store = _FakePreferencesStore(
      CalculatorPreferences.defaults(),
    );

    await tester.pumpWidget(KalkulatorLekowApp(preferencesStore: store));
    await tester.pumpAndSettle();
    await _selectUnit(tester, selectorKey: 'unit-Ilość leku-mg', option: 'µg');
    await tester.pumpAndSettle();

    expect(store.saved, isNotEmpty);
    final CalculatorPreferences latest = store.saved.last;
    expect(latest.unitFor(QuantityKind.drugAmount), UnitCatalog.microgram);
    expect(latest.unitCodes.keys, contains(QuantityKind.drugAmount));
    expect(await _fieldText(tester, 'value-drugAmount'), isEmpty);
  });

  testWidgets('preference load failure keeps calculator usable', (
    WidgetTester tester,
  ) async {
    final _FakePreferencesStore store = _FakePreferencesStore(
      CalculatorPreferences.defaults(),
      failLoad: true,
    );

    await tester.pumpWidget(KalkulatorLekowApp(preferencesStore: store));
    await tester.pumpAndSettle();

    expect(
      find.textContaining(
        'Nie udało się odczytać ustawień jednostek. '
        'Użyto wartości domyślnych.',
      ),
      findsOneWidget,
    );
    await _enter(tester, 'value-drugAmount', '4');
    expect(await _fieldText(tester, 'value-drugAmount'), '4');
  });

  testWidgets('preference save failure does not interrupt calculations', (
    WidgetTester tester,
  ) async {
    final _FakePreferencesStore store = _FakePreferencesStore(
      CalculatorPreferences.defaults(),
      failSave: true,
    );

    await tester.pumpWidget(KalkulatorLekowApp(preferencesStore: store));
    await tester.pumpAndSettle();
    await _selectUnit(tester, selectorKey: 'unit-Ilość leku-mg', option: 'µg');
    await tester.pumpAndSettle();

    expect(
      find.textContaining(
        'Nie udało się zapisać ustawień jednostek. '
        'Obliczenia pozostają dostępne.',
      ),
      findsOneWidget,
    );
    await _enter(tester, 'value-drugAmount', '4000');
    await _enter(tester, 'value-solutionVolume', '50');
    expect(await _fieldText(tester, 'value-concentration'), '80');
  });
}

final class _FakePreferencesStore implements CalculatorPreferencesStore {
  _FakePreferencesStore(
    this.initial, {
    this.failLoad = false,
    this.failSave = false,
  });

  final CalculatorPreferences initial;
  final bool failLoad;
  final bool failSave;
  final List<CalculatorPreferences> saved = <CalculatorPreferences>[];

  @override
  Future<CalculatorPreferences> load() async {
    if (failLoad) {
      throw StateError('load failed');
    }
    return initial;
  }

  @override
  Future<void> save(CalculatorPreferences preferences) async {
    if (failSave) {
      throw StateError('save failed');
    }
    saved.add(preferences);
  }
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
