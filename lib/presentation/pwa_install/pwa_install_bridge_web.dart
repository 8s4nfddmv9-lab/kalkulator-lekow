import 'dart:async';
import 'dart:convert';
import 'dart:js_interop';

import 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_bridge_types.dart';

@JS('infusionCalcPwaGetState')
external JSString _getState();

@JS('infusionCalcPwaPrompt')
external JSPromise<JSString> _promptInstall();

@JS('infusionCalcPwaSubscribe')
external JSString _subscribe(JSFunction callback);

@JS('infusionCalcPwaUnsubscribe')
external void _unsubscribe(JSString token);

/// Creates the browser-backed PWA installation bridge.
PwaInstallBridge createPwaInstallBridge() => _WebPwaInstallBridge();

final class _WebPwaInstallBridge implements PwaInstallBridge {
  _WebPwaInstallBridge() : _snapshot = _decodeSnapshot(_getState().toDart) {
    _callback = ((JSString rawState) {
      final PwaInstallSnapshot next = _decodeSnapshot(rawState.toDart);
      _snapshot = next;
      if (!_changes.isClosed) {
        _changes.add(next);
      }
    }).toJS;
    _subscriptionToken = _subscribe(_callback);
  }

  final StreamController<PwaInstallSnapshot> _changes =
      StreamController<PwaInstallSnapshot>.broadcast(sync: true);
  late final JSFunction _callback;
  late final JSString _subscriptionToken;
  PwaInstallSnapshot _snapshot;
  bool _disposed = false;

  @override
  PwaInstallSnapshot get snapshot => _snapshot;

  @override
  Stream<PwaInstallSnapshot> get changes => _changes.stream;

  @override
  Future<PwaInstallOutcome> prompt() async {
    if (_disposed) {
      return PwaInstallOutcome.unavailable;
    }
    try {
      final JSString rawOutcome = await _promptInstall().toDart;
      return switch (rawOutcome.toDart) {
        'accepted' => PwaInstallOutcome.accepted,
        'dismissed' => PwaInstallOutcome.dismissed,
        _ => PwaInstallOutcome.unavailable,
      };
    } on Object {
      return PwaInstallOutcome.unavailable;
    }
  }

  @override
  void dispose() {
    if (_disposed) {
      return;
    }
    _disposed = true;
    _unsubscribe(_subscriptionToken);
    unawaited(_changes.close());
  }
}

PwaInstallSnapshot _decodeSnapshot(String source) {
  try {
    final Object? decoded = jsonDecode(source);
    if (decoded is! Map<String, dynamic>) {
      return _fallbackSnapshot;
    }
    return PwaInstallSnapshot(
      platform: switch (decoded['platform']) {
        'ios' => PwaInstallPlatform.ios,
        'android' => PwaInstallPlatform.android,
        _ => PwaInstallPlatform.other,
      },
      browser: switch (decoded['browser']) {
        'safari' => PwaInstallBrowser.safari,
        'chromium' => PwaInstallBrowser.chromium,
        _ => PwaInstallBrowser.other,
      },
      isStandalone: decoded['standalone'] == true,
      canPrompt: decoded['canPrompt'] == true,
    );
  } on Object {
    return _fallbackSnapshot;
  }
}

const PwaInstallSnapshot _fallbackSnapshot = PwaInstallSnapshot(
  platform: PwaInstallPlatform.other,
  browser: PwaInstallBrowser.other,
  isStandalone: false,
  canPrompt: false,
);
