import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../services/backup/archive_engine.dart';
import '../../../services/backup/backup_engine.dart';
import '../../../services/backup/backup_schema.dart';
import '../../../services/backup/backup_types.dart';
import '../../../services/backup/integrity_service.dart';
import '../../../services/backup/restore_engine.dart';
import '../../../services/backup/storage_stats_service.dart';
import '../../../services/backup/xlsx_export_engine.dart';

/// Immutable view-state for the Backup & Archive screen.
class BackupState {
  final bool loading;
  final bool busy;
  final double progress;
  final String message;
  final StorageStats? stats;
  final List<ArchiveCandidate> candidates;

  const BackupState({
    this.loading = true,
    this.busy = false,
    this.progress = 0,
    this.message = '',
    this.stats,
    this.candidates = const [],
  });

  BackupState copyWith({
    bool? loading,
    bool? busy,
    double? progress,
    String? message,
    StorageStats? stats,
    List<ArchiveCandidate>? candidates,
  }) =>
      BackupState(
        loading: loading ?? this.loading,
        busy: busy ?? this.busy,
        progress: progress ?? this.progress,
        message: message ?? this.message,
        stats: stats ?? this.stats,
        candidates: candidates ?? this.candidates,
      );
}

class BackupController extends StateNotifier<BackupState> {
  BackupController() : super(const BackupState()) {
    load();
  }

  Future<void> load() async {
    state = state.copyWith(loading: true);
    try {
      await IntegrityService.pruneOldSnapshots();
      final stats = await StorageStats.gather();
      final candidates = ArchiveEngine.analyze();
      state = state.copyWith(loading: false, stats: stats, candidates: candidates);
    } catch (e) {
      debugPrint('[BackupController] load failed: $e');
      state = state.copyWith(loading: false);
    }
  }

  void _progress(BackupProgress p) =>
      state = state.copyWith(busy: true, progress: p.fraction, message: p.message);

  Future<BackupOutcome> _wrap(Future<BackupOutcome> Function() op) async {
    state = state.copyWith(busy: true, progress: 0, message: 'Starting…');
    final outcome = await op();
    state = state.copyWith(busy: false, progress: 0, message: '');
    await load();
    return outcome;
  }

  Future<BackupOutcome> createBackup() =>
      _wrap(() => BackupEngine.exportAndShare(onProgress: _progress));

  Future<BackupOutcome> exportXlsx() =>
      _wrap(() => XlsxExportEngine.exportAndShare(onProgress: _progress));

  Future<BackupOutcome> restore(BackupValidation validation, ImportMode mode) =>
      _wrap(() => RestoreEngine.apply(validation, mode, onProgress: _progress));

  Future<BackupOutcome> archive(ArchiveLevel level) =>
      _wrap(() => ArchiveEngine.run(level, onProgress: _progress));
}

final backupControllerProvider =
    StateNotifierProvider<BackupController, BackupState>((ref) => BackupController());
