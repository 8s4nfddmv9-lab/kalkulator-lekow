import 'package:flutter/material.dart';
import 'package:kalkulator_lekow/presentation/calculator/widgets/calculation_field.dart';

/// Initial single-screen shell for the infusion calculator.
///
/// This milestone intentionally contains no clinical calculations. It validates
/// the information architecture and unit-selection interactions before the
/// dynamic solver is connected.
class CalculatorScreen extends StatefulWidget {
  /// Creates the calculator screen.
  const CalculatorScreen({super.key});

  @override
  State<CalculatorScreen> createState() => _CalculatorScreenState();
}

class _CalculatorScreenState extends State<CalculatorScreen> {
  final TextEditingController _bodyMassController = TextEditingController();
  final TextEditingController _amountController = TextEditingController();
  final TextEditingController _volumeController = TextEditingController();
  final TextEditingController _concentrationController =
      TextEditingController();
  final TextEditingController _flowController = TextEditingController();
  final TextEditingController _doseController = TextEditingController();

  String _bodyMassUnit = 'kg';
  String _amountUnit = 'mg';
  String _concentrationUnit = 'µg/ml';
  String _doseAmountUnit = 'µg';
  String _doseTimeUnit = 'min';
  bool _dosePerKilogram = true;

  @override
  void dispose() {
    _bodyMassController.dispose();
    _amountController.dispose();
    _volumeController.dispose();
    _concentrationController.dispose();
    _flowController.dispose();
    _doseController.dispose();
    super.dispose();
  }

  void _clearAll() {
    for (final TextEditingController controller in <TextEditingController>[
      _bodyMassController,
      _amountController,
      _volumeController,
      _concentrationController,
      _flowController,
      _doseController,
    ]) {
      controller.clear();
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('Kalkulator leków'),
      actions: <Widget>[
        IconButton(
          tooltip: 'Wyczyść',
          onPressed: _clearAll,
          icon: const Icon(Icons.delete_outline),
        ),
      ],
    ),
    body: SafeArea(
      child: ListView(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 32),
        children: <Widget>[
          _PrototypeWarning(),
          const SizedBox(height: 20),
          const _SectionHeading(
            title: 'Pacjent',
            subtitle:
                'Masa pozostaje wyłącznie daną wpisywaną przez użytkownika.',
          ),
          CalculationField(
            label: 'Masa pacjenta',
            controller: _bodyMassController,
            units: const <String>['kg', 'g'],
            selectedUnit: _bodyMassUnit,
            onUnitChanged: (String unit) {
              setState(() => _bodyMassUnit = unit);
            },
          ),
          const _SectionHeading(
            title: 'Roztwór',
            subtitle: 'Dowolne dwa parametry docelowo wyznaczą trzeci.',
          ),
          CalculationField(
            label: 'Ilość leku',
            controller: _amountController,
            units: const <String>['ng', 'µg', 'mg', 'g', 'IU'],
            selectedUnit: _amountUnit,
            onUnitChanged: (String unit) {
              setState(() => _amountUnit = unit);
            },
          ),
          CalculationField(
            label: 'Objętość roztworu',
            controller: _volumeController,
            units: const <String>['ml'],
            selectedUnit: 'ml',
            onUnitChanged: (_) {},
          ),
          CalculationField(
            label: 'Stężenie',
            controller: _concentrationController,
            units: const <String>['ng/ml', 'µg/ml', 'mg/ml', 'g/ml', 'IU/ml'],
            selectedUnit: _concentrationUnit,
            onUnitChanged: (String unit) {
              setState(() => _concentrationUnit = unit);
            },
          ),
          const _SectionHeading(
            title: 'Podawanie',
            subtitle: 'Przepływ i dawka będą przeliczane dwukierunkowo.',
          ),
          CalculationField(
            label: 'Przepływ',
            controller: _flowController,
            units: const <String>['ml/h'],
            selectedUnit: 'ml/h',
            onUnitChanged: (_) {},
          ),
          _DoseField(
            controller: _doseController,
            amountUnit: _doseAmountUnit,
            timeUnit: _doseTimeUnit,
            perKilogram: _dosePerKilogram,
            onAmountUnitChanged: (String unit) {
              setState(() => _doseAmountUnit = unit);
            },
            onTimeUnitChanged: (String unit) {
              setState(() => _doseTimeUnit = unit);
            },
            onPerKilogramChanged: (bool enabled) {
              setState(() => _dosePerKilogram = enabled);
            },
          ),
          const SizedBox(height: 8),
          FilledButton.tonalIcon(
            onPressed: null,
            icon: const Icon(Icons.calculate_outlined),
            label: const Text(
              'Silnik obliczeniowy zostanie podłączony w kolejnych etapach',
            ),
          ),
        ],
      ),
    ),
  );
}

