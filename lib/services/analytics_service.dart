import 'dart:math';
import '../models/meal_entry.dart';
import '../models/monthly_summary.dart';
import '../storage/hive_storage.dart';
import '../core/utils/extensions.dart';

class DailyNutrition {
  final DateTime date;
  final double calories;
  final double protein;
  final double carbs;
  final double fat;
  final double fiber;
  final double vitaminA;
  final double vitaminC;
  final double vitaminD;
  final double calcium;
  final double iron;
  final double potassium;
  final double magnesium;
  final double zinc;
  final int mealCount;
  final double burnedCalories;

  const DailyNutrition({
    required this.date,
    required this.calories,
    required this.protein,
    required this.carbs,
    required this.fat,
    required this.fiber,
    required this.vitaminA,
    required this.vitaminC,
    required this.vitaminD,
    required this.calcium,
    required this.iron,
    required this.potassium,
    required this.magnesium,
    required this.zinc,
    required this.mealCount,
    this.burnedCalories = 0,
  });

  bool get hasData => mealCount > 0;

  double goalCompletion(double goalCalories) =>
      goalCalories > 0 ? (calories / goalCalories).clamp(0.0, 1.0) : 0.0;

  static DailyNutrition empty(DateTime date) => DailyNutrition(
        date: date,
        calories: 0,
        protein: 0,
        carbs: 0,
        fat: 0,
        fiber: 0,
        vitaminA: 0,
        vitaminC: 0,
        vitaminD: 0,
        calcium: 0,
        iron: 0,
        potassium: 0,
        magnesium: 0,
        zinc: 0,
        mealCount: 0,
        burnedCalories: 0,
      );

  static DailyNutrition fromMeals(DateTime date, List<MealEntry> meals) {
    if (meals.isEmpty) return empty(date);
    double micro(double? Function(dynamic) getter) => meals.fold<double>(0, (s, m) {
          final factor = m.foodItem.servingSize > 0
              ? m.quantityG / m.foodItem.servingSize
              : 1.0;
          return s + ((getter(m.foodItem) ?? 0.0) * factor);
        });

    return DailyNutrition(
      date: date,
      calories: meals.fold(0, (s, m) => s + m.calories),
      protein: meals.fold(0, (s, m) => s + m.proteinG),
      carbs: meals.fold(0, (s, m) => s + m.carbsG),
      fat: meals.fold(0, (s, m) => s + m.fatG),
      fiber: meals.fold(0, (s, m) => s + m.fiberG),
      vitaminA: micro((f) => f.vitaminAMcg),
      vitaminC: micro((f) => f.vitaminCMg),
      vitaminD: micro((f) => f.vitaminDMcg),
      calcium: micro((f) => f.calciumMg),
      iron: micro((f) => f.ironMg),
      potassium: micro((f) => f.potassiumMg),
      magnesium: micro((f) => f.magnesiumMg),
      zinc: micro((f) => f.zincMg),
      mealCount: meals.length,
      burnedCalories: HiveStorage.getBurnedCalories(date.toLogKey()),
    );
  }
}

class MonthSummaryData {
  final String label;
  final String sortKey;
  final double avgCalories;
  final double avgProtein;
  final double avgCarbs;
  final double avgFat;
  final double consistencyScore;
  final int daysLogged;

  const MonthSummaryData({
    required this.label,
    required this.sortKey,
    required this.avgCalories,
    required this.avgProtein,
    required this.avgCarbs,
    required this.avgFat,
    required this.consistencyScore,
    required this.daysLogged,
  });

  static MonthSummaryData fromMonthlySummary(MonthlySummary s) => MonthSummaryData(
        label: s.label,
        sortKey: s.key,
        avgCalories: s.avgCalories,
        avgProtein: s.avgProtein,
        avgCarbs: s.avgCarbs,
        avgFat: s.avgFat,
        consistencyScore: s.consistencyScore,
        daysLogged: s.daysLogged,
      );
}

class AnalyticsService {
  static List<DailyNutrition> getLastNDays(int n) {
    final today = DateTime.now();
    return List.generate(n, (i) {
      final date = today.subtract(Duration(days: n - 1 - i));
      final meals = HiveStorage.getMealsForDate(date.toLogKey());
      return DailyNutrition.fromMeals(date, meals); // burnedCalories loaded inside fromMeals
    });
  }

  static int computeStreak() {
    int streak = 0;
    DateTime current = DateTime.now();
    for (int i = 0; i < 365; i++) {
      final meals = HiveStorage.getMealsForDate(current.toLogKey());
      if (meals.isEmpty) break;
      streak++;
      current = current.subtract(const Duration(days: 1));
    }
    return streak;
  }

