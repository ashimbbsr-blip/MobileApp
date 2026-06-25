import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import '../../storage/hive_storage.dart';
import 'backup_collector.dart';
import 'backup_schema.dart';
import 'backup_types.dart';
import 'compression_service.dart';

/// Creates the recommended `.iht` backup (GZIP-compressed JSON) and hands it to
/// the OS share sheet so the user can save it to Drive / Files / email / etc.
class BackupEngine {
  /// Build a `.iht` file in the temp dir and return its path + size. Heavy
  /// compression runs on a background isolate (UI stays responsive).
  static Future<BackupOutcome> createBackupFile({ProgressCallback? onProgress}) async {
    try {
      onProgress?.call(const BackupProgress(0.1, 'Collecting your data…'));
      final collected = BackupCollector.collect();

      onProgress?.call(const BackupProgress(0.4, 'Packaging backup…'));
      final envelope = BackupSchema.buildEnvelope(
        payload: collected.payload,
        counts: collected.counts,
      );

      onProgress?.call(const BackupProgress(0.6, 'Compressing…'));
      final bytes = await CompressionService.encodeJsonGzip(envelope);

      onProgress?.call(const BackupProgress(0.85, 'Writing file…'));
      final dir = await getTemporaryDirectory();
      final fileName = _backupFileName();
      final file = File('${dir.path}/$fileName');
      await file.writeAsBytes(bytes, flush: true);

      await HiveStorage.setLastBackupAt(DateTime.now());
      onProgress?.call(const BackupProgress(1.0, 'Done'));

      return BackupOutcome(
        success: true,
        filePath: file.path,
        sizeBytes: bytes.length,
        counts: collected.counts,
      );
    } catch (e) {
      debugPrint('[BackupEngine] createBackupFile failed: $e');
      return BackupOutcome.failure('Could not create backup: $e');
    }
  }

  /// Create + share in one step.
  static Future<BackupOutcome> exportAndShare({ProgressCallback? onProgress}) async {
    final outcome = await createBackupFile(onProgress: onProgress);
    if (!outcome.success || outcome.filePath == null) return outcome;
    try {
      await Share.shareXFiles(
        [XFile(outcome.filePath!, mimeType: 'application/octet-stream')],
        subject: 'Infinity Nutrition Backup',
        text: 'Infinity Nutrition Tracker — full backup (.iht). '
            'Keep this file safe to restore on a new device.',
      );
      return outcome;
    } catch (e) {
      debugPrint('[BackupEngine] share failed: $e');
      return BackupOutcome.failure('Backup created but sharing failed: $e');
    }
  }

  static String _backupFileName() {
    final now = DateTime.now();
    final y = now.year.toString().padLeft(4, '0');
    final m = now.month.toString().padLeft(2, '0');
    final d = now.day.toString().padLeft(2, '0');
    return 'Infinity_Nutrition_Backup_$y$m$d.iht';
  }
}
