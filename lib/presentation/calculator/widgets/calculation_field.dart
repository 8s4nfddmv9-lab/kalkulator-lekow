import 'package:flutter/material.dart';

/// Reusable input row used by the initial calculator screen.
class CalculationField extends StatelessWidget {
  /// Creates a labelled numeric field with a unit selector.
  const CalculationField({
    required this.label,
    required this.controller,
    required this.units,
    required this.selectedUnit,
    required this.onUnitChanged,
    this.helperText,
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

  /// Called when the unit selection changes.
  final ValueChanged<String> onUnitChanged;

  /// Optional explanatory text shown below the row.
  final String? helperText;

  /// Whether the numeric field can be edited.
  final bool enabled;

  @override
  Widget build(BuildContext context) => Card(
    margin: const EdgeInsets.only(bottom: 12),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(label, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 12),
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Expanded(
                child: TextField(
                  controller: controller,
                  enabled: enabled,
                  keyboardType: const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(
                    hintText: 'Wpisz wartość',
                  ),
                ),
              ),
              const SizedBox(width: 12),
              SizedBox(
                width: 112,
                child: DropdownButtonFormField<String>(
                  initialValue: selectedUnit,
                  decoration: const InputDecoration(labelText: 'Jednostka'),
                  items: units
                      .map(
                        (String unit) => DropdownMenuItem<String>(
                          value: unit,
                          child: Text(unit),
                        ),
                      )
                      .toList(growable: false),
                  onChanged: (String? unit) {
                    if (unit != null) {
                      onUnitChanged(unit);
                    }
                  },
                ),
              ),
            ],
          ),
          if (helperText != null) ...<Widget>[
            const SizedBox(height: 8),
            Text(
              helperText!,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ],
      ),
    ),
  );
}