  static double computeAvgGoalCompletion(List<DailyNutrition> days, double goalCalories) {
    final logged = days.where((d) => d.hasData).toList();
    if (logged.isEmpty || goalCalories <= 0) return 0;
    final sum = logged.fold<double>(0, (s, d) => s + d.goalCompletion(goalCalories));
    return sum / logged.length;
  }

  static List<MonthSummaryData> getMonthlyBreakdown() {
    final allMeals = HiveStorage.getAllMealEntries();
    final archived = HiveStorage.getMonthlySummaries();
    final archivedKeys = archived.map((s) => s.key).toSet();

    // Group recent meal entries by year-month
    final monthMap = <String, List<MealEntry>>{};
    for (final meal in allMeals) {
      final key =
          '${meal.loggedAt.year}_${meal.loggedAt.month.toString().padLeft(2, '0')}';
      if (!archivedKeys.contains(key)) {
        monthMap.putIfAbsent(key, () => []).add(meal);
      }
    }

    const monthNames = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];

    final result = <MonthSummaryData>[];

    for (final entry in monthMap.entries) {
      final parts = entry.key.split('_');
      final year = int.tryParse(parts[0]) ?? 0;
      final month = int.tryParse(parts[1]) ?? 1;
      final meals = entry.value;

      final byDay = <String, int>{};
      for (final m in meals) { byDay[m.dateKey] = 1; }
      final daysLogged = byDay.length;
      final daysInMonth = DateTime(year, month + 1, 0).day;

      if (daysLogged == 0) continue;

      result.add(MonthSummaryData(
        label: '${monthNames[month - 1]} $year',
        sortKey: entry.key,
        avgCalories: meals.fold<double>(0, (s, m) => s + m.calories) / daysLogged,
        avgProtein: meals.fold<double>(0, (s, m) => s + m.proteinG) / daysLogged,
        avgCarbs: meals.fold<double>(0, (s, m) => s + m.carbsG) / daysLogged,
        avgFat: meals.fold<double>(0, (s, m) => s + m.fatG) / daysLogged,
        consistencyScore: daysLogged / max(daysInMonth, 1),
        daysLogged: daysLogged,
      ));
    }

    for (final s in archived) {
      result.add(MonthSummaryData.fromMonthlySummary(s));
    }

    result.sort((a, b) => b.sortKey.compareTo(a.sortKey));
    return result;
  }

  /// Compresses meal entries older than [retainDays] days into monthly
  /// summaries, then deletes them. Safe to call in background.
  static Future<void> runCleanup({int retainDays = 90}) async {
    final cutoff = DateTime.now().subtract(Duration(days: retainDays));
    final oldMeals = HiveStorage.getMealsOlderThan(cutoff);
    if (oldMeals.isEmpty) return;

    // Group by year-month
    final monthMap = <String, List<MealEntry>>{};
    for (final m in oldMeals) {
      final key =
          '${m.loggedAt.year}_${m.loggedAt.month.toString().padLeft(2, '0')}';
      monthMap.putIfAbsent(key, () => []).add(m);
    }

    for (final entry in monthMap.entries) {
      final parts = entry.key.split('_');
      final year = int.tryParse(parts[0]) ?? 0;
      final month = int.tryParse(parts[1]) ?? 1;
      final meals = entry.value;

      // Skip current and previous month – may not be fully logged yet
      final entryDate = DateTime(year, month);
      if (entryDate.isAfter(cutoff.subtract(const Duration(days: 30)))) continue;

      final byDay = <String, int>{};
      for (final m in meals) { byDay[m.dateKey] = 1; }
      final daysLogged = byDay.length;
      if (daysLogged == 0) continue;

      final daysInMonth = DateTime(year, month + 1, 0).day;
      final existing = HiveStorage.getMonthlySummary(year, month);
      if (existing != null) continue; // already archived

      final summary = MonthlySummary(
        year: year,
        month: month,
        avgCalories: meals.fold<double>(0, (s, m) => s + m.calories) / daysLogged,
        avgProtein: meals.fold<double>(0, (s, m) => s + m.proteinG) / daysLogged,
        avgCarbs: meals.fold<double>(0, (s, m) => s + m.carbsG) / daysLogged,
        avgFat: meals.fold<double>(0, (s, m) => s + m.fatG) / daysLogged,
        avgFiber: meals.fold<double>(0, (s, m) => s + m.fiberG) / daysLogged,
        consistencyScore: daysLogged / max(daysInMonth, 1),
        daysLogged: daysLogged,
      );
      await HiveStorage.saveMonthlySummary(summary);
    }

    // Delete compressed meal entries
    final idsToDelete = oldMeals.map((m) => m.id).toList();
    await HiveStorage.deleteMealEntriesByIds(idsToDelete);
  }
}
