import 'package:flutter/foundation.dart';
import 'package:hive_flutter/hive_flutter.dart';
import '../models/user_profile.dart';
import '../models/food_item.dart';
import '../models/meal_entry.dart';
import '../models/monthly_summary.dart';
import '../models/legal_acceptance.dart';
import '../models/weight_entry.dart';
import '../models/daily_summary.dart';
import '../models/yearly_summary.dart';
import '../core/constants/app_constants.dart';

class HiveStorage {
  // Named subfolder keeps user data isolated and clearly scoped to this app.
  // Hive places it inside the OS-managed app documents directory, so data
  // survives upgrades automatically and is wiped when the user uninstalls.
  static const _dataFolder = 'infinite_health_data';
  static bool _initialized = false;

  static Future<void> init() async {
    if (_initialized) return; // idempotent — safe to call on hot-restart / re-launch
    try {
      await Hive.initFlutter(_dataFolder);
    } catch (e) {
      debugPrint('[HiveStorage] initFlutter warning: $e');
    }
    _registerAdapters();
    await _openBoxesSafely();
    _initialized = true;
  }

  static void _registerAdapters() {
    if (!Hive.isAdapterRegistered(0)) Hive.registerAdapter(UserProfileAdapter());
    if (!Hive.isAdapterRegistered(1)) Hive.registerAdapter(FoodItemAdapter());
    if (!Hive.isAdapterRegistered(2)) Hive.registerAdapter(MealEntryAdapter());
    if (!Hive.isAdapterRegistered(3)) Hive.registerAdapter(MonthlySummaryAdapter());
    if (!Hive.isAdapterRegistered(4)) Hive.registerAdapter(LegalAcceptanceAdapter());
    if (!Hive.isAdapterRegistered(5)) Hive.registerAdapter(WeightEntryAdapter());
    if (!Hive.isAdapterRegistered(6)) Hive.registerAdapter(DailySummaryAdapter());
    if (!Hive.isAdapterRegistered(7)) Hive.registerAdapter(YearlySummaryAdapter());
  }

  // Opens every box individually so one corrupt box cannot block the others.
  // If a box fails to open, it is deleted from disk and recreated empty —
  // user data in that box is lost but the app stays functional.
  static Future<void> _openBoxesSafely() async {
    await _safeOpen(AppConstants.hiveUserBox,            () => Hive.openBox(AppConstants.hiveUserBox));
    await _safeOpen(AppConstants.hiveMealsBox,           () => Hive.openBox<MealEntry>(AppConstants.hiveMealsBox));
    await _safeOpen(AppConstants.hiveFoodCacheBox,       () => Hive.openBox<FoodItem>(AppConstants.hiveFoodCacheBox));
    await _safeOpen(AppConstants.hiveLocalFoodBox,       () => Hive.openBox<FoodItem>(AppConstants.hiveLocalFoodBox));
    await _safeOpen(AppConstants.hiveSettingsBox,        () => Hive.openBox(AppConstants.hiveSettingsBox));
    await _safeOpen(AppConstants.hiveMonthlySummaryBox,  () => Hive.openBox<MonthlySummary>(AppConstants.hiveMonthlySummaryBox));
    await _safeOpen(AppConstants.hiveLegalBox,           () => Hive.openBox(AppConstants.hiveLegalBox));
    await _safeOpen(AppConstants.hiveWeightHistoryBox,   () => Hive.openBox<WeightEntry>(AppConstants.hiveWeightHistoryBox));
    await _safeOpen(AppConstants.hiveDailySummaryBox,    () => Hive.openBox<DailySummary>(AppConstants.hiveDailySummaryBox));
    await _safeOpen(AppConstants.hiveYearlySummaryBox,   () => Hive.openBox<YearlySummary>(AppConstants.hiveYearlySummaryBox));
  }

  static Future<void> _safeOpen(String name, Future<dynamic> Function() open) async {
    if (Hive.isBoxOpen(name)) return;
    try {
      await open();
    } catch (e) {
      debugPrint('[HiveStorage] box "$name" failed ($e) — deleting and recreating');
      try {
        await Hive.deleteBoxFromDisk(name);
        await open();
        debugPrint('[HiveStorage] box "$name" recreated successfully');
      } catch (e2) {
        debugPrint('[HiveStorage] box "$name" unrecoverable: $e2');
      }
    }
  }

