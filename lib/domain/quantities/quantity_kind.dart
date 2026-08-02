import 'package:kalkulator_lekow/domain/units/unit_definition.dart';
import 'package:kalkulator_lekow/domain/units/unit_dimension.dart';

const UnitDimension _medicineAmountDimension = UnitDimension(
  medicineMassExponent: 1,
);
const UnitDimension _biologicalActivityDimension = UnitDimension(
  biologicalActivityExponent: 1,
);
const UnitDimension _volumeDimension = UnitDimension(volumeExponent: 1);
const UnitDimension _bodyMassDimension = UnitDimension(bodyMassExponent: 1);
const UnitDimension _timeDimension = UnitDimension(timeExponent: 1);
const UnitDimension _medicineConcentrationDimension = UnitDimension(
  medicineMassExponent: 1,
  volumeExponent: -1,
);
const UnitDimension _activityConcentrationDimension = UnitDimension(
  biologicalActivityExponent: 1,
  volumeExponent: -1,
);
const UnitDimension _flowRateDimension = UnitDimension(
  volumeExponent: 1,
  timeExponent: -1,
);
const UnitDimension _medicineAdministrationRateDimension = UnitDimension(
  medicineMassExponent: 1,
  timeExponent: -1,
);
const UnitDimension _activityAdministrationRateDimension = UnitDimension(
  biologicalActivityExponent: 1,
  timeExponent: -1,
);
const UnitDimension _medicineWeightNormalizedDoseDimension = UnitDimension(
  medicineMassExponent: 1,
  bodyMassExponent: -1,
  timeExponent: -1,
);
const UnitDimension _activityWeightNormalizedDoseDimension = UnitDimension(
  biologicalActivityExponent: 1,
  bodyMassExponent: -1,
  timeExponent: -1,
);

/// Semantic quantities represented by fields and calculation results.
enum QuantityKind {
  /// Amount of medicine, expressed either as substance mass or IU.
  drugAmount,

  /// Final volume of the prepared solution.
  solutionVolume,

  /// Patient body mass; input only at application level.
  bodyMass,

  /// General time value.
  time,

  /// Amount of medicine per solution volume.
  concentration,

  /// Solution volume per time.
  flowRate,

  /// Amount of medicine per time, without body-mass normalization.
  administrationRate,

  /// Amount of medicine per body mass per time.
  weightNormalizedDose,

  /// Calculated duration of an infusion.
  infusionDuration,
}

/// Dimension constraints for each semantic quantity.
extension QuantityKindDimension on QuantityKind {
  /// Whether [unit] can represent this quantity.
  bool accepts(MeasurementUnit unit) => acceptsDimension(unit.dimension);

  /// Whether [dimension] can represent this quantity.
  bool acceptsDimension(UnitDimension dimension) => switch (this) {
    QuantityKind.drugAmount =>
      dimension == _medicineAmountDimension ||
          dimension == _biologicalActivityDimension,
    QuantityKind.solutionVolume => dimension == _volumeDimension,
    QuantityKind.bodyMass => dimension == _bodyMassDimension,
    QuantityKind.time => dimension == _timeDimension,
    QuantityKind.concentration =>
      dimension == _medicineConcentrationDimension ||
          dimension == _activityConcentrationDimension,
    QuantityKind.flowRate => dimension == _flowRateDimension,
    QuantityKind.administrationRate =>
      dimension == _medicineAdministrationRateDimension ||
          dimension == _activityAdministrationRateDimension,
    QuantityKind.weightNormalizedDose =>
      dimension == _medicineWeightNormalizedDoseDimension ||
          dimension == _activityWeightNormalizedDoseDimension,
    QuantityKind.infusionDuration => dimension == _timeDimension,
  };
}
