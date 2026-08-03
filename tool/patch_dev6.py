from pathlib import Path

path = Path('lib/presentation/calculator/calculator_screen.dart')
source = path.read_text()

replacements = [
    (
        "import 'package:flutter/material.dart';\n",
        "import 'dart:async';\n\nimport 'package:flutter/material.dart';\n",
    ),
    (
        "import 'package:kalkulator_lekow/application/calculator_session.dart';\n",
        "import 'package:kalkulator_lekow/application/calculator_session.dart';\n"
        "import 'package:kalkulator_lekow/application/calculator_unit_options.dart';\n"
        "import 'package:kalkulator_lekow/application/preferences/calculator_preferences.dart';\n",
    ),
    (
        "  /// Creates the calculator screen.\n"
        "  const CalculatorScreen({super.key});\n\n"
        "  @override\n",
        "  /// Creates the calculator screen.\n"
        "  const CalculatorScreen({\n"
        "    this.preferencesStore = const VolatileCalculatorPreferencesStore(),\n"
        "    super.key,\n"
        "  });\n\n"
        "  /// Store used only for non-clinical presentation preferences.\n"
        "  final CalculatorPreferencesStore preferencesStore;\n\n"
        "  @override\n",
    ),
    (
        "  late final Map<QuantityKind, MeasurementUnit> _presentationUnits;\n\n"
        "  final Map<QuantityKind, String> _inputErrors",
        "  late final Map<QuantityKind, MeasurementUnit> _presentationUnits;\n"
        "  late final CalculatorPreferencesStore _preferencesStore;\n"
        "  Future<void> _preferencesWriteQueue = Future<void>.value();\n\n"
        "  final Map<QuantityKind, String> _inputErrors",
    ),
    (
        "  bool _dosePerKilogram = true;\n"
        "  bool _isSynchronizing = false;\n",
        "  bool _dosePerKilogram = true;\n"
        "  bool _isSynchronizing = false;\n"
        "  bool _hasLocalPreferenceEdit = false;\n",
    ),
    (
        "    _session = CalculatorSession();\n"
        "    _solution = _session.solution;\n"
        "    _controllers = <QuantityKind, TextEditingController>{\n"
        "      for (final QuantityKind kind in _editableKinds)\n"
        "        kind: TextEditingController(),\n"
        "    };\n"
        "    _presentationUnits = <QuantityKind, MeasurementUnit>{\n"
        "      QuantityKind.bodyMass: UnitCatalog.kilogram,\n"
        "      QuantityKind.drugAmount: UnitCatalog.milligram,\n"
        "      QuantityKind.solutionVolume: UnitCatalog.millilitre,\n"
        "      QuantityKind.concentration: UnitCatalog.find('ug/mL'),\n"
        "      QuantityKind.flowRate: UnitCatalog.millilitresPerHour,\n"
        "      QuantityKind.administrationRate: UnitCatalog.find('ug/min'),\n"
        "      QuantityKind.weightNormalizedDose: UnitCatalog.find('ug/kg/min'),\n"
        "      QuantityKind.infusionDuration: UnitCatalog.hour,\n"
        "    };\n",
        "    _session = CalculatorSession();\n"
        "    _solution = _session.solution;\n"
        "    _preferencesStore = widget.preferencesStore;\n"
        "    _controllers = <QuantityKind, TextEditingController>{\n"
        "      for (final QuantityKind kind in _editableKinds)\n"
        "        kind: TextEditingController(),\n"
        "    };\n"
        "    final CalculatorPreferences defaults = CalculatorPreferences.defaults();\n"
        "    _presentationUnits = <QuantityKind, MeasurementUnit>{\n"
        "      for (final QuantityKind kind in CalculatorPreferences.persistedKinds)\n"
        "        kind: defaults.unitFor(kind),\n"
        "    };\n"
        "    _dosePerKilogram = defaults.dosePerKilogram;\n"
        "    unawaited(_restorePreferences());\n",
    ),
    (
        "  List<MeasurementUnit> _unitsFor(QuantityKind kind) => switch (kind) {\n"
        "    QuantityKind.bodyMass => <MeasurementUnit>[...UnitCatalog.bodyMassUnits],\n"
        "    QuantityKind.drugAmount => <MeasurementUnit>[\n"
        "      ...UnitCatalog.medicineAmountUnits,\n"
        "    ],\n"
        "    QuantityKind.solutionVolume => <MeasurementUnit>[UnitCatalog.millilitre],\n"
        "    QuantityKind.concentration => <MeasurementUnit>[\n"
        "      ...UnitCatalog.concentrationUnits,\n"
        "    ],\n"
        "    QuantityKind.flowRate => <MeasurementUnit>[UnitCatalog.millilitresPerHour],\n"
        "    QuantityKind.administrationRate => <MeasurementUnit>[\n"
        "      ...UnitCatalog.administrationRateUnits,\n"
        "    ],\n"
        "    QuantityKind.weightNormalizedDose => <MeasurementUnit>[\n"
        "      ...UnitCatalog.weightNormalizedDoseUnits,\n"
        "    ],\n"
        "    QuantityKind.infusionDuration || QuantityKind.time => <MeasurementUnit>[\n"
        "      UnitCatalog.minute,\n"
        "      UnitCatalog.hour,\n"
        "    ],\n"
        "  };\n",
        "  List<MeasurementUnit> _unitsFor(QuantityKind kind) =>\n"
        "      CalculatorUnitOptions.forKind(kind);\n",
    ),
    (
        "          _synchronizeControllers();\n"
        "        });\n"
        "      } on UnitConversionException {\n",
        "          _synchronizeControllers();\n"
        "        });\n"
        "        _queuePreferencesSave();\n"
        "      } on UnitConversionException {\n",
    ),
    (
        "          _synchronizeControllers();\n"
        "        });\n"
        "      }\n"
        "      return;\n",
        "          _synchronizeControllers();\n"
        "        });\n"
        "        _queuePreferencesSave();\n"
        "      }\n"
        "      return;\n",
    ),
    (
        "      _synchronizeControllers();\n"
        "    });\n"
        "  }\n\n"
        "  void _toggleDosePerKilogram(bool enabled) {\n",
        "      _synchronizeControllers();\n"
        "    });\n"
        "    _queuePreferencesSave();\n"
        "  }\n\n"
        "  void _toggleDosePerKilogram(bool enabled) {\n",
    ),
    (
        "      _synchronizeControllers();\n"
        "    });\n"
        "  }\n\n"
        "  void _clearAll() {\n",
        "      _synchronizeControllers();\n"
        "    });\n"
        "    _queuePreferencesSave();\n"
        "  }\n\n"
        "  Future<void> _restorePreferences() async {\n"
        "    try {\n"
        "      final CalculatorPreferences preferences =\n"
        "          await _preferencesStore.load();\n"
        "      if (!mounted || _hasLocalPreferenceEdit) {\n"
        "        return;\n"
        "      }\n"
        "      setState(() {\n"
        "        for (final QuantityKind kind\n"
        "            in CalculatorPreferences.persistedKinds) {\n"
        "          _presentationUnits[kind] = preferences.unitFor(kind);\n"
        "        }\n"
        "        _dosePerKilogram = preferences.dosePerKilogram;\n"
        "        _synchronizeControllers();\n"
        "      });\n"
        "    } on Object {\n"
        "      if (!mounted || _hasLocalPreferenceEdit) {\n"
        "        return;\n"
        "      }\n"
        "      setState(() {\n"
        "        _globalMessage =\n"
        "            'Nie udało się odczytać ustawień jednostek. ' \n"
        "            'Użyto wartości domyślnych.';\n"
        "      });\n"
        "    }\n"
        "  }\n\n"
        "  CalculatorPreferences _currentPreferences() => CalculatorPreferences(\n"
        "    unitCodes: <QuantityKind, String>{\n"
        "      for (final QuantityKind kind\n"
        "          in CalculatorPreferences.persistedKinds)\n"
        "        kind: _presentationUnits[kind]!.code,\n"
        "    },\n"
        "    dosePerKilogram: _dosePerKilogram,\n"
        "  );\n\n"
        "  void _queuePreferencesSave() {\n"
        "    _hasLocalPreferenceEdit = true;\n"
        "    final CalculatorPreferences snapshot = _currentPreferences();\n"
        "    _preferencesWriteQueue = _preferencesWriteQueue.then(\n"
        "      (_) => _savePreferencesSnapshot(snapshot),\n"
        "    );\n"
        "  }\n\n"
        "  Future<void> _savePreferencesSnapshot(\n"
        "    CalculatorPreferences snapshot,\n"
        "  ) async {\n"
        "    try {\n"
        "      await _preferencesStore.save(snapshot);\n"
        "    } on Object {\n"
        "      if (!mounted) {\n"
        "        return;\n"
        "      }\n"
        "      setState(() {\n"
        "        _globalMessage =\n"
        "            'Nie udało się zapisać ustawień jednostek. ' \n"
        "            'Obliczenia pozostają dostępne.';\n"
        "      });\n"
        "    }\n"
        "  }\n\n"
        "  void _clearAll() {\n",
    ),
]

for old, new in replacements:
    if old not in source:
        raise SystemExit(f'Expected source block not found:\n{old[:180]}')
    source = source.replace(old, new, 1)

path.write_text(source)
