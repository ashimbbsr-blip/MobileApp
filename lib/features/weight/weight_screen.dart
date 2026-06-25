import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../models/weight_entry.dart';
import '../../services/nutrition_calculator.dart';
import '../../theme/app_colors.dart';
import 'providers/weight_provider.dart';

/// Weight Tracker — quick weight logging plus weight & BMI history.
///
/// Populates the [WeightEntry] history that feeds the long-term trend, the
/// yearly weight-change figure, and the Weight/Health sheets in exports.
class WeightScreen extends ConsumerStatefulWidget {
  const WeightScreen({super.key});

  @override
  ConsumerState<WeightScreen> createState() => _WeightScreenState();
}

class _WeightScreenState extends ConsumerState<WeightScreen> {
  final _ctrl = TextEditingController();

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Future<void> _log() async {
    final kg = double.tryParse(_ctrl.text.trim());
    if (kg == null) {
      _toast('Enter a valid weight', false);
      return;
    }
    final ok = await ref.read(weightProvider.notifier).logWeight(kg);
    if (!mounted) return;
    if (ok) {
      _ctrl.clear();
      FocusScope.of(context).unfocus();
      _toast('Weight logged', true);
    } else {
      _toast('Weight must be between 1 and 600 kg', false);
    }
  }

  void _toast(String msg, bool ok) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(msg),
      backgroundColor: ok ? AppColors.primary : Colors.red,
    ));
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(weightProvider);
    final theme = Theme.of(context);
    final history = state.history.reversed.toList(); // newest first for the list
    final latest = state.latest;

    return Scaffold(
      appBar: AppBar(title: const Text('Weight Tracker')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // ── Summary ───────────────────────────────────────────────────────
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: _Metric(
                      label: 'Current',
                      value: latest != null
                          ? '${latest.weightKg.toStringAsFixed(1)} kg'
                          : '—',
                      color: AppColors.primary,
                    ),
                  ),
                  Expanded(
                    child: _Metric(
                      label: 'BMI',
                      value: latest != null ? latest.bmi.toStringAsFixed(1) : '—',
                      sub: latest != null
                          ? NutritionCalculator.bmiCategory(latest.bmi)
                          : null,
                      color: AppColors.secondary,
                    ),
                  ),
                  Expanded(
                    child: _Metric(
                      label: 'Change',
                      value: state.history.length >= 2
                          ? '${state.netChange >= 0 ? '+' : ''}${state.netChange.toStringAsFixed(1)} kg'
                          : '—',
                      color: state.netChange > 0
                          ? AppColors.calories
                          : AppColors.primary,
                    ),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // ── Quick log ─────────────────────────────────────────────────────
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _ctrl,
                      keyboardType:
                          const TextInputType.numberWithOptions(decimal: true),
                      inputFormatters: [
                        FilteringTextInputFormatter.allow(RegExp(r'[0-9.]')),
                      ],
                      decoration: InputDecoration(
                        labelText: 'Log today\'s weight',
                        suffixText: 'kg',
                        prefixIcon: const Icon(Icons.monitor_weight_outlined),
                        border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(10)),
                      ),
                      onSubmitted: (_) => _log(),
                    ),
                  ),
                  const SizedBox(width: 12),
                  FilledButton(
                    onPressed: state.saving ? null : _log,
                    style: FilledButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 20, vertical: 16),
                    ),
                    child: const Text('Log'),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // ── Trend ─────────────────────────────────────────────────────────
          if (state.history.length >= 2) ...[
            Card(
              child: Padding(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Trend',
                        style: theme.textTheme.titleSmall
                            ?.copyWith(fontWeight: FontWeight.w700)),
                    const SizedBox(height: 12),
                    SizedBox(
                      height: 120,
                      width: double.infinity,
                      child: CustomPaint(
                        painter: _SparklinePainter(
                          values: state.history.map((e) => e.weightKg).toList(),
                          color: AppColors.primary,
                          gridColor:
                              theme.colorScheme.onSurface.withValues(alpha: 0.08),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
          ],

          // ── History ───────────────────────────────────────────────────────
          Text('History',
              style:
                  theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          if (history.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 24),
              child: Center(child: Text('No weight entries yet. Log your first above.')),
            )
          else
            ...history.map((e) => _HistoryTile(
                  entry: e,
                  onDelete: () =>
                      ref.read(weightProvider.notifier).deleteEntry(e.dateKey),
                )),
          const SizedBox(height: 40),
        ],
      ),
    );
  }
}

