import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';

/// Low-level (de)compression used by the backup & archive pipeline.
///
/// All heavy work (JSON (de)serialisation + GZIP) is pushed onto a background
/// isolate via [compute] so the UI thread never janks, even on a 10-year-old
/// dataset. The on-disk `.iht` format is pure GZIP of UTF-8 JSON — this keeps
/// it recoverable with any standard gzip tool while still hitting the
/// 80–95 % size-reduction target on repetitive nutrition data.
class CompressionService {
  /// Encode a JSON-encodable map → GZIP bytes (off the UI thread).
  static Future<Uint8List> encodeJsonGzip(Map<String, dynamic> data) {
    return compute(_encodeTask, data);
  }

  /// GZIP bytes → decoded JSON map (off the UI thread).
  static Future<Map<String, dynamic>> decodeJsonGzip(Uint8List bytes) {
    return compute(_decodeTask, bytes);
  }

  /// Raw string → GZIP bytes (used for size estimation / generic payloads).
  static Future<Uint8List> gzipString(String s) => compute(_gzipStringTask, s);

  /// Synchronous helpers — only for small payloads / size estimates.
  static Uint8List gzipStringSync(String s) =>
      Uint8List.fromList(gzip.encode(utf8.encode(s)));

  static String gunzipToStringSync(List<int> bytes) =>
      utf8.decode(gzip.decode(bytes));

  /// Estimate the compressed size (bytes) of a JSON map without keeping the
  /// result. Runs on a background isolate.
  static Future<int> estimateCompressedSize(Map<String, dynamic> data) async {
    final bytes = await compute(_encodeTask, data);
    return bytes.length;
  }
}

// ── Top-level isolate entry points (must be static/top-level for compute) ────

Uint8List _encodeTask(Map<String, dynamic> data) {
  final jsonStr = jsonEncode(data);
  final compressed = gzip.encode(utf8.encode(jsonStr));
  return Uint8List.fromList(compressed);
}

Map<String, dynamic> _decodeTask(Uint8List bytes) {
  final jsonStr = utf8.decode(gzip.decode(bytes));
  final decoded = jsonDecode(jsonStr);
  return (decoded as Map).cast<String, dynamic>();
}

Uint8List _gzipStringTask(String s) {
  return Uint8List.fromList(gzip.encode(utf8.encode(s)));
}
