import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';
import 'package:kalkulator_lekow/domain/solver/calculator_solver.dart';
import 'package:kalkulator_lekow/domain/solver/solver_models.dart';
import 'package:kalkulator_lekow/domain/units/unit_catalog.dart';

void main() {
  final _ReferenceMatrix matrix = _ReferenceMatrix.load();

  test('reference manifest expands to the declared 480 cases', () {
    expect(matrix.schemaVersion, 1);
    expect(matrix.manualReviewStatus, 'pending-second-person-review');

    final Map<String, int> counts = <String, int>{
      'preparationForward':
          matrix.amountUnits.length *
          matrix.preparationAmountValues.length *
          matrix.preparationVolumes.length,
      'preparationInverseAmount':
          matrix.amountUnits.length *
          matrix.preparationConcentrationValues.length *
          matrix.preparationInverseVolumes.length,
      'preparationInverseVolume':
          matrix.amountUnits.length *
          matrix.preparationAmountValues.length *
          matrix.preparationInverseConcentrations.length,
      'administrationForward':
          matrix.amountUnits.length *
          matrix.administrationConcentrationValues.length *
          matrix.administrationFlows.length,
      'administrationInverseFlow':
          matrix.amountUnits.length *
          matrix.administrationRates.length *
          matrix.administrationInverseConcentrations.length,
      'administrationInverseConcentration':
          matrix.amountUnits.length *
          matrix.administrationRates.length *
          matrix.administrationInverseFlows.length,
      'doseForward':
          matrix.amountUnits.length *
          matrix.doseRates.length *
          matrix.bodyMasses.length,
      'doseInverseRate':
          matrix.amountUnits.length *
          matrix.doseValues.length *
          matrix.inverseBodyMasses.length,
      'fullChain':
          matrix.amountUnits.length *
          matrix.fullChainAmountValues.length *
          matrix.fullChainVolumes.length *
          matrix.fullChainFlows.length,
    };

    expect(counts, matrix.categoryCounts);
    expect(
      counts.values.fold<int>(0, (int total, int value) => total + value),
      matrix.expectedCaseCount,
    );
  });

  test('preparation forward reference matrix', () {
    int executed = 0;
    for (final String amountUnit in matrix.amountUnits) {
      for (final String amountValue in matrix.preparationAmountValues) {
        for (final String volumeValue in matrix.preparationVolumes) {
          final int caseIndex = executed;
          final _OracleFraction expectedConcentration =
              _canonical(amountValue, amountUnit) /
              _canonical(volumeValue, 'mL');
          final String outputAmountUnit = _presentationAmountUnit(
            amountUnit,
            caseIndex,
          );

          _expectSolution(
            id: 'preparation-forward-$caseIndex',
            inputs: <_InputFact>[
              _InputFact(QuantityKind.drugAmount, amountValue, amountUnit),
              _InputFact(QuantityKind.solutionVolume, volumeValue, 'mL'),
            ],
            expected: <_ExpectedFact>[
              _ExpectedFact(
                QuantityKind.concentration,
                expectedConcentration,
                '$outputAmountUnit/mL',
              ),
            ],
          );
          executed += 1;
        }
      }
    }
    expect(executed, matrix.categoryCounts['preparationForward']);
  });

  test('preparation inverse amount reference matrix', () {
    int executed = 0;
    for (final String amountUnit in matrix.amountUnits) {
      for (final String concentrationValue
          in matrix.preparationConcentrationValues) {
        for (final String volumeValue in matrix.preparationInverseVolumes) {
          final int caseIndex = executed;
          final String concentrationUnit = '$amountUnit/mL';
          final _OracleFraction expectedAmount =
              _canonical(concentrationValue, concentrationUnit) *
              _canonical(volumeValue, 'mL');
          final String outputAmountUnit = _presentationAmountUnit(
            amountUnit,
            caseIndex,
          );

          _expectSolution(
            id: 'preparation-inverse-amount-$caseIndex',
            inputs: <_InputFact>[
              _InputFact(
                QuantityKind.concentration,
                concentrationValue,
                concentrationUnit,
              ),
              _InputFact(QuantityKind.solutionVolume, volumeValue, 'mL'),
            ],
            expected: <_ExpectedFact>[
              _ExpectedFact(
                QuantityKind.drugAmount,
                expectedAmount,
                outputAmountUnit,
              ),
            ],
          );
          executed += 1;
        }
      }
    }
    expect(executed, matrix.categoryCounts['preparationInverseAmount']);
  });

  test('preparation inverse volume reference matrix', () {
    int executed = 0;
    for (final String amountUnit in matrix.amountUnits) {
      for (final String amountValue in matrix.preparationAmountValues) {
        for (final String concentrationValue
            in matrix.preparationInverseConcentrations) {
          final int caseIndex = executed;
          final String concentrationUnit = '$amountUnit/mL';
          final _OracleFraction expectedVolume =
              _canonical(amountValue, amountUnit) /
              _canonical(concentrationValue, concentrationUnit);

          _expectSolution(
            id: 'preparation-inverse-volume-$caseIndex',
            inputs: <_InputFact>[
              _InputFact(QuantityKind.drugAmount, amountValue, amountUnit),
              _InputFact(
                QuantityKind.concentration,
                concentrationValue,
                concentrationUnit,
              ),
            ],
            expected: <_ExpectedFact>[
              _ExpectedFact(QuantityKind.solutionVolume, expectedVolume, 'mL'),
            ],
          );
          executed += 1;
        }
      }
    }
    expect(executed, matrix.categoryCounts['preparationInverseVolume']);
  });

  test('administration forward reference matrix', () {
    int executed = 0;
    for (final String amountUnit in matrix.amountUnits) {
      for (final String concentrationValue
          in matrix.administrationConcentrationValues) {
        for (final _ValueUnit flow in matrix.administrationFlows) {
          final int caseIndex = executed;
          final String concentrationUnit = '$amountUnit/mL';
          final _OracleFraction expectedRate =
              _canonical(concentrationValue, concentrationUnit) *
              _canonical(flow.value, flow.unit);
          final String outputAmountUnit = _presentationAmountUnit(
            amountUnit,
            caseIndex,
          );
          final String outputTime = caseIndex.isEven ? 'min' : 'h';

          _expectSolution(
            id: 'administration-forward-$caseIndex',
            inputs: <_InputFact>[
              _InputFact(
                QuantityKind.concentration,
                concentrationValue,
                concentrationUnit,
              ),
              _InputFact(QuantityKind.flowRate, flow.value, flow.unit),
            ],
            expected: <_ExpectedFact>[
              _ExpectedFact(
                QuantityKind.administrationRate,
                expectedRate,
                '$outputAmountUnit/$outputTime',
              ),
            ],
          );
          executed += 1;
        }
      }
    }
    expect(executed, matrix.categoryCounts['administrationForward']);
  });

  test('administration inverse flow reference matrix', () {
    int executed = 0;
    for (final String amountUnit in matrix.amountUnits) {
      for (final _ValueTime rate in matrix.administrationRates) {
        for (final String concentrationValue
            in matrix.administrationInverseConcentrations) {
          final int caseIndex = executed;
          final String rateUnit = '$amountUnit/${rate.time}';
          final String concentrationUnit = '$amountUnit/mL';
          final _OracleFraction expectedFlow =
              _canonical(rate.value, rateUnit) /
              _canonical(concentrationValue, concentrationUnit);
          final String outputUnit = caseIndex.isEven ? 'mL/h' : 'mL/min';

          _expectSolution(
            id: 'administration-inverse-flow-$caseIndex',
            inputs: <_InputFact>[
              _InputFact(QuantityKind.administrationRate, rate.value, rateUnit),
              _InputFact(
                QuantityKind.concentration,
                concentrationValue,
                concentrationUnit,
              ),
            ],
            expected: <_ExpectedFact>[
              _ExpectedFact(QuantityKind.flowRate, expectedFlow, outputUnit),
            ],
          );
          executed += 1;
        }
      }
    }
    expect(executed, matrix.categoryCounts['administrationInverseFlow']);
  });

  test('administration inverse concentration reference matrix', () {
    int executed = 0;
    for (final String amountUnit in matrix.amountUnits) {
      for (final _ValueTime rate in matrix.administrationRates) {
        for (final _ValueUnit flow in matrix.administrationInverseFlows) {
          final int caseIndex = executed;
          final String rateUnit = '$amountUnit/${rate.time}';
          final _OracleFraction expectedConcentration =
              _canonical(rate.value, rateUnit) /
              _canonical(flow.value, flow.unit);
          final String outputAmountUnit = _presentationAmountUnit(
            amountUnit,
            caseIndex,
          );

          _expectSolution(
            id: 'administration-inverse-concentration-$caseIndex',
            inputs: <_InputFact>[
              _InputFact(QuantityKind.administrationRate, rate.value, rateUnit),
              _InputFact(QuantityKind.flowRate, flow.value, flow.unit),
            ],
            expected: <_ExpectedFact>[
              _ExpectedFact(
                QuantityKind.concentration,
                expectedConcentration,
                '$outputAmountUnit/mL',
              ),
            ],
          );
          executed += 1;
        }
      }
    }
    expect(
      executed,
      matrix.categoryCounts['administrationInverseConcentration'],
    );
  });

  test('dose forward reference matrix', () {
    int executed = 0;
    for (final String amountUnit in matrix.amountUnits) {
      for (final _ValueTime rate in matrix.doseRates) {
        for (final _ValueUnit bodyMass in matrix.bodyMasses) {
          final int caseIndex = executed;
          final String rateUnit = '$amountUnit/${rate.time}';
          final _OracleFraction expectedDose =
              _canonical(rate.value, rateUnit) /
              _canonical(bodyMass.value, bodyMass.unit);
          final String outputAmountUnit = _presentationAmountUnit(
            amountUnit,
            caseIndex,
          );
          final String outputTime = caseIndex.isEven ? 'min' : 'h';

          _expectSolution(
            id: 'dose-forward-$caseIndex',
            inputs: <_InputFact>[
              _InputFact(QuantityKind.administrationRate, rate.value, rateUnit),
              _InputFact(QuantityKind.bodyMass, bodyMass.value, bodyMass.unit),
            ],
            expected: <_ExpectedFact>[
              _ExpectedFact(
                QuantityKind.weightNormalizedDose,
                expectedDose,
                '$outputAmountUnit/kg/$outputTime',
              ),
            ],
          );
          executed += 1;
        }
      }
    }
    expect(executed, matrix.categoryCounts['doseForward']);
  });

  test('dose inverse administration-rate reference matrix', () {
    int executed = 0;
    for (final String amountUnit in matrix.amountUnits) {
      for (final _ValueTime dose in matrix.doseValues) {
        for (final _ValueUnit bodyMass in matrix.inverseBodyMasses) {
          final int caseIndex = executed;
          final String doseUnit = '$amountUnit/kg/${dose.time}';
          final _OracleFraction expectedRate =
              _canonical(dose.value, doseUnit) *
              _canonical(bodyMass.value, bodyMass.unit);
          final String outputAmountUnit = _presentationAmountUnit(
            amountUnit,
            caseIndex,
          );
          final String outputTime = caseIndex.isEven ? 'min' : 'h';

          _expectSolution(
            id: 'dose-inverse-rate-$caseIndex',
            inputs: <_InputFact>[
              _InputFact(
                QuantityKind.weightNormalizedDose,
                dose.value,
                doseUnit,
              ),
              _InputFact(QuantityKind.bodyMass, bodyMass.value, bodyMass.unit),
            ],
            expected: <_ExpectedFact>[
              _ExpectedFact(
                QuantityKind.administrationRate,
                expectedRate,
                '$outputAmountUnit/$outputTime',
              ),
            ],
          );
          executed += 1;
        }
      }
    }
    expect(executed, matrix.categoryCounts['doseInverseRate']);
  });

  test('full-chain reference matrix', () {
    int executed = 0;
    for (final String amountUnit in matrix.amountUnits) {
      for (final String amountValue in matrix.fullChainAmountValues) {
        for (final String volumeValue in matrix.fullChainVolumes) {
          for (final _ValueUnit flow in matrix.fullChainFlows) {
            final int caseIndex = executed;
            final _ValueUnit bodyMass = matrix.fullChainBodyMass;
            final _OracleFraction amountCanonical = _canonical(
              amountValue,
              amountUnit,
            );
            final _OracleFraction volumeCanonical = _canonical(
              volumeValue,
              'mL',
            );
            final _OracleFraction flowCanonical = _canonical(
              flow.value,
              flow.unit,
            );
            final _OracleFraction concentrationCanonical =
                amountCanonical / volumeCanonical;
            final _OracleFraction rateCanonical =
                concentrationCanonical * flowCanonical;
            final _OracleFraction doseCanonical =
                rateCanonical / _canonical(bodyMass.value, bodyMass.unit);
            final _OracleFraction durationCanonical =
                volumeCanonical / flowCanonical;
            final String outputAmountUnit = _presentationAmountUnit(
              amountUnit,
              caseIndex,
            );
            final String outputTime = caseIndex.isEven ? 'min' : 'h';
            final String durationUnit = caseIndex.isEven ? 'h' : 'min';

            _expectSolution(
              id: 'full-chain-$caseIndex',
              inputs: <_InputFact>[
                _InputFact(QuantityKind.drugAmount, amountValue, amountUnit),
                _InputFact(QuantityKind.solutionVolume, volumeValue, 'mL'),
                _InputFact(QuantityKind.flowRate, flow.value, flow.unit),
                _InputFact(
                  QuantityKind.bodyMass,
                  bodyMass.value,
                  bodyMass.unit,
                ),
              ],
              expected: <_ExpectedFact>[
                _ExpectedFact(
                  QuantityKind.concentration,
                  concentrationCanonical,
                  '$outputAmountUnit/mL',
                ),
                _ExpectedFact(
                  QuantityKind.administrationRate,
                  rateCanonical,
                  '$outputAmountUnit/$outputTime',
                ),
                _ExpectedFact(
                  QuantityKind.weightNormalizedDose,
                  doseCanonical,
                  '$outputAmountUnit/kg/$outputTime',
                ),
                _ExpectedFact(
                  QuantityKind.infusionDuration,
                  durationCanonical,
                  durationUnit,
                ),
              ],
            );
            executed += 1;
          }
        }
      }
    }
    expect(executed, matrix.categoryCounts['fullChain']);
  });
}