  // Box accessors
  static Box get userBox => Hive.box(AppConstants.hiveUserBox);
  static Box<MealEntry> get mealsBox => Hive.box<MealEntry>(AppConstants.hiveMealsBox);
  static Box<FoodItem> get foodCacheBox => Hive.box<FoodItem>(AppConstants.hiveFoodCacheBox);
  static Box<FoodItem> get localFoodBox => Hive.box<FoodItem>(AppConstants.hiveLocalFoodBox);
  static Box get settingsBox => Hive.box(AppConstants.hiveSettingsBox);
  static Box<MonthlySummary> get monthlySummaryBox =>
      Hive.box<MonthlySummary>(AppConstants.hiveMonthlySummaryBox);
  static Box get legalBox => Hive.box(AppConstants.hiveLegalBox);
  static Box<WeightEntry> get weightHistoryBox =>
      Hive.box<WeightEntry>(AppConstants.hiveWeightHistoryBox);
  static Box<DailySummary> get dailySummaryBox =>
      Hive.box<DailySummary>(AppConstants.hiveDailySummaryBox);
  static Box<YearlySummary> get yearlySummaryBox =>
      Hive.box<YearlySummary>(AppConstants.hiveYearlySummaryBox);

  // ── User Profile ─────────────────────────────────────────────────────────

  static UserProfile? getUserProfile() {
    final data = userBox.get(AppConstants.keyUserProfile);
    if (data is UserProfile) return data;
    return null;
  }

  static Future<void> saveUserProfile(UserProfile profile) async {
    await userBox.put(AppConstants.keyUserProfile, profile);
  }

  // ── Settings ─────────────────────────────────────────────────────────────

  static bool get isOnboardingDone =>
      settingsBox.get(AppConstants.keyOnboardingDone, defaultValue: false) as bool;

  static Future<void> setOnboardingDone() async {
    await settingsBox.put(AppConstants.keyOnboardingDone, true);
  }

  static String get themeMode =>
      settingsBox.get(AppConstants.keyThemeMode, defaultValue: 'system') as String;

  static Future<void> saveThemeMode(String mode) async {
    await settingsBox.put(AppConstants.keyThemeMode, mode);
  }

  static String get language =>
      settingsBox.get(AppConstants.keyLanguage, defaultValue: 'en') as String;

  static Future<void> saveLanguage(String lang) async {
    await settingsBox.put(AppConstants.keyLanguage, lang);
  }

  // ── Meal Entries ──────────────────────────────────────────────────────────

  static List<MealEntry> getMealsForDate(String dateKey) {
    return mealsBox.values.where((m) => m.dateKey == dateKey).toList()
      ..sort((a, b) => a.loggedAt.compareTo(b.loggedAt));
  }

  static List<MealEntry> getAllMealEntries() {
    return mealsBox.values.toList();
  }

  static List<MealEntry> getMealsOlderThan(DateTime cutoff) {
    return mealsBox.values
        .where((m) => m.loggedAt.isBefore(cutoff))
        .toList();
  }

  static Future<void> addMealEntry(MealEntry entry) async {
    await mealsBox.put(entry.id, entry);
  }

  static Future<void> deleteMealEntry(String id) async {
    await mealsBox.delete(id);
  }

  static Future<void> updateMealEntry(MealEntry entry) async {
    await mealsBox.put(entry.id, entry);
  }

  static Future<void> deleteMealEntriesByIds(List<String> ids) async {
    await mealsBox.deleteAll(ids);
  }

  // ── Food Cache ────────────────────────────────────────────────────────────

  static Future<void> cacheFoodItem(FoodItem food) async {
    // Use fdcId as key for USDA foods to prevent duplicate cache entries
    final key = food.usdaFdcId ?? food.id;
    if (foodCacheBox.containsKey(key)) {
      await foodCacheBox.put(key, food);
      return;
    }
    if (foodCacheBox.length >= AppConstants.maxCachedFoods &&
        foodCacheBox.isNotEmpty) {
      await foodCacheBox.delete(foodCacheBox.keys.first);
    }
    await foodCacheBox.put(key, food);
  }

  static List<FoodItem> getCachedFoods() {
    return foodCacheBox.values.toList();
  }

  /// Searches local food cache by name/brand — used before hitting the API.
  static List<FoodItem> searchLocalCache(String query) {
    final q = query.toLowerCase().trim();
    if (q.isEmpty) return [];
    final all = foodCacheBox.values
        .where((f) =>
            f.name.toLowerCase().contains(q) ||
            (f.brand?.toLowerCase().contains(q) ?? false))
        .toList();
    // Prioritise exact name-starts-with matches first
    all.sort((a, b) {
      final aStarts = a.name.toLowerCase().startsWith(q) ? 0 : 1;
      final bStarts = b.name.toLowerCase().startsWith(q) ? 0 : 1;
      return aStarts.compareTo(bStarts);
    });
    return all.take(20).toList();
  }

