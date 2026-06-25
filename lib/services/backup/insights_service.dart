import 'dart:math';
import '../../models/meal_entry.dart';
import '../../models/daily_summary.dart';
import '../../models/monthly_summary.dart';
import '../../models/yearly_summary.dart';
import '../../models/user_profile.dart';
import '../../models/nutrition_goals.dart';
import '../../storage/hive_storage.dart';
import '../nutrition_calculator.dart';

/// Derives the meaningful, long-term health signals the lifecycle system is
/// built to preserve: daily/monthly/yearly summaries, a 0–100 daily health
/// score, and the aggregate insights surfaced in the XLSX report.
///
/// Everything here is *derived* from existing data — no new tracking UI — and
/// is the single source of truth shared by the archive engine and exporters.
class InsightsService {
  /// User goals (falls back to sensible defaults when no profile exists).
  static NutritionGoals goalsFor(UserProfile? p) {
    if (p == null) {
      return const NutritionGoals(
        calories: 2000,
        proteinG: 60,
        carbsG: 250,
        fatG: 60,
        fiberG: 30,
        waterMl: 2500,
        bmr: 1500,
        tdee: 2000,
      );
    }
    // Honour user-set custom limits when active.
    if (HiveStorage.useCustomLimits) {
      final base = NutritionCalculator.calculate(p);
      return NutritionGoals(
        calories: HiveStorage.customCalories ?? base.calories,
        proteinG: HiveStorage.customProteinG ?? base.proteinG,
        carbsG: HiveStorage.customCarbsG ?? base.carbsG,
        fatG: HiveStorage.customFatG ?? base.fatG,
        fiberG: base.fiberG,
        waterMl: base.waterMl,
        bmr: base.bmr,
        tdee: base.tdee,
      );
    }
    return NutritionCalculator.calculate(p);
  }

  /// 0–100 daily health score: weighted closeness to calorie / protein /
  /// water / fiber goals. Returns 0 for an unlogged day.
  static double dayScore({
    required double kcal,
    required double protein,
    required double fiber,
    required double waterMl,
    required int mealCount,
    required NutritionGoals goals,
  }) {
    if (mealCount == 0) return 0;
    double clamp01(double v) => v.clamp(0.0, 1.0);

    final calScore = goals.calories > 0
        ? 1.0 - clamp01((kcal - goals.calories).abs() / goals.calories)
        : 0.0;
    final proScore = goals.proteinG > 0 ? clamp01(protein / goals.proteinG) : 0.0;
    final waterScore = goals.waterMl > 0 ? clamp01(waterMl / goals.waterMl) : 0.0;
    final fiberScore = goals.fiberG > 0 ? clamp01(fiber / goals.fiberG) : 0.0;

    final score =
        (0.35 * calScore + 0.30 * proScore + 0.20 * waterScore + 0.15 * fiberScore) *
            100;
    return double.parse(score.toStringAsFixed(1));
  }

  /// Builds daily summaries from the currently-active meal entries (grouped by
  /// day), merging in water intake and a computed score.
  static List<DailySummary> activeDailySummaries() {
    final meals = HiveStorage.getAllMealEntries();
    final water = HiveStorage.getAllWaterEntries();
    final goals = goalsFor(HiveStorage.getUserProfile());

    final byDay = <String, List<MealEntry>>{};
    for (final m in meals) {
      byDay.putIfAbsent(m.dateKey, () => []).add(m);
    }

    final out = <DailySummary>[];
    final seenDays = <String>{...byDay.keys, ...water.keys};
    for (final dk in seenDays) {
      final dayMeals = byDay[dk] ?? const <MealEntry>[];
      final kcal = dayMeals.fold<double>(0, (s, m) => s + m.calories);
      final protein = dayMeals.fold<double>(0, (s, m) => s + m.proteinG);
      final carbs = dayMeals.fold<double>(0, (s, m) => s + m.carbsG);
      final fat = dayMeals.fold<double>(0, (s, m) => s + m.fatG);
      final fiber = dayMeals.fold<double>(0, (s, m) => s + m.fiberG);
      final waterMl = water[dk] ?? 0;
      final date = _parseDayKey(dk);
      out.add(DailySummary(
        dateKey: dk,
        date: date,
        kcal: kcal,
        protein: protein,
        carbs: carbs,
        fat: fat,
        fiber: fiber,
        waterMl: waterMl,
        score: dayScore(
          kcal: kcal,
          protein: protein,
          fiber: fiber,
          waterMl: waterMl,
          mealCount: dayMeals.length,
          goals: goals,
        ),
        mealCount: dayMeals.length,
      ));
    }
    out.sort((a, b) => a.date.compareTo(b.date));
    return out;
  }

