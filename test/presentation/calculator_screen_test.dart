import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/app.dart';
import 'package:kalkulator_lekow/presentation/calculator/calculator_screen.dart';

void main() {
  testWidgets('shows the calculator sections and safety warning', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());

    expect(find.text('Kalkulator leków'), findsOneWidget);
    expect(
      find.text('Prototyp — nie używać do podejmowania decyzji klinicznych.'),
      findsOneWidget,
    );
    expect(find.text('Masa pacjenta'), findsOneWidget);
    expect(find.text('Ilość leku'), findsOneWidget);

    await tester.drag(find.byType(ListView), const Offset(0, -1400));
    await tester.pumpAndSettle();

    expect(find.text('Przepływ'), findsOneWidget);
    expect(find.text('Dawka / szybkość podaży'), findsOneWidget);
  });

  testWidgets('allows disabling the per-kilogram dose component', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KalkulatorLekowApp());
    await tester.drag(find.byType(ListView), const Offset(0, -1400));
    await tester.pumpAndSettle();

    final Finder preview = find.byKey(const Key('dose-unit-preview'));
    expect(tester.widget<Text>(preview).data, 'µg/kg/min');

    await tester.tap(find.byKey(const Key('per-kilogram-toggle')));
    await tester.pump();

    expect(tester.widget<Text>(preview).data, 'µg/min');
  });

  testWidgets('supports a small dark screen with enlarged text', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(320, 568);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      MaterialApp(
        theme: ThemeData.dark(useMaterial3: true),
        home: MediaQuery(
          data: MediaQueryData(textScaler: TextScaler.linear(1.5)),
          child: const CalculatorScreen(),
        ),
      ),
    );
    await tester.pumpAndSettle();

    expect(tester.takeException(), isNull);
    expect(find.byType(ListView), findsOneWidget);

    final Finder doseHeading = find.text('Dawka / szybkość podaży');
    for (int attempt = 0; attempt < 12; attempt++) {
      if (doseHeading.evaluate().isNotEmpty) {
        break;
      }
      await tester.drag(find.byType(ListView), const Offset(0, -300));
      await tester.pumpAndSettle();
    }

    expect(tester.takeException(), isNull);
    expect(doseHeading, findsOneWidget);
  });
}