class _PrototypeWarning extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Semantics(
    label: 'Ostrzeżenie: prototyp nie jest przeznaczony do użycia klinicznego.',
    child: Card(
      color: Theme.of(context).colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            Icon(
              Icons.warning_amber_rounded,
              color: Theme.of(context).colorScheme.onErrorContainer,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'Prototyp — nie używać do podejmowania decyzji klinicznych.',
                style: TextStyle(
                  color: Theme.of(context).colorScheme.onErrorContainer,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

class _SectionHeading extends StatelessWidget {
  const _SectionHeading({required this.title, required this.subtitle});

  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(top: 4, bottom: 12),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(title, style: Theme.of(context).textTheme.headlineSmall),
        const SizedBox(height: 4),
        Text(subtitle, style: Theme.of(context).textTheme.bodyMedium),
      ],
    ),
  );
}

class _DoseField extends StatelessWidget {
  const _DoseField({
    required this.controller,
    required this.amountUnit,
    required this.timeUnit,
    required this.perKilogram,
    required this.onAmountUnitChanged,
    required this.onTimeUnitChanged,
    required this.onPerKilogramChanged,
  });

  final TextEditingController controller;
  final String amountUnit;
  final String timeUnit;
  final bool perKilogram;
  final ValueChanged<String> onAmountUnitChanged;
  final ValueChanged<String> onTimeUnitChanged;
  final ValueChanged<bool> onPerKilogramChanged;

  String get _composedUnit =>
      '$amountUnit${perKilogram ? '/kg' : ''}/$timeUnit';

  @override
  Widget build(BuildContext context) => Card(
    margin: const EdgeInsets.only(bottom: 12),
    child: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            children: <Widget>[
              Expanded(
                child: Text(
                  'Dawka / szybkość podaży',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ),
              Text(
                _composedUnit,
                key: const Key('dose-unit-preview'),
                style: Theme.of(context).textTheme.labelLarge,
              ),
            ],
          ),
          const SizedBox(height: 12),
          TextField(
            controller: controller,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: const InputDecoration(hintText: 'Wpisz wartość'),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            crossAxisAlignment: WrapCrossAlignment.center,
            children: <Widget>[
              SizedBox(
                width: 112,
                child: DropdownButtonFormField<String>(
                  initialValue: amountUnit,
                  decoration: const InputDecoration(labelText: 'Ilość'),
                  items: const <String>['ng', 'µg', 'mg', 'g', 'IU']
                      .map(
                        (String unit) => DropdownMenuItem<String>(
                          value: unit,
                          child: Text(unit),
                        ),
                      )
                      .toList(growable: false),
                  onChanged: (String? unit) {
                    if (unit != null) {
                      onAmountUnitChanged(unit);
                    }
                  },
                ),
              ),
              FilterChip(
                key: const Key('per-kilogram-toggle'),
                label: const Text('/kg'),
                selected: perKilogram,
                onSelected: onPerKilogramChanged,
              ),
              SegmentedButton<String>(
                segments: const <ButtonSegment<String>>[
                  ButtonSegment<String>(value: 'min', label: Text('/min')),
                  ButtonSegment<String>(value: 'h', label: Text('/h')),
                ],
                selected: <String>{timeUnit},
                onSelectionChanged: (Set<String> selection) {
                  onTimeUnitChanged(selection.single);
                },
              ),
            ],
          ),
        ],
      ),
    ),
  );
}
