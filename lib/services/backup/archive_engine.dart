import 'dart:convert';
import 'dart:math';
import 'package:flutter/foundation.dart';
import '../../core/constants/app_constants.dart';
import '../../models/daily_summary.dart';
import '../../models/meal_entry.dart';
import '../../models/monthly_summary.dart';
import '../../models/yearly_summary.dart';
import '../../storage/hive_storage.dart';
import 'backup_serializers.dart';
import 'backup_types.dart';
import 'insights_service.dart';
import 'integrity_service.dart';

enum ArchiveLevel { level1, level2, level3 }

/// A description of what one archive level *would* compress, shown to the user
/// before any data is touched (the spec forbids silent deletion).
class ArchiveCandidate {
  final ArchiveLevel level;
  final String title;
  final String description;
  final int recordsAffected;
  final int estimatedBytesSaved;

  const ArchiveCandidate({
    required this.level,
    required this.title,
    required this.description,
    required this.recordsAffected,
    required this.estimatedBytesSaved,
  });

  bool get hasWork => recordsAffected > 0;
}

/// Long-term data lifecycle engine.
///
/// Level 1 (>12 mo): meal-level food logs  → daily summaries
/// Level 2 (>24 mo): daily summaries       → monthly summaries
/// Level 3 (>5 yr):  monthly summaries     → yearly summaries
///
/// Every run is wrapped in a [SafetySnapshot]; meal/summary deletion happens
/// only *after* the compressed record is written, and rolls back on any error.
class ArchiveEngine {
  // ── Analysis (read-only, safe to call anytime) ─────────────────────────────

  static List<ArchiveCandidate> analyze() {
    return [
      _analyzeLevel1(),
      _analyzeLevel2(),
      _analyzeLevel3(),
    ];
  }

  static ArchiveCandidate _analyzeLevel1() {
    final cutoff = DateTime.now().subtract(const Duration(days: AppConstants.activeDataDays));
    final old = HiveStorage.getMealsOlderThan(cutoff);
    final days = old.map((m) => m.dateKey).toSet().length;
    final rawBytes = _bytesOf(old.map(BackupSerializers.mealToJson).toList());
    final newBytes = days * 90; // ~90 bytes per compact daily summary
    return ArchiveCandidate(
      level: ArchiveLevel.level1,
      title: 'Meal logs older than 12 months',
      description:
          'Compress ${old.length} detailed food logs into $days daily summaries.',
      recordsAffected: old.length,
      estimatedBytesSaved: max(0, rawBytes - newBytes),
    );
  }

  static ArchiveCandidate _analyzeLevel2() {
    final cutoff = DateTime.now().subtract(const Duration(days: AppConstants.archiveLevel2Days));
    final old =
        HiveStorage.getDailySummaries().where((d) => d.date.isBefore(cutoff)).toList();
    final months = old.map((d) => d.monthKey).toSet().length;
    final rawBytes = _bytesOf(old.map((d) => d.toJson()).toList());
    return ArchiveCandidate(
      level: ArchiveLevel.level2,
      title: 'Daily summaries older than 24 months',
      description:
          'Compress ${old.length} daily summaries into $months monthly summaries.',
      recordsAffected: old.length,
      estimatedBytesSaved: max(0, rawBytes - months * 80),
    );
  }

  static ArchiveCandidate _analyzeLevel3() {
    final cutoffYear = DateTime.now().subtract(const Duration(days: AppConstants.archiveLevel3Days)).year;
    final old =
        HiveStorage.getMonthlySummaries().where((m) => m.year < cutoffYear).toList();
    final years = old.map((m) => m.year).toSet().length;
    final rawBytes = _bytesOf(old.map(BackupSerializers.monthlyToJson).toList());
    return ArchiveCandidate(
      level: ArchiveLevel.level3,
      title: 'Monthly summaries older than 5 years',
      description:
          'Compress ${old.length} monthly summaries into $years yearly summaries.',
      recordsAffected: old.length,
      estimatedBytesSaved: max(0, rawBytes - years * 70),
    );
  }

  // ── Execution (destructive — always snapshot-guarded) ──────────────────────

