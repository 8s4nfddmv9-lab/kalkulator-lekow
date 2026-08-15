import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:kalkulator_lekow/application/analytics/analytics_tracker.dart';
import 'package:kalkulator_lekow/presentation/common/external_link.dart';
import 'package:kalkulator_lekow/presentation/localization/app_localizations.dart';

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
    final AppLocalizations l10n = AppLocalizations.of(context);
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
                l10n.footerTagline,
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
                    onPressed: () => _openExternal(
                      context,
                      title: l10n.aboutLink,
                      url: _aboutUrl,
                    ),
                    child: Text(l10n.aboutLink),
                  ),
                  TextButton(
                    onPressed: () => _openExternal(
                      context,
                      title: l10n.changelogLink,
                      url: _changelogUrl,
                    ),
                    child: Text(l10n.changelogLink),
                  ),
                  TextButton(
                    onPressed: () => _openPrivacy(context),
                    child: Text(l10n.privacyLink),
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
                      title: l10n.contactLink,
                      url: _contactUrl,
                    ),
                    child: Text(l10n.contactLink),
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
            child: Text(AppLocalizations.of(dialogContext).close),
          ),
          FilledButton.tonal(
            onPressed: () async {
              await Clipboard.setData(ClipboardData(text: url));
              if (dialogContext.mounted) {
                Navigator.of(dialogContext).pop();
              }
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(AppLocalizations.of(context).addressCopied),
                  ),
                );
              }
            },
            child: Text(AppLocalizations.of(dialogContext).copyAddress),
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
      builder: (BuildContext dialogContext) {
        final AppLocalizations l10n = AppLocalizations.of(dialogContext);
        return AlertDialog(
          key: const Key('privacy-dialog'),
          title: Text(l10n.privacyTitle),
          content: SingleChildScrollView(child: Text(l10n.privacyBody)),
          actions: <Widget>[
            FilledButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: Text(l10n.acknowledge),
            ),
          ],
        );
      },
    );
  }
}