  static Future<void> clearCache() async {
    await foodCacheBox.clear();
  }

  // ── Monthly Summaries ─────────────────────────────────────────────────────

  static List<MonthlySummary> getMonthlySummaries() {
    return monthlySummaryBox.values.toList()
      ..sort((a, b) {
        final aKey = a.year * 100 + a.month;
        final bKey = b.year * 100 + b.month;
        return bKey.compareTo(aKey);
      });
  }

  static MonthlySummary? getMonthlySummary(int year, int month) {
    final key = '${year}_${month.toString().padLeft(2, '0')}';
    return monthlySummaryBox.get(key);
  }

  static Future<void> saveMonthlySummary(MonthlySummary summary) async {
    await monthlySummaryBox.put(summary.key, summary);
  }

  // ── Legal Acceptance ──────────────────────────────────────────────────────

  static LegalAcceptance? getLegalAcceptance() {
    final data = legalBox.get(AppConstants.keyLegalAcceptance);
    if (data is LegalAcceptance) return data;
    return null;
  }

  static Future<void> saveLegalAcceptance(LegalAcceptance acceptance) async {
    await legalBox.put(AppConstants.keyLegalAcceptance, acceptance);
  }

  static bool get isLegalAccepted =>
      legalBox.get(AppConstants.keyLegalAcceptance) is LegalAcceptance;

  /// Returns true when the stored policy version differs from the current one,
  /// requiring the user to re-accept the updated terms.
  static bool get needsPolicyReAcceptance {
    final stored = getLegalAcceptance();
    if (stored == null) return false;
    return stored.policyVersion != AppConstants.currentPolicyVersion;
  }

  // ── Notification Settings ────────────────────────────────────────────────

  static bool get notificationEnabled =>
      settingsBox.get(AppConstants.keyNotifEnabled, defaultValue: true) as bool;

  static int get notificationHour =>
      settingsBox.get(AppConstants.keyNotifHour, defaultValue: 18) as int;

  static int get notificationMinute =>
      settingsBox.get(AppConstants.keyNotifMinute, defaultValue: 0) as int;

  static Future<void> setNotificationEnabled(bool enabled) =>
      settingsBox.put(AppConstants.keyNotifEnabled, enabled);

  static Future<void> setNotificationTime(int hour, int minute) async {
    await settingsBox.put(AppConstants.keyNotifHour, hour);
    await settingsBox.put(AppConstants.keyNotifMinute, minute);
  }

  // ── Reset ─────────────────────────────────────────────────────────────────

  // ── Local Dataset ─────────────────────────────────────────────────────────

  static bool get isLocalDatasetLoaded =>
      settingsBox.get(AppConstants.keyLocalDatasetLoaded, defaultValue: false) as bool;

  // ── Custom Foods ──────────────────────────────────────────────────────────

  static List<FoodItem> getCustomFoods() {
    return localFoodBox.values
        .where((f) => f.isCustom || f.source == 'custom')
        .toList()
      ..sort((a, b) => a.name.toLowerCase().compareTo(b.name.toLowerCase()));
  }

  static Future<void> saveCustomFood(FoodItem food) async {
    await localFoodBox.put(food.id, food);
  }

  static Future<void> deleteCustomFood(String id) async {
    await localFoodBox.delete(id);
  }

  // ── Saved USDA Foods (user-selected from International search) ────────────

  static Future<void> saveUsdaFood(FoodItem food) async {
    final key = 'usda_${food.usdaFdcId ?? food.id}';
    await localFoodBox.put(key, food);
  }

  static List<FoodItem> getSavedUsdaFoods() {
    return localFoodBox.values
        .where((f) => f.source == 'usda' && !f.isCustom)
        .toList()
      ..sort((a, b) => a.name.toLowerCase().compareTo(b.name.toLowerCase()));
  }

  static Future<void> deleteSavedUsdaFood(String fdcId) async {
    await localFoodBox.delete('usda_$fdcId');
  }

  static Future<void> setLocalDatasetLoaded() async {
    await settingsBox.put(AppConstants.keyLocalDatasetLoaded, true);
  }

  // ── Water Intake (per-day, stored in settingsBox) ────────────────────────

