import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';
import 'package:kalkulator_lekow/presentation/common/external_link.dart';

/// Compact application footer shared by all current presentation targets.
class AppFooter extends StatelessWidget {
  /// Creates the InfusionCalc footer.
  const AppFooter({
    this.analyticsTracker = const NoopAnalyticsTracker(),
    super.key,
  });

  /// Privacy-reviewed analytics sink isolated from calculator values.
  final AnalyticsTracker analyticsTracker;

  static const String _aboutUrl = 'https://infusioncalc.eu/about/';
  static const String _privacyUrl = 'https://infusioncalc.eu/privacy/';
  static const String _changelogUrl = 'https://infusioncalc.eu/changelog/';
  static const String _licenseUrl =
      'https://github.com/8s4nfddmv9-lab/kalkulator-lekow/blob/main/LICENSE';
  static const String _repositoryUrl =
      'https://github.com/8s4nfddmv9-lab/kalkulator-lekow';
  static const String _contactUrl =
      'https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18';

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    final ColorScheme colors = theme.colorScheme;

    return Material(
      color: colors.surfaceContainerLow,
      child: SafeArea(
        top: false,
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.fromLTRB(8, 8, 8, 6),
          decoration: BoxDecoration(
            border: Border(top: BorderSide(color: colors.outlineVariant)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
              Text(
                'InfusionCalc · Technical infusion calculator',
                style: theme.textTheme.labelMedium,
                textAlign: TextAlign.center,
              ),
              TextButton(
                style: TextButton.styleFrom(
                  minimumSize: const Size(0, 32),
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  visualDensity: VisualDensity.compact,
                ),
                onPressed: () => _openExternal(
                  context,
                  title: 'MIT License',
                  url: _licenseUrl,
                ),
                child: const Text('© 2026 M W · MIT License'),
              ),
              Wrap(
                alignment: WrapAlignment.center,
                spacing: 2,
                runSpacing: 0,
                children: <Widget>[
                  TextButton(
                    onPressed: () =>
                        _openExternal(context, title: 'About', url: _aboutUrl),
                    child: const Text('About'),
                  ),
                  TextButton(
                    onPressed: () => _openExternal(
                      context,
                      title: 'Changelog',
                      url: _changelogUrl,
                    ),
                    child: const Text('Changelog'),
                  ),
                  TextButton(
                    onPressed: () => _openPrivacy(context),
                    child: const Text('Privacy'),
                  ),
                  TextButton(
                    onPressed: () => _openTrackedExternal(
                      context,
                      event: AnalyticsEvent.githubClicked,
                      title: 'GitHub',
                      url: _repositoryUrl,
                    ),
                    child: const Text('GitHub'),
                  ),
                  TextButton(
                    onPressed: () => _openTrackedExternal(
                      context,
                      event: AnalyticsEvent.contactClicked,
                      title: 'Contact',
                      url: _contactUrl,
                    ),
                    child: const Text('Contact'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _openTrackedExternal(
    BuildContext context, {
    required AnalyticsEvent event,
    required String title,
    required String url,
  }) {
    analyticsTracker.track(event);
    return _openExternal(context, title: title, url: url);
  }

  Future<void> _openExternal(
    BuildContext context, {
    required String title,
    required String url,
  }) async {
    final bool opened = await openExternalLink(url);
    if (opened || !context.mounted) {
      return;
    }

    await showDialog<void>(
      context: context,
      builder: (BuildContext dialogContext) => AlertDialog(
        title: Text(title),
        content: SelectableText(url),
        actions: <Widget>[
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: const Text('Zamknij'),
          ),
          FilledButton.tonal(
            onPressed: () async {
              await Clipboard.setData(ClipboardData(text: url));
              if (dialogContext.mounted) {
                Navigator.of(dialogContext).pop();
              }
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Adres skopiowany.')),
                );
              }
            },
            child: const Text('Kopiuj adres'),
          ),
        ],
      ),
    );
  }

  Future<void> _openPrivacy(BuildContext context) async {
    analyticsTracker.track(AnalyticsEvent.privacyOpened);
    final bool opened = await openExternalLink(_privacyUrl);
    if (opened || !context.mounted) {
      return;
    }
    await _showPrivacyDialog(context);
  }

  Future<void> _showPrivacyDialog(BuildContext context) {
    return showDialog<void>(
      context: context,
      builder: (BuildContext dialogContext) => AlertDialog(
        key: const Key('privacy-dialog'),
        title: const Text('Privacy'),
        content: const SingleChildScrollView(
          child: Text(
            'Obliczenia wykonują się lokalnie na urządzeniu. InfusionCalc '
            'nie wysyła masy, ilości leku, stężenia, dawki, przepływu ani '
            'wyników do analityki. Nie wpisuj danych identyfikujących '
            'pacjenta.\n\n'
            'Aplikacja korzysta z minimalnej analityki Umami Cloud. '
            'Rejestrowane są odsłony strony oraz stała lista zdarzeń '
            'interfejsu, takich jak uruchomienie aplikacji, otwarcie '
            'informacji i działania związane z instalacją PWA. Zdarzenia '
            'mogą zawierać wyłącznie wersję aplikacji, platformę, tryb '
            'przeglądarki/PWA i metodę instalacji. Nie tworzymy własnego '
            'identyfikatora użytkownika.\n\n'
            'Pełny tryb offline zapisuje lokalnie publiczny kod i statyczne '
            'zasoby aplikacji, takie jak skrypty, fonty, ikony oraz strony '
            'informacyjne. Cache offline nie zawiera wartości formularza, '
            'wyników ani historii obliczeń.\n\n'
            'Lokalnie zapisywane są wyłącznie niekliniczne ustawienia: '
            'wybrane jednostki, tryb /kg oraz data odroczenia komunikatu '
            'instalacji PWA po wybraniu „Nie teraz”. Pola liczbowe, wyniki '
            'i historia obliczeń nie są utrwalane.',
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
}
