import 'dart:async';

import 'package:flutter/material.dart';
import 'package:kalkulator_lekow/application/pwa_install/pwa_install_prompt_store.dart';
import 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_bridge.dart';

/// Context-aware invitation to install InfusionCalc as a mobile PWA.
class PwaInstallBanner extends StatefulWidget {
  /// Creates the installation invitation.
  const PwaInstallBanner({
    required this.promptStore,
    this.bridge,
    this.now,
    super.key,
  });

  /// Local store for the optional 30-day postponement.
  final PwaInstallPromptStore promptStore;

  /// Optional injected bridge used by tests.
  final PwaInstallBridge? bridge;

  /// Optional clock used by deterministic tests.
  final DateTime Function()? now;

  @override
  State<PwaInstallBanner> createState() => _PwaInstallBannerState();
}

class _PwaInstallBannerState extends State<PwaInstallBanner> {
  static const Duration _snoozeDuration = Duration(days: 30);

  late final PwaInstallBridge _bridge;
  late final bool _ownsBridge;
  late PwaInstallSnapshot _snapshot;
  StreamSubscription<PwaInstallSnapshot>? _subscription;
  DateTime? _snoozedUntil;
  bool _preferencesLoaded = false;
  bool _hiddenForSession = false;
  bool _busy = false;

  DateTime get _now => (widget.now?.call() ?? DateTime.now()).toUtc();

  @override
  void initState() {
    super.initState();
    _ownsBridge = widget.bridge == null;
    _bridge = widget.bridge ?? createPwaInstallBridge();
    _snapshot = _bridge.snapshot;
    _subscription = _bridge.changes.listen(_handleSnapshot);
    unawaited(_loadSnooze());
  }

  @override
  void dispose() {
    unawaited(_subscription?.cancel());
    if (_ownsBridge) {
      _bridge.dispose();
    }
    super.dispose();
  }

  void _handleSnapshot(PwaInstallSnapshot snapshot) {
    if (!mounted) {
      return;
    }
    setState(() {
      _snapshot = snapshot;
      if (snapshot.isStandalone) {
        _hiddenForSession = true;
      }
    });
  }

  Future<void> _loadSnooze() async {
    DateTime? stored;
    try {
      stored = await widget.promptStore.loadSnoozedUntil();
    } on Object {
      stored = null;
    }
    if (!mounted) {
      return;
    }

    final DateTime? normalized = stored?.toUtc();
    final bool expired = normalized != null && !normalized.isAfter(_now);
    setState(() {
      _snoozedUntil = expired ? null : normalized;
      _preferencesLoaded = true;
    });
    if (expired) {
      unawaited(_clearStoredSnooze());
    }
  }

  bool get _shouldShow {
    if (!_preferencesLoaded ||
        _hiddenForSession ||
        _snapshot.isStandalone ||
        !_snapshot.supportsInstallInvitation) {
      return false;
    }
    final DateTime? snoozedUntil = _snoozedUntil;
    return snoozedUntil == null || !snoozedUntil.isAfter(_now);
  }