final CalculatorSolver _solver = CalculatorSolver();

void _expectSolution({
  required String id,
  required List<_InputFact> inputs,
  required List<_ExpectedFact> expected,
}) {
  final List<SolverInput> solverInputs = <SolverInput>[
    for (int index = 0; index < inputs.length; index++)
      SolverInput(
        quantity: inputs[index].toQuantity(),
        editSequence: index + 1,
      ),
  ];
  final SolverSolution solution = _solver.solve(solverInputs);

  expect(solution.conflicts, isEmpty, reason: '$id produced a conflict');
  expect(solution.diagnostics, isEmpty, reason: '$id produced a diagnostic');

  for (final _ExpectedFact expectedFact in expected) {
    final SolverFact? fact = solution.fact(expectedFact.kind);
    expect(fact, isNotNull, reason: '$id did not derive ${expectedFact.kind}');
    expect(
      fact!.origin,
      SolverFactOrigin.calculated,
      reason: '$id returned ${expectedFact.kind} as an input',
    );

    final Quantity converted = fact.quantity.convertTo(
      UnitCatalog.find(expectedFact.unitCode),
    );
    final _OracleFraction expectedValue =
        expectedFact.canonicalValue / _unitFactor(expectedFact.unitCode);

    expect(
      converted.value.numerator,
      expectedValue.numerator,
      reason: '$id numerator in ${expectedFact.unitCode}',
    );
    expect(
      converted.value.denominator,
      expectedValue.denominator,
      reason: '$id denominator in ${expectedFact.unitCode}',
    );
  }
}

