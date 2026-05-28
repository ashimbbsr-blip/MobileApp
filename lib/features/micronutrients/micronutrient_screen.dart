import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../core/constants/nutrition_constants.dart';
import '../../models/meal_entry.dart';
import '../dashboard/providers/dashboard_provider.dart';

class MicronutrientScreen extends ConsumerWidget {
  const MicronutrientScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(dashboardProvider);
    final l10n = ref.watch(appStringsProvider);
    final meals = state.todaysMeals;

    final totals = _calculateTotals(meals);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.micronutrients)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _SectionHeader(title: l10n.vitamins),
            const SizedBox(height: 12),
            _MicroCard(
              name: l10n.vitaminA,
              current: totals['vitaminA'] ?? 0,
              goal: NutritionConstants.vitaminAMcg,
              unit: 'mcg',
              color: AppColors.vitaminA,
            ),
            _MicroCard(
              name: l10n.vitaminC,
              current: totals['vitaminC'] ?? 0,
              goal: NutritionConstants.vitaminCMg,
              unit: 'mg',
              color: AppColors.vitaminC,
            ),
            _MicroCard(
              name: l10n.vitaminD,
              current: totals['vitaminD'] ?? 0,
              goal: NutritionConstants.vitaminDMcg,
              unit: 'mcg',
              color: AppColors.vitaminD,
            ),
            const SizedBox(height: 16),
            _SectionHeader(title: l10n.minerals),
            const SizedBox(height: 12),
            _MicroCard(
              name: l10n.calcium,
              current: totals['calcium'] ?? 0,
              goal: NutritionConstants.calciumMg,
              unit: 'mg',
              color: AppColors.calcium,
            ),
            _MicroCard(
              name: l10n.iron,
              current: totals['iron'] ?? 0,
              goal: NutritionConstants.ironForGender(state.userProfile?.gender ?? 'male'),
              unit: 'mg',
              color: AppColors.iron,
            ),
            _MicroCard(
              name: l10n.magnesium,
              current: totals['magnesium'] ?? 0,
              goal: NutritionConstants.magnesiumMg,
              unit: 'mg',
              color: AppColors.magnesium,
            ),
            _MicroCard(
              name: l10n.potassium,
              current: totals['potassium'] ?? 0,
              goal: NutritionConstants.potassiumMg,
              unit: 'mg',
              color: AppColors.potassium,
            ),
            _MicroCard(
              name: l10n.zinc,
              current: totals['zinc'] ?? 0,
              goal: NutritionConstants.zincForGender(state.userProfile?.gender ?? 'male'),
              unit: 'mg',
              color: AppColors.zinc,
            ),
            const SizedBox(height: 80),
          ],
        ),
      ),
    );
  }

  Map<String, double> _calculateTotals(List<MealEntry> meals) {
    final totals = <String, double>{};
    for (final meal in meals) {
      final food = meal.foodItem;
      final factor = meal.quantityG / food.servingSize;
      if (food.vitaminAMcg != null) totals['vitaminA'] = (totals['vitaminA'] ?? 0) + food.vitaminAMcg! * factor;
      if (food.vitaminCMg != null) totals['vitaminC'] = (totals['vitaminC'] ?? 0) + food.vitaminCMg! * factor;
      if (food.vitaminDMcg != null) totals['vitaminD'] = (totals['vitaminD'] ?? 0) + food.vitaminDMcg! * factor;
      if (food.calciumMg != null) totals['calcium'] = (totals['calcium'] ?? 0) + food.calciumMg! * factor;
      if (food.ironMg != null) totals['iron'] = (totals['iron'] ?? 0) + food.ironMg! * factor;
      if (food.magnesiumMg != null) totals['magnesium'] = (totals['magnesium'] ?? 0) + food.magnesiumMg! * factor;
      if (food.potassiumMg != null) totals['potassium'] = (totals['potassium'] ?? 0) + food.potassiumMg! * factor;
      if (food.zincMg != null) totals['zinc'] = (totals['zinc'] ?? 0) + food.zincMg! * factor;
    }
    return totals;
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
    );
  }
}

class _MicroCard extends StatelessWidget {
  final String name, unit;
  final double current, goal;
  final Color color;

  const _MicroCard({
    required this.name, required this.current, required this.goal,
    required this.unit, required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final progress = goal > 0 ? (current / goal).clamp(0.0, 1.0) : 0.0;
    final theme = Theme.of(context);

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Center(
                child: Text(
                  '${(progress * 100).toStringAsFixed(0)}%',
                  style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.w700),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(name, style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600)),
                  const SizedBox(height: 6),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: progress,
                      backgroundColor: color.withOpacity(0.15),
                      valueColor: AlwaysStoppedAnimation(progress >= 1.0 ? AppColors.primary : color),
                      minHeight: 6,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '${current.toStringAsFixed(1)}$unit',
                  style: theme.textTheme.bodySmall?.copyWith(color: color, fontWeight: FontWeight.w600),
                ),
                Text(
                  '/ ${goal.toStringAsFixed(0)}$unit',
                  style: theme.textTheme.bodySmall,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

