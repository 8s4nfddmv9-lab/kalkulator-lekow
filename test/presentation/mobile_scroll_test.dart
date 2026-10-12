import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/app.dart';
import 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';

void main() {
  testWidgets('narrow viewport with enlarged text can reach the footer', (
    WidgetTester tester,
  ) async {
    _mobileViewport(tester);
    tester.view.physicalSize = const Size(320, 568);
    tester.platformDispatcher.textScaleFactorTestValue = 2;
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);
    await tester.pumpWidget(const KalkulatorLekowApp());
    await tester.pumpAndSettle();
    final ScrollableState scroll = tester.state<ScrollableState>(
      find.byType(Scrollable).first,
    );
    scroll.position.jumpTo(scroll.position.maxScrollExtent);
    await tester.pumpAndSettle();
    final Rect footer = tester.getRect(find.byKey(const Key('app-footer')));
    expect(footer.bottom, lessThanOrEqualTo(568));
    expect(tester.takeException(), isNull);
  });

  for (final String state in <String>['filled', 'invalid', 'reverse']) {
    testWidgets('mobile $state form has stable geometry during touch drags', (
      WidgetTester tester,
    ) async {
      _mobileViewport(tester);
      await tester.pumpWidget(const KalkulatorLekowApp());
      await tester.pumpAndSettle();
      for (final (String key, String value) in <(String, String)>[
        ('value-bodyMass', '70'),
        ('value-drugAmount', '4'),
        ('value-solutionVolume', '50'),
        ('value-flowRate', '5'),
      ]) {
        await tester.enterText(find.byKey(Key(key)), value);
        await tester.pumpAndSettle();
      }
      expect(_text(tester, 'value-concentration'), '80');
      expect(_text(tester, 'dose-value-field'), '0,095238095');
      if (state == 'invalid') {
        await tester.enterText(find.byKey(const Key('value-bodyMass')), 'bad');
      } else if (state == 'reverse') {
        await tester.enterText(
          find.byKey(const Key('value-concentration')),
          '100',
        );
      }
      FocusManager.instance.primaryFocus?.unfocus();
      await tester.pumpAndSettle();
      final ScrollableState scroll = tester.state<ScrollableState>(
        find.byType(Scrollable).first,
      );
      scroll.position.jumpTo(0);
      await tester.pumpAndSettle();
      final double extent = scroll.position.maxScrollExtent;
      final String dose = _text(tester, 'dose-value-field');
      for (final double direction in <double>[-1, 1]) {
        final TestGesture gesture = await tester.startGesture(
          const Offset(200, 400),
        );
        for (int step = 0; step < 12; step++) {
          final double previous = scroll.position.pixels;
          await gesture.moveBy(Offset(0, direction * 12));
          await tester.pump(const Duration(milliseconds: 16));
          expect(
            (scroll.position.pixels - previous).abs(),
            lessThanOrEqualTo(12.1),
          );
          expect(
            scroll.position.maxScrollExtent,
            moreOrLessEquals(extent, epsilon: 0.1),
          );
        }
        await gesture.up();
        await tester.pumpAndSettle();
      }
      expect(_text(tester, 'dose-value-field'), dose);
      if (state == 'invalid') expect(find.text('Sprawdź dane'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  }

  testWidgets(
    'keyboard resizing and scrolling preserve focus and draft input',
    (WidgetTester tester) async {
      _mobileViewport(tester);
      addTearDown(tester.view.resetViewInsets);
      await tester.pumpWidget(const KalkulatorLekowApp());
      await tester.pumpAndSettle();
      for (final (String key, String value) in <(String, String)>[
        ('value-bodyMass', '70'),
        ('value-drugAmount', '4'),
        ('value-solutionVolume', '50'),
      ]) {
        await tester.enterText(find.byKey(Key(key)), value);
        await tester.pumpAndSettle();
      }
      final Finder input = find.byKey(const Key('dose-value-field'));
      await tester.ensureVisible(input);
      await tester.tap(input);
      await tester.enterText(input, '1,');
      await tester.pumpAndSettle();
      final FocusNode focus = tester.widget<TextField>(input).focusNode!;
      expect(focus.hasFocus, isTrue);
      tester.view.viewInsets = const FakeViewPadding(bottom: 300);
      await tester.pumpAndSettle();
      await tester.drag(
        find.byKey(const Key('mobile-calculator-scroll')),
        const Offset(0, 120),
      );
      await tester.pumpAndSettle();
      expect(focus.hasFocus, isTrue);
      expect(_text(tester, 'dose-value-field'), '1,');
      tester.view.resetViewInsets();
      await tester.pumpAndSettle();
      expect(focus.hasFocus, isTrue);
      await tester.enterText(input, '1,0');
      await tester.pumpAndSettle();
      expect(_text(tester, 'value-flowRate'), '52,5');
      focus.unfocus();
      await tester.pumpAndSettle();
      expect(_text(tester, 'dose-value-field'), '1,0');
      expect(_text(tester, 'value-flowRate'), '52,5');
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('scrolling the finite form retains fields and PWA state', (
    WidgetTester tester,
  ) async {
    _mobileViewport(tester);
    final _CountingPromptStore store = _CountingPromptStore();
    await tester.pumpWidget(KalkulatorLekowApp(pwaInstallPromptStore: store));
    await tester.pumpAndSettle();
    final Element bodyMass = tester.element(
      find.byKey(const Key('value-bodyMass')),
    );
    final ScrollableState scroll = tester.state<ScrollableState>(
      find.byType(Scrollable).first,
    );
    final double extent = scroll.position.maxScrollExtent;

    await tester.fling(
      find.byType(Scrollable).first,
      const Offset(0, -1800),
      1400,
    );
    await tester.pumpAndSettle();
    expect(
      bodyMass.mounted,
      isTrue,
      reason: 'Offscreen form fields must not be recreated during a gesture.',
    );
    expect(
      scroll.position.maxScrollExtent,
      moreOrLessEquals(extent, epsilon: 0.1),
    );
    await tester.fling(
      find.byType(Scrollable).first,
      const Offset(0, 1800),
      1400,
    );
    await tester.pumpAndSettle();
    expect(
      store.loads,
      1,
      reason:
          'Returning to the banner must not reload its asynchronous visibility preference.',
    );
    expect(
      tester.element(find.byKey(const Key('value-bodyMass'))),
      same(bodyMass),
    );
    expect(tester.takeException(), isNull);
  });
}

String _text(WidgetTester tester, String key) =>
    tester.widget<TextField>(find.byKey(Key(key))).controller!.text;

void _mobileViewport(WidgetTester tester) {
  tester.view.physicalSize = const Size(390, 844);
  tester.view.devicePixelRatio = 1;
  addTearDown(() {
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });
}

class _CountingPromptStore implements PwaInstallPromptStore {
  int loads = 0;
  @override
  Future<DateTime?> loadSnoozedUntil() async {
    loads++;
    return null;
  }

  @override
  Future<void> saveSnoozedUntil(DateTime value) async {}
  @override
  Future<void> clearSnooze() async {}
}
