/// Opens an external link when the current platform supports browser windows.
///
/// Native builds deliberately return `false`; the caller then presents a
/// copyable address instead of depending on another plugin.
Future<bool> openExternalLink(String url) async => false;
