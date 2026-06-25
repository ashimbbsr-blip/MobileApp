// Shared value types for the backup / restore / archive pipeline.

enum ImportMode {
  /// Wipe current data and replace entirely (new phone / full restore).
  replace,

  /// Keep current data and fold in the backup, de-duplicating intelligently.
  merge,
}

/// Strategy applied when a record with the same key already exists during merge.
enum DuplicateStrategy { skip, updateExisting }

/// Progress update emitted by long-running operations.
class BackupProgress {
  final double fraction; // 0.0 – 1.0
  final String message;
  const BackupProgress(this.fraction, this.message);
}

typedef ProgressCallback = void Function(BackupProgress progress);

/// Report describing what a merge changed.
class MergeReport {
  final Map<String, int> added;
  final Map<String, int> skipped;
  final Map<String, int> updated;

  MergeReport()
      : added = {},
        skipped = {},
        updated = {};

  void addOne(String section) => added[section] = (added[section] ?? 0) + 1;
  void skipOne(String section) => skipped[section] = (skipped[section] ?? 0) + 1;
  void updateOne(String section) => updated[section] = (updated[section] ?? 0) + 1;

  int get totalAdded => added.values.fold(0, (s, v) => s + v);
  int get totalSkipped => skipped.values.fold(0, (s, v) => s + v);
  int get totalUpdated => updated.values.fold(0, (s, v) => s + v);
}

/// Generic outcome of a backup / restore / import / archive operation.
class BackupOutcome {
  final bool success;
  final String? error;
  final String? filePath;
  final int? sizeBytes;
  final Map<String, int> counts;
  final MergeReport? mergeReport;

  const BackupOutcome({
    required this.success,
    this.error,
    this.filePath,
    this.sizeBytes,
    this.counts = const {},
    this.mergeReport,
  });

  factory BackupOutcome.failure(String message) =>
      BackupOutcome(success: false, error: message);
}
