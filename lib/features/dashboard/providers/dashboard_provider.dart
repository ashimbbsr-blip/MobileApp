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

  const DashboardState({
    this.userProfile,
    this.goals,
    this.todaysMeals = const [],
    required this.selectedDateKey,
  });

  double get totalCalories => todaysMeals.fold(0, (sum, m) => sum + m.calories);
  double get totalProtein => todaysMeals.fold(0, (sum, m) => sum + m.proteinG);
  double get totalCarbs => todaysMeals.fold(0, (sum, m) => sum + m.carbsG);
  double get totalFat => todaysMeals.fold(0, (sum, m) => sum + m.fatG);
  double get totalFiber => todaysMeals.fold(0, (sum, m) => sum + m.fiberG);

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
  }) {
    return DashboardState(
      userProfile: userProfile ?? this.userProfile,
      goals: goals ?? this.goals,
      todaysMeals: todaysMeals ?? this.todaysMeals,
      selectedDateKey: selectedDateKey ?? this.selectedDateKey,
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
    state = state.copyWith(
      userProfile: profile,
      goals: goals,
      todaysMeals: meals,
    );
  }

  void refresh() => _loadData();

  void selectDate(DateTime date) {
    state = state.copyWith(selectedDateKey: date.toLogKey());
    _loadData();
  }
}

final dashboardProvider = StateNotifierProvider<DashboardNotifier, DashboardState>(
  (ref) => DashboardNotifier(),
);
