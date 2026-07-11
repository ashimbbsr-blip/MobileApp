import '../models/user_profile.dart';
import '../models/nutrition_goals.dart';
import '../core/constants/nutrition_constants.dart';

class NutritionCalculator {
  static NutritionGoals calculate(UserProfile profile) {
    final bmr = _calculateBMR(profile);
    final tdee = bmr * (NutritionConstants.activityMultipliers[profile.activityLevel] ?? 1.55);
    final bmi = calculateBMI(profile.weightKg, profile.heightCm);
    final baseCalories = _adjustForGoal(tdee, profile.fitnessGoal, bmi);
    final pregnancyBonus = _pregnancyCalorieBonus(profile.gender, profile.pregnancyStatus);
    final calories = baseCalories + pregnancyBonus;
    final calorieFloor = profile.gender == 'male' ? 1500.0 : 1400.0; // 1400 kcal minimum for Indian women (1200 kcal is at or below BMR)

    final protein = _calculateProtein(profile.weightKg, profile.fitnessGoal, profile.activityLevel);
    final fat = _calculateFat(calories);
    final remainingCalories = calories - (protein * NutritionConstants.proteinCaloriesPerGram) - (fat * NutritionConstants.fatCaloriesPerGram);
    final carbs = remainingCalories / NutritionConstants.carbCaloriesPerGram;
    final water = _calculateWater(profile.weightKg, profile.activityLevel);

    return NutritionGoals(
      calories: calories.clamp(calorieFloor, 4000),
      proteinG: protein.clamp(50, 300),
      carbsG: carbs.clamp(50, 500),
      fatG: fat.clamp(30, 200),
      fiberG: NutritionConstants.fiberG,
      waterMl: water,
      bmr: bmr,
      tdee: tdee,
    );
  }

  static double _calculateBMR(UserProfile profile) {
    // Mifflin-St Jeor Equation — use computedAge (from DOB) when available
    final age = profile.computedAge;
    if (profile.gender == 'male') {
      return (10 * profile.weightKg) + (6.25 * profile.heightCm) - (5 * age) + 5;
    } else {
      return (10 * profile.weightKg) + (6.25 * profile.heightCm) - (5 * age) - 161;
    }
  }

  static double _adjustForGoal(double tdee, String goal, double bmi) {
    switch (goal) {
      case 'lose_weight':
      case 'healthy_fat_loss':
        // Do not impose a deficit on underweight users — maintain TDEE instead
        if (bmi < 18.5) return tdee;
        return tdee - NutritionConstants.fatLossDeficit;
      case 'gain_muscle':
        return tdee + 300;
      case 'maintain':
      default:
        return tdee;
    }
  }

  // Protein targets aligned with ICMR 2020 for sedentary/maintenance;
  // higher values for active/goal-specific use (still evidence-based).
  static double _calculateProtein(double weightKg, String goal, String activityLevel) {
    switch (goal) {
      case 'gain_muscle':
        return weightKg * 1.8;
      case 'lose_weight':
      case 'healthy_fat_loss':
        return weightKg * 1.4;
      default: // maintain
        switch (activityLevel) {
          case 'sedentary':      return weightKg * 0.83; // ICMR 2020 RDA
          case 'lightly_active': return weightKg * 1.0;
          case 'moderately_active': return weightKg * 1.2;
          default:               return weightKg * 1.6;  // very/extra active
        }
    }
  }

  static double _calculateFat(double calories) {
    return (calories * 0.25) / NutritionConstants.fatCaloriesPerGram;
  }

  static double _calculateWater(double weightKg, String activityLevel) {
    double base = weightKg * 35; // 35ml per kg
    if (activityLevel == 'very_active' || activityLevel == 'extra_active') {
      base += 500;
    } else if (activityLevel == 'moderately_active') {
      base += 250;
    }
    return base;
  }

  // ICMR 2020 extra calorie allowances for pregnancy/lactation
  static double _pregnancyCalorieBonus(String gender, String? status) {
    if (gender != 'female' || status == null) return 0;
    switch (status) {
      case 'pregnant_1st': return 150;   // ICMR 2020: +150 kcal in 1st trimester
      case 'pregnant_2nd': return 250;   // ICMR 2020: +250 kcal in 2nd trimester
      case 'pregnant_3rd': return 350;   // ICMR 2020: +350 kcal in 3rd trimester
      case 'lactating':    return 550;
      default:             return 0;
    }
  }

  static double calculateBMI(double weightKg, double heightCm) {
    final heightM = heightCm / 100;
    return weightKg / (heightM * heightM);
  }

  // WHO 2004 / ICMR South Asian BMI cutoffs (lower thresholds than Western norms)
  static String bmiCategory(double bmi) {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 23.0) return 'Normal';
    if (bmi < 27.5) return 'Overweight';
    return 'Obese';
  }

  /// Returns true when the calorie target is clamped to the safe floor
  /// (1500 kcal for males, 1200 kcal for females). Used to show a
  /// doctor-consultation prompt in the UI.
  static bool isAtCalorieFloor(UserProfile profile) {
    final bmr = _calculateBMR(profile);
    final tdee = bmr * (NutritionConstants.activityMultipliers[profile.activityLevel] ?? 1.55);
    final bmi = calculateBMI(profile.weightKg, profile.heightCm);
    final base = _adjustForGoal(tdee, profile.fitnessGoal, bmi);
    final bonus = _pregnancyCalorieBonus(profile.gender, profile.pregnancyStatus);
    final floor = profile.gender == 'male' ? 1500.0 : 1400.0;
    return (base + bonus) < floor;
  }

  static double estimateWeeklyFatLoss(double caloricDeficit) {
    // 7700 kcal ≈ 1 kg of fat
    return (caloricDeficit * 7) / 7700;
  }
}
