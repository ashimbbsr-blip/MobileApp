class NutritionConstants {
  // Recommended Daily Allowances
  static const double vitaminAMcg = 900;
  static const double vitaminBMg = 2.4;
  static const double vitaminCMg = 90;
  static const double vitaminDMcg = 20;
  static const double vitaminEMg = 15;
  static const double calciumMg = 1000;
  static const double ironMg = 8;
  static const double magnesiumMg = 420;
  static const double potassiumMg = 4700;
  static const double zincMg = 11;
  static const double fiberG = 38;
  static const double waterMl = 3700;

  // Macro ratios for balanced diet
  static const double proteinCaloriesPerGram = 4;
  static const double carbCaloriesPerGram = 4;
  static const double fatCaloriesPerGram = 9;

  // Deficit for healthy fat loss (500 kcal/day = ~0.5kg/week)
  static const double fatLossDeficit = 500;

  // Activity multipliers (Mifflin-St Jeor)
  static const Map<String, double> activityMultipliers = {
    'sedentary': 1.2,
    'lightly_active': 1.375,
    'moderately_active': 1.55,
    'very_active': 1.725,
    'extra_active': 1.9,
  };
}
