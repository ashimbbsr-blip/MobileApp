import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../models/food_item.dart';
import '../../../services/usda_api_service.dart';
import '../../../storage/hive_storage.dart';
import '../../../core/constants/app_constants.dart';

enum FoodSearchStatus { idle, loading, success, error, offline, rateLimited }

class _CacheEntry {
  final List<FoodItem> results;
  final DateTime cachedAt;
  _CacheEntry(this.results) : cachedAt = DateTime.now();

  bool get isExpired =>
      DateTime.now().difference(cachedAt).inMinutes >= AppConstants.searchCacheTtlMinutes;
}

class FoodSearchState {
  final List<FoodItem> results;
  final List<FoodItem> recentFoods;
  final FoodSearchStatus status;
  final String? errorMessage;
  final String query;
  final bool fromCache;

  const FoodSearchState({
    this.results = const [],
    this.recentFoods = const [],
    this.status = FoodSearchStatus.idle,
    this.errorMessage,
    this.query = '',
    this.fromCache = false,
  });

  FoodSearchState copyWith({
    List<FoodItem>? results,
    List<FoodItem>? recentFoods,
    FoodSearchStatus? status,
    String? errorMessage,
    String? query,
    bool? fromCache,
  }) {
    return FoodSearchState(
      results: results ?? this.results,
      recentFoods: recentFoods ?? this.recentFoods,
      status: status ?? this.status,
      errorMessage: errorMessage,
      query: query ?? this.query,
      fromCache: fromCache ?? this.fromCache,
    );
  }
}

class FoodSearchNotifier extends StateNotifier<FoodSearchState> {
  final UsdaApiService _apiService;

  // Session-level cache: query → results (10-min TTL, cleared on app restart)
  final Map<String, _CacheEntry> _sessionCache = {};
  bool _disposed = false;

  FoodSearchNotifier(this._apiService) : super(const FoodSearchState()) {
    _loadRecent();
  }

  void _loadRecent() {
    state = state.copyWith(recentFoods: HiveStorage.getCachedFoods().take(10).toList());
  }

  Future<void> search(String query) async {
    final normalized = query.trim().toLowerCase();

    // Ignore very short queries — don't waste API calls
    if (normalized.length < AppConstants.minSearchQueryLength) {
      state = state.copyWith(
        status: FoodSearchStatus.idle,
        results: [],
        query: '',
        fromCache: false,
      );
      return;
    }

    // ── 1. Session cache (fast path, avoids all network) ────────────────────
    final cached = _sessionCache[normalized];
    if (cached != null && !cached.isExpired) {
      _setIfMounted(state.copyWith(
        status: FoodSearchStatus.success,
        results: cached.results,
        query: query,
        fromCache: true,
      ));
      // Silently refresh in the background without showing a loading state
      _silentApiRefresh(query, normalized);
      return;
    }

    // ── 2. Local Hive food cache (instant, no network) ───────────────────────
    final localResults = HiveStorage.searchLocalCache(normalized);
    if (localResults.isNotEmpty) {
      _setIfMounted(state.copyWith(
        status: FoodSearchStatus.success,
        results: localResults,
        query: query,
        fromCache: true,
      ));
      // Silently refresh to get fresher/more results
      _silentApiRefresh(query, normalized);
      return;
    }

    // ── 3. USDA API (only when cache is empty) ───────────────────────────────
    _setIfMounted(state.copyWith(
      status: FoodSearchStatus.loading,
      query: query,
      fromCache: false,
    ));
    await _fetchFromApi(query, normalized);
  }

  Future<void> _fetchFromApi(String query, String normalized) async {
    try {
      final results = await _apiService.searchFoods(query);
      _sessionCache[normalized] = _CacheEntry(results);
      _evictOldestSessionEntries();
      for (final food in results.take(5)) {
        await HiveStorage.cacheFoodItem(food);
      }
      _setIfMounted(state.copyWith(
        status: FoodSearchStatus.success,
        results: results,
        fromCache: false,
      ));
    } on RateLimitException catch (e) {
      _setIfMounted(state.copyWith(
        status: FoodSearchStatus.rateLimited,
        errorMessage: e.message,
        results: [],
      ));
    } catch (e) {
      if (_disposed) return;
      final msg = e.toString();
      final isOffline = msg.contains('connection') ||
          msg.contains('network') ||
          msg.contains('timeout');
      state = state.copyWith(
        status: isOffline ? FoodSearchStatus.offline : FoodSearchStatus.error,
        errorMessage: msg.replaceAll('Exception: ', ''),
        results: [],
      );
    }
  }

  void _silentApiRefresh(String query, String normalized) {
    if (_apiService.isRateLimited) return;
    _apiService.searchFoods(query).then((results) {
      if (_disposed || results.isEmpty) return;
      _sessionCache[normalized] = _CacheEntry(results);
      for (final food in results.take(5)) {
        HiveStorage.cacheFoodItem(food);
      }
      // Only update state if the user is still on the same query
      if (!_disposed && state.query == query) {
        state = state.copyWith(results: results, fromCache: false);
      }
    }).catchError((_) {
      // Suppress all background refresh errors — user already has cached results
    });
  }

  void _evictOldestSessionEntries() {
    if (_sessionCache.length <= AppConstants.maxSessionCacheEntries) return;
    final oldest = _sessionCache.entries
        .reduce((a, b) =>
            a.value.cachedAt.isBefore(b.value.cachedAt) ? a : b)
        .key;
    _sessionCache.remove(oldest);
  }

  void _setIfMounted(FoodSearchState newState) {
    if (!_disposed) state = newState;
  }

  void clearSearch() {
    state = const FoodSearchState();
    _loadRecent();
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}

final foodSearchProvider =
    StateNotifierProvider<FoodSearchNotifier, FoodSearchState>(
  (ref) => FoodSearchNotifier(UsdaApiService()),
);
