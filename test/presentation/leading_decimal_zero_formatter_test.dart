import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/presentation/calculator/formatting/leading_decimal_zero_formatter.dart';

void main() {
  const LeadingDecimalZeroFormatter formatter = LeadingDecimalZeroFormatter();
  const TextEditingValue empty = TextEditingValue.empty;

  test('prefixes a comma entered into an empty field', () {
    final TextEditingValue result = formatter.formatEditUpdate(
      empty,
      const TextEditingValue(
        text: ',',
        selection: TextSelection.collapsed(offset: 1),
      ),
    );

    expect(result.text, '0,');
    expect(result.selection, const TextSelection.collapsed(offset: 2));
  });

  test('normalizes a leading dot to the application comma notation', () {
    final TextEditingValue result = formatter.formatEditUpdate(
      empty,
      const TextEditingValue(
        text: '.05',
        selection: TextSelection.collapsed(offset: 3),
      ),
    );

    expect(result.text, '0,05');
    expect(result.selection, const TextSelection.collapsed(offset: 4));
  });

  test('does not rewrite a separator added after an existing digit', () {
    const TextEditingValue oldValue = TextEditingValue(
      text: '1',
      selection: TextSelection.collapsed(offset: 1),
    );
    const TextEditingValue newValue = TextEditingValue(
      text: '1.',
      selection: TextSelection.collapsed(offset: 2),
    );

    expect(formatter.formatEditUpdate(oldValue, newValue), newValue);
  });
}
