import 'package:flutter/material.dart';
import 'package:kalkulator_lekow/presentation/calculator/formatting/leading_decimal_zero_formatter.dart';
import 'package:kalkulator_lekow/presentation/localization/app_localizations.dart';

/// Visual state of one calculator field.
enum CalculationFieldAppearance {
  /// Field has no usable value.
  empty,

  /// Value was explicitly entered by the user.
  userInput,

  /// Value was produced by the solver.
  calculated,

  /// Redundant values disagree.
  conflict,

  /// Current text cannot be parsed or validated.
  invalid,
}

/// Reusable numeric field with a unit selector and explicit provenance state.
class CalculationField extends StatelessWidget {
  /// Creates a labelled numeric field with a unit selector.
  const CalculationField({
    required this.fieldId,
    required this.label,
    required this.controller,
    required this.units,
    required this.selectedUnit,
    required this.onChanged,
    required this.onUnitChanged,
    required this.appearance,
    this.focusNode,
    this.helperText,
    this.errorText,
    this.valueFieldKey,
    this.compact = false,
    this.enabled = true,
    super.key,
  });

  /// Stable semantic identifier independent of the translated field label.
  final String fieldId;

  /// Field label.
  final String label;

  /// Text editing controller.
  final TextEditingController controller;

  /// Stable focus node owned by the parent calculator screen.
  final FocusNode? focusNode;

  /// Unit symbols available in the selector.
  final List<String> units;

  /// Currently selected unit symbol.
  final String selectedUnit;

  /// Called for every user text edit.
  final ValueChanged<String> onChanged;

  /// Called when the unit selection changes.
  final ValueChanged<String> onUnitChanged;

  /// Current provenance or error appearance.
  final CalculationFieldAppearance appearance;

  /// Optional explanatory text shown below the row.
  final String? helperText;

  /// Optional validation or conflict text.
  final String? errorText;

  /// Stable key for widget tests and accessibility automation.
  final Key? valueFieldKey;

  /// Reduces spacing for the wide desktop dashboard.
  final bool compact;

  /// Whether the numeric field can be edited.
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    final ColorScheme colorScheme = Theme.of(context).colorScheme;
    final Color? cardColor = switch (appearance) {
      CalculationFieldAppearance.calculated =>
        colorScheme.secondaryContainer.withValues(alpha: 0.45),
      CalculationFieldAppearance.conflict ||
      CalculationFieldAppearance.invalid =>
        colorScheme.errorContainer.withValues(alpha: 0.55),
      _ => null,
    };
    final Color borderColor = switch (appearance) {
      CalculationFieldAppearance.userInput => colorScheme.primary,
      CalculationFieldAppearance.calculated => colorScheme.secondary,
      CalculationFieldAppearance.conflict ||
      CalculationFieldAppearance.invalid => colorScheme.error,
      CalculationFieldAppearance.empty => colorScheme.outlineVariant,
    };

