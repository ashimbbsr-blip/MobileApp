import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'backup_collector.dart';
import 'backup_schema.dart';
import 'compression_service.dart';
import 'payload_writer.dart';

/// Provides the "never corrupt the user's data" guarantee.
///
/// Before any destructive operation (replace-restore, archive compression) the
/// caller takes a [SafetySnapshot] of the entire current dataset, performs the
/// operation inside a try/catch, and on failure calls [SafetySnapshot.restore]
/// to roll back to the exact prior state.
class IntegrityService {
  /// Deletes snapshots older than [maxAgeDays] days to prevent storage leaks.
  /// Called on each screen load — safe to call frequently.
  static Future<void> pruneOldSnapshots({int maxAgeDays = 7}) async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final snapDir = Directory('${dir.path}/iht_snapshots');
      if (!snapDir.existsSync()) return;
      final cutoff = DateTime.now().subtract(Duration(days: maxAgeDays));
      await for (final entity in snapDir.list()) {
        if (entity is File) {
          final modified = await entity.lastModified();
          if (modified.isBefore(cutoff)) {
            await entity.delete();
            debugPrint('[IntegrityService] pruned snapshot: ${entity.path}');
          }
        }
      }
    } catch (e) {
      debugPrint('[IntegrityService] pruneOldSnapshots failed: $e');
    }
  }

  /// Capture the current dataset to a private on-disk snapshot file.
  static Future<SafetySnapshot> createSnapshot() async {
    final collected = BackupCollector.collect();
    final envelope = BackupSchema.buildEnvelope(
      payload: collected.payload,
      counts: collected.counts,
    );
    final bytes = await CompressionService.encodeJsonGzip(envelope);

    final dir = await getApplicationDocumentsDirectory();
    final snapDir = Directory('${dir.path}/iht_snapshots');
    if (!snapDir.existsSync()) snapDir.createSync(recursive: true);
    final ts = DateTime.now();
    final unique = '${ts.millisecondsSinceEpoch}_${ts.microsecond}';
    final file = File('${snapDir.path}/snapshot_$unique.iht');
    await file.writeAsBytes(bytes, flush: true);
    return SafetySnapshot._(file.path, bytes.length);
  }
}

class SafetySnapshot {
  final String path;
  final int sizeBytes;
  const SafetySnapshot._(this.path, this.sizeBytes);

  /// Roll the dataset back to this snapshot (used when an operation fails).
  Future<bool> restore() async {
    try {
      final file = File(path);
      if (!file.existsSync()) return false;
      final bytes = await file.readAsBytes();
      final envelope = await CompressionService.decodeJsonGzip(bytes);
      final validation = BackupSchema.validate(envelope);
      if (!validation.ok) return false;
      await PayloadWriter.applyReplace(validation.payload);
      return true;
    } catch (e) {
      debugPrint('[IntegrityService] rollback failed: $e');
      return false;
    }
  }

  /// Delete the snapshot once the operation has safely completed.
  Future<void> dispose() async {
    try {
      final f = File(path);
      if (f.existsSync()) await f.delete();
    } catch (e) {
      debugPrint('[IntegrityService] snapshot cleanup failed: $e');
    }
  }
}
