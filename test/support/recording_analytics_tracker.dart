import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';

/// One analytics call captured by widget tests.
final class RecordedAnalyticsCall {
  const RecordedAnalyticsCall(this.event, this.dimensions);

  final AnalyticsEvent event;
  final Map<AnalyticsDimension, String> dimensions;
}

/// In-memory analytics implementation for deterministic tests.
final class RecordingAnalyticsTracker implements AnalyticsTracker {
  final List<RecordedAnalyticsCall> calls = <RecordedAnalyticsCall>[];

  @override
  void track(
    AnalyticsEvent event, {
    Map<AnalyticsDimension, String> dimensions =
        const <AnalyticsDimension, String>{},
  }) {
    calls.add(
      RecordedAnalyticsCall(
        event,
        Map<AnalyticsDimension, String>.unmodifiable(dimensions),
      ),
    );
  }

  int count(AnalyticsEvent event) =>
      calls.where((RecordedAnalyticsCall call) => call.event == event).length;

  RecordedAnalyticsCall single(AnalyticsEvent event) =>
      calls.singleWhere((RecordedAnalyticsCall call) => call.event == event);
}
