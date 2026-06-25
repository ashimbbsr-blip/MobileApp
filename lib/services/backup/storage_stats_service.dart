import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import '../../storage/hive_storage.dart';
import 'backup_collector.dart';

/// Computes the numbers shown on the Storage Usage / Data Health sections:
/// record counts, an estimate of raw data size, and the (compressed) backup
/// size. Used both for display and to drive archive savings estimates.
class StorageStats {
  final int totalRecords;
  final int mealCount;
  final int dailySummaryCount;
  final int monthlySummaryCount;
  final int yearlySummaryCount;
  final int weightCount;
  final int waterCount;
  final int customFoodCount;
  final int rawBytes;
  final int compressedBytes;
  final DateTime? lastBackupAt;
  final DateTime? lastArchiveAt;

  const StorageStats({
    required this.totalRecords,
    required this.mealCount,
    required this.dailySummaryCount,
    required this.monthlySummaryCount,
    required this.yearlySummaryCount,
    required this.weightCount,
    required this.waterCount,
    required this.customFoodCount,
    required this.rawBytes,
    required this.compressedBytes,
    required this.lastBackupAt,
    required this.lastArchiveAt,
  });

  double get compressionRatio =>
      rawBytes > 0 ? compressedBytes / rawBytes : 0;

  /// Percentage saved by compression (0–100).
  double get savingsPercent =>
      rawBytes > 0 ? (1 - compressedBytes / rawBytes) * 100 : 0;

  static String formatBytes(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(2)} MB';
  }

  /// Gather all stats. All encoding/compression runs on a background isolate
  /// so the main thread (and Hive) are never blocked.
  static Future<StorageStats> gather() async {
    final collected = BackupCollector.collect(); // Hive reads — must be main thread
    // JSON encode + gzip on background isolate to avoid blocking the UI
    final sizes = await compute(_computeSizesTask, collected.payload);
    return StorageStats(
      totalRecords: collected.counts.values.fold(0, (s, v) => s + v),
      mealCount: collected.counts['foodLogs'] ?? 0,
      dailySummaryCount: collected.counts['dailySummaries'] ?? 0,
      monthlySummaryCount: collected.counts['monthlySummaries'] ?? 0,
      yearlySummaryCount: collected.counts['yearlySummaries'] ?? 0,
      weightCount: collected.counts['weightEntries'] ?? 0,
      waterCount: collected.counts['waterLogs'] ?? 0,
      customFoodCount: collected.counts['customFoods'] ?? 0,
      rawBytes: sizes[0],
      compressedBytes: sizes[1],
      lastBackupAt: HiveStorage.lastBackupAt,
      lastArchiveAt: HiveStorage.lastArchiveAt,
    );
  }
}

/// Isolate entry — must NOT access Hive. Encodes and compresses the payload,
/// returning [rawBytes, compressedBytes].
List<int> _computeSizesTask(Map<String, dynamic> payload) {
  final jsonStr = jsonEncode(payload);
  final rawBytes = utf8.encode(jsonStr).length;
  final compressedBytes = gzip.encode(utf8.encode(jsonStr)).length;
  return [rawBytes, compressedBytes];
}
