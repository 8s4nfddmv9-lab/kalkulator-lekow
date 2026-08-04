/// Mobile platform relevant to the PWA installation experience.
enum PwaInstallPlatform {
  /// Apple mobile platform, including iPadOS desktop-style user agents.
  ios,

  /// Android browser.
  android,

  /// Desktop, native application or an unsupported environment.
  other,
}

/// Browser family needed to explain platform-specific installation steps.
enum PwaInstallBrowser {
  /// Safari on iOS or iPadOS.
  safari,

  /// Chromium-family browser.
  chromium,

  /// Any other browser or an unsupported environment.
  other,
}

/// Result of requesting the browser-native PWA installation prompt.
enum PwaInstallOutcome {
  /// The user accepted installation.
  accepted,

  /// The user dismissed the browser prompt.
  dismissed,

  /// The browser-native prompt was not available.
  unavailable,
}

/// Current browser-side PWA installation state.
final class PwaInstallSnapshot {
  /// Creates an immutable installation-state snapshot.
  const PwaInstallSnapshot({
    required this.platform,
    required this.browser,
    required this.isStandalone,
    required this.canPrompt,
  });

  /// Detected mobile platform.
  final PwaInstallPlatform platform;

  /// Detected browser family.
  final PwaInstallBrowser browser;

  /// Whether the app is currently running in installed standalone mode.
  final bool isStandalone;

  /// Whether a deferred browser-native installation prompt is available.
  final bool canPrompt;

  /// Whether a mobile browser invitation can be useful for this state.
  bool get supportsInstallInvitation =>
      platform == PwaInstallPlatform.ios ||
      platform == PwaInstallPlatform.android;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PwaInstallSnapshot &&
          other.platform == platform &&
          other.browser == browser &&
          other.isStandalone == isStandalone &&
          other.canPrompt == canPrompt;

  @override
  int get hashCode => Object.hash(
    platform,
    browser,
    isStandalone,
    canPrompt,
  );
}

/// Browser bridge used by the Flutter installation invitation.
abstract interface class PwaInstallBridge {
  /// Latest known browser-side installation state.
  PwaInstallSnapshot get snapshot;

  /// State changes caused by installability, installation or display mode.
  Stream<PwaInstallSnapshot> get changes;

  /// Requests the deferred browser-native installation dialog when available.
  Future<PwaInstallOutcome> prompt();

  /// Releases browser listeners and stream resources.
  void dispose();
}
