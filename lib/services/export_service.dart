import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import '../storage/hive_storage.dart';
import '../services/analytics_service.dart';
import '../models/user_profile.dart';
import '../models/meal_entry.dart';
import '../models/monthly_summary.dart';

class ExportService {
  // ── CSV Export ────────────────────────────────────────────────────────────

  static Future<bool> exportCsv({int days = 90}) async {
    try {
      final data = AnalyticsService.getLastNDays(days);
      final profile = HiveStorage.getUserProfile();
      final goalCalories = profile != null ? _estimateGoal(profile) : 2000.0;

      final buffer = StringBuffer();
      buffer.writeln([
        'Date', 'Calories', 'Goal Calories', 'Goal %',
        'Protein(g)', 'Carbs(g)', 'Fat(g)', 'Fiber(g)',
      ].map(_csvField).join(','));

      for (final d in data) {
        if (!d.hasData) continue;
        final pct = (d.goalCompletion(goalCalories) * 100).toStringAsFixed(1);
        buffer.writeln([
          _csvField(_formatDate(d.date)),
          d.calories.toStringAsFixed(0),
          goalCalories.toStringAsFixed(0),
          pct,
          d.protein.toStringAsFixed(1),
          d.carbs.toStringAsFixed(1),
          d.fat.toStringAsFixed(1),
          d.fiber.toStringAsFixed(1),
        ].join(','));
      }

      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/nutrition_export.csv');
      await file.writeAsString(buffer.toString());

      await Share.shareXFiles(
        [XFile(file.path, mimeType: 'text/csv')],
        subject: 'Nutrition History Export',
      );
      return true;
    } catch (_) {
      return false;
    }
  }

  // ── JSON Backup ───────────────────────────────────────────────────────────

  static Future<bool> exportJsonBackup() async {
    try {
      final profile = HiveStorage.getUserProfile();
      final meals = HiveStorage.getAllMealEntries();
      final summaries = HiveStorage.getMonthlySummaries();

      final backup = {
        'version': '1.0',
        'exportDate': DateTime.now().toIso8601String(),
        'appName': 'Infinite Nutrition Tracker',
        'profile': profile != null ? _profileToJson(profile) : null,
        'meals': meals.map(_mealToJson).toList(),
        'monthlySummaries': summaries.map(_summaryToJson).toList(),
        'settings': {
          'themeMode': HiveStorage.themeMode,
          'language': HiveStorage.language,
        },
      };

      final json = const JsonEncoder.withIndent('  ').convert(backup);
      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/infinity_health_backup.json');
      await file.writeAsString(json);

      await Share.shareXFiles(
        [XFile(file.path, mimeType: 'application/json')],
        subject: 'Infinite Nutrition Tracker Backup',
      );
      return true;
    } catch (_) {
      return false;
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  static String _formatDate(DateTime d) =>
      '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

  // RFC 4180: quote fields that contain commas, quotes, or newlines.
  static String _csvField(String value) {
    if (value.contains(',') || value.contains('"') || value.contains('\n') || value.contains('\r')) {
      return '"${value.replaceAll('"', '""')}"';
    }
    return value;
  }

  static double _estimateGoal(UserProfile p) {
    double bmr;
    if (p.gender == 'male') {
      bmr = 10 * p.weightKg + 6.25 * p.heightCm - 5 * p.computedAge + 5;
    } else {
      bmr = 10 * p.weightKg + 6.25 * p.heightCm - 5 * p.computedAge - 161;
    }
    const multipliers = {
      'sedentary': 1.2,
      'lightly_active': 1.375,
      'moderately_active': 1.55,
      'very_active': 1.725,
      'extra_active': 1.9,
    };
    return bmr * (multipliers[p.activityLevel] ?? 1.55);
  }

  static Map<String, dynamic> _profileToJson(UserProfile p) => {
        'id': p.id,
        'fullName': p.fullName,
        'age': p.computedAge,
        'dateOfBirth': p.dateOfBirth?.toIso8601String(),
        'gender': p.gender,
        'heightCm': p.heightCm,
        'weightKg': p.weightKg,
        'activityLevel': p.activityLevel,
        'fitnessGoal': p.fitnessGoal,
        'createdAt': p.createdAt.toIso8601String(),
      };

  static Map<String, dynamic> _mealToJson(MealEntry m) => {
        'id': m.id,
        'mealType': m.mealType,
        'dateKey': m.dateKey,
        'loggedAt': m.loggedAt.toIso8601String(),
        'quantityG': m.quantityG,
        'food': m.foodItem.toJson(),
      };

  static Map<String, dynamic> _summaryToJson(MonthlySummary s) => {
        'year': s.year,
        'month': s.month,
        'avgCalories': s.avgCalories,
        'avgProtein': s.avgProtein,
        'avgCarbs': s.avgCarbs,
        'avgFat': s.avgFat,
        'avgFiber': s.avgFiber,
        'consistencyScore': s.consistencyScore,
        'daysLogged': s.daysLogged,
      };
}
