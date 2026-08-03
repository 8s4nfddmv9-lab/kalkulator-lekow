import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/presentation/common/app_footer.dart';

void main() {
  Widget subject() => const MaterialApp(
    home: Scaffold(
      body: SizedBox.expand(),
      bottomNavigationBar: AppFooter(),
    ),
  );

  testWidgets('shows all requested footer sections', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(subject());

    expect(find.text('InfusionCalc · Technical infusion calculator'), findsOneWidget);
    expect(find.text('Changelog'), findsOneWidget);
    expect(find.text('Privacy'), findsOneWidget);
    expect(find.text('GitHub'), findsOneWidget);
    expect(find.text('Contact'), findsOneWidget);
  });

  testWidgets('privacy dialog explains local processing', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(subject());

    await tester.tap(find.text('Privacy'));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('privacy-dialog')), findsOneWidget);
    expect(
      find.textContaining('Obliczenia wykonują się lokalnie na urządzeniu'),
      findsOneWidget,
    );
    expect(
      find.textContaining('Nie wpisuj danych identyfikujących pacjenta'),
      findsOneWidget,
    );
  });

  testWidgets('native contact fallback exposes the feedback issue address', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(subject());

    await tester.tap(find.text('Contact'));
    await tester.pumpAndSettle();

    expect(
      find.text(
        'https://github.com/8s4nfddmv9-lab/kalkulator-lekow/issues/18',
      ),
      findsOneWidget,
    );
    expect(find.text('Kopiuj adres'), findsOneWidget);
  });
}
