import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../models/food_item.dart';
import '../../storage/hive_storage.dart';
import '../meal_tracking/providers/meal_provider.dart';
import '../dashboard/providers/dashboard_provider.dart';
import '../../core/utils/meal_time_utils.dart';

class FoodDetailScreen extends ConsumerStatefulWidget {
  final FoodItem foodItem;
  final String? initialMealType;
  const FoodDetailScreen({super.key, required this.foodItem, this.initialMealType});

  @override
  ConsumerState<FoodDetailScreen> createState() => _FoodDetailScreenState();
}

class _FoodDetailScreenState extends ConsumerState<FoodDetailScreen> {
  late double _quantity;
  late String _selectedMeal;
  late FoodItem _scaledFood;
  final _quantityController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _selectedMeal = widget.initialMealType ?? mealTypeForNow();
    _quantity = widget.foodItem.servingSize;
    _quantityController.text = _quantity.toStringAsFixed(
        _quantity == _quantity.truncateToDouble() ? 0 : 1);
    _scaledFood = widget.foodItem.scaledTo(_quantity);
  }

  @override
  void dispose() {
    _quantityController.dispose();
    super.dispose();
  }

  Future<void> _addToMeal() async {
    if (_quantity <= 0) return;
    await ref.read(mealProvider.notifier).addFood(widget.foodItem, _selectedMeal, _quantity);
    if (!mounted) return;
    if (widget.foodItem.source == 'usda' || widget.foodItem.usdaFdcId != null) {
      await HiveStorage.saveUsdaFood(widget.foodItem);
      if (!mounted) return;
      await HiveStorage.cacheFoodItem(widget.foodItem);
      if (!mounted) return;
    }
    ref.read(dashboardProvider.notifier).refresh();
    if (mounted) {
      final l10n = ref.read(appStringsProvider);
      final mealNames = {
        'breakfast': l10n.breakfast,
        'lunch': l10n.lunch,
        'dinner': l10n.dinner,
        'snack': l10n.snack,
      };
      final mealLabel = mealNames[_selectedMeal] ?? _selectedMeal;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${l10n.addedTo} $mealLabel'),
          backgroundColor: AppColors.primary,
          duration: const Duration(seconds: 2),
        ),
      );
      context.pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = ref.watch(appStringsProvider);
    final food = _scaledFood;
    final theme = Theme.of(context);
    final lang = l10n.language;

    final hasMinerals = (food.sodiumMg != null && food.sodiumMg! > 0) ||
        (food.potassiumMg != null && food.potassiumMg! > 0) ||
        (food.calciumMg != null && food.calciumMg! > 0) ||
        (food.ironMg != null && food.ironMg! > 0) ||
        (food.magnesiumMg != null && food.magnesiumMg! > 0) ||
        (food.zincMg != null && food.zincMg! > 0);
    final hasVitamins = (food.vitaminAMcg != null && food.vitaminAMcg! > 0) ||
        (food.vitaminCMg != null && food.vitaminCMg! > 0) ||
        (food.vitaminDMcg != null && food.vitaminDMcg! > 0) ||
        (food.vitaminB12Mcg != null && food.vitaminB12Mcg! > 0);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.nutritionFacts)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Card 1: Food name + quantity + calorie display ─────────
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      lang == 'bn' && widget.foodItem.nameBn != null && widget.foodItem.nameBn!.isNotEmpty
                          ? widget.foodItem.nameBn!
                          : widget.foodItem.name,
                      style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700),
                    ),
                    // Show alternate name (EN↔BN)
                    if (lang == 'bn' && widget.foodItem.nameBn != null && widget.foodItem.nameBn!.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(widget.foodItem.name, style: theme.textTheme.bodySmall?.copyWith(fontSize: 12, color: Colors.grey)),
                    ] else if (lang != 'bn' && widget.foodItem.nameBn != null && widget.foodItem.nameBn!.isNotEmpty) ...[
                      const SizedBox(height: 2),
                      Text(widget.foodItem.nameBn!, style: theme.textTheme.bodySmall?.copyWith(fontSize: 12, color: Colors.grey)),
                    ],
                    if (widget.foodItem.brand != null) ...[
                      const SizedBox(height: 4),
                      Text(widget.foodItem.brand!, style: theme.textTheme.bodyMedium),
                    ],
                    const Divider(height: 24),
                    Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(l10n.quantity, style: theme.textTheme.bodyMedium),
                              const SizedBox(height: 4),
                              TextField(
                                controller: _quantityController,
                                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                                decoration: InputDecoration(
                                  suffix: Text(widget.foodItem.servingUnit),
                                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                  isDense: true,
                                ),
                                onChanged: (v) {
                                  final parsed = double.tryParse(v);
                                  if (parsed != null && parsed > 0) {
                                    setState(() {
                                      _quantity = parsed;
                                      _scaledFood = widget.foodItem.scaledTo(parsed);
                                    });
                                  }
                                },
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 16),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              food.calories.toStringAsFixed(0),
                              style: theme.textTheme.headlineMedium?.copyWith(
                                fontWeight: FontWeight.w700,
                                color: AppColors.calories,
                              ),
                            ),
                            Text('kcal', style: theme.textTheme.bodySmall),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),

            // ── Card 2: Macronutrients ─────────────────────────────────
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.local_fire_department_rounded, size: 16, color: AppColors.calories),
                        const SizedBox(width: 6),
                        Text(
                          lang == 'bn' ? 'ম্যাক্রোনিউট্রিয়েন্ট' : 'Macronutrients',
                          style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _NutrientRow(label: l10n.protein, value: '${food.proteinG.toStringAsFixed(1)}g',  color: AppColors.protein),
                    _NutrientRow(label: l10n.carbs,   value: '${food.carbsG.toStringAsFixed(1)}g',    color: AppColors.carbs),
                    _NutrientRow(label: l10n.fat,     value: '${food.fatG.toStringAsFixed(1)}g',      color: AppColors.fat),
                    _NutrientRow(label: l10n.fiber,   value: '${food.fiberG.toStringAsFixed(1)}g',    color: AppColors.fiber),
                    if (food.sugarG != null && food.sugarG! >= 0)
                      _NutrientRow(label: l10n.sugarLabel, value: '${food.sugarG!.toStringAsFixed(1)}g', color: const Color(0xFFFF6B9D)),
                    if (food.alcoholG != null && food.alcoholG! > 0)
                      _NutrientRow(
                        label: lang == 'bn' ? 'অ্যালকোহল' : 'Alcohol',
                        value: '${food.alcoholG!.toStringAsFixed(1)}g',
                        color: const Color(0xFFAB47BC),
                      ),
                  ],
                ),
              ),
            ),

            // ── Card 3: Minerals & Vitamins (only if data present) ─────
            if (hasMinerals || hasVitamins) ...[
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.science_outlined, size: 16, color: Color(0xFF00897B)),
                          const SizedBox(width: 6),
                          Text(
                            lang == 'bn' ? 'মিনারেল ও ভিটামিন' : 'Minerals & Vitamins',
                            style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),

                      if (hasMinerals) ...[
                        const SizedBox(height: 12),
                        _SubSectionHeader(lang == 'bn' ? 'মিনারেল' : 'Minerals', const Color(0xFF5C6BC0)),
                        const SizedBox(height: 8),
                        if (food.sodiumMg != null && food.sodiumMg! > 0)
                          _NutrientRow(label: l10n.sodiumLabel, value: '${food.sodiumMg!.toStringAsFixed(0)}mg', color: const Color(0xFF7B61FF)),
                        if (food.potassiumMg != null && food.potassiumMg! > 0)
                          _NutrientRow(label: l10n.potassium, value: '${food.potassiumMg!.toStringAsFixed(0)}mg', color: const Color(0xFF00BCD4)),
                        if (food.calciumMg != null && food.calciumMg! > 0)
                          _NutrientRow(label: l10n.calcium, value: '${food.calciumMg!.toStringAsFixed(0)}mg', color: AppColors.calcium),
                        if (food.ironMg != null && food.ironMg! > 0)
                          _NutrientRow(label: l10n.iron, value: '${food.ironMg!.toStringAsFixed(1)}mg', color: AppColors.iron),
                        if (food.magnesiumMg != null && food.magnesiumMg! > 0)
                          _NutrientRow(label: l10n.magnesium, value: '${food.magnesiumMg!.toStringAsFixed(0)}mg', color: const Color(0xFF4CAF50)),
                        if (food.zincMg != null && food.zincMg! > 0)
                          _NutrientRow(label: l10n.zinc, value: '${food.zincMg!.toStringAsFixed(1)}mg', color: const Color(0xFF9E9E9E)),
                      ],

                      if (hasVitamins) ...[
                        if (hasMinerals) const Divider(height: 20),
                        _SubSectionHeader(lang == 'bn' ? 'ভিটামিন' : 'Vitamins', const Color(0xFFE65100)),
                        const SizedBox(height: 8),
                        if (food.vitaminAMcg != null && food.vitaminAMcg! > 0)
                          _NutrientRow(label: l10n.vitaminA, value: '${food.vitaminAMcg!.toStringAsFixed(0)}mcg', color: const Color(0xFFFF9800)),
                        if (food.vitaminCMg != null && food.vitaminCMg! > 0)
                          _NutrientRow(label: l10n.vitaminC, value: '${food.vitaminCMg!.toStringAsFixed(1)}mg', color: AppColors.vitaminC),
                        if (food.vitaminDMcg != null && food.vitaminDMcg! > 0)
                          _NutrientRow(label: l10n.vitaminD, value: '${food.vitaminDMcg!.toStringAsFixed(1)}mcg', color: const Color(0xFFFFEB3B)),
                        if (food.vitaminB12Mcg != null && food.vitaminB12Mcg! > 0)
                          _NutrientRow(label: 'Vitamin B12', value: '${food.vitaminB12Mcg!.toStringAsFixed(2)}mcg', color: const Color(0xFFE91E63)),
                      ],
                    ],
                  ),
                ),
              ),
            ],

            // ── USDA source badge ──────────────────────────────────────
            if (food.source == 'usda' || food.usdaFdcId != null) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFF1565C0).withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF1565C0).withValues(alpha: 0.25)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.verified_outlined, size: 16, color: Color(0xFF1565C0)),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'USDA FoodData Central${food.usdaFdcId != null ? " · FDC ID: ${food.usdaFdcId}" : ""}',
                        style: theme.textTheme.bodySmall?.copyWith(color: const Color(0xFF1565C0), fontSize: 11),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 16),

            // ── Card 4: Meal selector ──────────────────────────────────
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(l10n.selectMeal, style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 12),
                    _MealSelector(
                      selected: _selectedMeal,
                      onSelected: (m) => setState(() => _selectedMeal = m),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _quantity > 0 ? _addToMeal : null,
                icon: const Icon(Icons.add),
                label: Text(l10n.addToMeal),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }
}

