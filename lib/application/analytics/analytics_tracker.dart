/// Fixed, privacy-reviewed analytics events emitted by InfusionCalc.
enum AnalyticsEvent {
  /// One application bootstrap in a browser or installed PWA.
  appOpen('app_open'),

  /// The installation invitation became visible.
  installPromptOpened('install_prompt_opened'),

  /// The user selected the installation action.
  installButtonClicked('install_button_clicked'),

  /// The browser confirmed installation during the current session.
  pwaInstalled('pwa_installed'),

  /// The technical-purpose warning was opened.
  warningOpened('warning_opened'),

  /// The privacy information was opened.
  privacyOpened('privacy_opened'),

  /// The public repository link was selected.
  githubClicked('github_clicked'),

  /// The feedback/contact link was selected.
  contactClicked('contact_clicked');

  const AnalyticsEvent(this.wireName);

  /// Stable event name sent to the analytics provider.
  final String wireName;
}

/// Fixed dimensions allowed in custom analytics payloads.
enum AnalyticsDimension {
  /// Installation path selected by the browser and platform.
  installMethod('install_method');

  const AnalyticsDimension(this.wireName);

  /// Stable property name sent to the analytics provider.
  final String wireName;
}

/// Minimal analytics contract isolated from calculator state and values.
abstract interface class AnalyticsTracker {
  /// Records one approved event with approved, non-clinical dimensions.
  void track(
    AnalyticsEvent event, {
    Map<AnalyticsDimension, String> dimensions =
        const <AnalyticsDimension, String>{},
  });
}

/// No-op implementation used by tests, previews and native builds.
final class NoopAnalyticsTracker implements AnalyticsTracker {
  /// Creates a tracker that deliberately records nothing.
  const NoopAnalyticsTracker();

  @override
  void track(
    AnalyticsEvent event, {
    Map<AnalyticsDimension, String> dimensions =
        const <AnalyticsDimension, String>{},
  }) {}
}
