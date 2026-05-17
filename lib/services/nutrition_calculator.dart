import '../models/user_profile.dart';
import '../models/nutrition_goals.dart';
import '../core/constants/nutrition_constants.dart';

class NutritionCalculator {
  static NutritionGoals calculate(UserProfile profile) {
    final bmr = _calculateBMR(profile);
    final tdee = bmr * (NutritionConstants.activityMultipliers[profile.activityLevel] ?? 1.55);
    final calories = _adjustForGoal(tdee, profile.fitnessGoal);
    final protein = _calculateProtein(profile.weightKg, profile.fitnessGoal);
    final fat = _calculateFat(calories);
    final remainingCalories = calories - (protein * NutritionConstants.proteinCaloriesPerGram) - (fat * NutritionConstants.fatCaloriesPerGram);
    final carbs = remainingCalories / NutritionConstants.carbCaloriesPerGram;
    final water = _calculateWater(profile.weightKg, profile.activityLevel);

    return NutritionGoals(
      calories: calories.clamp(1200, 4000),
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
    // Mifflin-St Jeor Equation
    if (profile.gender == 'male') {
      return (10 * profile.weightKg) + (6.25 * profile.heightCm) - (5 * profile.age) + 5;
    } else {
      return (10 * profile.weightKg) + (6.25 * profile.heightCm) - (5 * profile.age) - 161;
    }
  }

  static double _adjustForGoal(double tdee, String goal) {
    switch (goal) {
      case 'lose_weight':
      case 'healthy_fat_loss':
        return tdee - NutritionConstants.fatLossDeficit;
      case 'gain_muscle':
        return tdee + 300;
      case 'maintain':
      default:
        return tdee;
    }
  }

  static double _calculateProtein(double weightKg, String goal) {
    switch (goal) {
      case 'gain_muscle':
        return weightKg * 2.2; // 2.2g per kg for muscle gain
      case 'lose_weight':
      case 'healthy_fat_loss':
        return weightKg * 2.0; // Higher protein to preserve muscle during deficit
      default:
        return weightKg * 1.6; // 1.6g per kg for maintenance
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

  static double calculateBMI(double weightKg, double heightCm) {
    final heightM = heightCm / 100;
    return weightKg / (heightM * heightM);
  }

  static String bmiCategory(double bmi) {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal weight';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
  }

  static double estimateWeeklyFatLoss(double caloricDeficit) {
    // 7700 kcal ≈ 1 kg of fat
    return (caloricDeficit * 7) / 7700;
  }
}
