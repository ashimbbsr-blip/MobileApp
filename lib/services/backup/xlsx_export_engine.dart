import 'dart:io';
import 'package:excel/excel.dart';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import '../../models/user_profile.dart';
import '../../storage/hive_storage.dart';
import 'backup_types.dart';
import 'insights_service.dart';

/// Generates a professional multi-sheet Excel workbook (.xlsx) suitable for a
/// nutritionist / doctor / trainer:
/// Profile · Daily Summary · Monthly Summary · Yearly Summary · Weight History
/// · Water History · Health Insights.
///
/// All cell data is assembled on the UI thread as plain primitives, then the
/// (heavy) workbook build + encode runs on a background isolate via [compute].
class XlsxExportEngine {
  static Future<BackupOutcome> exportAndShare({ProgressCallback? onProgress}) async {
    try {
      onProgress?.call(const BackupProgress(0.2, 'Gathering report data…'));
      final sheets = _buildSheetData();

      onProgress?.call(const BackupProgress(0.6, 'Building workbook…'));
      final bytes = await compute(_buildWorkbook, sheets);
      if (bytes.isEmpty) return BackupOutcome.failure('Could not generate the report.');

      onProgress?.call(const BackupProgress(0.9, 'Saving file…'));
      final dir = await getTemporaryDirectory();
      final name = 'Infinity_Nutrition_Report_${_dateStamp()}.xlsx';
      final file = File('${dir.path}/$name');
      await file.writeAsBytes(bytes, flush: true);

      await Share.shareXFiles(
        [
          XFile(file.path,
              mimeType:
                  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        ],
        subject: 'Infinity Nutrition Report',
      );
      onProgress?.call(const BackupProgress(1.0, 'Done'));
      return BackupOutcome(success: true, filePath: file.path, sizeBytes: bytes.length);
    } catch (e) {
      debugPrint('[XlsxExportEngine] failed: $e');
      return BackupOutcome.failure('Report export failed: $e');
    }
  }

  // ── Sheet assembly (plain data; runs on UI thread) ─────────────────────────

  static Map<String, List<List<Object?>>> _buildSheetData() {
    final profile = HiveStorage.getUserProfile();
    final days = InsightsService.allDailySummaries();
    final months = InsightsService.allMonthlySummaries();
    final years = InsightsService.allYearlySummaries();
    final weights = HiveStorage.getWeightHistory();
    final goals = InsightsService.goalsFor(profile);
    final insights = InsightsService.aggregateInsights();

    return {
      'Profile': _profileSheet(profile),
      'Daily Summary': _dailySheet(days),
      'Monthly Summary': _monthlySheet(months),
      'Yearly Summary': _yearlySheet(years),
      'Weight History': _weightSheet(weights),
      'Water History': _waterSheet(days, goals.waterMl),
      'Health Insights': _insightsSheet(insights),
    };
  }

  static List<List<Object?>> _profileSheet(UserProfile? p) {
    final rows = <List<Object?>>[
      ['Infinity Nutrition Tracker — Profile'],
      [],
      ['Field', 'Value'],
    ];
    if (p == null) {
      rows.add(['No profile', '']);
      return rows;
    }
    rows.addAll([
      ['Name', p.displayName],
      ['Date of Birth', p.dateOfBirth != null ? _fmtDate(p.dateOfBirth!) : '—'],
      ['Age', p.computedAge],
      ['Gender', p.gender],
      ['Height (cm)', _r(p.heightCm)],
      ['Current Weight (kg)', _r(p.weightKg)],
      ['BMI', _r(p.bmi)],
      ['BMI Category', p.bmiCategory],
      ['Activity Level', p.activityLevel],
      ['Goal', p.fitnessGoal],
      ['Member Since', _fmtDate(p.createdAt)],
    ]);
    return rows;
  }

  static List<List<Object?>> _dailySheet(List days) {
    final rows = <List<Object?>>[
      ['Date', 'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Fiber (g)', 'Water (ml)', 'Health Score'],
    ];
    for (final d in days) {
      rows.add([
        d.dateKey.replaceAll('_', '-'),
        _r(d.kcal),
        _r(d.protein),
        _r(d.carbs),
        _r(d.fat),
        _r(d.fiber),
        _r(d.waterMl),
        _r(d.score),
      ]);
    }
    return rows;
  }

  static List<List<Object?>> _monthlySheet(List months) {
    final rows = <List<Object?>>[
      ['Month', 'Avg Calories', 'Avg Protein (g)', 'Avg Carbs (g)', 'Avg Fat (g)', 'Days Logged', 'Goal Achievement %'],
    ];
    for (final m in months) {
      rows.add([
        m.label,
        _r(m.avgCalories),
        _r(m.avgProtein),
        _r(m.avgCarbs),
        _r(m.avgFat),
        m.daysLogged,
        _r(m.consistencyScore * 100),
      ]);
    }
    return rows;
  }

  static List<List<Object?>> _yearlySheet(List years) {
    final rows = <List<Object?>>[
      ['Year', 'Avg Calories', 'Avg Protein (g)', 'Avg Water (ml)', 'Avg Score', 'Weight Change (kg)', 'Days Logged'],
    ];
    for (final y in years) {
      rows.add([
        y.year,
        _r(y.avgKcal),
        _r(y.avgProtein),
        _r(y.avgWater),
        _r(y.avgScore),
        _r(y.weightChange),
        y.daysLogged,
      ]);
    }
    return rows;
  }

  static List<List<Object?>> _weightSheet(List weights) {
    final rows = <List<Object?>>[
      ['Date', 'Weight (kg)', 'BMI'],
    ];
    for (final w in weights) {
      rows.add([_fmtDate(w.recordedAt), _r(w.weightKg), _r(w.bmi)]);
    }
    return rows;
  }

  static List<List<Object?>> _waterSheet(List days, double goalMl) {
    final rows = <List<Object?>>[
      ['Date', 'Water Consumed (ml)', 'Goal (ml)', 'Goal Achieved'],
    ];
    for (final d in days) {
      rows.add([
        d.dateKey.replaceAll('_', '-'),
        _r(d.waterMl),
        _r(goalMl),
        d.waterMl >= goalMl ? 'Yes' : 'No',
      ]);
    }
    return rows;
  }

  static List<List<Object?>> _insightsSheet(HealthInsights i) {
    return [
      ['Health Insights'],
      [],
      ['Metric', 'Value'],
      ['Best Month', i.bestMonth],
      ['Worst Month', i.worstMonth],
      ['Longest Streak (days)', i.longestStreak],
      ['Total Days Logged', i.totalDaysLogged],
      ['Average Calories', _r(i.avgCalories)],
      ['Average Protein (g)', _r(i.avgProtein)],
      ['Average Water (ml)', _r(i.avgWater)],
      ['Average Health Score', _r(i.avgScore)],
      ['Goal Achievement %', _r(i.goalAchievementPct)],
      ['Weight Change (kg)', _r(i.weightChange)],
      ['Overall Health Trend', i.trend],
    ];
  }

  static double _r(double v) => double.parse(v.toStringAsFixed(1));
  static String _fmtDate(DateTime d) =>
      '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
  static String _dateStamp() {
    final n = DateTime.now();
    return '${n.year}${n.month.toString().padLeft(2, '0')}${n.day.toString().padLeft(2, '0')}';
  }
}

// ── Isolate entry point: build + encode the workbook ─────────────────────────

Uint8List _buildWorkbook(Map<String, List<List<Object?>>> sheets) {
  final workbook = Excel.createExcel();
  final defaultSheet = workbook.getDefaultSheet();

  sheets.forEach((name, rows) {
    final sheet = workbook[name];
    for (final row in rows) {
      sheet.appendRow(row.map(_toCell).toList());
    }
    // Bold the header row for each sheet
    final hRow = _headerRowIndex(name);
    if (hRow < rows.length) {
      final colCount = rows[hRow].length;
      for (var col = 0; col < colCount; col++) {
        final cell = sheet.cell(
          CellIndex.indexByColumnRow(columnIndex: col, rowIndex: hRow),
        );
        cell.cellStyle = CellStyle(bold: true);
      }
    }
  });

  // Remove the auto-created default sheet if it isn't one of ours.
  if (defaultSheet != null && !sheets.containsKey(defaultSheet)) {
    workbook.delete(defaultSheet);
  }

  final encoded = workbook.encode();
  return Uint8List.fromList(encoded ?? const <int>[]);
}

int _headerRowIndex(String sheetName) {
  // Profile and Health Insights have a title row + blank row before the header
  if (sheetName == 'Profile' || sheetName == 'Health Insights') return 2;
  return 0;
}

CellValue? _toCell(Object? v) {
  if (v == null) return TextCellValue('');
  if (v is int) return IntCellValue(v);
  if (v is double) return DoubleCellValue(v);
  if (v is num) return DoubleCellValue(v.toDouble());
  if (v is bool) return TextCellValue(v ? 'Yes' : 'No');
  return TextCellValue(v.toString());
}
