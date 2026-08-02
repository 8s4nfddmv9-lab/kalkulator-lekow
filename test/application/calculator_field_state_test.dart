import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/application/calculator_field_state.dart';

void main() {
  group('CalculatorFieldState', () {
    test('allows body mass as user input', () {
      const CalculatorFieldState<int> state =
          CalculatorFieldState<int>.userInput(
            id: CalculatorFieldId.bodyMass,
            value: 70,
          );

      expect(state.origin, FieldOrigin.userInput);
      expect(state.value, 70);
    });

    test('never allows body mass as a calculated result', () {
      expect(
        () => CalculatorFieldState<int>.calculated(
          id: CalculatorFieldId.bodyMass,
          value: 70,
        ),
        throwsArgumentError,
      );
    });
  });
}
