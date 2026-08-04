import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/app.dart';
import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';
import 'package:kalkulator_lekow/presentation/calculator/calculator_screen.dart';

import '../support/recording_analytics_tracker.dart';

void main() {
  testWidgets('shows the InfusionCalc header and compact utility row', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    expect(find.text('InfusionCalc'), findsOneWidget);
    expect(find.byKey(const Key('technical-warning-button')), findsOneWidget);
    expect(
      find.text(
        'Techniczny kalkulator — nie jest przeznaczony do podejmowania '
        'decyzji klinicznych.',
      ),
      findsNothing,
    );
    final Rect utilityRow = tester.getRect(
      find.byKey(const Key('top-utility-row')),
    );
    final Rect warningButton = tester.getRect(
      find.byKey(const Key('technical-warning-button')),
    );
    expect(warningButton.center.dx, lessThan(utilityRow.center.dx));
    expect(find.text('Masa pacjenta'), findsOneWidget);
    expect(find.text('Ilość leku'), findsOneWidget);

    await _reveal(tester, find.text('Dawka / szybkość podaży'));

    expect(find.text('Przepływ'), findsOneWidget);
    expect(find.text('Dawka / szybkość podaży'), findsOneWidget);
    expect(find.textContaining('bez przycisku'), findsOneWidget);
  });

  testWidgets('opens, tracks and acknowledges the technical warning', (
    WidgetTester tester,
  ) async {
    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();
    await tester.pumpWidget(KalkulatorLekowApp(analyticsTracker: tracker));

    const String warningText =
        'Techniczny kalkulator — nie jest przeznaczony do podejmowania '
        'decyzji klinicznych.';
    expect(find.text(warningText), findsNothing);

    await tester.tap(find.byKey(const Key('technical-warning-button')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('technical-warning-dialog')), findsOneWidget);
    expect(find.text(warningText), findsOneWidget);
    expect(tracker.count(AnalyticsEvent.warningOpened), 1);
    expect(find.text('Rozumiem'), findsOneWidget);

    await tester.tap(
      find.byKey(const Key('technical-warning-acknowledge-button')),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('technical-warning-dialog')), findsNothing);
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

  testWidgets('prefixes comma and dot entered into an empty field', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());
    final Finder field = find.byKey(const Key('value-concentration'));
    await _reveal(tester, field);
    await tester.showKeyboard(field);

    tester.testTextInput.enterText(',');
    await tester.pump();

    expect(tester.widget<TextField>(field).controller!.text, '0,');
    _expectKeyboardActive(tester, field);

    tester.testTextInput.enterText('');
    await tester.pump();
    tester.testTextInput.enterText('.');
    await tester.pump();

    expect(tester.widget<TextField>(field).controller!.text, '0,');
    _expectKeyboardActive(tester, field);
  });

  testWidgets('keeps keyboard active while typing and deleting a fraction', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());
    final Finder field = find.byKey(const Key('value-concentration'));
    await _reveal(tester, field);
    await tester.showKeyboard(field);

    for (final String text in <String>[
      '0',
      '0,',
      '0,0',
      '0,05',
      '0,0',
      '0,',
      '0',
    ]) {
      tester.testTextInput.enterText(text);
      await tester.pump();

      expect(tester.widget<TextField>(field).controller!.text, text);
      expect(find.text('Wartość musi być większa od zera.'), findsNothing);
      _expectKeyboardActive(tester, field);
    }
  });

  testWidgets('shows an inline error for a zero body mass after editing', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-bodyMass', '0');
    expect(find.text('Wartość musi być większa od zera.'), findsNothing);

    await tester.tap(find.byKey(const Key('value-drugAmount')));
    await tester.pumpAndSettle();

    expect(find.text('Wartość musi być większa od zera.'), findsOneWidget);
    await _reveal(tester, find.text('Sprawdź dane'));
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

  testWidgets('renders the footer inside the scrollable page end', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    expect(
      find.text('InfusionCalc · Technical infusion calculator'),
      findsNothing,
    );

    final Finder footer = find.byKey(const Key('app-footer'));
    await _reveal(tester, footer);

    expect(footer, findsOneWidget);
    expect(
      find.ancestor(of: footer, matching: find.byType(ListView)),
      findsOneWidget,
    );
    expect(
      find.text('InfusionCalc · Technical infusion calculator'),
      findsOneWidget,
    );
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

void _expectKeyboardActive(WidgetTester tester, Finder field) {
  final TextField textField = tester.widget<TextField>(field);
  expect(textField.focusNode, isNotNull);
  expect(textField.focusNode!.hasFocus, isTrue);
  expect(tester.testTextInput.isVisible, isTrue);
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
