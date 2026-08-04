import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';
import 'package:kalkulator_lekow/presentation/common/app_footer.dart';

import '../support/recording_analytics_tracker.dart';

void main() {
  Widget subject({AnalyticsTracker? analyticsTracker}) => MaterialApp(
    home: Scaffold(
      body: const SizedBox.expand(),
      bottomNavigationBar: AppFooter(
        analyticsTracker: analyticsTracker ?? const NoopAnalyticsTracker(),
      ),
    ),
  );

  testWidgets('shows all requested footer sections', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(subject());

    expect(
      find.text('InfusionCalc · Technical infusion calculator'),
      findsOneWidget,
    );
    expect(find.text('© 2026 M W · MIT License'), findsOneWidget);
    expect(find.text('Changelog'), findsOneWidget);
    expect(find.text('Privacy'), findsOneWidget);
    expect(find.text('GitHub'), findsOneWidget);
    expect(find.text('Contact'), findsOneWidget);
  });

  testWidgets('privacy dialog explains local processing, Umami and offline cache', (
    WidgetTester tester,
  ) async {
    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();
    await tester.pumpWidget(subject(analyticsTracker: tracker));

    await tester.tap(find.text('Privacy'));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('privacy-dialog')), findsOneWidget);
    expect(
      find.textContaining('Obliczenia wykonują się lokalnie na urządzeniu'),
      findsOneWidget,
    );
    expect(find.textContaining('Umami Cloud'), findsOneWidget);
    expect(
      find.textContaining('Nie tworzymy własnego identyfikatora użytkownika'),
      findsOneWidget,
    );
    expect(
      find.textContaining('Pełny tryb offline zapisuje lokalnie publiczny kod'),
      findsOneWidget,
    );
    expect(
      find.textContaining('Cache offline nie zawiera wartości formularza'),
      findsOneWidget,
    );
    expect(tracker.count(AnalyticsEvent.privacyOpened), 1);
    expect(
      find.textContaining('Nie wpisuj danych identyfikujących pacjenta'),
      findsOneWidget,
    );
  });

  testWidgets('native license fallback exposes the MIT license address', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(subject());

    await tester.tap(find.text('© 2026 M W · MIT License'));
    await tester.pumpAndSettle();

    expect(
      find.text(
        'https://github.com/8s4nfddmv9-lab/kalkulator-lekow/blob/main/LICENSE',
      ),
      findsOneWidget,
    );
    expect(find.text('Kopiuj adres'), findsOneWidget);
  });

  testWidgets('GitHub and contact links report fixed events', (
    WidgetTester tester,
  ) async {
    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();
    await tester.pumpWidget(subject(analyticsTracker: tracker));

    await tester.tap(find.text('GitHub'));
    await tester.pumpAndSettle();
    expect(tracker.count(AnalyticsEvent.githubClicked), 1);
    await tester.tap(find.text('Zamknij'));
    await tester.pumpAndSettle();

    final Finder contact = find.text('Contact');
    await tester.ensureVisible(contact);
    await tester.pumpAndSettle();
    await tester.tap(contact);
    await tester.pumpAndSettle();

    expect(
      find.text('https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18'),
      findsOneWidget,
    );
    expect(find.text('Kopiuj adres'), findsOneWidget);
    expect(tracker.count(AnalyticsEvent.contactClicked), 1);
  });
}
