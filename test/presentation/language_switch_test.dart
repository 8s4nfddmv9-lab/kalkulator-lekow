import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/app.dart';
import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';
import 'package:kalkulator_lekow/application/preferences/app_language.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/presentation/localization/app_localizations.dart';

import '../support/recording_analytics_tracker.dart';

void main() {
  testWidgets('starts in English before the first application frame', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const KalkulatorLekowApp(initialLanguage: AppLanguage.english),
    );

    expect(find.text('Patient'), findsOneWidget);
    expect(find.text('Patient body weight'), findsOneWidget);
    expect(find.text('Drug amount'), findsOneWidget);
    expect(find.text('Pacjent'), findsNothing);
    expect(
      Localizations.localeOf(tester.element(find.byType(Scaffold))),
      const Locale('en'),
    );
    expect(
      MaterialLocalizations.of(
        tester.element(find.byType(Scaffold)),
      ).closeButtonLabel,
      'Close',
    );
  });

  testWidgets(
    'language control is aligned, accessible and preserves calculator state',
    (WidgetTester tester) async {
      final SemanticsHandle semantics = tester.ensureSemantics();
      final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();
      await tester.pumpWidget(KalkulatorLekowApp(analyticsTracker: tracker));

      final Finder row = find.byKey(const Key('top-utility-row'));
      final Finder warning = find.byKey(const Key('technical-warning-button'));
      final Finder language = find.byKey(const Key('language-switch-button'));
      final Rect rowRect = tester.getRect(row);
      final Rect warningRect = tester.getRect(warning);
      final Rect languageRect = tester.getRect(language);

      expect(warningRect.center.dy, languageRect.center.dy);
      expect(languageRect.right, rowRect.right);
      expect(warningRect.width, greaterThanOrEqualTo(48));
      expect(warningRect.height, greaterThanOrEqualTo(48));
      expect(languageRect.width, greaterThanOrEqualTo(48));
      expect(languageRect.height, greaterThanOrEqualTo(48));
      expect(
        find.bySemanticsLabel('Przełącz na język angielski'),
        findsOneWidget,
      );

      await _enter(tester, 'value-drugAmount', '4');
      await _enter(tester, 'value-solutionVolume', '50');
      expect(await _fieldText(tester, 'value-concentration'), '80');

      await _reveal(tester, language);
      await tester.tap(language);
      await tester.pumpAndSettle();

      expect(find.text('Patient'), findsOneWidget);
      expect(find.text('Drug amount'), findsOneWidget);
      expect(find.text('Pacjent'), findsNothing);
      expect(await _fieldText(tester, 'value-drugAmount'), '4');
      expect(await _fieldText(tester, 'value-solutionVolume'), '50');
      expect(await _fieldText(tester, 'value-concentration'), '80');
      final Finder amountUnit = find.byKey(
        const ValueKey<String>('unit-drugAmount-mg'),
      );
      await _reveal(tester, amountUnit);
      expect(amountUnit, findsOneWidget);
      await _reveal(tester, language);
      expect(find.bySemanticsLabel('Switch to Polish'), findsOneWidget);
      expect(tracker.count(AnalyticsEvent.appOpen), 1);

      await _reveal(tester, language);
      await tester.tap(language);
      await tester.pumpAndSettle();
      expect(find.text('Pacjent'), findsOneWidget);
      expect(await _fieldText(tester, 'value-concentration'), '80');
      expect(tracker.count(AnalyticsEvent.appOpen), 1);
      semantics.dispose();
    },
  );

  testWidgets('active errors, warning and calculation details are translated', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    await _enter(tester, 'value-bodyMass', '0');
    await tester.tap(find.byKey(const Key('value-drugAmount')));
    await tester.pumpAndSettle();
    expect(find.text('Wartość musi być większa od zera.'), findsOneWidget);

    final Finder language = find.byKey(const Key('language-switch-button'));
    await _reveal(tester, language);
    await tester.tap(language);
    await tester.pumpAndSettle();
    expect(find.text('The value must be greater than zero.'), findsOneWidget);
    expect(find.text('Wartość musi być większa od zera.'), findsNothing);

    await tester.tap(find.byKey(const Key('technical-warning-button')));
    await tester.pumpAndSettle();
    expect(find.text('Important information'), findsOneWidget);
    expect(
      find.text(
        'Technical calculator — not intended for clinical decision-making.',
      ),
      findsOneWidget,
    );
    expect(find.text('I understand'), findsOneWidget);
    await tester.tap(
      find.byKey(const Key('technical-warning-acknowledge-button')),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byTooltip('Clear all fields'));
    await tester.pumpAndSettle();
    await _enter(tester, 'value-drugAmount', '4');
    await _enter(tester, 'value-solutionVolume', '50');
    final Finder details = find.byKey(const Key('calculation-details'));
    await _reveal(tester, details);
    await tester.tap(details);
    await tester.pumpAndSettle();
    expect(find.text('Calculation details'), findsOneWidget);
    expect(find.text('Result: 80 µg/ml'), findsOneWidget);
    expect(find.text('Copy result'), findsOneWidget);
  });

  testWidgets('rapid EN then PL writes persist the final selection in order', (
    WidgetTester tester,
  ) async {
    final _ControlledLanguageStore store = _ControlledLanguageStore();
    await tester.pumpWidget(KalkulatorLekowApp(languageStore: store));

    final Finder switchButton = find.byKey(const Key('language-switch-button'));
    await tester.tap(switchButton);
    await tester.pump();
    expect(find.text('Patient'), findsOneWidget);
    expect(store.requested, <AppLanguage>[AppLanguage.english]);

    await tester.tap(switchButton);
    await tester.pump();
    expect(find.text('Pacjent'), findsOneWidget);
    expect(store.requested, <AppLanguage>[AppLanguage.english]);

    store.completeNext();
    await tester.pump();
    expect(store.requested, <AppLanguage>[
      AppLanguage.english,
      AppLanguage.polish,
    ]);
    store.completeNext();
    await tester.pump();
    expect(store.completed, <AppLanguage>[
      AppLanguage.english,
      AppLanguage.polish,
    ]);
  });

  testWidgets('a language save failure does not roll back the interface', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      KalkulatorLekowApp(languageStore: _FailingLanguageStore()),
    );

    await tester.tap(find.byKey(const Key('language-switch-button')));
    await tester.pumpAndSettle();

    expect(find.text('Patient'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('English interface fits a 320 px screen with enlarged text', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(320, 568);
    tester.view.devicePixelRatio = 1;
    tester.platformDispatcher.textScaleFactorTestValue = 1.5;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    addTearDown(tester.platformDispatcher.clearTextScaleFactorTestValue);

    await tester.pumpWidget(
      const KalkulatorLekowApp(initialLanguage: AppLanguage.english),
    );
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);

    final Rect warning = tester.getRect(
      find.byKey(const Key('technical-warning-button')),
    );
    final Rect language = tester.getRect(
      find.byKey(const Key('language-switch-button')),
    );
    expect(warning.center.dy, language.center.dy);
    expect(language.width, greaterThanOrEqualTo(48));

    await _reveal(tester, find.byKey(const Key('app-footer')));
    expect(find.byKey(const Key('app-footer')), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  test('every domain error has distinct non-empty copy in both languages', () {
    const AppLocalizations polish = AppLocalizations(AppLanguage.polish);
    const AppLocalizations english = AppLocalizations(AppLanguage.english);

    for (final DomainErrorCode code in DomainErrorCode.values) {
      expect(polish.domainError(code), isNotEmpty, reason: code.name);
      expect(english.domainError(code), isNotEmpty, reason: code.name);
      expect(
        english.domainError(code),
        isNot(polish.domainError(code)),
        reason: code.name,
      );
    }
  });
}

final class _ControlledLanguageStore implements AppLanguageStore {
  final List<AppLanguage> requested = <AppLanguage>[];
  final List<AppLanguage> completed = <AppLanguage>[];
  final List<({AppLanguage language, Completer<void> completer})> _pending =
      <({AppLanguage language, Completer<void> completer})>[];

  @override
  Future<AppLanguage> load() async => AppLanguage.polish;

  @override
  Future<void> save(AppLanguage language) {
    requested.add(language);
    final Completer<void> completer = Completer<void>();
    _pending.add((language: language, completer: completer));
    return completer.future.whenComplete(() => completed.add(language));
  }

  void completeNext() {
    final ({AppLanguage language, Completer<void> completer}) pending = _pending
        .firstWhere((entry) => !entry.completer.isCompleted);
    pending.completer.complete();
  }
}

final class _FailingLanguageStore implements AppLanguageStore {
  @override
  Future<AppLanguage> load() async => AppLanguage.polish;

  @override
  Future<void> save(AppLanguage language) =>
      Future<void>.error(StateError('storage unavailable'));
}

Future<void> _enter(WidgetTester tester, String key, String value) async {
  final Finder field = find.byKey(Key(key));
  await _reveal(tester, field);
  await tester.enterText(field, value);
  await tester.pumpAndSettle();
}

Future<String> _fieldText(WidgetTester tester, String key) async {
  final Finder field = find.byKey(Key(key));
  await _reveal(tester, field);
  return tester.widget<TextField>(field).controller!.text;
}

Future<void> _reveal(WidgetTester tester, Finder target) async {
  if (target.evaluate().isNotEmpty) {
    await tester.ensureVisible(target.first);
    await tester.pumpAndSettle();
    return;
  }

  final Finder listView = find.byType(ListView);
  for (int attempt = 0; attempt < 24; attempt++) {
    await tester.drag(listView, const Offset(0, -280));
    await tester.pumpAndSettle();
    if (target.evaluate().isNotEmpty) {
      await tester.ensureVisible(target.first);
      await tester.pumpAndSettle();
      return;
    }
  }
  for (int attempt = 0; attempt < 48; attempt++) {
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
