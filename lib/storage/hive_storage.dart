import 'package:hive_flutter/hive_flutter.dart';
import '../models/user_profile.dart';
import '../models/food_item.dart';
import '../models/meal_entry.dart';
import '../models/monthly_summary.dart';
import '../models/legal_acceptance.dart';
import '../core/constants/app_constants.dart';

class HiveStorage {
  static Future<void> init() async {
    await Hive.initFlutter();
    _registerAdapters();
    await _openBoxes();
  }

  static void _registerAdapters() {
    if (!Hive.isAdapterRegistered(0)) Hive.registerAdapter(UserProfileAdapter());
    if (!Hive.isAdapterRegistered(1)) Hive.registerAdapter(FoodItemAdapter());
    if (!Hive.isAdapterRegistered(2)) Hive.registerAdapter(MealEntryAdapter());
    if (!Hive.isAdapterRegistered(3)) Hive.registerAdapter(MonthlySummaryAdapter());
    if (!Hive.isAdapterRegistered(4)) Hive.registerAdapter(LegalAcceptanceAdapter());
  }

  static Future<void> _openBoxes() async {
    await Future.wait([
      Hive.openBox(AppConstants.hiveUserBox),
      Hive.openBox<MealEntry>(AppConstants.hiveMealsBox),
      Hive.openBox<FoodItem>(AppConstants.hiveFoodCacheBox),
      Hive.openBox(AppConstants.hiveSettingsBox),
      Hive.openBox(AppConstants.hiveDailyLogsBox),
      Hive.openBox<MonthlySummary>(AppConstants.hiveMonthlySummaryBox),
      Hive.openBox(AppConstants.hiveLegalBox),
    ]);
  }

  // Box accessors
  static Box get userBox => Hive.box(AppConstants.hiveUserBox);
  static Box<MealEntry> get mealsBox => Hive.box<MealEntry>(AppConstants.hiveMealsBox);
  static Box<FoodItem> get foodCacheBox => Hive.box<FoodItem>(AppConstants.hiveFoodCacheBox);
  static Box get settingsBox => Hive.box(AppConstants.hiveSettingsBox);
  static Box get dailyLogsBox => Hive.box(AppConstants.hiveDailyLogsBox);
  static Box<MonthlySummary> get monthlySummaryBox =>
      Hive.box<MonthlySummary>(AppConstants.hiveMonthlySummaryBox);
  static Box get legalBox => Hive.box(AppConstants.hiveLegalBox);

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
    if (foodCacheBox.length >= AppConstants.maxCachedFoods) {
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

  // ── API Key ──────────────────────────────────────────────────────────────

  static String? getApiKey() =>
      settingsBox.get(AppConstants.keyApiKey) as String?;

  static Future<void> saveApiKey(String key) async =>
      settingsBox.put(AppConstants.keyApiKey, key);

  static Future<void> removeApiKey() async =>
      settingsBox.delete(AppConstants.keyApiKey);

  static bool get hasApiKey =>
      settingsBox.containsKey(AppConstants.keyApiKey);

  // ── Reset ─────────────────────────────────────────────────────────────────

  static Future<void> resetAllData() async {
    await userBox.clear();
    await mealsBox.clear();
    await foodCacheBox.clear();
    await settingsBox.clear();
    await dailyLogsBox.clear();
    await monthlySummaryBox.clear();
    // Legal acceptance is intentionally preserved — the user already agreed
    // to the terms; resetting their nutrition data doesn't invalidate that.
  }
}
