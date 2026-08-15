import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/application/preferences/app_language.dart';

void main() {
  test('language codes are stable and unknown values fall back to Polish', () {
    expect(AppLanguage.polish.code, 'pl');
    expect(AppLanguage.english.code, 'en');
    expect(AppLanguage.fromCode('pl'), AppLanguage.polish);
    expect(AppLanguage.fromCode('en'), AppLanguage.english);
    expect(AppLanguage.fromCode('de'), AppLanguage.polish);
    expect(AppLanguage.fromCode(null), AppLanguage.polish);
  });

  test('the two-state language switch is reversible', () {
    expect(AppLanguage.polish.toggled, AppLanguage.english);
    expect(AppLanguage.english.toggled, AppLanguage.polish);
  });
}
