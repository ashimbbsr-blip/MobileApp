import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../theme/app_colors.dart';

class MacroRingChart extends StatelessWidget {
  final double calories;
  final double calorieGoal;
  final double protein;
  final double carbs;
  final double fat;

  const MacroRingChart({
    super.key,
    required this.calories,
    required this.calorieGoal,
    required this.protein,
    required this.carbs,
    required this.fat,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final remaining = (calorieGoal - calories).clamp(0.0, calorieGoal);
    final total = protein + carbs + fat;

    return SizedBox(
      width: 180,
      height: 180,
      child: Stack(
        alignment: Alignment.center,
        children: [
          PieChart(
            PieChartData(
              sections: total > 0
                  ? [
                      PieChartSectionData(
                        value: protein * 4,
                        color: AppColors.protein,
                        radius: 28,
                        showTitle: false,
                      ),
                      PieChartSectionData(
                        value: carbs * 4,
                        color: AppColors.carbs,
                        radius: 28,
                        showTitle: false,
                      ),
                      PieChartSectionData(
                        value: fat * 9,
                        color: AppColors.fat,
                        radius: 28,
                        showTitle: false,
                      ),
                      if (remaining > 0)
                        PieChartSectionData(
                          value: remaining,
                          color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.3),
                          radius: 28,
                          showTitle: false,
                        ),
                    ]
                  : [
                      PieChartSectionData(
                        value: 1,
                        color: theme.colorScheme.surfaceContainerHighest.withOpacity(0.3),
                        radius: 28,
                        showTitle: false,
                      ),
                    ],
              centerSpaceRadius: 60,
              sectionsSpace: 2,
            ),
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                calories.toStringAsFixed(0),
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: AppColors.calories,
                ),
              ),
              Text(
                'kcal',
                style: theme.textTheme.bodySmall,
              ),
              Text(
                '/ ${calorieGoal.toStringAsFixed(0)}',
                style: theme.textTheme.bodySmall?.copyWith(fontSize: 10),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
