class NutritionGoals {
  final double calories;
  final double proteinG;
  final double carbsG;
  final double fatG;
  final double fiberG;
  final double waterMl;
  final double bmr;
  final double tdee;

  const NutritionGoals({
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.fiberG,
    required this.waterMl,
    required this.bmr,
    required this.tdee,
  });

  static const NutritionGoals defaults = NutritionGoals(
    calories: 2000,
    proteinG: 120,
    carbsG: 225,
    fatG: 65,
    fiberG: 40,
    waterMl: 2450,
    bmr: 1700,
    tdee: 2500,
  );
}
