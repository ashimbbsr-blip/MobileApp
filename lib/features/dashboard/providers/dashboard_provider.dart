import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../models/user_profile.dart';
import '../../../models/food_item.dart';
import '../../../models/meal_entry.dart';
import '../../../models/nutrition_goals.dart';
import '../../../storage/hive_storage.dart';
import '../../../services/nutrition_calculator.dart';
import '../../../core/utils/extensions.dart';

class DashboardState {
  final UserProfile? userProfile;
  final NutritionGoals? goals;
  final List<MealEntry> todaysMeals;
  final String selectedDateKey;
  final double waterIntakeMl;

  const DashboardState({
    this.userProfile,
    this.goals,
    this.todaysMeals = const [],
    required this.selectedDateKey,
    this.waterIntakeMl = 0,
  });

  double get totalCalories => todaysMeals.fold(0, (sum, m) => sum + m.calories);
  double get totalProtein => todaysMeals.fold(0, (sum, m) => sum + m.proteinG);
  double get totalCarbs => todaysMeals.fold(0, (sum, m) => sum + m.carbsG);
  double get totalFat => todaysMeals.fold(0, (sum, m) => sum + m.fatG);
  double get totalFiber => todaysMeals.fold(0, (sum, m) => sum + m.fiberG);
  double get totalAlcohol => todaysMeals.fold(0, (sum, m) => sum + m.alcoholG);
  double get totalSodium => todaysMeals.fold(0, (sum, m) => sum + m.sodiumMg);

  double _microSum(double? Function(FoodItem) getter) =>
      todaysMeals.fold<double>(0, (sum, m) {
        final factor = m.quantityG / m.foodItem.servingSize;
        return sum + ((getter(m.foodItem) ?? 0) * factor);
      });

  double get totalVitaminA => _microSum((f) => f.vitaminAMcg);
  double get totalVitaminC => _microSum((f) => f.vitaminCMg);
  double get totalVitaminD => _microSum((f) => f.vitaminDMcg);
  double get totalCalcium => _microSum((f) => f.calciumMg);
  double get totalIron => _microSum((f) => f.ironMg);
  double get totalPotassium => _microSum((f) => f.potassiumMg);
  double get totalMagnesium => _microSum((f) => f.magnesiumMg);
  double get totalZinc => _microSum((f) => f.zincMg);
  double get totalVitaminB12 => _microSum((f) => f.vitaminB12Mcg);

  double get calorieProgress => goals != null && goals!.calories > 0
      ? (totalCalories / goals!.calories).clamp(0.0, 1.0)
      : 0;

  List<MealEntry> mealsForType(String type) =>
      todaysMeals.where((m) => m.mealType == type).toList();

  DashboardState copyWith({
    UserProfile? userProfile,
    NutritionGoals? goals,
    List<MealEntry>? todaysMeals,
    String? selectedDateKey,
    double? waterIntakeMl,
  }) {
    return DashboardState(
      userProfile: userProfile ?? this.userProfile,
      goals: goals ?? this.goals,
      todaysMeals: todaysMeals ?? this.todaysMeals,
      selectedDateKey: selectedDateKey ?? this.selectedDateKey,
      waterIntakeMl: waterIntakeMl ?? this.waterIntakeMl,
    );
  }
}

class DashboardNotifier extends StateNotifier<DashboardState> {
  DashboardNotifier()
      : super(DashboardState(selectedDateKey: DateTime.now().toLogKey())) {
    _loadData();
  }

  void _loadData() {
    final profile = HiveStorage.getUserProfile();
    final goals = profile != null ? NutritionCalculator.calculate(profile) : null;
    final meals = HiveStorage.getMealsForDate(state.selectedDateKey);
    final water = HiveStorage.getWaterMl(state.selectedDateKey);
    state = state.copyWith(
      userProfile: profile,
      goals: goals,
      todaysMeals: meals,
      waterIntakeMl: water,
    );
  }

  void refresh() => _loadData();

  void selectDate(DateTime date) {
    state = state.copyWith(selectedDateKey: date.toLogKey());
    _loadData();
  }

  Future<void> addWater(double ml) async {
    final newTotal = (state.waterIntakeMl + ml).clamp(0.0, 5000.0);
    await HiveStorage.saveWaterMl(state.selectedDateKey, newTotal);
    state = state.copyWith(waterIntakeMl: newTotal);
  }

  Future<void> setWater(double ml) async {
    final clamped = ml.clamp(0.0, 5000.0);
    await HiveStorage.saveWaterMl(state.selectedDateKey, clamped);
    state = state.copyWith(waterIntakeMl: clamped);
  }
}

final dashboardProvider = StateNotifierProvider<DashboardNotifier, DashboardState>(
  (ref) => DashboardNotifier(),
);