  static Future<BackupOutcome> run(ArchiveLevel level,
      {ProgressCallback? onProgress}) async {
    onProgress?.call(const BackupProgress(0.1, 'Creating safety snapshot…'));
    SafetySnapshot? snapshot;
    try {
      snapshot = await IntegrityService.createSnapshot();
    } catch (e) {
      return BackupOutcome.failure('Could not create a safety snapshot — archive aborted.');
    }

    try {
      onProgress?.call(const BackupProgress(0.4, 'Compressing records…'));
      final int affected;
      switch (level) {
        case ArchiveLevel.level1:
          affected = await _runLevel1(onProgress: onProgress);
          break;
        case ArchiveLevel.level2:
          affected = await _runLevel2(onProgress: onProgress);
          break;
        case ArchiveLevel.level3:
          affected = await _runLevel3(onProgress: onProgress);
          break;
      }
      await HiveStorage.setLastArchiveAt(DateTime.now());
      await snapshot.dispose();
      onProgress?.call(const BackupProgress(1.0, 'Done'));
      return BackupOutcome(success: true, counts: {'archived': affected});
    } catch (e) {
      debugPrint('[ArchiveEngine] archive failed, rolling back: $e');
      final ok = await snapshot.restore();
      await snapshot.dispose();
      return BackupOutcome.failure(ok
          ? 'Archiving failed — your data was safely restored.'
          : 'Archiving failed and rollback could not complete.');
    }
  }

  // Level 1: meals → daily summaries.
  static Future<int> _runLevel1({ProgressCallback? onProgress}) async {
    final cutoff = DateTime.now().subtract(const Duration(days: AppConstants.activeDataDays));
    final old = HiveStorage.getMealsOlderThan(cutoff);
    if (old.isEmpty) return 0;

    final goals = InsightsService.goalsFor(HiveStorage.getUserProfile());
    final byDay = <String, List<MealEntry>>{};
    for (final m in old) {
      byDay.putIfAbsent(m.dateKey, () => []).add(m);
    }
    final water = HiveStorage.getAllWaterEntries();

    int completed = 0;
    for (final entry in byDay.entries) {
      final dk = entry.key;
      final meals = entry.value;
      // Merge with any existing summary for that day (in case of partial archive).
      final existing = HiveStorage.getDailySummary(dk);
      final kcal = meals.fold<double>(0, (s, m) => s + m.calories) + (existing?.kcal ?? 0);
      final protein = meals.fold<double>(0, (s, m) => s + m.proteinG) + (existing?.protein ?? 0);
      final carbs = meals.fold<double>(0, (s, m) => s + m.carbsG) + (existing?.carbs ?? 0);
      final fat = meals.fold<double>(0, (s, m) => s + m.fatG) + (existing?.fat ?? 0);
      final fiber = meals.fold<double>(0, (s, m) => s + m.fiberG) + (existing?.fiber ?? 0);
      final waterMl = water[dk] ?? existing?.waterMl ?? 0;
      final mealCount = meals.length + (existing?.mealCount ?? 0);
      final date = _parseDayKey(dk);

      await HiveStorage.saveDailySummary(DailySummary(
        dateKey: dk,
        date: date,
        kcal: kcal,
        protein: protein,
        carbs: carbs,
        fat: fat,
        fiber: fiber,
        waterMl: waterMl,
        score: InsightsService.dayScore(
          kcal: kcal,
          protein: protein,
          fiber: fiber,
          waterMl: waterMl,
          mealCount: mealCount,
          goals: goals,
        ),
        mealCount: mealCount,
      ));
      completed++;
      onProgress?.call(BackupProgress(
        0.4 + 0.55 * (completed / byDay.length),
        'Compressing day $completed of ${byDay.length}…',
      ));
    }

    // Delete meals ONLY after all summaries are safely written.
    await HiveStorage.deleteMealEntriesByIds(old.map((m) => m.id).toList());
    return old.length;
  }

