import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';
import 'package:kalkulator_lekow/application/app_metadata.dart';

void main() {
  test('analytics event names are fixed and privacy-reviewed', () {
    expect(
      AnalyticsEvent.values.map((AnalyticsEvent event) => event.wireName),
      <String>[
        'app_open',
        'install_prompt_opened',
        'install_button_clicked',
        'pwa_installed',
        'warning_opened',
        'privacy_opened',
        'github_clicked',
        'contact_clicked',
      ],
    );
  });

  test('custom payloads expose only the installation method dimension', () {
    expect(
      AnalyticsDimension.values.map(
        (AnalyticsDimension dimension) => dimension.wireName,
      ),
      <String>['install_method'],
    );
  });

  test('analytics version metadata matches pubspec', () async {
    final String pubspec = await File('pubspec.yaml').readAsString();
    final RegExpMatch? match = RegExp(
      r'^version:\s*([^\s]+)\s*$',
      multiLine: true,
    ).firstMatch(pubspec);

    expect(match, isNotNull);
    expect(AppMetadata.version, match!.group(1));
  });
}