    return Card(
      color: cardColor,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: borderColor),
      ),
      margin: EdgeInsets.only(bottom: compact ? 4 : 12),
      child: Padding(
        padding: EdgeInsets.all(compact ? 6 : 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Row(
              children: <Widget>[
                Expanded(
                  child: Text(
                    label,
                    style: compact
                        ? Theme.of(context).textTheme.titleSmall
                        : Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                if (appearance != CalculationFieldAppearance.empty)
                  _FieldStateBadge(appearance: appearance, compact: compact),
              ],
            ),
            SizedBox(height: compact ? 2 : 12),
            LayoutBuilder(
              builder: (BuildContext context, BoxConstraints constraints) {
                final Widget valueInput = _buildValueInput(context);
                final Widget unitSelector = _buildUnitSelector(context);

                if (constraints.maxWidth < (compact ? 290 : 360)) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      valueInput,
                      SizedBox(height: compact ? 6 : 12),
                      unitSelector,
                    ],
                  );
                }

                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Expanded(child: valueInput),
                    SizedBox(width: compact ? 6 : 12),
                    SizedBox(width: compact ? 146 : 144, child: unitSelector),
                  ],
                );
              },
            ),
            if (helperText != null) ...<Widget>[
              SizedBox(height: compact ? 2 : 8),
              Text(helperText!, style: Theme.of(context).textTheme.bodySmall),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildValueInput(BuildContext context) {
    final AppLocalizations l10n = AppLocalizations.of(context);
    return Semantics(
      label: '$label, ${l10n.enterValue}',
      textField: true,
      child: TextField(
        key: valueFieldKey,
        controller: controller,
        focusNode: focusNode,
        enabled: enabled,
        keyboardType: const TextInputType.numberWithOptions(
          decimal: true,
          signed: false,
        ),
        inputFormatters: const <LeadingDecimalZeroFormatter>[
          LeadingDecimalZeroFormatter(),
        ],
        onChanged: onChanged,
        decoration: InputDecoration(
          isDense: compact,
          contentPadding: compact
              ? const EdgeInsets.symmetric(horizontal: 10, vertical: 10)
              : null,
          hintText: l10n.enterValue,
          errorText: compact ? null : errorText,
          errorMaxLines: 3,
          suffixIcon: switch (appearance) {
            CalculationFieldAppearance.calculated => const Icon(
              Icons.calculate_outlined,
            ),
            CalculationFieldAppearance.conflict => Tooltip(
              message: errorText ?? '',
              child: const Icon(Icons.warning_amber_rounded),
            ),
            CalculationFieldAppearance.invalid => Tooltip(
              message: errorText ?? '',
              child: const Icon(Icons.error_outline),
            ),
            CalculationFieldAppearance.userInput => const Icon(
              Icons.edit_outlined,
            ),
            CalculationFieldAppearance.empty => null,
          },
        ),
      ),
    );
  }

  Widget _buildUnitSelector(BuildContext context) {
    final AppLocalizations l10n = AppLocalizations.of(context);
    return Semantics(
      label: '$label, ${l10n.unitLabel}',
      button: true,
      child: DropdownButtonFormField<String>(
        key: ValueKey<String>('unit-$fieldId-$selectedUnit'),
        initialValue: selectedUnit,
        isExpanded: true,
        decoration: InputDecoration(
          labelText: l10n.unitLabel,
          isDense: compact,
          contentPadding: compact
              ? const EdgeInsets.symmetric(horizontal: 10, vertical: 10)
              : null,
        ),
        items: units
            .map(
              (String unit) => DropdownMenuItem<String>(
                value: unit,
                child: Text(unit, overflow: TextOverflow.ellipsis),
              ),
            )
            .toList(growable: false),
        onChanged: enabled
            ? (String? unit) {
                if (unit != null) {
                  onUnitChanged(unit);
                }
              }
            : null,
      ),
    );
  }
}

class _FieldStateBadge extends StatelessWidget {
  const _FieldStateBadge({required this.appearance, required this.compact});

  final CalculationFieldAppearance appearance;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final String label = AppLocalizations.of(
      context,
    ).fieldStateLabel(appearance.name);
    final IconData icon = switch (appearance) {
      CalculationFieldAppearance.userInput => Icons.edit_outlined,
      CalculationFieldAppearance.calculated => Icons.calculate_outlined,
      CalculationFieldAppearance.conflict => Icons.warning_amber_rounded,
      CalculationFieldAppearance.invalid => Icons.error_outline,
      CalculationFieldAppearance.empty => Icons.circle_outlined,
    };

    return Semantics(
      label: label,
      excludeSemantics: true,
      child: Chip(
        avatar: Icon(icon, size: compact ? 15 : 18),
        label: Text(
          label,
          style: compact ? Theme.of(context).textTheme.labelSmall : null,
        ),
        visualDensity: VisualDensity.compact,
        materialTapTargetSize: compact
            ? MaterialTapTargetSize.shrinkWrap
            : null,
      ),
    );
  }
}
