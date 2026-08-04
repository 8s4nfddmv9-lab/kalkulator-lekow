import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';
import 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_banner.dart';
import 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_bridge.dart';

void main() {
  final DateTime now = DateTime.utc(2026, 8, 4, 8, 0);

  Widget subject({
    required PwaInstallBridge bridge,
    required PwaInstallPromptStore store,
  }) => MaterialApp(
    home: Scaffold(
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: <Widget>[
          PwaInstallBanner(
            bridge: bridge,
            promptStore: store,
            now: () => now,
          ),
        ],
      ),
    ),
  );

  testWidgets('shows iOS Safari instructions with a share icon', (
    WidgetTester tester,
  ) async {
    final _FakeBridge bridge = _FakeBridge(
      const PwaInstallSnapshot(
        platform: PwaInstallPlatform.ios,
        browser: PwaInstallBrowser.safari,
        isStandalone: false,
        canPrompt: false,
      ),
    );
    addTearDown(bridge.close);

    await tester.pumpWidget(subject(bridge: bridge, store: _FakeStore()));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('pwa-install-banner')), findsOneWidget);
    await tester.tap(find.byKey(const Key('pwa-install-button')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('ios-pwa-install-dialog')), findsOneWidget);
    expect(find.byKey(const Key('ios-share-icon')), findsOneWidget);
    expect(find.textContaining('przycisku Udostępnij'), findsOneWidget);
    expect(find.textContaining('Dodaj do ekranu głównego'), findsWidgets);
    expect(find.textContaining('Otwórz jako aplikację'), findsOneWidget);
  });

  testWidgets('tells iOS users in another browser to open Safari', (
    WidgetTester tester,
  ) async {
    final _FakeBridge bridge = _FakeBridge(
      const PwaInstallSnapshot(
        platform: PwaInstallPlatform.ios,
        browser: PwaInstallBrowser.chromium,
        isStandalone: false,
        canPrompt: false,
      ),
    );
    addTearDown(bridge.close);

    await tester.pumpWidget(subject(bridge: bridge, store: _FakeStore()));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('pwa-install-button')));
    await tester.pumpAndSettle();

    expect(
      find.textContaining('Otwórz adres infusioncalc.eu w Safari'),
      findsOneWidget,
    );
  });

  testWidgets('uses the native Android prompt and hides after acceptance', (
    WidgetTester tester,
  ) async {
    final _FakeBridge bridge = _FakeBridge(
      const PwaInstallSnapshot(
        platform: PwaInstallPlatform.android,
        browser: PwaInstallBrowser.chromium,
        isStandalone: false,
        canPrompt: true,
      ),
      promptOutcome: PwaInstallOutcome.accepted,
    );
    addTearDown(bridge.close);
    final _FakeStore store = _FakeStore();

    await tester.pumpWidget(subject(bridge: bridge, store: store));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('pwa-install-button')));
    await tester.pumpAndSettle();

    expect(bridge.promptCalls, 1);
    expect(find.byKey(const Key('pwa-install-banner')), findsNothing);
    expect(store.clearCalls, 1);
  });

  testWidgets('shows manual Android instructions when prompt is unavailable', (
    WidgetTester tester,
  ) async {
    final _FakeBridge bridge = _FakeBridge(
      const PwaInstallSnapshot(
        platform: PwaInstallPlatform.android,
        browser: PwaInstallBrowser.other,
        isStandalone: false,
        canPrompt: false,
      ),
    );
    addTearDown(bridge.close);

    await tester.pumpWidget(subject(bridge: bridge, store: _FakeStore()));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('pwa-install-button')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('android-pwa-install-dialog')), findsOneWidget);
    expect(find.byKey(const Key('android-menu-icon')), findsOneWidget);
    expect(find.textContaining('Zainstaluj aplikację'), findsWidgets);
  });

  testWidgets('hides the invitation in standalone display mode', (
    WidgetTester tester,
  ) async {
    final _FakeBridge bridge = _FakeBridge(
      const PwaInstallSnapshot(
        platform: PwaInstallPlatform.ios,
        browser: PwaInstallBrowser.safari,
        isStandalone: true,
        canPrompt: false,
      ),
    );
    addTearDown(bridge.close);

    await tester.pumpWidget(subject(bridge: bridge, store: _FakeStore()));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('pwa-install-banner')), findsNothing);
  });

  testWidgets('not now postpones the invitation for thirty days', (
    WidgetTester tester,
  ) async {
    final _FakeBridge bridge = _FakeBridge(
      const PwaInstallSnapshot(
        platform: PwaInstallPlatform.android,
        browser: PwaInstallBrowser.chromium,
        isStandalone: false,
        canPrompt: true,
      ),
    );
    addTearDown(bridge.close);
    final _FakeStore store = _FakeStore();

    await tester.pumpWidget(subject(bridge: bridge, store: store));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('pwa-install-dismiss-button')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('pwa-install-banner')), findsNothing);
    expect(store.savedUntil, now.add(const Duration(days: 30)));
  });

  testWidgets('respects an existing local postponement', (
    WidgetTester tester,
  ) async {
    final _FakeBridge bridge = _FakeBridge(
      const PwaInstallSnapshot(
        platform: PwaInstallPlatform.ios,
        browser: PwaInstallBrowser.safari,
        isStandalone: false,
        canPrompt: false,
      ),
    );
    addTearDown(bridge.close);
    final _FakeStore store = _FakeStore(
      snoozedUntil: now.add(const Duration(days: 7)),
    );

    await tester.pumpWidget(subject(bridge: bridge, store: store));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('pwa-install-banner')), findsNothing);
  });

  testWidgets('hides when browser state changes to standalone', (
    WidgetTester tester,
  ) async {
    final _FakeBridge bridge = _FakeBridge(
      const PwaInstallSnapshot(
        platform: PwaInstallPlatform.android,
        browser: PwaInstallBrowser.chromium,
        isStandalone: false,
        canPrompt: true,
      ),
    );
    addTearDown(bridge.close);

    await tester.pumpWidget(subject(bridge: bridge, store: _FakeStore()));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('pwa-install-banner')), findsOneWidget);

    bridge.emit(
      const PwaInstallSnapshot(
        platform: PwaInstallPlatform.android,
        browser: PwaInstallBrowser.chromium,
        isStandalone: true,
        canPrompt: false,
      ),
    );
    await tester.pump();

    expect(find.byKey(const Key('pwa-install-banner')), findsNothing);
  });
}

