/// Local persistence boundary for the optional PWA installation reminder.
abstract interface class PwaInstallPromptStore {
  /// Returns the instant until which the installation invitation is hidden.
  Future<DateTime?> loadSnoozedUntil();

  /// Hides the installation invitation until [value].
  Future<void> saveSnoozedUntil(DateTime value);

  /// Removes a previously stored postponement.
  Future<void> clearSnooze();
}

/// Non-persistent default used by tests, previews and unsupported platforms.
final class EphemeralPwaInstallPromptStore implements PwaInstallPromptStore {
  /// Creates a store that never persists data between widget instances.
  const EphemeralPwaInstallPromptStore();

  @override
  Future<DateTime?> loadSnoozedUntil() async => null;

  @override
  Future<void> saveSnoozedUntil(DateTime value) async {}

  @override
  Future<void> clearSnooze() async {}
}
