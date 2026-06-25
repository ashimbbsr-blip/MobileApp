import 'package:flutter/foundation.dart';
import 'backup_schema.dart';
import 'backup_types.dart';
import 'integrity_service.dart';
import 'payload_writer.dart';

/// Applies a validated backup to the live dataset, wrapped in an automatic
/// safety snapshot so a mid-restore failure can never leave partial/corrupt
/// data behind.
class RestoreEngine {
  /// Restore a previously-validated backup.
  ///
  /// [ImportMode.replace] → wipe & restore (new phone / full restore).
  /// [ImportMode.merge]   → fold into existing data with de-duplication.
  static Future<BackupOutcome> apply(
    BackupValidation validation,
    ImportMode mode, {
    ProgressCallback? onProgress,
  }) async {
    if (!validation.ok) {
      return BackupOutcome.failure(validation.error ?? 'Invalid backup.');
    }

    onProgress?.call(const BackupProgress(0.1, 'Verifying backup…'));
    final payload =
        BackupMigrator.migrate(validation.payload, validation.version);

    onProgress?.call(const BackupProgress(0.2, 'Creating safety snapshot…'));
    SafetySnapshot? snapshot;
    try {
      snapshot = await IntegrityService.createSnapshot();
    } catch (e) {
      debugPrint('[RestoreEngine] snapshot failed: $e');
      // Proceed cautiously only for merge (non-destructive). Abort replace.
      if (mode == ImportMode.replace) {
        return BackupOutcome.failure(
            'Could not create a safety snapshot — restore aborted to protect your data.');
      }
    }

    try {
      MergeReport? report;
      if (mode == ImportMode.replace) {
        onProgress?.call(const BackupProgress(0.5, 'Restoring data…'));
        await PayloadWriter.applyReplace(payload);
      } else {
        onProgress?.call(const BackupProgress(0.5, 'Merging records…'));
        report = await PayloadWriter.applyMerge(payload);
      }

      onProgress?.call(const BackupProgress(0.95, 'Verifying integrity…'));
      await snapshot?.dispose();
      onProgress?.call(const BackupProgress(1.0, 'Done'));

      return BackupOutcome(
        success: true,
        counts: validation.counts,
        mergeReport: report,
      );
    } catch (e) {
      debugPrint('[RestoreEngine] restore failed, rolling back: $e');
      final rolledBack = await snapshot?.restore() ?? false;
      await snapshot?.dispose();
      return BackupOutcome.failure(rolledBack
          ? 'Restore failed — your previous data was safely restored.'
          : 'Restore failed and rollback could not complete. Please reinstall or import a known-good backup.');
    }
  }
}
