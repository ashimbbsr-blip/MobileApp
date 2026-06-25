import '../../storage/hive_storage.dart';
import '../analytics_service.dart';
import 'backup_serializers.dart';
import 'insights_service.dart';

/// Reads every *meaningful* piece of user data out of Hive and assembles the
/// backup payload map. Runs on the main isolate (Hive is not isolate-safe);
/// the heavy compression that follows is offloaded by [CompressionService].
///
/// Excluded by design (regenerable, per the spec): USDA search cache, search
/// suggestions, session/temp data, analytics & debug logs. The food cache box
/// is *not* exported.
class BackupCollector {
  /// Build the full payload + per-section record counts.
  static ({Map<String, dynamic> payload, Map<String, int> counts}) collect() {
    final profile = HiveStorage.getUserProfile();
    final meals = HiveStorage.getAllMealEntries();
    final customFoods = HiveStorage.getCustomFoods();
    final dailyArchived = HiveStorage.getDailySummaries();
    final monthly = HiveStorage.getMonthlySummaries();
    final yearly = HiveStorage.getYearlySummaries();
    final weights = HiveStorage.getWeightHistory();
    final water = HiveStorage.getAllWaterEntries();
    final burned = HiveStorage.getAllBurnedEntries();
    final legal = HiveStorage.getLegalAcceptance();
    final insights = InsightsService.aggregateInsights();

    final payload = <String, dynamic>{
      // ── Profile ──────────────────────────────────────────────────────────
      'profile': profile != null ? BackupSerializers.profileToJson(profile) : null,

      // ── Settings & preferences ───────────────────────────────────────────
      'settings': HiveStorage.exportSettingsSnapshot(),

      // ── Nutrition ────────────────────────────────────────────────────────
      'nutrition': {
        'foodLogs': meals.map(BackupSerializers.mealToJson).toList(),
        'customFoods': customFoods.map(BackupSerializers.foodToJson).toList(),
        'dailySummaries': dailyArchived.map((d) => d.toJson()).toList(),
        'monthlySummaries': monthly.map(BackupSerializers.monthlyToJson).toList(),
        'yearlySummaries': yearly.map((y) => y.toJson()).toList(),
      },

      // ── Hydration ────────────────────────────────────────────────────────
      'hydration': {
        'waterLogs': water, // {dateKey: ml}
      },

      // ── Energy / activity ────────────────────────────────────────────────
      'activity': {
        'burnedLogs': burned, // {dateKey: kcal}
      },

      // ── Weight & BMI ─────────────────────────────────────────────────────
      'weight': {
        'history': weights.map((w) => w.toJson()).toList(),
      },

      // ── Health snapshot (derived; recomputable, kept for portability) ─────
      'health': {
        'currentStreak': AnalyticsService.computeStreak(),
        'longestStreak': insights.longestStreak,
        'avgScore': insights.avgScore,
        'goalAchievementPct': insights.goalAchievementPct,
        'trend': insights.trend,
        'totalDaysLogged': insights.totalDaysLogged,
      },

      // ── Legal acceptance (so a restored device stays compliant) ──────────
      'legal': legal != null
          ? {
              'acceptedAt': legal.acceptedAt.toIso8601String(),
              'policyVersion': legal.policyVersion,
              'appVersion': legal.appVersion,
              'termsAccepted': legal.termsAccepted,
              'healthDisclaimerAccepted': legal.healthDisclaimerAccepted,
            }
          : null,
    };

    final counts = <String, int>{
      'foodLogs': meals.length,
      'customFoods': customFoods.length,
      'dailySummaries': dailyArchived.length,
      'monthlySummaries': monthly.length,
      'yearlySummaries': yearly.length,
      'waterLogs': water.length,
      'weightEntries': weights.length,
    };

    return (payload: payload, counts: counts);
  }
}
