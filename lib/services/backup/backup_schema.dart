import 'dart:convert';
import '../../core/constants/app_constants.dart';

/// Defines the `.iht` backup envelope, a stable content checksum, and the
/// validation primitives used by the restore/import engines.
///
/// Forward compatibility: every backup carries [AppConstants.backupSchemaVersion].
/// When the schema evolves, add a migration step in [BackupMigrator.migrate]
/// keyed on the stored version — never remove old reader paths.
class BackupSchema {
  /// Wrap a payload map in the versioned envelope, computing the content
  /// checksum over the canonical payload encoding.
  static Map<String, dynamic> buildEnvelope({
    required Map<String, dynamic> payload,
    required Map<String, int> counts,
  }) {
    final canonical = _canonical(payload);
    return {
      'magic': AppConstants.backupMagic,
      'backupVersion': AppConstants.backupSchemaVersion,
      'appVersion': AppConstants.currentAppVersion,
      'createdAt': DateTime.now().toIso8601String(),
      'checksum': fnv1a64(canonical),
      'counts': counts,
      'payload': payload,
    };
  }

  /// Deterministic JSON encoding (sorted keys) so the checksum is reproducible
  /// across encode/decode round-trips and platforms.
  static String _canonical(Object? node) {
    if (node is Map) {
      final keys = node.keys.map((k) => k.toString()).toList()..sort();
      final sb = StringBuffer('{');
      for (var i = 0; i < keys.length; i++) {
        if (i > 0) sb.write(',');
        sb
          ..write(jsonEncode(keys[i]))
          ..write(':')
          ..write(_canonical(node[keys[i]]));
      }
      sb.write('}');
      return sb.toString();
    }
    if (node is List) {
      final sb = StringBuffer('[');
      for (var i = 0; i < node.length; i++) {
        if (i > 0) sb.write(',');
        sb.write(_canonical(node[i]));
      }
      sb.write(']');
      return sb.toString();
    }
    return jsonEncode(node);
  }

  static String canonicalEncode(Map<String, dynamic> payload) => _canonical(payload);

  /// FNV-1a 64-bit hash → hex string. Stable, dependency-free integrity check
  /// (corruption detection — not a cryptographic guarantee).
  static String fnv1a64(String input) {
    // 64-bit FNV-1a implemented with BigInt to stay exact on the web target.
    final mask = (BigInt.one << 64) - BigInt.one;
    BigInt hash = BigInt.parse('14695981039346656037');
    final prime = BigInt.parse('1099511628211');
    final bytes = utf8.encode(input);
    for (final b in bytes) {
      hash = (hash ^ BigInt.from(b)) & mask;
      hash = (hash * prime) & mask;
    }
    return hash.toRadixString(16).padLeft(16, '0');
  }

  /// Validate envelope structure + version + checksum.
  static BackupValidation validate(Map<String, dynamic> envelope) {
    if (envelope['magic'] != AppConstants.backupMagic) {
      return const BackupValidation.invalid('Not a valid Infinity backup file.');
    }
    final ver = envelope['backupVersion'];
    if (ver is! int) {
      return const BackupValidation.invalid('Backup is missing a version number.');
    }
    if (ver > AppConstants.backupSchemaVersion) {
      return BackupValidation.invalid(
          'This backup was created by a newer app version ($ver). Please update the app to restore it.');
    }
    final payload = envelope['payload'];
    if (payload is! Map) {
      return const BackupValidation.invalid('Backup payload is missing or corrupt.');
    }
    final expected = envelope['checksum'];
    if (expected is String) {
      final actual = fnv1a64(_canonical(payload));
      if (actual != expected) {
        return const BackupValidation.invalid(
            'Integrity check failed — the backup file appears to be corrupted.');
      }
    }
    final counts = <String, int>{};
    final rawCounts = envelope['counts'];
    if (rawCounts is Map) {
      rawCounts.forEach((k, v) {
        if (v is int) counts[k.toString()] = v;
      });
    }
    return BackupValidation.valid(
      version: ver,
      appVersion: envelope['appVersion']?.toString() ?? 'unknown',
      createdAt: DateTime.tryParse(envelope['createdAt']?.toString() ?? ''),
      counts: counts,
      payload: (payload).cast<String, dynamic>(),
    );
  }
}

/// Result of validating a backup envelope.
class BackupValidation {
  final bool ok;
  final String? error;
  final int version;
  final String appVersion;
  final DateTime? createdAt;
  final Map<String, int> counts;
  final Map<String, dynamic> payload;

  const BackupValidation._(
    this.ok,
    this.error,
    this.version,
    this.appVersion,
    this.createdAt,
    this.counts,
    this.payload,
  );

  const BackupValidation.invalid(String message)
      : this._(false, message, 0, 'unknown', null, const {}, const {});

  factory BackupValidation.valid({
    required int version,
    required String appVersion,
    required DateTime? createdAt,
    required Map<String, int> counts,
    required Map<String, dynamic> payload,
  }) =>
      BackupValidation._(true, null, version, appVersion, createdAt, counts, payload);

  int get totalRecords => counts.values.fold(0, (s, v) => s + v);
}

/// Hook point for forward-compatible schema migrations.
class BackupMigrator {
  /// Upgrade an older payload to the current schema. Currently a pass-through
  /// (v1 is the first format); add `if (fromVersion < N) { ... }` blocks here.
  static Map<String, dynamic> migrate(Map<String, dynamic> payload, int fromVersion) {
    var p = payload;
    // Example for the future:
    // if (fromVersion < 2) { p = _v1ToV2(p); }
    return p;
  }
}
