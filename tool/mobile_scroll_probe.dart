// Benchmark-only entry point. Production continues to use lib/main.dart.
import 'dart:convert';
import 'dart:js_interop';

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart'
    show debugProfileLayoutsEnabled, debugProfilePaintsEnabled;
import 'package:kalkulator_lekow/main.dart' as production;

@JS('infusionProbeRead')
external set _read(JSFunction callback);
@JS('infusionProbeJump')
external set _jump(JSFunction callback);
@JS('infusionProbeEdit')
external set _edit(JSFunction callback);
@JS('infusionProbeBlur')
external set _blur(JSFunction callback);

List<Element> _elements() {
  final List<Element> result = <Element>[];
  void visit(Element element) {
    result.add(element);
    element.visitChildren(visit);
  }

  WidgetsBinding.instance.rootElement?.visitChildren(visit);
  return result;
}

ScrollPosition? _position;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Enable only for a separate profile-mode diagnostic trace, never for the
  // release-mode timing comparison (timeline instrumentation adds overhead).
  debugProfileBuildsEnabled = const bool.fromEnvironment('SCROLL_TRACE');
  debugProfileLayoutsEnabled = const bool.fromEnvironment('SCROLL_TRACE');
  debugProfilePaintsEnabled = const bool.fromEnvironment('SCROLL_TRACE');
  _read = (() {
    if (_position == null || !_position!.hasPixels) {
      for (final Element element in _elements()) {
        if (element is StatefulElement && element.state is ScrollableState) {
          _position = (element.state as ScrollableState).position;
          break;
        }
      }
    }
    final ScrollPosition? position = _position;
    return jsonEncode(<String, Object?>{
      'pixels': position?.pixels,
      'max': position?.maxScrollExtent,
      'viewport': position?.viewportDimension,
    }).toJS;
  }).toJS;
  _jump = ((JSNumber offset) {
    _position?.jumpTo(offset.toDartDouble);
  }).toJS;
  _edit = ((JSString key, JSString value) {
    for (final Element element in _elements()) {
      final Widget widget = element.widget;
      if (widget is TextField && widget.key == Key(key.toDart)) {
        widget.controller!.text = value.toDart;
        widget.onChanged!(value.toDart);
        return true.toJS;
      }
    }
    return false.toJS;
  }).toJS;
  _blur = (() => FocusManager.instance.primaryFocus?.unfocus()).toJS;
  await production.main();
}
