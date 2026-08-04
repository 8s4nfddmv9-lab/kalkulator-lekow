import 'dart:convert';
import 'dart:js_interop';

import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';
import 'package:kalkulator_lekow/application/app_metadata.dart';

@JS('window.infusionCalcAnalyticsTrack')
external JSAny? _trackAnalytics(JSString eventName, JSString payloadJson);

/// Creates the Umami-backed tracker for Flutter Web.
AnalyticsTracker createAnalyticsTracker() => const UmamiAnalyticsTracker();

/// Narrow adapter from approved Dart events to the browser analytics bridge.
final class UmamiAnalyticsTracker implements AnalyticsTracker {
  /// Creates the web analytics adapter.
  const UmamiAnalyticsTracker();

  @override
  void track(
    AnalyticsEvent event, {
    Map<AnalyticsDimension, String> dimensions = const
        <AnalyticsDimension, String>{},
  }) {
    final Map<String, String> payload = <String, String>{
      'app_version': AppMetadata.version,
      for (final MapEntry<AnalyticsDimension, String> entry
          in dimensions.entries)
        entry.key.wireName: entry.value,
    };

    try {
      _trackAnalytics(event.wireName.toJS, jsonEncode(payload).toJS);
    } on Object {
      // Analytics must never interrupt calculations or application startup.
    }
  }
}
