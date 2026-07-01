import 'package:flutter_test/flutter_test.dart';
import 'package:infinity_health_tracker/services/nutrition_calculator.dart';
import 'package:infinity_health_tracker/models/user_profile.dart';

void main() {
  group('NutritionCalculator', () {
    UserProfile makeMale({
      int age = 30,
      double height = 175,
      double weight = 80,
      String activity = 'moderately_active',
      String goal = 'maintain',
    }) {
      return UserProfile(
        id: 'test',
        age: age,
        gender: 'male',
        heightCm: height,
        weightKg: weight,
        activityLevel: activity,
        fitnessGoal: goal,
        createdAt: DateTime(2024),
      );
    }

    UserProfile makeFemale({
      int age = 25,
      double height = 165,
      double weight = 60,
      String activity = 'lightly_active',
      String goal = 'lose_weight',
    }) {
      return UserProfile(
        id: 'test2',
        age: age,
        gender: 'female',
        heightCm: height,
        weightKg: weight,
        activityLevel: activity,
        fitnessGoal: goal,
        createdAt: DateTime(2024),
      );
    }

    test('male BMR calculation is correct (Mifflin-St Jeor)', () {
      // BMR = (10 * 80) + (6.25 * 175) - (5 * 30) + 5 = 800 + 1093.75 - 150 + 5 = 1748.75
      final profile = makeMale();
      final goals = NutritionCalculator.calculate(profile);
      expect(goals.bmr, closeTo(1748.75, 1.0));
    });

    test('female BMR calculation is correct (Mifflin-St Jeor)', () {
      // BMR = (10 * 60) + (6.25 * 165) - (5 * 25) - 161 = 600 + 1031.25 - 125 - 161 = 1345.25
      final profile = makeFemale();
      final goals = NutritionCalculator.calculate(profile);
      expect(goals.bmr, closeTo(1345.25, 1.0));
    });

    test('TDEE is BMR * activity multiplier for moderately active', () {
      final profile = makeMale(activity: 'moderately_active');
      final goals = NutritionCalculator.calculate(profile);
      expect(goals.tdee, closeTo(goals.bmr * 1.55, 1.0));
    });

    test('lose weight goal applies 500 kcal deficit', () {
      final maintain = NutritionCalculator.calculate(makeMale(goal: 'maintain'));
      final loseWeight = NutritionCalculator.calculate(makeMale(goal: 'lose_weight'));
      expect(maintain.calories - loseWeight.calories, closeTo(500, 5.0));
    });

    test('gain muscle goal adds 300 kcal surplus', () {
      final maintain = NutritionCalculator.calculate(makeMale(goal: 'maintain'));
      final gainMuscle = NutritionCalculator.calculate(makeMale(goal: 'gain_muscle'));
      expect(gainMuscle.calories - maintain.calories, closeTo(300, 5.0));
    });

    test('healthy fat loss goal applies same deficit as lose_weight', () {
      final loseWeight = NutritionCalculator.calculate(makeMale(goal: 'lose_weight'));
      final fatLoss = NutritionCalculator.calculate(makeMale(goal: 'healthy_fat_loss'));
      expect(loseWeight.calories, closeTo(fatLoss.calories, 1.0));
    });

    test('calorie target is clamped between 1200 and 4000', () {
      final goals = NutritionCalculator.calculate(makeMale());
      expect(goals.calories, greaterThanOrEqualTo(1200));
      expect(goals.calories, lessThanOrEqualTo(4000));
    });

    test('protein is higher for muscle gain than maintenance', () {
      final maintain = NutritionCalculator.calculate(makeMale(goal: 'maintain'));
      final gain = NutritionCalculator.calculate(makeMale(goal: 'gain_muscle'));
      expect(gain.proteinG, greaterThan(maintain.proteinG));
    });

    test('BMI calculation is correct', () {
      // 80 / (1.75^2) = 80 / 3.0625 = 26.12
      final bmi = NutritionCalculator.calculateBMI(80, 175);
      expect(bmi, closeTo(26.12, 0.1));
    });

    test('BMI categories are correct', () {
      expect(NutritionCalculator.bmiCategory(17.0), 'Underweight');
      expect(NutritionCalculator.bmiCategory(22.0), 'Normal weight');
      expect(NutritionCalculator.bmiCategory(27.0), 'Overweight');
      expect(NutritionCalculator.bmiCategory(32.0), 'Obese');
    });

    test('weekly fat loss estimate is realistic', () {
      // 500 kcal/day deficit * 7 = 3500 kcal per week / 7700 ≈ 0.45 kg
      final loss = NutritionCalculator.estimateWeeklyFatLoss(500);
      expect(loss, closeTo(0.45, 0.05));
    });

    test('water intake increases with activity level', () {
      final sedentary = NutritionCalculator.calculate(makeMale(activity: 'sedentary'));
      final veryActive = NutritionCalculator.calculate(makeMale(activity: 'very_active'));
      expect(veryActive.waterMl, greaterThan(sedentary.waterMl));
    });

    test('goals object has valid fiber target', () {
      final goals = NutritionCalculator.calculate(makeMale());
      expect(goals.fiberG, equals(38.0));
    });

    test('all macros produce positive values', () {
      final goals = NutritionCalculator.calculate(makeFemale());
      expect(goals.calories, isPositive);
      expect(goals.proteinG, isPositive);
      expect(goals.carbsG, isPositive);
      expect(goals.fatG, isPositive);
    });
  });
}