_OracleFraction _canonical(String value, String unitCode) =>
    _OracleFraction.parseDecimal(value) * _unitFactor(unitCode);

_OracleFraction _unitFactor(String unitCode) {
  final List<String> components = unitCode.split('/');
  _OracleFraction result = _primitiveFactor(components.first);
  for (final String denominator in components.skip(1)) {
    result = result / _primitiveFactor(denominator);
  }
  return result;
}

_OracleFraction _primitiveFactor(String code) => switch (code) {
  'ng' => _OracleFraction.fromInt(1),
  'ug' => _OracleFraction.fromInt(1000),
  'mg' => _OracleFraction.fromInt(1000000),
  'g' => _OracleFraction.fromInt(1000000000),
  'IU' => _OracleFraction.fromInt(1),
  'mL' => _OracleFraction.fromInt(1),
  'kg' => _OracleFraction.fromInt(1),
  'body_g' => _OracleFraction(BigInt.one, BigInt.from(1000)),
  'min' => _OracleFraction.fromInt(1),
  'h' => _OracleFraction.fromInt(60),
  _ => throw ArgumentError.value(code, 'code', 'Unknown oracle unit.'),
};

const List<String> _massAmountUnits = <String>['ng', 'ug', 'mg', 'g'];

String _presentationAmountUnit(String source, int index) {
  if (source == 'IU') {
    return 'IU';
  }
  final int sourceIndex = _massAmountUnits.indexOf(source);
  if (sourceIndex < 0) {
    throw ArgumentError.value(
      source,
      'source',
      'Unknown amount family for oracle presentation.',
    );
  }
  return _massAmountUnits[(sourceIndex + index + 1) % _massAmountUnits.length];
}

