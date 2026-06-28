import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import '../models/food_item.dart';

// Top-level function for compute() — decodes JSON in a background isolate.
List<Map<String, dynamic>> _decodeJsonIsolate(String jsonStr) {
  final List<dynamic> raw = json.decode(jsonStr);
  return raw.whereType<Map<String, dynamic>>().toList();
}

/// In-memory bilingual food repository backed by assets/data/food_master.json.
///
/// Loaded once at startup via [init()]. All subsequent [search] calls are
/// pure in-memory operations — no Hive, no network, < 5ms per query.
class LocalFoodRepository {
  static List<FoodItem>? _items;
  static String? _initError;
  static int _skippedCount = 0;

  static Future<void> init() async {
    if (_items != null) return;
    try {
      final jsonStr =
          await rootBundle.loadString('assets/data/food_master_v8_2.json');
      if (jsonStr.isEmpty) {
        debugPrint('[LocalFoodRepo] food_master.json is empty');
        _items = [];
        return;
      }
      // Decode JSON in background isolate — avoids blocking main thread.
      final rawMaps = await compute(_decodeJsonIsolate, jsonStr);
      final list = <FoodItem>[];
      int skipped = 0;
      for (final m in rawMaps) {
        try {
          list.add(FoodItem.fromLocalJson(m));
        } catch (e) {
          skipped++;
          debugPrint('[LocalFoodRepo] skipped item id=${m['id']}: $e');
        }
      }
      _skippedCount = skipped;
      _items = list;
      if (skipped > 0) debugPrint('[LocalFoodRepo] $skipped items skipped');
      debugPrint('[LocalFoodRepo] loaded ${_items!.length} items');
    } catch (e, st) {
      _initError = e.toString();
      debugPrint('[LocalFoodRepo] init failed: $e\n$st');
      _items = [];
    }
  }

  static bool get isReady => _items != null && _items!.isNotEmpty;
  static int get itemCount => _items?.length ?? 0;
  static int get skippedCount => _skippedCount;
  static String? get initError => _initError;

  // ── Search ────────────────────────────────────────────────────────────────

  /// Full-text search across English name, Bengali name, and keywords.
  /// Handles single-character queries with word-start matching to keep results
  /// relevant. Returns up to [limit] results sorted by relevance score.
  static List<FoodItem> search(String query,
      {String? category, int limit = 25}) {
    if (_items == null || _items!.isEmpty) return [];
    final q = query.toLowerCase().trim();

    // Empty query with category → browse all items, sorted by searchPriority.
    if (q.isEmpty && category != null) {
      final items = _items!.where((f) => f.category == category).toList()
        ..sort((a, b) => (b.searchPriority ?? 50).compareTo(a.searchPriority ?? 50));
      return items.take(limit).toList();
    }
    if (q.isEmpty) return [];

    final results = <_Scored>[];
    for (final food in _items!) {
      if (category != null && food.category != category) continue;
      final s = _score(food, q);
      if (s > 0) results.add(_Scored(food, s));
    }
    results.sort((a, b) => b.score.compareTo(a.score));
    return results.take(limit).map((s) => s.food).toList();
  }

  // Returns a relevance score in [0, 1000].
  // Tiers: exact=900, word-start=700, phrase-start=600, contains=500,
  //        keyword-match=400, multi-word=350.
  // searchPriority (0-100) is added as a 0-90 tiebreaker within each tier
  // so that higher-quality / more-popular foods rank first when match strength
  // is equal.
  static int _score(FoodItem food, String q) {
    final en     = food.name.toLowerCase();
    final bn     = food.nameBn?.toLowerCase() ?? '';
    final kwList = food.keywords ?? [];
    final kw     = kwList.join(' ');
    final alList = food.aliases ?? [];
    final al     = alList.join(' ');
    final pri    = food.searchPriority ?? 50; // 0-100
    final bonus  = (pri * 0.9).round();       // up to +90

    if (en == q || bn == q) return 900 + bonus;
    if (en.startsWith(q) || bn.startsWith(q)) return 700 + bonus;

    if (q.length == 1) {
      final enWords = en.split(RegExp(r'[\s/\-]+'));
      final bnWords = bn.split(RegExp(r'[\s/\-]+'));
      if (enWords.any((w) => w.startsWith(q)) ||
          bnWords.any((w) => w.startsWith(q)) ||
          kwList.any((w) => w.startsWith(q))) { return 600 + bonus; }
      return 0;
    }

    if (en.contains(q) || bn.contains(q)) return 500 + bonus;
    if (kw.contains(q) || al.contains(q))  return 400 + bonus;

    final words = q.split(RegExp(r'\s+'));
    if (words.length > 1) {
      final combined = '$en $bn $kw $al';
      if (words.every(combined.contains)) return 350 + bonus;
    }
    return 0;
  }
}

class _Scored {
  final FoodItem food;
  final int score;
  const _Scored(this.food, this.score);
}
