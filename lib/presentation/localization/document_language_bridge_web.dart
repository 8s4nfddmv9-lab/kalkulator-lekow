import 'dart:js_interop';

import 'package:kalkulator_lekow/application/preferences/app_language.dart';

@JS('infusionCalcSetLanguage')
external void _setDocumentLanguage(JSString languageCode);

/// Updates the host page language without coupling shared code to the web DOM.
void updateDocumentLanguageOnPlatform(AppLanguage language) {
  _setDocumentLanguage(language.code.toJS);
}