final class _InputFact {
  const _InputFact(this.kind, this.value, this.unitCode);

  final QuantityKind kind;
  final String value;
  final String unitCode;

  Quantity toQuantity() => Quantity.parse(
    kind: kind,
    source: value,
    unit: UnitCatalog.find(unitCode),
  );
}

final class _ExpectedFact {
  const _ExpectedFact(this.kind, this.canonicalValue, this.unitCode);

  final QuantityKind kind;
  final _OracleFraction canonicalValue;
  final String unitCode;
}

final class _ValueUnit {
  const _ValueUnit(this.value, this.unit);

  factory _ValueUnit.fromJson(Object? source) {
    final Map<String, dynamic> json = Map<String, dynamic>.from(
      source! as Map<dynamic, dynamic>,
    );
    return _ValueUnit(json['value']! as String, json['unit']! as String);
  }

  final String value;
  final String unit;
}

final class _ValueTime {
  const _ValueTime(this.value, this.time);

  factory _ValueTime.fromJson(Object? source) {
    final Map<String, dynamic> json = Map<String, dynamic>.from(
      source! as Map<dynamic, dynamic>,
    );
    return _ValueTime(json['value']! as String, json['time']! as String);
  }

  final String value;
  final String time;
}

final class _ReferenceMatrix {
  _ReferenceMatrix(this._root);

