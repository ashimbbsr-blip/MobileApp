import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import '../models/food_item.dart';
import 'local_search_service.dart';

List<Map<String, dynamic>> _decodeJsonIsolate(String jsonStr) {
  final List<dynamic> raw = json.decode(jsonStr);
  return raw.whereType<Map<String, dynamic>>().toList();
}

/// In-memory bilingual food repository backed by assets/data/food_master_v9_0.json.
///
/// Loaded once at startup via [init()]. All subsequent [search] calls are
/// pure in-memory operations — no Hive, no network, < 5ms per query.
///
/// Search uses [LocalSearchService] as a candidate pre-filter when loaded,
/// reducing the scoring pass from 4000 to ~50–300 items per query.
class LocalFoodRepository {
  static List<FoodItem>? _items;
  static Map<String, FoodItem> _idMap = {};
  static String? _initError;
  static int _skippedCount = 0;

  static Future<void> init() async {
    if (_items != null) return;
    try {
      final jsonStr =
          await rootBundle.loadString('assets/data/food_master_v9_0.json');
      if (jsonStr.isEmpty) {
        debugPrint('[LocalFoodRepo] food_master.json is empty');
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
          debugPrint('[LocalFoodRepo] skipped item id=${m['id']}: $e');
        }
      }
      _skippedCount = skipped;
      _items = list;
      // Index by the numeric part of the local ID (e.g. 'local_1234' → 1234)
      // so we can look up by integer IDs from LocalSearchService.
      _idMap = {for (final f in list) f.id: f};
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

  // ── Search ─────────────────────────────────────────────────────────────────

  /// Full-text bilingual search with multi-tier relevance scoring.
  ///
  /// When [LocalSearchService] is loaded, uses candidate pre-filtering to
  /// score only relevant foods (~50–300) instead of the full 4000-item list.
  ///
  /// Score tiers:
  ///   950  exact match (EN or BN)
  ///   800  word-start match in EN/BN
  ///   700  phrase-start (EN/BN startsWith query)
  ///   600  any word in name starts with query (single-char supported)
  ///   500  substring match in EN or BN
  ///   430  alias / keyword exact match
  ///   400  keyword / alias contains query
  ///   350  all words of query present in combined fields
  ///
  /// searchPriority (0-100) adds up to +90 as tiebreaker within each tier.
  static List<FoodItem> search(String query,
      {String? category, int limit = 25}) {
    if (_items == null || _items!.isEmpty) return [];
    final q = query.toLowerCase().trim();

    if (q.isEmpty && category != null) {
      final items = _items!.where((f) => f.category == category).toList()
        ..sort((a, b) => (b.searchPriority ?? 50).compareTo(a.searchPriority ?? 50));
      return items.take(limit).toList();
    }
    if (q.isEmpty) return [];

    // Use search service candidate pre-filter when available.
    // Falls back to full scan if the index isn't loaded yet or returns too few hits.
    Iterable<FoodItem> pool;
    if (LocalSearchService.isLoaded) {
      final candidateSet = LocalSearchService.candidateIds(q);
      if (candidateSet.length >= 5) {
        // Search service returns int IDs; local items have 'local_N' string IDs.
        pool = candidateSet
            .map((id) => _idMap['local_$id'])
            .whereType<FoodItem>();
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
    final en     = food.name.toLowerCase();
    final bn     = (food.nameBn ?? '').toLowerCase();
    final kwList = food.keywords ?? [];
    final kw     = kwList.join(' ').toLowerCase();
    final alList = food.aliases ?? [];
    final al     = alList.join(' ').toLowerCase();
    final pri    = food.searchPriority ?? 50;
    final bonus  = (pri * 0.9).round(); // up to +90

    // ── Tier 1: Exact match ──────────────────────────────────────────────────
    if (en == q || bn == q) return 950 + bonus;

    // ── Tier 2: Word-start match ─────────────────────────────────────────────
    // Any word in the name starts with the entire query
    final enWords = en.split(RegExp(r'[\s/\-\(\)]+'));
    final bnWords = bn.split(RegExp(r'[\s/\-\(\)]+'));
    if (enWords.any((w) => w.isNotEmpty && w.startsWith(q)) ||
        bnWords.any((w) => w.isNotEmpty && w.startsWith(q))) {
      return 800 + bonus;
    }

    // ── Tier 3: Phrase-start ─────────────────────────────────────────────────
    if (en.startsWith(q) || bn.startsWith(q)) return 700 + bonus;

    // ── Single character: word-start only ────────────────────────────────────
    if (q.length == 1) {
      if (kwList.any((w) => w.toLowerCase().startsWith(q))) return 600 + bonus;
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
    }

    // ── Fuzzy: partial word overlap (last resort) ─────────────────────────────
    // Check if at least one meaningful word from query matches
    if (q.length >= 4) {
      final combined = '$en $bn $kw $al';
      for (final w in qWords) {
        if (w.length >= 4 && combined.contains(w)) return 280 + bonus;
      }
      // Check prefix of query against prefix of any word
      final qPrefix3 = q.length >= 3 ? q.substring(0, 3) : q;
      if (enWords.any((w) => w.startsWith(qPrefix3)) ||
          bnWords.any((w) => w.startsWith(qPrefix3))) {
        return 250 + bonus;
      }
    }

    return 0;
  }
}

class _Scored {
  final FoodItem food;
  final int score;
  const _Scored(this.food, this.score);
}
