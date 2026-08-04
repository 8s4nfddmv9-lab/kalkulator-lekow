import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';
import 'package:kalkulator_lekow/infrastructure/analytics/analytics_factory_stub.dart'
    if (dart.library.js_interop)
        'package:kalkulator_lekow/infrastructure/analytics/analytics_factory_web.dart'
    as implementation;

/// Creates the platform-appropriate analytics tracker.
AnalyticsTracker createAnalyticsTracker() =>
    implementation.createAnalyticsTracker();