  // Level 2: daily summaries → monthly summaries.
  static Future<int> _runLevel2({ProgressCallback? onProgress}) async {
    final cutoff = DateTime.now().subtract(const Duration(days: AppConstants.archiveLevel2Days));
    final old =
        HiveStorage.getDailySummaries().where((d) => d.date.isBefore(cutoff)).toList();
    if (old.isEmpty) return 0;

    final byMonth = <String, List<DailySummary>>{};
    for (final d in old) {
      byMonth.putIfAbsent(d.monthKey, () => []).add(d);
    }

    int completed = 0;
    for (final entry in byMonth.entries) {
      final days = entry.value;
      final logged = days.where((d) => d.mealCount > 0).toList();
      final n = max(logged.length, 1);
      final first = days.first.date;
      if (HiveStorage.getMonthlySummary(first.year, first.month) != null) continue;
      final daysInMonth = DateTime(first.year, first.month + 1, 0).day;
      await HiveStorage.saveMonthlySummary(MonthlySummary(
        year: first.year,
        month: first.month,
        avgCalories: logged.fold<double>(0, (s, d) => s + d.kcal) / n,
        avgProtein: logged.fold<double>(0, (s, d) => s + d.protein) / n,
        avgCarbs: logged.fold<double>(0, (s, d) => s + d.carbs) / n,
        avgFat: logged.fold<double>(0, (s, d) => s + d.fat) / n,
        avgFiber: logged.fold<double>(0, (s, d) => s + d.fiber) / n,
        consistencyScore: logged.length / max(daysInMonth, 1),
        daysLogged: logged.length,
      ));
      completed++;
      onProgress?.call(BackupProgress(
        0.4 + 0.55 * (completed / byMonth.length),
        'Compressing month $completed of ${byMonth.length}…',
      ));
    }

    await HiveStorage.dailySummaryBox.deleteAll(old.map((d) => d.dateKey));
    return old.length;
  }

  // Level 3: monthly summaries → yearly summaries.
  static Future<int> _runLevel3({ProgressCallback? onProgress}) async {
    final cutoffYear =
        DateTime.now().subtract(const Duration(days: AppConstants.archiveLevel3Days)).year;
    final old =
        HiveStorage.getMonthlySummaries().where((m) => m.year < cutoffYear).toList();
    if (old.isEmpty) return 0;

    final weights = HiveStorage.getWeightHistory();
    final water = HiveStorage.getAllWaterEntries();
    final byYear = <int, List<MonthlySummary>>{};
    for (final m in old) {
      byYear.putIfAbsent(m.year, () => []).add(m);
    }

    int completed = 0;
    for (final entry in byYear.entries) {
      final year = entry.key;
      final months = entry.value;
      final n = max(months.length, 1);
      final inYear = weights.where((w) => w.recordedAt.year == year).toList()
        ..sort((a, b) => a.recordedAt.compareTo(b.recordedAt));
      final weightChange =
          inYear.length >= 2 ? inYear.last.weightKg - inYear.first.weightKg : 0.0;

      final yearWaterValues = water.entries
          .where((e) {
            final parts = e.key.split('_');
            return parts.length == 3 && int.tryParse(parts[0]) == year;
          })
          .map((e) => e.value)
          .toList();
      final avgWater = yearWaterValues.isEmpty
          ? 0.0
          : yearWaterValues.fold(0.0, (s, v) => s + v) / yearWaterValues.length;

      await HiveStorage.saveYearlySummary(YearlySummary(
        year: year,
        avgKcal: months.fold<double>(0, (s, m) => s + m.avgCalories) / n,
        avgProtein: months.fold<double>(0, (s, m) => s + m.avgProtein) / n,
        avgCarbs: months.fold<double>(0, (s, m) => s + m.avgCarbs) / n,
        avgFat: months.fold<double>(0, (s, m) => s + m.avgFat) / n,
        avgWater: double.parse(avgWater.toStringAsFixed(1)),
        avgScore: months.fold<double>(0, (s, m) => s + m.consistencyScore * 100) / n,
        weightChange: double.parse(weightChange.toStringAsFixed(1)),
        daysLogged: months.fold<int>(0, (s, m) => s + m.daysLogged),
      ));
      completed++;
      onProgress?.call(BackupProgress(
        0.4 + 0.55 * (completed / byYear.length),
        'Compressing year $completed of ${byYear.length}…',
      ));
    }

    await HiveStorage.deleteMonthlySummariesByKeys(old.map((m) => m.key).toList());
    return old.length;
  }

  // ── helpers ────────────────────────────────────────────────────────────────

  static int _bytesOf(List<Map<String, dynamic>> records) =>
      utf8.encode(jsonEncode(records)).length;

  static DateTime _parseDayKey(String key) {
    final p = key.split('_');
    if (p.length == 3) {
      return DateTime(int.tryParse(p[0]) ?? 2000, int.tryParse(p[1]) ?? 1,
          int.tryParse(p[2]) ?? 1);
    }
    return DateTime(2000);
  }
}