  static double getWaterMl(String dateKey) =>
      (settingsBox.get('water_$dateKey', defaultValue: 0.0) as num).toDouble();

  static Future<void> saveWaterMl(String dateKey, double ml) async =>
      settingsBox.put('water_$dateKey', ml.clamp(0, 5000));

  // ── Activity Burned Calories (per-day) ───────────────────────────────────

  static double getBurnedCalories(String dateKey) =>
      (settingsBox.get('burned_$dateKey', defaultValue: 0.0) as num).toDouble();

  static Future<void> saveBurnedCalories(String dateKey, double kcal) async =>
      settingsBox.put('burned_$dateKey', kcal.clamp(0, 5000));

  static bool get deductBurnedCalories =>
      settingsBox.get('deductBurnedCalories', defaultValue: false) as bool;

  static Future<void> setDeductBurnedCalories(bool v) async =>
      settingsBox.put('deductBurnedCalories', v);

  // ── USDA User API Key ─────────────────────────────────────────────────────

  static String? get userApiKey {
    final v = settingsBox.get(AppConstants.keyUserApiKey);
    return v is String && v.isNotEmpty ? v : null;
  }

  static Future<void> saveUserApiKey(String key) async =>
      settingsBox.put(AppConstants.keyUserApiKey, key.trim());

  static Future<void> clearUserApiKey() async =>
      settingsBox.delete(AppConstants.keyUserApiKey);

  // ── Custom Nutrition Limits ──────────────────────────────────────────────

  static bool get useCustomLimits =>
      settingsBox.get('useCustomLimits', defaultValue: false) as bool;

  static Future<void> setUseCustomLimits(bool v) async =>
      settingsBox.put('useCustomLimits', v);

  static double? get customCalories {
    final v = settingsBox.get('customCalories');
    return v is num ? v.toDouble() : null;
  }

  static Future<void> saveCustomCalories(double? v) async => v == null
      ? settingsBox.delete('customCalories')
      : settingsBox.put('customCalories', v);

  static double? get customProteinG {
    final v = settingsBox.get('customProteinG');
    return v is num ? v.toDouble() : null;
  }

  static Future<void> saveCustomProteinG(double? v) async => v == null
      ? settingsBox.delete('customProteinG')
      : settingsBox.put('customProteinG', v);

  static double? get customCarbsG {
    final v = settingsBox.get('customCarbsG');
    return v is num ? v.toDouble() : null;
  }

  static Future<void> saveCustomCarbsG(double? v) async => v == null
      ? settingsBox.delete('customCarbsG')
      : settingsBox.put('customCarbsG', v);

  static double? get customFatG {
    final v = settingsBox.get('customFatG');
    return v is num ? v.toDouble() : null;
  }

  static Future<void> saveCustomFatG(double? v) async => v == null
      ? settingsBox.delete('customFatG')
      : settingsBox.put('customFatG', v);

  // ── Weight History ────────────────────────────────────────────────────────

  static List<WeightEntry> getWeightHistory() {
    final list = weightHistoryBox.values.toList()
      ..sort((a, b) => a.recordedAt.compareTo(b.recordedAt));
    return list;
  }

  /// Stores one canonical weight entry per day (keyed by dateKey).
  static Future<void> saveWeightEntry(WeightEntry entry) async {
    await weightHistoryBox.put(entry.dateKey, entry);
  }

  static Future<void> deleteWeightEntry(String dateKey) async {
    await weightHistoryBox.delete(dateKey);
  }

  // ── Archived Daily Summaries ──────────────────────────────────────────────

  static List<DailySummary> getDailySummaries() {
    return dailySummaryBox.values.toList()
      ..sort((a, b) => a.date.compareTo(b.date));
  }

  static DailySummary? getDailySummary(String dateKey) =>
      dailySummaryBox.get(dateKey);

  static Future<void> saveDailySummary(DailySummary s) async {
    await dailySummaryBox.put(s.dateKey, s);
  }

  // ── Archived Yearly Summaries ─────────────────────────────────────────────

  static List<YearlySummary> getYearlySummaries() {
    return yearlySummaryBox.values.toList()
      ..sort((a, b) => a.year.compareTo(b.year));
  }

  static YearlySummary? getYearlySummary(int year) =>
      yearlySummaryBox.get(year.toString());

  static Future<void> saveYearlySummary(YearlySummary s) async {
    await yearlySummaryBox.put(s.key, s);
  }

  static Future<void> deleteMonthlySummariesByKeys(List<String> keys) async {
    await monthlySummaryBox.deleteAll(keys);
  }

