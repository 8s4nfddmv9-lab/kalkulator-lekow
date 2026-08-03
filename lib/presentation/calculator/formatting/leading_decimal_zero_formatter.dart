import 'package:flutter/services.dart';

/// Inserts a leading zero when a decimal separator starts an empty field.
///
/// Both locale variants are normalized to the comma used by the application,
/// so typing `,` or `.` into an empty field immediately produces `0,`.
final class LeadingDecimalZeroFormatter extends TextInputFormatter {
  /// Creates the formatter.
  const LeadingDecimalZeroFormatter();

  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    final String text = newValue.text;
    final bool startsWithDecimalSeparator =
        text.startsWith(',') || text.startsWith('.');
    if (oldValue.text.isNotEmpty || !startsWithDecimalSeparator) {
      return newValue;
    }

    final String normalized = '0,${text.substring(1)}';
    return TextEditingValue(
      text: normalized,
      selection: TextSelection.collapsed(offset: normalized.length),
    );
  }
}