  factory _ReferenceMatrix.load() {
    final Object? decoded = jsonDecode(
      File('test/reference/technical_reference_matrix.json').readAsStringSync(),
    );
    return _ReferenceMatrix(
      Map<String, dynamic>.from(decoded! as Map<dynamic, dynamic>),
    );
  }

  final Map<String, dynamic> _root;

  int get schemaVersion => _root['schemaVersion']! as int;
  String get manualReviewStatus => _root['manualReviewStatus']! as String;
  int get expectedCaseCount => _root['expectedCaseCount']! as int;

  Map<String, int> get categoryCounts => <String, int>{
    for (final MapEntry<String, dynamic> entry in _map(
      'categoryCounts',
    ).entries)
      entry.key: entry.value! as int,
  };

  List<String> get amountUnits => _strings(_root, 'amountUnits');

  List<String> get preparationAmountValues =>
      _strings(_map('preparation'), 'amountValues');
  List<String> get preparationVolumes =>
      _strings(_map('preparation'), 'volumes');
  List<String> get preparationConcentrationValues =>
      _strings(_map('preparation'), 'concentrationValues');
  List<String> get preparationInverseVolumes =>
      _strings(_map('preparation'), 'inverseVolumes');
  List<String> get preparationInverseConcentrations =>
      _strings(_map('preparation'), 'inverseConcentrations');

  List<String> get administrationConcentrationValues =>
      _strings(_map('administration'), 'concentrationValues');
  List<_ValueUnit> get administrationFlows =>
      _valueUnits(_map('administration'), 'flows');
  List<_ValueTime> get administrationRates =>
      _valueTimes(_map('administration'), 'rates');
  List<String> get administrationInverseConcentrations =>
      _strings(_map('administration'), 'inverseConcentrations');
  List<_ValueUnit> get administrationInverseFlows =>
      _valueUnits(_map('administration'), 'inverseFlows');

