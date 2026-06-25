import 'dart:async';
import 'dart:convert';
import 'package:flutter/services.dart';

/// Loads search_index_v2.json (unified EN+BN+alias+family index) into memory
/// and provides fast O(1) candidate lookup by prefix.
///
/// v2 structure:
///   en_prefix     : Map<prefix, List<id>>  — English prefix → food IDs
///   bn_prefix     : Map<prefix, List<id>>  — Bengali  prefix → food IDs
///   alias_lookup  : Map<term,   List<id>>  — alias term     → food IDs
///   family_index  : Map<family, List<id>>  — food family    → food IDs
///   top_foods     : List<id>               — top-100 by search_priority
class LocalSearchService {
  static Map<String, List<int>>? _enPrefix;
  static Map<String, List<int>>? _bnPrefix;
  static Map<String, List<int>>? _aliasLookup;
  static Map<String, List<int>>? _familyIndex;
  static List<int> _topFoods = const [];

  static Completer<void>? _loadCompleter;

  static Future<void> ensureLoaded() async {
    if (_enPrefix != null) return;
    if (_loadCompleter != null) return _loadCompleter!.future;
    _loadCompleter = Completer<void>();
    try {
      final raw = await rootBundle.loadString('assets/data/search_index_v2.json');
      final map = json.decode(raw) as Map<String, dynamic>;
      _enPrefix    = _parseSection(map['en_prefix']);
      _bnPrefix    = _parseSection(map['bn_prefix']);
      _aliasLookup = _parseSection(map['alias_lookup']);
      _familyIndex = _parseSection(map['family_index']);
      _topFoods    = (map['top_foods'] as List?)?.cast<int>() ?? const [];
      _loadCompleter!.complete();
    } catch (e) {
      final c = _loadCompleter!;
      _loadCompleter = null;
      c.completeError(e);
      rethrow;
    }
  }

  static Map<String, List<int>> _parseSection(dynamic raw) {
    if (raw == null) return {};
    return (raw as Map<String, dynamic>)
        .map((k, v) => MapEntry(k, (v as List).cast<int>()));
  }

  /// Returns candidate food IDs matching any prefix of any word in [query].
  /// Also checks alias index for the full query.
  static Set<int> candidateIds(String query) {
    if (_enPrefix == null) return {};
    final q = query.toLowerCase().trim();
    if (q.length < 2) return {};

    final result = <int>{};
    final isBengali = _containsBengali(q);

    for (final word in q.split(RegExp(r'\s+'))) {
      if (word.length < 2) continue;
      if (isBengali) {
        // Bengali: use 2-char prefix
        final prefix = word.substring(0, 2);
        result.addAll(_bnPrefix?[prefix] ?? const []);
      } else {
        // English: use 2-char and 3-char prefixes
        result.addAll(_enPrefix?[word.substring(0, 2)] ?? const []);
        if (word.length >= 3) {
          result.addAll(_enPrefix?[word.substring(0, 3)] ?? const []);
        }
        // Also check alias index for whole word
        result.addAll(_aliasLookup?[word] ?? const []);
      }
    }
    return result;
  }

  /// Returns IDs for a specific food family (for grouping / filtered browse).
  static List<int> familyIds(String family) =>
      _familyIndex?[family] ?? const [];

  /// Top-100 food IDs by search_priority — useful for default / empty-search display.
  static List<int> get topFoodIds => _topFoods;

  static bool _containsBengali(String text) =>
      text.codeUnits.any((c) => c >= 0x0980 && c <= 0x09FF);

  static bool get isLoaded => _enPrefix != null;
}
