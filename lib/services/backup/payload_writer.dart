import '../../models/daily_summary.dart';
import '../../models/legal_acceptance.dart';
import '../../models/weight_entry.dart';
import '../../models/yearly_summary.dart';
import '../../storage/hive_storage.dart';
import 'backup_serializers.dart';
import 'backup_types.dart';

/// The only place that actually mutates Hive boxes during a restore/import or a
/// rollback. Kept separate from the orchestration engines so both the restore
/// path and the safety-snapshot rollback can share identical, well-tested write
/// logic. All methods are idempotent at the record level (keyed puts).
class PayloadWriter {
  // ── REPLACE: wipe user data, then write the backup verbatim ────────────────

  static Future<void> applyReplace(Map<String, dynamic> payload) async {
    // Clear all mutable user boxes (localFoodBox = immutable app data, kept).
    await HiveStorage.userBox.clear();
    await HiveStorage.mealsBox.clear();
    await HiveStorage.monthlySummaryBox.clear();
    await HiveStorage.dailySummaryBox.clear();
    await HiveStorage.yearlySummaryBox.clear();
    await HiveStorage.weightHistoryBox.clear();
    await _clearWaterBurnedKeys();

    await _writeProfile(payload, overwrite: true);
    await _writeSettings(payload, overwrite: true);
    await _writeCustomFoods(payload, overwrite: true);
    await _writeMeals(payload, overwrite: true, report: null);
    await _writeDailySummaries(payload, overwrite: true, report: null);
    await _writeMonthlySummaries(payload, overwrite: true, report: null);
    await _writeYearlySummaries(payload, overwrite: true, report: null);
    await _writeWater(payload, overwrite: true, report: null);
    await _writeBurned(payload, overwrite: true);
    await _writeWeight(payload, overwrite: true, report: null);
    await _writeLegal(payload, overwrite: true);
  }

  // ── MERGE: keep current data, fold in the backup with de-duplication ───────

  static Future<MergeReport> applyMerge(Map<String, dynamic> payload) async {
    final report = MergeReport();
    // Profile/settings only fill gaps in merge mode — never clobber the device.
    await _writeProfile(payload, overwrite: false);
    await _writeSettings(payload, overwrite: false);
    await _writeCustomFoods(payload, overwrite: false);
    await _writeMeals(payload, overwrite: false, report: report);
    await _writeDailySummaries(payload, overwrite: false, report: report);
    await _writeMonthlySummaries(payload, overwrite: false, report: report);
    await _writeYearlySummaries(payload, overwrite: false, report: report);
    await _writeWater(payload, overwrite: false, report: report);
    await _writeBurned(payload, overwrite: false);
    await _writeWeight(payload, overwrite: false, report: report);
    return report;
  }

  // ── Section writers ────────────────────────────────────────────────────────

  static Map<String, dynamic> _nutrition(Map<String, dynamic> p) =>
      (p['nutrition'] as Map?)?.cast<String, dynamic>() ?? const {};

  static Future<void> _writeProfile(Map<String, dynamic> p,
      {required bool overwrite}) async {
    final m = p['profile'];
    if (m is! Map) return;
    if (!overwrite && HiveStorage.getUserProfile() != null) return;
    await HiveStorage.saveUserProfile(
        BackupSerializers.profileFromJson(m.cast<String, dynamic>()));
  }

  static Future<void> _writeSettings(Map<String, dynamic> p,
      {required bool overwrite}) async {
    final s = p['settings'];
    if (s is! Map) return;
    final box = HiveStorage.settingsBox;
    s.forEach((k, v) {
      if (k is! String) return;
      if (v == null) return;
      if (!overwrite && box.containsKey(k)) return;
      box.put(k, v);
    });
  }

  static Future<void> _writeCustomFoods(Map<String, dynamic> p,
      {required bool overwrite}) async {
    final list = (_nutrition(p)['customFoods'] as List?) ?? const [];
    for (final raw in list) {
      if (raw is! Map) continue;
      final food = BackupSerializers.foodFromJson(raw);
      if (!overwrite && HiveStorage.localFoodBox.containsKey(food.id)) continue;
      await HiveStorage.saveCustomFood(food);
    }
  }

  static Future<void> _writeMeals(Map<String, dynamic> p,
      {required bool overwrite, MergeReport? report}) async {
    final list = (_nutrition(p)['foodLogs'] as List?) ?? const [];
    for (final raw in list) {
      if (raw is! Map) continue;
      final meal = BackupSerializers.mealFromJson(raw);
      final exists = HiveStorage.mealsBox.containsKey(meal.id);
      if (!overwrite && exists) {
        report?.skipOne('foodLogs');
        continue;
      }
      await HiveStorage.addMealEntry(meal);
      report?.addOne('foodLogs');
    }
  }

