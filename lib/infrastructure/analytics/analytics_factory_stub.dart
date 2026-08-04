import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';

/// Native and unsupported platforms deliberately disable web analytics.
AnalyticsTracker createAnalyticsTracker() => const NoopAnalyticsTracker();