  // ── Per-day Water history (stored as 'water_<dateKey>' in settingsBox) ─────

  /// Returns a map of dateKey → ml for every recorded water entry.
  static Map<String, double> getAllWaterEntries() {
    final out = <String, double>{};
    for (final k in settingsBox.keys) {
      if (k is String && k.startsWith('water_')) {
        final v = settingsBox.get(k);
        if (v is num) out[k.substring(6)] = v.toDouble();
      }
    }
    return out;
  }

  static Map<String, double> getAllBurnedEntries() {
    final out = <String, double>{};
    for (final k in settingsBox.keys) {
      if (k is String && k.startsWith('burned_')) {
        final v = settingsBox.get(k);
        if (v is num) out[k.substring(7)] = v.toDouble();
      }
    }
    return out;
  }

  // ── Measurement unit ──────────────────────────────────────────────────────

  static String get measurementUnit =>
      settingsBox.get(AppConstants.keyMeasurementUnit, defaultValue: 'metric') as String;

  static Future<void> setMeasurementUnit(String unit) async =>
      settingsBox.put(AppConstants.keyMeasurementUnit, unit);

  // ── Backup / Archive bookkeeping ──────────────────────────────────────────

  static DateTime? get lastBackupAt {
    final v = settingsBox.get(AppConstants.keyLastBackupAt);
    return v is String ? DateTime.tryParse(v) : null;
  }

  static Future<void> setLastBackupAt(DateTime t) async =>
      settingsBox.put(AppConstants.keyLastBackupAt, t.toIso8601String());

  static DateTime? get lastArchiveAt {
    final v = settingsBox.get(AppConstants.keyLastArchiveAt);
    return v is String ? DateTime.tryParse(v) : null;
  }

  static Future<void> setLastArchiveAt(DateTime t) async =>
      settingsBox.put(AppConstants.keyLastArchiveAt, t.toIso8601String());

  /// Snapshot of all user-preference settings entries (everything except the
  /// regenerable per-day water/burned caches), for inclusion in backups.
  static Map<String, dynamic> exportSettingsSnapshot() {
    final out = <String, dynamic>{};
    for (final k in settingsBox.keys) {
      if (k is! String) continue;
      // Water & burned per-day values are exported separately as structured
      // history; skip the legal blob (restored from its own box).
      if (k.startsWith('water_') || k.startsWith('burned_')) continue;
      final v = settingsBox.get(k);
      if (v == null || v is bool || v is num || v is String) {
        out[k] = v;
      }
    }
    return out;
  }

  static Future<void> resetAllData() async {
    // Preserve user preferences across a data reset.
    final theme = settingsBox.get(AppConstants.keyThemeMode);
    final lang = settingsBox.get(AppConstants.keyLanguage);
    final legal = settingsBox.get(AppConstants.keyLegalAcceptance);
    final datasetLoaded = settingsBox.get(AppConstants.keyLocalDatasetLoaded);
    final notifEnabled = settingsBox.get(AppConstants.keyNotifEnabled);
    final notifHour = settingsBox.get(AppConstants.keyNotifHour);
    final notifMinute = settingsBox.get(AppConstants.keyNotifMinute);
    final apiKey = settingsBox.get(AppConstants.keyUserApiKey);

    await userBox.clear();
    await mealsBox.clear();
    await foodCacheBox.clear();
    await settingsBox.clear();
    await monthlySummaryBox.clear();
    await weightHistoryBox.clear();
    await dailySummaryBox.clear();
    await yearlySummaryBox.clear();
    // localFoodBox is immutable app data — never cleared.

    // Restore preserved preferences.
    if (theme != null) await settingsBox.put(AppConstants.keyThemeMode, theme);
    if (lang != null) await settingsBox.put(AppConstants.keyLanguage, lang);
    if (legal != null) await settingsBox.put(AppConstants.keyLegalAcceptance, legal);
    if (datasetLoaded != null) await settingsBox.put(AppConstants.keyLocalDatasetLoaded, datasetLoaded);
    if (notifEnabled != null) await settingsBox.put(AppConstants.keyNotifEnabled, notifEnabled);
    if (notifHour != null) await settingsBox.put(AppConstants.keyNotifHour, notifHour);
    if (notifMinute != null) await settingsBox.put(AppConstants.keyNotifMinute, notifMinute);
    if (apiKey != null) await settingsBox.put(AppConstants.keyUserApiKey, apiKey);
  }
}
