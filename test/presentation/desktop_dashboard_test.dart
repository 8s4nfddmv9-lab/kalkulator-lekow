import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/app.dart';

void main() {
  const List<Size> desktopSizes = <Size>[
    Size(1280, 720),
    Size(1366, 768),
    Size(1440, 900),
    Size(1508, 900),
    Size(1920, 1080),
  ];

  for (final Size size in desktopSizes) {
    testWidgets('desktop dashboard fits $size empty and calculated', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = size;
      tester.view.devicePixelRatio = 1;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(const KalkulatorLekowApp());
      await tester.pumpAndSettle();
      _expectNoScroll(tester);
      _expectResultAligned(tester);
      if (size.width == 1508) _expectDoseNearDrug(tester);

      for (final (String key, String value) in <(String, String)>[
        ('value-bodyMass', '70'),
        ('value-drugAmount', '4'),
        ('value-solutionVolume', '50'),
        ('value-flowRate', '5'),
      ]) {
        await tester.enterText(find.byKey(Key(key)), value);
        await tester.pump();
      }
      await tester.pumpAndSettle();
      expect(find.text('0,095238095 µg/kg/min'), findsWidgets);
      expect(find.text('10 h'), findsOneWidget);
      _expectNoScroll(tester);
      _expectResultAligned(tester);
      if (size.width == 1508) _expectDoseNearDrug(tester);

      await tester.tap(find.byKey(const Key('calculation-details')));
      await tester.pumpAndSettle();
      expect(
        find.byKey(const Key('calculation-details-dialog')),
        findsOneWidget,
      );
      await tester.tap(find.text('Zamknij'));
      await tester.pumpAndSettle();
      _expectNoScroll(tester);

      await tester.tap(find.byKey(const Key('language-switch-button')));
      await tester.pumpAndSettle();
      _expectNoScroll(tester);
      _expectResultAligned(tester);
      if (size.width == 1508) _expectDoseNearDrug(tester);
    });
  }

  testWidgets('validation remains visible in the shortest desktop viewport', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1280, 720);
    tester.view.devicePixelRatio = 1;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const KalkulatorLekowApp());
    await tester.enterText(find.byKey(const Key('value-bodyMass')), '0');
    await tester.tap(find.byKey(const Key('value-drugAmount')));
    await tester.pumpAndSettle();

    expect(find.text('Sprawdź dane'), findsOneWidget);
    expect(
      find.textContaining('Wartość musi być większa od zera.'),
      findsWidgets,
    );
    _expectNoScroll(tester);
  });

  testWidgets(
    'invalid input with filled values remains readable at 1280 by 720',
    (WidgetTester tester) async {
      tester.view.physicalSize = const Size(1280, 720);
      tester.view.devicePixelRatio = 1;
      addTearDown(() {
        tester.view.resetPhysicalSize();
        tester.view.resetDevicePixelRatio();
      });

      await tester.pumpWidget(const KalkulatorLekowApp());
      for (final (String key, String value) in <(String, String)>[
        ('value-bodyMass', '70'),
        ('value-drugAmount', '4'),
        ('value-solutionVolume', '50'),
        ('value-flowRate', '5'),
      ]) {
        await tester.enterText(find.byKey(Key(key)), value);
        await tester.pump();
      }
      await tester.enterText(find.byKey(const Key('value-bodyMass')), '0');
      await tester.tap(find.byKey(const Key('value-drugAmount')));
      await tester.pumpAndSettle();
      expect(find.text('Sprawdź dane'), findsOneWidget);
      _expectNoScroll(tester);
    },
  );

  testWidgets('long numerical results wrap without dashboard overflow', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1280, 720);
    tester.view.devicePixelRatio = 1;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(const KalkulatorLekowApp());
    for (final (String key, String value) in <(String, String)>[
      ('value-bodyMass', '70'),
      ('value-drugAmount', '12345678901234567890'),
      ('value-solutionVolume', '50'),
      ('value-flowRate', '5'),
    ]) {
      await tester.enterText(find.byKey(Key(key)), value);
      await tester.pump();
    }
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('desktop-main-result')), findsOneWidget);
    _expectNoScroll(tester);
  });
}

void _expectResultAligned(WidgetTester tester) {
  final double flowTop = tester
      .getTopLeft(find.byKey(const Key('calculation-field-flowRate')))
      .dy;
  final double resultTop = tester
      .getTopLeft(find.byKey(const Key('desktop-results-card')))
      .dy;
  expect(resultTop, moreOrLessEquals(flowTop, epsilon: 0.5));
}

void _expectDoseNearDrug(WidgetTester tester) {
  final double drugTop = tester
      .getTopLeft(find.byKey(const Key('calculation-field-drugAmount')))
      .dy;
  final double doseTop = tester
      .getTopLeft(
        find.byKey(const Key('calculation-field-weightNormalizedDose')),
      )
      .dy;
  expect(doseTop, moreOrLessEquals(drugTop, epsilon: 12));
}

void _expectNoScroll(WidgetTester tester) {
  final Finder scrollable = find.descendant(
    of: find.byKey(const Key('desktop-dashboard-scroll')),
    matching: find.byType(Scrollable),
  );
  expect(scrollable, findsWidgets);
  final ScrollableState state = tester.state<ScrollableState>(scrollable.first);
  expect(state.position.maxScrollExtent, 0);
  expect(tester.takeException(), isNull);
}
