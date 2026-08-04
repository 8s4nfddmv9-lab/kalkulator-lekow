import 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_bridge_stub.dart'
    if (dart.library.js_interop)
        'package:kalkulator_lekow/presentation/pwa_install/pwa_install_bridge_web.dart'
    as implementation;
import 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_bridge_types.dart';

export 'package:kalkulator_lekow/presentation/pwa_install/pwa_install_bridge_types.dart';

/// Creates the platform-appropriate browser bridge.
PwaInstallBridge createPwaInstallBridge() =>
    implementation.createPwaInstallBridge();
