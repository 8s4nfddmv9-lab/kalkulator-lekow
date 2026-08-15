import 'package:kalkulator_lekow/application/preferences/app_language.dart';

import 'document_language_bridge_stub.dart'
    if (dart.library.js_interop) 'document_language_bridge_web.dart';

/// Keeps the host document language in sync with the Flutter interface.
void updateDocumentLanguage(AppLanguage language) =>
    updateDocumentLanguageOnPlatform(language);