class _Metric extends StatelessWidget {
  final String label;
  final String value;
  final String? sub;
  final Color color;
  const _Metric({required this.label, required this.value, this.sub, required this.color});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Column(
      children: [
        Text(label, style: theme.textTheme.bodySmall),
        const SizedBox(height: 4),
        Text(value,
            style: theme.textTheme.titleMedium
                ?.copyWith(fontWeight: FontWeight.w800, color: color)),
        if (sub != null)
          Text(sub!, style: theme.textTheme.bodySmall?.copyWith(color: color)),
      ],
    );
  }
}

class _HistoryTile extends StatelessWidget {
  final WeightEntry entry;
  final VoidCallback onDelete;
  const _HistoryTile({required this.entry, required this.onDelete});

  @override
  Widget build(BuildContext context) {
    final d = entry.recordedAt;
    final dateStr =
        '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: const Icon(Icons.monitor_weight_outlined, color: AppColors.primary),
        title: Text('${entry.weightKg.toStringAsFixed(1)} kg',
            style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text('$dateStr · BMI ${entry.bmi.toStringAsFixed(1)}'),
        trailing: IconButton(
          icon: const Icon(Icons.delete_outline, size: 20),
          onPressed: () async {
            final ctx = context;
            final confirmed = await showDialog<bool>(
              context: ctx,
              builder: (dlgCtx) => AlertDialog(
                title: const Text('Delete entry?'),
                content: Text(
                    'Remove weight entry for $dateStr?'),
                actions: [
                  TextButton(
                      onPressed: () => Navigator.pop(dlgCtx, false),
                      child: const Text('Cancel')),
                  FilledButton(
                    onPressed: () => Navigator.pop(dlgCtx, true),
                    style:
                        FilledButton.styleFrom(backgroundColor: Colors.red),
                    child: const Text('Delete'),
                  ),
                ],
              ),
            );
            if (confirmed == true) onDelete();
          },
        ),
      ),
    );
  }
}

/// Minimal dependency-free line chart for the weight trend.
class _SparklinePainter extends CustomPainter {
  final List<double> values;
  final Color color;
  final Color gridColor;
  _SparklinePainter({required this.values, required this.color, required this.gridColor});

  @override
  void paint(Canvas canvas, Size size) {
    if (values.length < 2) return;
    final minV = values.reduce((a, b) => a < b ? a : b);
    final maxV = values.reduce((a, b) => a > b ? a : b);
    final range = (maxV - minV).abs() < 0.001 ? 1.0 : (maxV - minV);

    // Baseline grid.
    final grid = Paint()
      ..color = gridColor
      ..strokeWidth = 1;
    for (int i = 0; i <= 3; i++) {
      final y = size.height * i / 3;
      canvas.drawLine(Offset(0, y), Offset(size.width, y), grid);
    }

    Offset pointAt(int i) {
      final x = size.width * i / (values.length - 1);
      final y = size.height - ((values[i] - minV) / range) * size.height;
      return Offset(x, y.clamp(0, size.height));
    }

    // Filled area.
    final path = Path()..moveTo(0, size.height);
    for (int i = 0; i < values.length; i++) {
      final p = pointAt(i);
      if (i == 0) {
        path.lineTo(p.dx, p.dy);
      } else {
        path.lineTo(p.dx, p.dy);
      }
    }
    path.lineTo(size.width, size.height);
    path.close();
    canvas.drawPath(
      path,
      Paint()..color = color.withValues(alpha: 0.12),
    );

    // Line.
    final line = Paint()
      ..color = color
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke
      ..strokeJoin = StrokeJoin.round;
    final linePath = Path()..moveTo(pointAt(0).dx, pointAt(0).dy);
    for (int i = 1; i < values.length; i++) {
      linePath.lineTo(pointAt(i).dx, pointAt(i).dy);
    }
    canvas.drawPath(linePath, line);

    // Dots.
    final dot = Paint()..color = color;
    for (int i = 0; i < values.length; i++) {
      canvas.drawCircle(pointAt(i), 3, dot);
    }
  }

  @override
  bool shouldRepaint(covariant _SparklinePainter old) {
    if (old.color != color || old.gridColor != gridColor) return true;
    if (old.values.length != values.length) return true;
    for (var i = 0; i < values.length; i++) {
      if (old.values[i] != values[i]) return true;
    }
    return false;
  }
}
