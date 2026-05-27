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
          await rootBundle.loadString('assets/data/food_master_v5_3.json');
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

    // Empty query with category → browse all items in that category.
    if (q.isEmpty && category != null) {
      return _items!.where((f) => f.category == category).take(limit).toList();
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

  static int _score(FoodItem food, String q) {
    final en = food.name.toLowerCase();
    final bn = food.nameBn?.toLowerCase() ?? '';
    final kwList = food.keywords ?? [];
    final kw = kwList.join(' ');

    if (en == q || bn == q) return 100;
    if (en.startsWith(q) || bn.startsWith(q)) return 80;

    if (q.length == 1) {
      final enWords = en.split(RegExp(r'[\s/\-]+'));
      final bnWords = bn.split(RegExp(r'[\s/\-]+'));
      if (enWords.any((w) => w.startsWith(q)) ||
          bnWords.any((w) => w.startsWith(q)) ||
          kwList.any((w) => w.startsWith(q))) return 70;
      return 0;
    }

    if (en.contains(q) || bn.contains(q)) return 60;
    if (kw.contains(q)) return 40;

    final words = q.split(RegExp(r'\s+'));
    if (words.length > 1) {
      final combined = '$en $bn $kw';
      if (words.every(combined.contains)) return 50;
    }
    return 0;
  }
}

class _Scored {
  final FoodItem food;
  final int score;
  const _Scored(this.food, this.score);
}
