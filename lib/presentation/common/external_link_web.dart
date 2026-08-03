import 'dart:js_interop';

@JS('window.open')
external JSAny? _windowOpen(JSString url, JSString target, JSString features);

/// Opens [url] in a separate browser context without exposing `window.opener`.
Future<bool> openExternalLink(String url) async {
  _windowOpen(url.toJS, '_blank'.toJS, 'noopener,noreferrer'.toJS);
  return true;
}
