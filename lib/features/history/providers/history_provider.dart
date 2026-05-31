import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../services/analytics_service.dart';
import '../../../storage/hive_storage.dart';
import '../../../services/nutrition_calculator.dart';

class HistoryState {
  final List<DailyNutrition> week;
  final List<DailyNutrition> month;
  final List<MonthSummaryData> byMonth;
  final int streak;
  final double weekAvgCompletion;
  final double monthAvgCompletion;
  final double goalCalories;
  final double tdee;
  final bool isLoading;

  const HistoryState({
    this.week = const [],
    this.month = const [],
    this.byMonth = const [],
    this.streak = 0,
    this.weekAvgCompletion = 0,
    this.monthAvgCompletion = 0,
    this.goalCalories = 2000,
    this.tdee = 0,
    this.isLoading = false,
  });

  HistoryState copyWith({
    List<DailyNutrition>? week,
    List<DailyNutrition>? month,
    List<MonthSummaryData>? byMonth,
    int? streak,
    double? weekAvgCompletion,
    double? monthAvgCompletion,
    double? goalCalories,
    double? tdee,
    bool? isLoading,
  }) {
    return HistoryState(
      week: week ?? this.week,
      month: month ?? this.month,
      byMonth: byMonth ?? this.byMonth,
      streak: streak ?? this.streak,
      weekAvgCompletion: weekAvgCompletion ?? this.weekAvgCompletion,
      monthAvgCompletion: monthAvgCompletion ?? this.monthAvgCompletion,
      goalCalories: goalCalories ?? this.goalCalories,
      tdee: tdee ?? this.tdee,
      isLoading: isLoading ?? this.isLoading,
    );
  }
}

class HistoryNotifier extends StateNotifier<HistoryState> {
  HistoryNotifier() : super(const HistoryState(isLoading: true)) {
    load();
  }

  void load() {
    state = state.copyWith(isLoading: true);
    final profile = HiveStorage.getUserProfile();
    final goals = profile != null ? NutritionCalculator.calculate(profile) : null;
    final goalCal = goals?.calories ?? 2000;

    final week = AnalyticsService.getLastNDays(7);
    final month = AnalyticsService.getLastNDays(30);
    final byMonth = AnalyticsService.getMonthlyBreakdown();
    final streak = AnalyticsService.computeStreak();

    state = state.copyWith(
      week: week,
      month: month,
      byMonth: byMonth,
      streak: streak,
      weekAvgCompletion: AnalyticsService.computeAvgGoalCompletion(week, goalCal),
      monthAvgCompletion: AnalyticsService.computeAvgGoalCompletion(month, goalCal),
      goalCalories: goalCal,
      tdee: goals?.tdee ?? 0,
      isLoading: false,
    );
  }
}

final historyProvider =
    StateNotifierProvider<HistoryNotifier, HistoryState>((ref) => HistoryNotifier());
