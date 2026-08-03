import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/app.dart';
import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  testWidgets(
    'late preferences cannot relabel a value entered during startup',
    (WidgetTester tester) async {
      final _DelayedPreferencesStore store = _DelayedPreferencesStore(
        CalculatorPreferences(
          unitCodes: <QuantityKind, String>{
            QuantityKind.drugAmount: UnitCatalog.microgram.code,
            QuantityKind.concentration: UnitCatalog.find('mg/mL').code,
          },
          dosePerKilogram: false,
        ),
      );

      await tester.pumpWidget(KalkulatorLekowApp(preferencesStore: store));
      await tester.pump();

      await _enter(tester, 'value-drugAmount', '1');
      await _enter(tester, 'value-solutionVolume', '1');

      expect(await _fieldText(tester, 'value-concentration'), '1000');
      expect(
        find.byKey(const ValueKey<String>('unit-Ilość leku-mg')),
        findsOneWidget,
      );

      store.completeLoad();
      await tester.pumpAndSettle();

      expect(await _fieldText(tester, 'value-drugAmount'), '1');
      expect(await _fieldText(tester, 'value-concentration'), '1000');
      expect(
        find.byKey(const ValueKey<String>('unit-Ilość leku-mg')),
        findsOneWidget,
      );
      expect(
        tester
            .widget<FilterChip>(find.byKey(const Key('per-kilogram-toggle')))
            .selected,
        isTrue,
      );
    },
  );

  testWidgets(
    'preferences may still restore after transient values are cleared',
    (WidgetTester tester) async {
      final _DelayedPreferencesStore store = _DelayedPreferencesStore(
        CalculatorPreferences(
          unitCodes: <QuantityKind, String>{
            QuantityKind.drugAmount: UnitCatalog.microgram.code,
          },
          dosePerKilogram: false,
        ),
      );

      await tester.pumpWidget(KalkulatorLekowApp(preferencesStore: store));
      await tester.pump();

      await _enter(tester, 'value-drugAmount', '1');
      await tester.tap(find.byTooltip('Wyczyść wszystkie pola'));
      await tester.pumpAndSettle();

      store.completeLoad();
      await tester.pumpAndSettle();

      expect(await _fieldText(tester, 'value-drugAmount'), isEmpty);
      expect(
        find.byKey(const ValueKey<String>('unit-Ilość leku-µg')),
        findsOneWidget,
      );
      expect(
        tester
            .widget<FilterChip>(find.byKey(const Key('per-kilogram-toggle')))
            .selected,
        isFalse,
      );
    },
  );
}

final class _DelayedPreferencesStore implements CalculatorPreferencesStore {
  _DelayedPreferencesStore(this.preferences);

  final CalculatorPreferences preferences;
  final Completer<CalculatorPreferences> _loadCompleter =
      Completer<CalculatorPreferences>();

  void completeLoad() {
    if (!_loadCompleter.isCompleted) {
      _loadCompleter.complete(preferences);
    }
  }

  @override
  Future<CalculatorPreferences> load() => _loadCompleter.future;

  @override
  Future<void> save(CalculatorPreferences preferences) async {}
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