  /// All daily summaries available for reporting: archived (box) + derived from
  /// active meals, de-duplicated by dateKey (archived wins).
  static List<DailySummary> allDailySummaries() {
    final archived = {for (final s in HiveStorage.getDailySummaries()) s.dateKey: s};
    for (final s in activeDailySummaries()) {
      archived.putIfAbsent(s.dateKey, () => s);
    }
    final list = archived.values.toList()..sort((a, b) => a.date.compareTo(b.date));
    return list;
  }

  /// Aggregate monthly summaries from daily summaries (for reporting), merged
  /// with already-archived [MonthlySummary] records.
  static List<MonthlySummary> allMonthlySummaries() {
    final out = <String, MonthlySummary>{};
    for (final s in HiveStorage.getMonthlySummaries()) {
      out[s.key] = s;
    }
    final byMonth = <String, List<DailySummary>>{};
    for (final d in allDailySummaries()) {
      byMonth.putIfAbsent(d.monthKey, () => []).add(d);
    }
    byMonth.forEach((key, days) {
      if (out.containsKey(key)) return; // archived record already authoritative
      final logged = days.where((d) => d.mealCount > 0).toList();
      final n = max(logged.length, 1);
      final first = days.first.date;
      final daysInMonth = DateTime(first.year, first.month + 1, 0).day;
      out[key] = MonthlySummary(
        year: first.year,
        month: first.month,
        avgCalories: logged.fold<double>(0, (s, d) => s + d.kcal) / n,
        avgProtein: logged.fold<double>(0, (s, d) => s + d.protein) / n,
        avgCarbs: logged.fold<double>(0, (s, d) => s + d.carbs) / n,
        avgFat: logged.fold<double>(0, (s, d) => s + d.fat) / n,
        avgFiber: logged.fold<double>(0, (s, d) => s + d.fiber) / n,
        consistencyScore: logged.length / max(daysInMonth, 1),
        daysLogged: logged.length,
      );
    });
    final list = out.values.toList()
      ..sort((a, b) => (a.year * 100 + a.month).compareTo(b.year * 100 + b.month));
    return list;
  }

  /// Aggregate yearly summaries (archived box + derived from monthly/daily).
  static List<YearlySummary> allYearlySummaries() {
    final out = <int, YearlySummary>{};
    for (final y in HiveStorage.getYearlySummaries()) {
      out[y.year] = y;
    }
    final byYear = <int, List<DailySummary>>{};
    for (final d in allDailySummaries()) {
      byYear.putIfAbsent(d.year, () => []).add(d);
    }
    final weights = HiveStorage.getWeightHistory();
    byYear.forEach((year, days) {
      if (out.containsKey(year)) return;
      final logged = days.where((d) => d.mealCount > 0).toList();
      final n = max(logged.length, 1);
      out[year] = YearlySummary(
        year: year,
        avgKcal: logged.fold<double>(0, (s, d) => s + d.kcal) / n,
        avgProtein: logged.fold<double>(0, (s, d) => s + d.protein) / n,
        avgCarbs: logged.fold<double>(0, (s, d) => s + d.carbs) / n,
        avgFat: logged.fold<double>(0, (s, d) => s + d.fat) / n,
        avgWater: days.fold<double>(0, (s, d) => s + d.waterMl) / max(days.length, 1),
        avgScore: logged.fold<double>(0, (s, d) => s + d.score) / n,
        weightChange: _weightChangeForYear(weights, year),
        daysLogged: logged.length,
      );
    });
    final list = out.values.toList()..sort((a, b) => a.year.compareTo(b.year));
    return list;
  }

