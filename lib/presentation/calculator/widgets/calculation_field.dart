import 'package:flutter/material.dart';

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
    required this.label,
    required this.controller,
    required this.units,
    required this.selectedUnit,
    required this.onChanged,
    required this.onUnitChanged,
    required this.appearance,
    this.helperText,
    this.errorText,
    this.valueFieldKey,
    this.enabled = true,
    super.key,
  });

  /// Field label.
  final String label;

  /// Text editing controller.
  final TextEditingController controller;

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
      CalculationFieldAppearance.invalid =>
        colorScheme.error,
      CalculationFieldAppearance.empty => colorScheme.outlineVariant,
    };

    return Card(
      color: cardColor,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: borderColor),
      ),
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Row(
              children: <Widget>[
                Expanded(
                  child: Text(
                    label,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
                if (appearance != CalculationFieldAppearance.empty)
                  _FieldStateBadge(appearance: appearance),
              ],
            ),
            const SizedBox(height: 12),
            LayoutBuilder(
              builder: (BuildContext context, BoxConstraints constraints) {
                final Widget valueInput = _buildValueInput();
                final Widget unitSelector = _buildUnitSelector();

                if (constraints.maxWidth < 360) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: <Widget>[
                      valueInput,
                      const SizedBox(height: 12),
                      unitSelector,
                    ],
                  );
                }

                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: <Widget>[
                    Expanded(child: valueInput),
                    const SizedBox(width: 12),
                    SizedBox(width: 144, child: unitSelector),
                  ],
                );
              },
            ),
            if (helperText != null) ...<Widget>[
              const SizedBox(height: 8),
              Text(helperText!, style: Theme.of(context).textTheme.bodySmall),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildValueInput() => TextField(
    key: valueFieldKey,
    controller: controller,
    enabled: enabled,
    keyboardType: const TextInputType.numberWithOptions(
      decimal: true,
      signed: false,
    ),
    onChanged: onChanged,
    decoration: InputDecoration(
      hintText: 'Wpisz wartość',
      errorText: errorText,
      suffixIcon: switch (appearance) {
        CalculationFieldAppearance.calculated =>
          const Icon(Icons.calculate_outlined),
        CalculationFieldAppearance.conflict =>
          const Icon(Icons.warning_amber_rounded),
        CalculationFieldAppearance.invalid => const Icon(Icons.error_outline),
        CalculationFieldAppearance.userInput => const Icon(Icons.edit_outlined),
        CalculationFieldAppearance.empty => null,
      },
    ),
  );

  Widget _buildUnitSelector() => DropdownButtonFormField<String>(
    key: ValueKey<String>('unit-$label-$selectedUnit'),
    initialValue: selectedUnit,
    isExpanded: true,
    decoration: const InputDecoration(labelText: 'Jednostka'),
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
  );
}

class _FieldStateBadge extends StatelessWidget {
  const _FieldStateBadge({required this.appearance});

  final CalculationFieldAppearance appearance;

  @override
  Widget build(BuildContext context) {
    final (String label, IconData icon) = switch (appearance) {
      CalculationFieldAppearance.userInput => ('Wpisane', Icons.edit_outlined),
      CalculationFieldAppearance.calculated =>
        ('Wyliczone', Icons.calculate_outlined),
      CalculationFieldAppearance.conflict =>
        ('Konflikt', Icons.warning_amber_rounded),
      CalculationFieldAppearance.invalid => ('Błąd', Icons.error_outline),
      CalculationFieldAppearance.empty => ('', Icons.circle_outlined),
    };

    return Semantics(
      label: label,
      child: Chip(
        avatar: Icon(icon, size: 18),
        label: Text(label),
        visualDensity: VisualDensity.compact,
      ),
    );
  }
}
