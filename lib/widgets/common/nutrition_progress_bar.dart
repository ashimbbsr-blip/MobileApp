import 'package:flutter/material.dart';

class NutritionProgressBar extends StatelessWidget {
  final String label;
  final double current;
  final double goal;
  final Color color;
  final String unit;
  final bool showValues;

  const NutritionProgressBar({
    super.key,
    required this.label,
    required this.current,
    required this.goal,
    required this.color,
    this.unit = 'g',
    this.showValues = true,
  });

  @override
  Widget build(BuildContext context) {
    final progress = goal > 0 ? (current / goal).clamp(0.0, 1.0) : 0.0;
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (showValues)
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500)),
              Text(
                '${current.toStringAsFixed(1)}$unit / ${goal.toStringAsFixed(0)}$unit',
                style: theme.textTheme.bodySmall?.copyWith(color: color),
              ),
            ],
          ),
        if (showValues) const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: progress,
            backgroundColor: color.withValues(alpha:0.15),
            valueColor: AlwaysStoppedAnimation<Color>(
              progress >= 1.0 ? Colors.red.shade400 : color,
            ),
            minHeight: 8,
          ),
        ),
      ],
    );
  }
}