class _NutrientRow extends StatelessWidget {
  final String label, value;
  final Color color;
  const _NutrientRow({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Container(width: 8, height: 8, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
          const SizedBox(width: 10),
          Expanded(child: Text(label, style: Theme.of(context).textTheme.bodyMedium)),
          Text(value, style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class _SubSectionHeader extends StatelessWidget {
  final String text;
  final Color color;
  const _SubSectionHeader(this.text, this.color);

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 3,
          height: 13,
          decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(2)),
        ),
        const SizedBox(width: 8),
        Text(
          text,
          style: Theme.of(context).textTheme.labelMedium?.copyWith(
            color: color,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.4,
          ),
        ),
      ],
    );
  }
}

class _MealSelector extends StatelessWidget {
  final String selected;
  final void Function(String) onSelected;
  const _MealSelector({required this.selected, required this.onSelected});

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, _) {
      final l10n = ref.watch(appStringsProvider);
      final meals = [
        ('breakfast', l10n.breakfast, Icons.wb_sunny_outlined),
        ('lunch', l10n.lunch, Icons.lunch_dining_outlined),
        ('dinner', l10n.dinner, Icons.dinner_dining_outlined),
        ('snack', l10n.snack, Icons.cookie_outlined),
      ];

      return Wrap(
        spacing: 8,
        children: meals.map((m) => ChoiceChip(
          label: Text(m.$2),
          selected: selected == m.$1,
          onSelected: (_) => onSelected(m.$1),
          avatar: Icon(m.$3, size: 16),
          selectedColor: AppColors.primary.withValues(alpha: 0.2),
        )).toList(),
      );
    });
  }
}