  @override
  Widget build(BuildContext context) {
    if (!_shouldShow) {
      return const SizedBox.shrink();
    }

    final ThemeData theme = Theme.of(context);
    final ColorScheme colors = theme.colorScheme;
    final bool isIos = _snapshot.platform == PwaInstallPlatform.ios;
    final String description = switch (_snapshot.platform) {
      PwaInstallPlatform.ios when
          _snapshot.browser != PwaInstallBrowser.safari =>
        'Na iPhonie i iPadzie instalacja odbywa się przez Safari.',
      PwaInstallPlatform.ios =>
        'Uruchamiaj InfusionCalc jak osobną aplikację z ekranu głównego.',
      PwaInstallPlatform.android when _snapshot.canPrompt =>
        'Zainstaluj aplikację przez systemowe okno przeglądarki.',
      PwaInstallPlatform.android =>
        'Pokażemy, gdzie znaleźć instalację w menu przeglądarki.',
      PwaInstallPlatform.other => '',
    };

    return Semantics(
      container: true,
      label: 'Instalacja InfusionCalc na ekranie głównym',
      child: Card(
        key: const Key('pwa-install-banner'),
        margin: const EdgeInsets.only(bottom: 12),
        color: colors.primaryContainer.withValues(alpha: 0.72),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Icon(
                    isIos
                        ? Icons.add_to_home_screen_rounded
                        : Icons.install_mobile_rounded,
                    color: colors.onPrimaryContainer,
                    size: 30,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        Text(
                          'Dodaj InfusionCalc do ekranu głównego',
                          style: theme.textTheme.titleMedium?.copyWith(
                            color: colors.onPrimaryContainer,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          description,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: colors.onPrimaryContainer,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                alignment: WrapAlignment.end,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: <Widget>[
                  TextButton(
                    key: const Key('pwa-install-dismiss-button'),
                    onPressed: _busy ? null : _snooze,
                    child: const Text('Nie teraz'),
                  ),
                  FilledButton.icon(
                    key: const Key('pwa-install-button'),
                    onPressed: _busy ? null : _startInstallation,
                    icon: _busy
                        ? const SizedBox.square(
                            dimension: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.add_to_home_screen_rounded),
                    label: const Text('Dodaj do ekranu głównego'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _startInstallation() async {
    switch (_snapshot.platform) {
      case PwaInstallPlatform.ios:
        await _showIosInstructions();
      case PwaInstallPlatform.android:
        await _startAndroidInstallation();
      case PwaInstallPlatform.other:
        return;
    }
  }

  Future<void> _startAndroidInstallation() async {
    if (!_snapshot.canPrompt) {
      await _showAndroidInstructions();
      return;
    }

    setState(() => _busy = true);
    final PwaInstallOutcome outcome = await _bridge.prompt();
    if (!mounted) {
      return;
    }
    setState(() => _busy = false);

    switch (outcome) {
      case PwaInstallOutcome.accepted:
        setState(() {
          _hiddenForSession = true;
          _snoozedUntil = null;
        });
        unawaited(_clearStoredSnooze());
      case PwaInstallOutcome.dismissed:
        await _snooze();
      case PwaInstallOutcome.unavailable:
        await _showAndroidInstructions();
    }
  }

  Future<void> _snooze() async {
    final DateTime until = _now.add(_snoozeDuration);
    if (mounted) {
      setState(() {
        _snoozedUntil = until;
        _hiddenForSession = true;
      });
    }
    try {
      await widget.promptStore.saveSnoozedUntil(until);
    } on Object {
      // The invitation still stays hidden for the current browser session.
    }
  }

  Future<void> _clearStoredSnooze() async {
    try {
      await widget.promptStore.clearSnooze();
    } on Object {
      // Installation remains usable even if local preference cleanup fails.
    }
  }

  Future<void> _showIosInstructions() => showDialog<void>(
    context: context,
    builder: (BuildContext dialogContext) => AlertDialog(
      key: const Key('ios-pwa-install-dialog'),
      title: const Text('Dodaj InfusionCalc do ekranu głównego'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            Center(
              child: Container(
                width: 72,
                height: 72,
                decoration: BoxDecoration(
                  color: Theme.of(dialogContext).colorScheme.primaryContainer,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.ios_share_rounded,
                  key: const Key('ios-share-icon'),
                  size: 42,
                  color: Theme.of(
                    dialogContext,
                  ).colorScheme.onPrimaryContainer,
                  semanticLabel: 'Ikona Udostępnij w Safari',
                ),
              ),
            ),
            const SizedBox(height: 16),
            if (_snapshot.browser != PwaInstallBrowser.safari) ...<Widget>[
              _InstructionNotice(
                icon: Icons.info_outline_rounded,
                text:
                    'Otwórz adres infusioncalc.eu w Safari. Instalacja z '
                    'ekranu głównego na iPhonie i iPadzie jest dostępna '
                    'z menu Safari.',
              ),
              const SizedBox(height: 12),
            ],
            const _InstructionStep(
              number: 1,
              text:
                  'W Safari dotknij przycisku Udostępnij — ikony strzałki '
                  'wychodzącej z kwadratu.',
            ),
            const _InstructionStep(
              number: 2,
              text:
                  'Przewiń listę czynności i wybierz „Dodaj do ekranu '
                  'głównego”.',
            ),
            const _InstructionStep(
              number: 3,
              text:
                  'Włącz „Otwórz jako aplikację”, jeśli ta opcja jest '
                  'widoczna, a następnie dotknij „Dodaj”.',
            ),
          ],
        ),
      ),
      actions: <Widget>[
        FilledButton(
          onPressed: () => Navigator.of(dialogContext).pop(),
          child: const Text('Rozumiem'),
        ),
      ],
    ),
  );

  Future<void> _showAndroidInstructions() => showDialog<void>(
    context: context,
    builder: (BuildContext dialogContext) => AlertDialog(
      key: const Key('android-pwa-install-dialog'),
      title: const Text('Zainstaluj InfusionCalc'),
      content: const SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            Center(
              child: Icon(
                Icons.more_vert_rounded,
                key: Key('android-menu-icon'),
                size: 48,
                semanticLabel: 'Menu przeglądarki',
              ),
            ),
            SizedBox(height: 16),
            _InstructionStep(
              number: 1,
              text:
                  'Otwórz menu przeglądarki oznaczone trzema kropkami.',
            ),
            _InstructionStep(
              number: 2,
              text:
                  'Wybierz „Zainstaluj aplikację” albo „Dodaj do ekranu '
                  'głównego”.',
            ),
            _InstructionStep(
              number: 3,
              text: 'Potwierdź instalację w oknie systemowym.',
            ),
          ],
        ),
      ),
      actions: <Widget>[
        FilledButton(
          onPressed: () => Navigator.of(dialogContext).pop(),
          child: const Text('Rozumiem'),
        ),
      ],
    ),
  );
}

class _InstructionStep extends StatelessWidget {
  const _InstructionStep({required this.number, required this.text});

  final int number;
  final String text;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        CircleAvatar(
          radius: 14,
          child: Text('$number'),
        ),
        const SizedBox(width: 12),
        Expanded(child: Text(text)),
      ],
    ),
  );
}

class _InstructionNotice extends StatelessWidget {
  const _InstructionNotice({required this.icon, required this.text});

  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    final ColorScheme colors = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: colors.secondaryContainer,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Icon(icon, color: colors.onSecondaryContainer),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              text,
              style: TextStyle(color: colors.onSecondaryContainer),
            ),
          ),
        ],
      ),
    );
  }
}
