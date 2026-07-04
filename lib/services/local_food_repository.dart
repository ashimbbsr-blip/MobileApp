import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import '../models/food_item.dart';
import 'local_search_service.dart';

List<Map<String, dynamic>> _decodeJsonIsolate(String jsonStr) {
  final List<dynamic> raw = json.decode(jsonStr);
  return raw.whereType<Map<String, dynamic>>().toList();
}

/// In-memory bilingual food repository backed by assets/data/food_master_v10.json.
///
/// Loaded once at startup via [init()]. All subsequent [search] calls are
/// pure in-memory operations — no Hive, no network, < 5ms per query.
///
/// Search uses [LocalSearchService] as a candidate pre-filter when loaded,
/// reducing the scoring pass from 5000 to ~50–300 items per query.
class LocalFoodRepository {
  static List<FoodItem>? _items;
  static Map<String, FoodItem> _idMap = {};
  static String? _initError;
  static int _skippedCount = 0;

  static Future<void> init() async {
    if (_items != null) return;
    try {
      final jsonStr =
          await rootBundle.loadString('assets/data/food_master_v10.json');
      if (jsonStr.isEmpty) {
        _initError = 'Food database is empty. Please reinstall the app.';
        _items = [];
        return;
      }
      final rawMaps = await compute(_decodeJsonIsolate, jsonStr);
      final list = <FoodItem>[];
      int skipped = 0;
      for (final m in rawMaps) {
        try {
          final item = FoodItem.fromLocalJson(m);
          list.add(item);
        } catch (e) {
          skipped++;
          debugPrint('[LocalFoodRepo] skipped id=${m['id']}: $e');
        }
      }
      _skippedCount = skipped;
      _items = list;
      _idMap = {for (final f in list) f.id: f};
      if (skipped > 0) {
        debugPrint('[LocalFoodRepo] $skipped items skipped');
        if (skipped > 100) {
          _initError = 'Warning: $skipped foods failed to load correctly.';
        }
      }
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

  // ── Search ─────────────────────────────────────────────────────────────────

  /// Full-text bilingual search with multi-tier relevance scoring.
  ///
  /// Score tiers:
  ///   950  exact match (EN or BN)
  ///   800  word-start match in EN/BN
  ///   700  phrase-start (EN/BN startsWith query)
  ///   600  any word in name starts with query
  ///   500  substring match in EN or BN name
  ///   430  keyword/alias exact match
  ///   400  keyword/alias contains query
  ///   350  all query words present anywhere
  ///   280  any query word (>=4 chars) found
  ///   250  3-char prefix match on any word
  ///
  /// searchPriority (0-100) adds up to +90 as tiebreaker within each tier.
  static List<FoodItem> search(String query,
      {String? category, int limit = 25}) {
    if (_items == null || _items!.isEmpty) return [];
    final q = query.toLowerCase().trim();

    // Category browse: no query, just show top items in that category
    if (q.isEmpty && category != null) {
      final items = _items!.where((f) => f.category == category).toList()
        ..sort((a, b) => (b.searchPriority ?? 50).compareTo(a.searchPriority ?? 50));
      return items.take(limit).toList();
    }
    if (q.isEmpty) return [];

    // Candidate pre-filter via search index (if loaded).
    // Use a low threshold (1) so the index is always used when it returns any results.
    Iterable<FoodItem> pool;
    if (LocalSearchService.isLoaded) {
      final candidateSet = LocalSearchService.candidateIds(q);
      if (candidateSet.isNotEmpty) {
        pool = candidateSet
            .map((id) => _idMap['local_$id'])
            .whereType<FoodItem>();
        // If fewer than 20 candidates, supplement with full scan for safety
        if (candidateSet.length < 20) {
          pool = _items!;
        }
      } else {
        pool = _items!;
      }
    } else {
      pool = _items!;
    }

    final results = <_Scored>[];
    for (final food in pool) {
      if (category != null && food.category != category) continue;
      final s = _score(food, q);
      if (s > 0) results.add(_Scored(food, s));
    }
    results.sort((a, b) => b.score.compareTo(a.score));
    return results.take(limit).map((s) => s.food).toList();
  }

  static int _score(FoodItem food, String q) {
    final en     = food.name.toLowerCase().trim();
    final bn     = (food.nameBn ?? '').toLowerCase().trim();
    final kwList = food.keywords ?? [];
    final kw     = kwList.join(' ').toLowerCase();
    final alList = food.aliases ?? [];
    final al     = alList.join(' ').toLowerCase();
    final pri    = food.searchPriority ?? 50;
    final bonus  = (pri * 0.9).round(); // up to +90

    // ── Tier 1: Exact match ──────────────────────────────────────────────────
    if (en == q || bn == q) return 950 + bonus;

    final enWords = en.split(RegExp(r'[\s/\-\(\),\.]+'));
    final bnWords = bn.split(RegExp(r'[\s/\-\(\),\.]+'));

    // ── Tier 2: Word-start match (any word in name starts with query) ────────
    if (enWords.any((w) => w.isNotEmpty && w.startsWith(q)) ||
        bnWords.any((w) => w.isNotEmpty && w.startsWith(q))) {
      return 800 + bonus;
    }

    // ── Tier 3: Phrase-start ─────────────────────────────────────────────────
    if (en.startsWith(q) || bn.startsWith(q)) return 700 + bonus;

    // ── Single character: word-start in name or keywords ─────────────────────
    if (q.length == 1) {
      if (enWords.any((w) => w.isNotEmpty && w.startsWith(q))) return 600 + bonus;
      if (bnWords.any((w) => w.isNotEmpty && w.startsWith(q))) return 600 + bonus;
      if (kwList.any((w) => w.toLowerCase().startsWith(q))) return 550 + bonus;
      return 0;
    }

    // ── Tier 4: Substring in name ────────────────────────────────────────────
    if (en.contains(q) || bn.contains(q)) return 500 + bonus;

    // ── Tier 5: Keyword / alias exact word match ─────────────────────────────
    if (kwList.any((w) => w.toLowerCase() == q) ||
        alList.any((w) => w.toLowerCase() == q)) {
      return 430 + bonus;
    }

    // ── Tier 6: Keyword / alias substring match ───────────────────────────────
    if (kw.contains(q) || al.contains(q)) return 400 + bonus;

    // ── Tier 7: Multi-word — all words present anywhere ──────────────────────
    final qWords = q.split(RegExp(r'\s+'));
    if (qWords.length > 1) {
      final combined = '$en $bn $kw $al';
      if (qWords.every((w) => combined.contains(w))) return 350 + bonus;
      // Partial multi-word: most words match
      final matchCount = qWords.where((w) => combined.contains(w)).length;
      if (matchCount >= (qWords.length * 0.75).ceil()) return 320 + bonus;
    }

    // ── Fuzzy: partial word overlap (last resort) ─────────────────────────────
    if (q.length >= 3) {
      final combined = '$en $bn $kw $al';
      for (final w in qWords) {
        if (w.length >= 4 && combined.contains(w)) return 280 + bonus;
      }
      final qPfx = q.substring(0, q.length.clamp(0, 3));
      if (enWords.any((w) => w.startsWith(qPfx)) ||
          bnWords.any((w) => w.startsWith(qPfx))) {
        return 250 + bonus;
      }
    }

    return 0;
  }

  /// Returns the top foods (by searchPriority) for the initial browse state.
  static List<FoodItem> topFoods({int limit = 50}) {
    if (_items == null || _items!.isEmpty) return [];
    if (LocalSearchService.isLoaded) {
      final topIds = LocalSearchService.topFoodIds;
      final top = topIds
          .map((id) => _idMap['local_$id'])
          .whereType<FoodItem>()
          .take(limit)
          .toList();
      if (top.isNotEmpty) return top;
    }
    return (_items!.toList()
      ..sort((a, b) =>
          (b.searchPriority ?? 50).compareTo(a.searchPriority ?? 50)))
        .take(limit)
        .toList();
  }
}

class _Scored {
  final FoodItem food;
  final int score;
  const _Scored(this.food, this.score);
}