final class _FakeBridge implements PwaInstallBridge {
  _FakeBridge(this._snapshot, {
    this.promptOutcome = PwaInstallOutcome.unavailable,
  });

  final StreamController<PwaInstallSnapshot> _controller =
      StreamController<PwaInstallSnapshot>.broadcast(sync: true);
  PwaInstallSnapshot _snapshot;
  final PwaInstallOutcome promptOutcome;
  int promptCalls = 0;

  @override
  PwaInstallSnapshot get snapshot => _snapshot;

  @override
  Stream<PwaInstallSnapshot> get changes => _controller.stream;

  void emit(PwaInstallSnapshot value) {
    _snapshot = value;
    _controller.add(value);
  }

  @override
  Future<PwaInstallOutcome> prompt() async {
    promptCalls += 1;
    return promptOutcome;
  }

  Future<void> close() => _controller.close();

  @override
  void dispose() {}
}

final class _FakeStore implements PwaInstallPromptStore {
  _FakeStore({this.snoozedUntil});

  DateTime? snoozedUntil;
  DateTime? savedUntil;
  int clearCalls = 0;

  @override
  Future<DateTime?> loadSnoozedUntil() async => snoozedUntil;

  @override
  Future<void> saveSnoozedUntil(DateTime value) async {
    savedUntil = value;
    snoozedUntil = value;
  }

  @override
  Future<void> clearSnooze() async {
    clearCalls += 1;
    snoozedUntil = null;
  }
}
