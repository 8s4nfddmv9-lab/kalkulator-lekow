import 'dart:async';

import 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_bridge_types.dart';

/// Creates a bridge that suppresses web installation UI on native platforms.
PwaInstallBridge createPwaInstallBridge() =>
    const _UnsupportedPwaInstallBridge();

final class _UnsupportedPwaInstallBridge implements PwaInstallBridge {
  const _UnsupportedPwaInstallBridge();

  static const PwaInstallSnapshot _snapshot = PwaInstallSnapshot(
    platform: PwaInstallPlatform.other,
    browser: PwaInstallBrowser.other,
    isStandalone: false,
    canPrompt: false,
  );

  @override
  PwaInstallSnapshot get snapshot => _snapshot;

  @override
  Stream<PwaInstallSnapshot> get changes =>
      const Stream<PwaInstallSnapshot>.empty();

  @override
  Future<PwaInstallOutcome> prompt() async => PwaInstallOutcome.unavailable;

  @override
  void dispose() {}
}
