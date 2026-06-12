import 'dart:async';
import 'dart:convert';
import 'package:flutter/services.dart';

/// Loads the prebuilt prefix indexes into memory and provides O(1) candidate lookup.
/// Index files are ~36KB total — loaded once and kept for the app lifetime.
class LocalSearchService {
  static Map<String, List<int>>? _indexEn;
  static Map<String, List<int>>? _indexBn;
  static Completer<void>? _loadCompleter;

  static Future<void> ensureLoaded() async {
    if (_indexEn != null) return;
    if (_loadCompleter != null) return _loadCompleter!.future;
    _loadCompleter = Completer<void>();
    try {
      final results = await Future.wait([
        rootBundle.loadString('assets/data/index_en_v7_0.json'),
        rootBundle.loadString('assets/data/index_bn_v7_0.json'),
      ]);
      _indexEn = _parseIndex(results[0]);
      _indexBn = _parseIndex(results[1]);
      _loadCompleter!.complete();
    } catch (e) {
      final completer = _loadCompleter!;
      _loadCompleter = null;
      completer.completeError(e);
      rethrow;
    }
  }

  static Map<String, List<int>> _parseIndex(String raw) {
    final map = json.decode(raw) as Map<String, dynamic>;
    return map.map((k, v) => MapEntry(k, (v as List).cast<int>()));
  }

  /// Returns candidate food IDs matching any prefix of any word in [query].
  /// Returns an empty set if indexes are not loaded yet.
  static Set<int> candidateIds(String query) {
    if (_indexEn == null) return {};
    final q = query.toLowerCase().trim();
    if (q.length < 2) return {};

    final result = <int>{};
    final isBengali = _containsBengali(q);

    for (final word in q.split(RegExp(r'\s+'))) {
      if (word.length < 2) continue;
      if (isBengali) {
        // Bengali 2-char prefix (each char is one UTF-16 code unit in BMP)
        final prefix = word.length >= 2 ? word.substring(0, 2) : word;
        result.addAll(_indexBn?[prefix] ?? []);
      } else {
        // English 2-char and 3-char prefixes
        result.addAll(_indexEn?[word.substring(0, 2)] ?? []);
        if (word.length >= 3) {
          result.addAll(_indexEn?[word.substring(0, 3)] ?? []);
        }
      }
    }
    return result;
  }

  static bool _containsBengali(String text) =>
      text.codeUnits.any((c) => c >= 0x0980 && c <= 0x09FF);

  static bool get isLoaded => _indexEn != null;
}
