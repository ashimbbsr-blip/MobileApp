import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:file_picker/file_picker.dart';
import 'backup_schema.dart';
import 'compression_service.dart';

/// Handles getting a `.iht` file off the device (file picker), decompressing it,
/// and validating it — producing a [BackupValidation] the UI shows as a preview
/// before the user commits to Replace or Merge.
class ImportService {
  /// Let the user pick a backup file. Returns null if cancelled.
  static Future<PickedBackup?> pickFile() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.any,
      withData: true,
      dialogTitle: 'Select an Infinity backup (.iht)',
    );
    if (result == null || result.files.isEmpty) return null;
    final f = result.files.first;

    Uint8List? bytes = f.bytes;
    if (bytes == null && f.path != null) {
      bytes = Uint8List.fromList(await File(f.path!).readAsBytes());
    }
    if (bytes == null) return null;
    return PickedBackup(name: f.name, bytes: bytes);
  }

  /// Decompress + validate raw `.iht` bytes.
  static Future<BackupValidation> validateBytes(Uint8List bytes) async {
    try {
      final envelope = await CompressionService.decodeJsonGzip(bytes);
      return BackupSchema.validate(envelope);
    } catch (e) {
      debugPrint('[ImportService] decode failed: $e');
      return const BackupValidation.invalid(
          'Could not read this file. It may be corrupted or not an Infinity backup.');
    }
  }

  /// Convenience: pick + validate in one step.
  static Future<({PickedBackup? file, BackupValidation? validation})>
      pickAndValidate() async {
    final picked = await pickFile();
    if (picked == null) return (file: null, validation: null);
    final validation = await validateBytes(picked.bytes);
    return (file: picked, validation: validation);
  }
}

class PickedBackup {
  final String name;
  final Uint8List bytes;
  const PickedBackup({required this.name, required this.bytes});
}
