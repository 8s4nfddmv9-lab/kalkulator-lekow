import 'package:kalkulator_lekow/domain/calculations/calculation_trace.dart';
import 'package:kalkulator_lekow/domain/errors/domain_exception.dart';
import 'package:kalkulator_lekow/domain/math/rational.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity.dart';
import 'package:kalkulator_lekow/domain/quantities/quantity_kind.dart';

/// Provenance of a fact available to the dynamic solver.
enum SolverFactOrigin {
  /// Value explicitly supplied by the user.
  userInput,

  /// Value derived by one registered equation.
  calculated,
}

/// One explicit user input with a monotonically increasing edit sequence.
final class SolverInput {
  /// Creates a solver input.
  const SolverInput({required this.quantity, required this.editSequence});

  /// Exact user-supplied quantity.
  final Quantity quantity;

  /// Monotonic sequence assigned by the application layer.
  final int editSequence;
}

/// A usable value known by the solver, together with complete provenance.
final class SolverFact {
  SolverFact._({
    required this.quantity,
    required this.origin,
    required this.latestEditSequence,
    required Set<QuantityKind> rootInputKinds,
    required Set<QuantityKind> pathKinds,
    this.trace,
  }) : rootInputKinds = Set<QuantityKind>.unmodifiable(rootInputKinds),
       pathKinds = Set<QuantityKind>.unmodifiable(pathKinds);

  /// Creates a root user fact.
  factory SolverFact.userInput(SolverInput input) => SolverFact._(
    quantity: input.quantity,
    origin: SolverFactOrigin.userInput,
    latestEditSequence: input.editSequence,
    rootInputKinds: <QuantityKind>{input.quantity.kind},
    pathKinds: <QuantityKind>{input.quantity.kind},
  );

  /// Creates a calculated fact from exact source facts and a calculation.
  factory SolverFact.calculated({
    required CalculationResult result,
    required List<SolverFact> sources,
  }) {
    final Set<QuantityKind> rootInputKinds = <QuantityKind>{};
    final Set<QuantityKind> pathKinds = <QuantityKind>{result.quantity.kind};
    int latestEditSequence = 0;

    for (final SolverFact source in sources) {
      rootInputKinds.addAll(source.rootInputKinds);
      pathKinds.addAll(source.pathKinds);
      if (source.latestEditSequence > latestEditSequence) {
        latestEditSequence = source.latestEditSequence;
      }
    }

    return SolverFact._(
      quantity: result.quantity,
      origin: SolverFactOrigin.calculated,
      latestEditSequence: latestEditSequence,
      rootInputKinds: rootInputKinds,
      pathKinds: pathKinds,
      trace: result.trace,
    );
  }

  /// Exact value represented by this fact.
  final Quantity quantity;

  /// Whether the value is user-provided or calculated.
  final SolverFactOrigin origin;

  /// Highest user-edit sequence among all root inputs of this fact.
  final int latestEditSequence;

  /// User-input quantity kinds that ultimately support this fact.
  final Set<QuantityKind> rootInputKinds;

  /// Every quantity kind traversed by the selected derivation path.
  final Set<QuantityKind> pathKinds;

  /// Derivation trace for calculated facts; absent for user inputs.
  final CalculationTrace? trace;
}

/// Source of a detected disagreement.
enum SolverConflictKind {
  /// A derived expectation differs from an explicit user input.
  userInputMismatch,

  /// Two independent derivation paths produce different values.
  derivedPathMismatch,
}

/// Exact description of a conflict that the solver refuses to resolve silently.
final class SolverConflict {
  /// Creates a solver conflict.
  SolverConflict({
    required this.kind,
    required this.existingFact,
    required this.candidateResult,
    required this.candidateInExistingUnit,
    required this.relativeDifference,
    required Set<QuantityKind> involvedUserInputs,
  }) : involvedUserInputs = Set<QuantityKind>.unmodifiable(involvedUserInputs),
       conflictKind = existingFact.origin == SolverFactOrigin.userInput
           ? SolverConflictKind.userInputMismatch
           : SolverConflictKind.derivedPathMismatch;

  /// Semantic quantity kind whose value is ambiguous.
  final QuantityKind kind;

  /// Value already selected before the conflicting path was evaluated.
  final SolverFact existingFact;

  /// Newly derived, incompatible candidate and its trace.
  final CalculationResult candidateResult;

  /// Candidate converted to the unit of [existingFact] for presentation.
  final Quantity candidateInExistingUnit;

  /// Exact relative difference between canonical values.
  final Rational relativeDifference;

  /// Root user inputs participating in either conflicting path.
  final Set<QuantityKind> involvedUserInputs;

  /// Whether the conflict challenges a user value or another derivation.
  final SolverConflictKind conflictKind;
}

/// A controlled equation failure that must be presented instead of thrown.
final class SolverDiagnostic {
  /// Creates a diagnostic for one equation evaluation.
  SolverDiagnostic({
    required this.equationId,
    required this.error,
    required Set<QuantityKind> involvedUserInputs,
  }) : involvedUserInputs = Set<QuantityKind>.unmodifiable(
         involvedUserInputs,
       );

  /// Stable identifier of the equation that could not be evaluated.
  final EquationId equationId;

  /// Typed domain failure, for example zero denominator or unit mismatch.
  final DomainException error;

  /// Root user inputs participating in the failed evaluation.
  final Set<QuantityKind> involvedUserInputs;
}

/// Immutable result of one complete fixed-point solver run.
final class SolverSolution {
  /// Creates a solver solution.
  SolverSolution({
    required Map<QuantityKind, SolverFact> userInputs,
    required Map<QuantityKind, SolverFact> facts,
    required Map<QuantityKind, SolverConflict> conflicts,
    List<SolverDiagnostic> diagnostics = const <SolverDiagnostic>[],
  }) : userInputs = Map<QuantityKind, SolverFact>.unmodifiable(userInputs),
       facts = Map<QuantityKind, SolverFact>.unmodifiable(facts),
       conflicts = Map<QuantityKind, SolverConflict>.unmodifiable(conflicts),
       diagnostics = List<SolverDiagnostic>.unmodifiable(diagnostics);

  /// Explicit inputs preserved exactly as supplied by the user.
  final Map<QuantityKind, SolverFact> userInputs;

  /// Usable, non-conflicted user and calculated facts.
  final Map<QuantityKind, SolverFact> facts;

  /// Conflicts keyed by the ambiguous target quantity kind.
  final Map<QuantityKind, SolverConflict> conflicts;

  /// Controlled equation failures collected during solving.
  final List<SolverDiagnostic> diagnostics;

  /// Returns a usable fact, or `null` when unknown or conflicted.
  SolverFact? fact(QuantityKind kind) => facts[kind];

  /// Whether [kind] is currently blocked by conflicting information.
  bool hasConflict(QuantityKind kind) => conflicts.containsKey(kind);

  /// Whether any value is conflicted or an equation produced a diagnostic.
  bool get hasProblems => conflicts.isNotEmpty || diagnostics.isNotEmpty;

  /// Calculated facts only, preserving deterministic map order.
  Iterable<SolverFact> get calculatedFacts => facts.values.where(
    (SolverFact fact) => fact.origin == SolverFactOrigin.calculated,
  );
}