  static double _weightChangeForYear(List weights, int year) {
    final inYear = weights.where((w) => w.recordedAt.year == year).toList()
      ..sort((a, b) => a.recordedAt.compareTo(b.recordedAt));
    if (inYear.length < 2) return 0;
    return double.parse(
        (inYear.last.weightKg - inYear.first.weightKg).toStringAsFixed(1));
  }

  /// Cross-cutting insights for the Health Insights sheet.
  static HealthInsights aggregateInsights() {
    final days = allDailySummaries().where((d) => d.mealCount > 0).toList();
    final months = allMonthlySummaries();
    final weights = HiveStorage.getWeightHistory();

    if (days.isEmpty) {
      return HealthInsights.empty();
    }

    final avgCal = days.fold<double>(0, (s, d) => s + d.kcal) / days.length;
    final avgPro = days.fold<double>(0, (s, d) => s + d.protein) / days.length;
    final avgWater = days.fold<double>(0, (s, d) => s + d.waterMl) / days.length;
    final avgScore = days.fold<double>(0, (s, d) => s + d.score) / days.length;

    MonthlySummary? best, worst;
    for (final m in months) {
      if (best == null || m.avgCalories.isFinite && m.consistencyScore > best.consistencyScore) {
        best = m;
      }
      if (worst == null || m.consistencyScore < worst.consistencyScore) {
        worst = m;
      }
    }

    final goals = goalsFor(HiveStorage.getUserProfile());
    final goalDays = days.where((d) => d.kcal >= goals.calories * 0.9 && d.kcal <= goals.calories * 1.1).length;
    final goalPct = days.isEmpty ? 0.0 : (goalDays / days.length) * 100;

    final weightChange = weights.length >= 2
        ? double.parse((weights.last.weightKg - weights.first.weightKg).toStringAsFixed(1))
        : 0.0;

    return HealthInsights(
      bestMonth: best?.label ?? '—',
      worstMonth: worst?.label ?? '—',
      longestStreak: _longestStreak(days),
      avgCalories: avgCal,
      avgProtein: avgPro,
      avgWater: avgWater,
      avgScore: avgScore,
      goalAchievementPct: goalPct,
      weightChange: weightChange,
      trend: avgScore >= 75
          ? 'Improving'
          : avgScore >= 55
              ? 'Stable'
              : 'Needs attention',
      totalDaysLogged: days.length,
    );
  }

  static int _longestStreak(List<DailySummary> days) {
    if (days.isEmpty) return 0;
    final sorted = [...days]..sort((a, b) => a.date.compareTo(b.date));
    int longest = 1, current = 1;
    for (var i = 1; i < sorted.length; i++) {
      final diff = sorted[i].date.difference(sorted[i - 1].date).inDays;
      if (diff == 1) {
        current++;
        longest = max(longest, current);
      } else if (diff > 1) {
        current = 1;
      }
    }
    return longest;
  }

  static DateTime _parseDayKey(String key) {
    final p = key.split('_');
    if (p.length == 3) {
      return DateTime(int.tryParse(p[0]) ?? 2000, int.tryParse(p[1]) ?? 1,
          int.tryParse(p[2]) ?? 1);
    }
    return DateTime(2000);
  }
}

/// Aggregate health insights for the report's Health Insights sheet.
class HealthInsights {
  final String bestMonth;
  final String worstMonth;
  final int longestStreak;
  final double avgCalories;
  final double avgProtein;
  final double avgWater;
  final double avgScore;
  final double goalAchievementPct;
  final double weightChange;
  final String trend;
  final int totalDaysLogged;

  const HealthInsights({
    required this.bestMonth,
    required this.worstMonth,
    required this.longestStreak,
    required this.avgCalories,
    required this.avgProtein,
    required this.avgWater,
    required this.avgScore,
    required this.goalAchievementPct,
    required this.weightChange,
    required this.trend,
    required this.totalDaysLogged,
  });

  factory HealthInsights.empty() => const HealthInsights(
        bestMonth: '—',
        worstMonth: '—',
        longestStreak: 0,
        avgCalories: 0,
        avgProtein: 0,
        avgWater: 0,
        avgScore: 0,
        goalAchievementPct: 0,
        weightChange: 0,
        trend: 'No data',
        totalDaysLogged: 0,
      );
}