  List<_ValueTime> get doseRates => _valueTimes(_map('dose'), 'rates');
  List<_ValueUnit> get bodyMasses => _valueUnits(_map('dose'), 'bodyMasses');
  List<_ValueTime> get doseValues => _valueTimes(_map('dose'), 'doses');
  List<_ValueUnit> get inverseBodyMasses =>
      _valueUnits(_map('dose'), 'inverseBodyMasses');

  List<String> get fullChainAmountValues =>
      _strings(_map('fullChain'), 'amountValues');
  List<String> get fullChainVolumes => _strings(_map('fullChain'), 'volumes');
  List<_ValueUnit> get fullChainFlows =>
      _valueUnits(_map('fullChain'), 'flows');
  _ValueUnit get fullChainBodyMass =>
      _ValueUnit.fromJson(_map('fullChain')['bodyMass']);

  Map<String, dynamic> _map(String key) =>
      Map<String, dynamic>.from(_root[key]! as Map<dynamic, dynamic>);

  static List<String> _strings(Map<String, dynamic> map, String key) =>
      List<String>.unmodifiable((map[key]! as List<dynamic>).cast<String>());

  static List<_ValueUnit> _valueUnits(Map<String, dynamic> map, String key) =>
      List<_ValueUnit>.unmodifiable(
        (map[key]! as List<dynamic>).map(_ValueUnit.fromJson),
      );

  static List<_ValueTime> _valueTimes(Map<String, dynamic> map, String key) =>
      List<_ValueTime>.unmodifiable(
        (map[key]! as List<dynamic>).map(_ValueTime.fromJson),
      );
}

final class _OracleFraction {
  _OracleFraction._(this.numerator, this.denominator);

  factory _OracleFraction(BigInt numerator, [BigInt? denominator]) {
    final BigInt resolvedDenominator = denominator ?? BigInt.one;
    if (resolvedDenominator == BigInt.zero) {
      throw ArgumentError.value(
        denominator,
        'denominator',
        'Oracle denominator cannot be zero.',
      );
    }
    if (numerator == BigInt.zero) {
      return _OracleFraction._(BigInt.zero, BigInt.one);
    }

    final bool denominatorIsNegative = resolvedDenominator.isNegative;
    final BigInt signedNumerator = denominatorIsNegative
        ? -numerator
        : numerator;
    final BigInt positiveDenominator = resolvedDenominator.abs();
    final BigInt divisor = signedNumerator.abs().gcd(positiveDenominator);

    return _OracleFraction._(
      signedNumerator ~/ divisor,
      positiveDenominator ~/ divisor,
    );
  }

  factory _OracleFraction.fromInt(int value) =>
      _OracleFraction(BigInt.from(value));

  factory _OracleFraction.parseDecimal(String source) {
    final String normalized = source.trim();
    final bool negative = normalized.startsWith('-');
    final String unsigned = negative || normalized.startsWith('+')
        ? normalized.substring(1)
        : normalized;
    final List<String> parts = unsigned.split('.');
    if (parts.length > 2 ||
        parts.first.isEmpty ||
        (parts.length == 2 && parts.last.isEmpty)) {
      throw ArgumentError.value(
        source,
        'source',
        'Unsupported oracle decimal.',
      );
    }

    if (parts.length == 1) {
      final BigInt value = BigInt.parse(parts.first);
      return _OracleFraction(negative ? -value : value);
    }

    final BigInt denominator = BigInt.from(10).pow(parts.last.length);
    final BigInt numerator =
        BigInt.parse(parts.first) * denominator + BigInt.parse(parts.last);
    return _OracleFraction(negative ? -numerator : numerator, denominator);
  }

  final BigInt numerator;
  final BigInt denominator;

  _OracleFraction operator *(_OracleFraction other) => _OracleFraction(
    numerator * other.numerator,
    denominator * other.denominator,
  );

  _OracleFraction operator /(_OracleFraction other) {
    if (other.numerator == BigInt.zero) {
      throw ArgumentError.value(other, 'other', 'Oracle division by zero.');
    }
    return _OracleFraction(
      numerator * other.denominator,
      denominator * other.numerator,
    );
  }

  @override
  String toString() => denominator == BigInt.one
      ? numerator.toString()
      : '$numerator/$denominator';
}
