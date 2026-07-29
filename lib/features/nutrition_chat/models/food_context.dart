import '../../../models/food_item.dart';

/// Converts a FoodItem into a compact, prompt-friendly string.
class FoodContext {
  final FoodItem food;
  const FoodContext(this.food);

  String toPromptString() {
    final b = StringBuffer();
    b.writeln('Name: ${food.name}${food.nameBn != null && food.nameBn!.isNotEmpty ? " (${food.nameBn})" : ""}');
    if (food.category != null) b.writeln('Category: ${food.category}');
    b.writeln('Serving: ${food.servingSize.toStringAsFixed(0)} ${food.servingUnit}');
    b.writeln('Calories: ${food.calories.toStringAsFixed(1)} kcal');
    b.writeln('Protein: ${food.proteinG.toStringAsFixed(1)} g');
    b.writeln('Carbohydrates: ${food.carbsG.toStringAsFixed(1)} g');
    b.writeln('Fat: ${food.fatG.toStringAsFixed(1)} g');
    b.writeln('Fiber: ${food.fiberG.toStringAsFixed(1)} g');

    void addIfPositive(String label, double? v, String unit) {
      if (v != null && v > 0) b.writeln('$label: ${v.toStringAsFixed(v < 10 ? 1 : 0)} $unit');
    }

    addIfPositive('Sugar', food.sugarG, 'g');
    addIfPositive('Alcohol', food.alcoholG, 'g');
    addIfPositive('Sodium', food.sodiumMg, 'mg');
    addIfPositive('Potassium', food.potassiumMg, 'mg');
    addIfPositive('Calcium', food.calciumMg, 'mg');
    addIfPositive('Iron', food.ironMg, 'mg');
    addIfPositive('Magnesium', food.magnesiumMg, 'mg');
    addIfPositive('Zinc', food.zincMg, 'mg');
    addIfPositive('Vitamin A', food.vitaminAMcg, 'mcg');
    addIfPositive('Vitamin C', food.vitaminCMg, 'mg');
    addIfPositive('Vitamin D', food.vitaminDMcg, 'mcg');
    addIfPositive('Vitamin B12', food.vitaminB12Mcg, 'mcg');

    return b.toString().trim();
  }
}
