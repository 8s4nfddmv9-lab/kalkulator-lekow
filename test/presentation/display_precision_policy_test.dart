import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/presentation/formatting/rational_decimal_formatter.dart';

void main() {
  final _PrecisionManifest manifest = _PrecisionManifest.load();

  test('display precision manifest declares the audited policy', () {
    expect(manifest.schemaVersion, 1);
    expect(manifest.policyVersion, '0.1.2-dev.2');
    expect(manifest.roundingMode, 'half-up');
    expect(manifest.decimalSeparator, ',');
    expect(manifest.scientificNotation, 'normalized lowercase e');
    expect(manifest.manualSecondPersonReview, 'pending');
    expect(manifest.cases, hasLength(manifest.caseCount));
  });

  test('every audited display case matches its independent expected text', () {
    for (final _PrecisionCase precisionCase in manifest.cases) {
      final String actual = RationalDecimalFormatter.format(
        Rational(precisionCase.numerator, precisionCase.denominator),
        significantDigits: precisionCase.significantDigits,
        maxFractionDigits: precisionCase.maxFractionDigits,
      );

      expect(actual, precisionCase.expected, reason: precisionCase.id);
    }
  });

  test('scientific notation is normalized after rounding carry', () {
    final RegExp normalizedScientific = RegExp(
      r'^-?[1-9](?:,[0-9]+)?e[+-]?[0-9]+$',
    );

    for (final _PrecisionCase precisionCase in manifest.cases.where(
      (_PrecisionCase candidate) => candidate.expected.contains('e'),
    )) {
      expect(
        normalizedScientific.hasMatch(precisionCase.expected),
        isTrue,
        reason: '${precisionCase.id}: ${precisionCase.expected}',
      );
      expect(
        precisionCase.expected,
        isNot(startsWith('10e')),
        reason: precisionCase.id,
      );
      expect(
        precisionCase.expected,
        isNot(startsWith('-10e')),
        reason: precisionCase.id,
      );
    }
  });

  test('display text never omits the zero before a decimal separator', () {
    for (final _PrecisionCase precisionCase in manifest.cases) {
      final String unsigned = precisionCase.expected.startsWith('-')
          ? precisionCase.expected.substring(1)
          : precisionCase.expected;
      expect(unsigned, isNot(startsWith(',')), reason: precisionCase.id);
    }
  });

  test('nonzero audited values are never displayed as zero', () {
    for (final _PrecisionCase precisionCase in manifest.cases.where(
      (_PrecisionCase candidate) => candidate.numerator != BigInt.zero,
    )) {
      expect(precisionCase.expected, isNot('0'), reason: precisionCase.id);
      expect(precisionCase.expected, isNot('-0'), reason: precisionCase.id);
    }
  });
}

final class _PrecisionManifest {
  _PrecisionManifest(this._json);

  factory _PrecisionManifest.load() {
    final Object? source = jsonDecode(
      File('test/reference/display_precision_cases.json').readAsStringSync(),
    );
    return _PrecisionManifest(
      Map<String, dynamic>.from(source! as Map<dynamic, dynamic>),
    );
  }

  final Map<String, dynamic> _json;

  int get schemaVersion => _json['schemaVersion']! as int;
  String get policyVersion => _json['policyVersion']! as String;
  String get roundingMode => _json['roundingMode']! as String;
  String get decimalSeparator => _json['decimalSeparator']! as String;
  String get scientificNotation => _json['scientificNotation']! as String;
  String get manualSecondPersonReview =>
      _json['manualSecondPersonReview']! as String;
  int get caseCount => _json['caseCount']! as int;

  List<_PrecisionCase> get cases => List<_PrecisionCase>.unmodifiable(
    (_json['cases']! as List<dynamic>).map(_PrecisionCase.fromJson),
  );
}

final class _PrecisionCase {
  const _PrecisionCase({
    required this.id,
    required this.numerator,
    required this.denominator,
    required this.significantDigits,
    required this.maxFractionDigits,
    required this.expected,
  });

  factory _PrecisionCase.fromJson(Object? source) {
    final Map<String, dynamic> json = Map<String, dynamic>.from(
      source! as Map<dynamic, dynamic>,
    );
    return _PrecisionCase(
      id: json['id']! as String,
      numerator: BigInt.parse(json['numerator']! as String),
      denominator: BigInt.parse(json['denominator']! as String),
      significantDigits: json['significantDigits']! as int,
      maxFractionDigits: json['maxFractionDigits']! as int,
      expected: json['expected']! as String,
    );
  }

  final String id;
  final BigInt numerator;
  final BigInt denominator;
  final int significantDigits;
  final int maxFractionDigits;
  final String expected;
}
