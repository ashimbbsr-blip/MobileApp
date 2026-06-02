class NutritionConstants {
  // ICMR 2020 Recommended Dietary Allowances (Indian adults)
  static const double vitaminAMcg = 800;      // ICMR 2020: 800 mcg RAE
  static const double vitaminB12Mcg = 1.0;    // ICMR 2020: 1.0 mcg (adults)
  static const double vitaminCMg = 80;        // ICMR 2020: 80 mg
  static const double vitaminDMcg = 10;       // ICMR 2020: 10 mcg (400 IU)
  static const double vitaminEMg = 15;
  static const double calciumMg = 1000;       // ICMR 2020: 1000 mg
  static const double potassiumMg = 3750;     // ICMR 2020: 3750 mg
  static const double magnesiumMg = 340;      // ICMR 2020: 340 mg
  static const double fiberG = 40;            // ICMR 2020: 40 g
  static const double sodiumMg = 2000;        // WHO/ICMR limit: 2000 mg/day (<2 g Na)
  // Reference value only — personalized water target is in NutritionCalculator._calculateWater()
  static const double waterMlIcmrReference = 3700; // ICMR 2020: 3700 ml/day (adult)

  // Gender-specific targets (ICMR 2020)
  static const double ironMgMale = 9;         // ICMR 2020: 9 mg (adult male)
  static const double ironMgFemale = 18;      // ICMR 2020: 18 mg (premenopausal female)
  static const double zincMgMale = 7.5;       // ICMR 2020: 7.5 mg (adult male)
  static const double zincMgFemale = 8.5;     // ICMR 2020: 8.5 mg (adult female)

  // Backward-compatible defaults (male values)
  static const double ironMg = ironMgMale;
  static const double zincMg = zincMgMale;

  static double ironForGender(String gender) =>
      gender == 'female' ? ironMgFemale : ironMgMale;

  static double zincForGender(String gender) =>
      gender == 'female' ? zincMgFemale : zincMgMale;

  // Macro ratios for balanced diet
  static const double proteinCaloriesPerGram = 4;
  static const double carbCaloriesPerGram = 4;
  static const double fatCaloriesPerGram = 9;
  static const double alcoholCaloriesPerGram = 7.0; // Atwater ethanol factor

  // Deficit for healthy fat loss (500 kcal/day = ~0.5 kg/week)
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