  static Future<void> _writeDailySummaries(Map<String, dynamic> p,
      {required bool overwrite, MergeReport? report}) async {
    final list = (_nutrition(p)['dailySummaries'] as List?) ?? const [];
    for (final raw in list) {
      if (raw is! Map) continue;
      final s = DailySummary.fromJson(raw.cast<String, dynamic>());
      if (s.dateKey.isEmpty) continue;
      final exists = HiveStorage.getDailySummary(s.dateKey) != null;
      if (!overwrite && exists) {
        report?.skipOne('dailySummaries');
        continue;
      }
      await HiveStorage.saveDailySummary(s);
      report?.addOne('dailySummaries');
    }
  }

  static Future<void> _writeMonthlySummaries(Map<String, dynamic> p,
      {required bool overwrite, MergeReport? report}) async {
    final list = (_nutrition(p)['monthlySummaries'] as List?) ?? const [];
    for (final raw in list) {
      if (raw is! Map) continue;
      final s = BackupSerializers.monthlyFromJson(raw);
      final exists = HiveStorage.getMonthlySummary(s.year, s.month) != null;
      if (!overwrite && exists) {
        report?.skipOne('monthlySummaries');
        continue;
      }
      await HiveStorage.saveMonthlySummary(s);
      report?.addOne('monthlySummaries');
    }
  }

  static Future<void> _writeYearlySummaries(Map<String, dynamic> p,
      {required bool overwrite, MergeReport? report}) async {
    final list = (_nutrition(p)['yearlySummaries'] as List?) ?? const [];
    for (final raw in list) {
      if (raw is! Map) continue;
      final s = YearlySummary.fromJson(raw.cast<String, dynamic>());
      final exists = HiveStorage.getYearlySummary(s.year) != null;
      if (!overwrite && exists) {
        report?.skipOne('yearlySummaries');
        continue;
      }
      await HiveStorage.saveYearlySummary(s);
      report?.addOne('yearlySummaries');
    }
  }

  static Future<void> _writeWater(Map<String, dynamic> p,
      {required bool overwrite, MergeReport? report}) async {
    final h = (p['hydration'] as Map?)?.cast<String, dynamic>() ?? const {};
    final logs = (h['waterLogs'] as Map?) ?? const {};
    logs.forEach((k, v) {
      if (k is! String || v is! num) return;
      final exists = HiveStorage.getWaterMl(k) > 0;
      if (!overwrite && exists) {
        report?.skipOne('waterLogs');
        return;
      }
      HiveStorage.saveWaterMl(k, v.toDouble());
      report?.addOne('waterLogs');
    });
  }

  static Future<void> _writeBurned(Map<String, dynamic> p,
      {required bool overwrite}) async {
    final a = (p['activity'] as Map?)?.cast<String, dynamic>() ?? const {};
    final logs = (a['burnedLogs'] as Map?) ?? const {};
    logs.forEach((k, v) {
      if (k is! String || v is! num) return;
      if (!overwrite && HiveStorage.getBurnedCalories(k) > 0) return;
      HiveStorage.saveBurnedCalories(k, v.toDouble());
    });
  }

  static Future<void> _writeWeight(Map<String, dynamic> p,
      {required bool overwrite, MergeReport? report}) async {
    final w = (p['weight'] as Map?)?.cast<String, dynamic>() ?? const {};
    final list = (w['history'] as List?) ?? const [];
    for (final raw in list) {
      if (raw is! Map) continue;
      final e = WeightEntry.fromJson(raw.cast<String, dynamic>());
      final exists = HiveStorage.weightHistoryBox.containsKey(e.dateKey);
      if (!overwrite && exists) {
        report?.skipOne('weightEntries');
        continue;
      }
      await HiveStorage.saveWeightEntry(e);
      report?.addOne('weightEntries');
    }
  }

  static Future<void> _writeLegal(Map<String, dynamic> p,
      {required bool overwrite}) async {
    final l = p['legal'];
    if (l is! Map) return;
    if (!overwrite && HiveStorage.isLegalAccepted) return;
    await HiveStorage.saveLegalAcceptance(LegalAcceptance(
      acceptedAt: DateTime.tryParse(l['acceptedAt']?.toString() ?? '') ?? DateTime.now(),
      policyVersion: l['policyVersion']?.toString() ?? '1.0.0',
      appVersion: l['appVersion']?.toString() ?? '1.0.0',
      termsAccepted: (l['termsAccepted'] as bool?) ?? true,
      healthDisclaimerAccepted: (l['healthDisclaimerAccepted'] as bool?) ?? true,
    ));
  }

  static Future<void> _clearWaterBurnedKeys() async {
    final box = HiveStorage.settingsBox;
    final keys = box.keys
        .whereType<String>()
        .where((k) => k.startsWith('water_') || k.startsWith('burned_'))
        .toList();
    await box.deleteAll(keys);
  }
}
