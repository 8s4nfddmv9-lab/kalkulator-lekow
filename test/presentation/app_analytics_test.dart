import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/app.dart';
import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';

import '../support/recording_analytics_tracker.dart';

void main() {
  testWidgets('reports one app open without tracking calculator values', (
    WidgetTester tester,
  ) async {
    final RecordingAnalyticsTracker tracker = RecordingAnalyticsTracker();

    await tester.pumpWidget(KalkulatorLekowApp(analyticsTracker: tracker));
    await tester.pump();

    expect(tracker.count(AnalyticsEvent.appOpen), 1);
    expect(tracker.single(AnalyticsEvent.appOpen).dimensions, isEmpty);

    await tester.pump();
    expect(tracker.count(AnalyticsEvent.appOpen), 1);
  });
}
