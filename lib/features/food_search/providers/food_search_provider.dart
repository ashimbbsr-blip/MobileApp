import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../models/food_item.dart';
import '../../../services/usda_api_service.dart';
import '../../../services/local_food_repository.dart';
import '../../../storage/hive_storage.dart';
import '../../../core/constants/app_constants.dart';

enum UsdaSearchStatus { idle, loading, success, error, offline, rateLimited }

/// State for the Food Search screen — three fully independent sections.
class FoodSearchState {
  // ── Section 1: Local Indian & Bengali DB ─────────────────────────────────
  final String localQuery;
  final String? localCategory;
  final List<FoodItem> localResults;
  final bool localHasSearched;

  // ── Section 2: USDA International API ────────────────────────────────────
  final String usdaQuery;
  final List<FoodItem> usdaResults;
  final UsdaSearchStatus usdaStatus;
  final String? usdaError;
  final int? usdaCooldownSeconds;

  // ── Section 3: Custom (user-created) foods ────────────────────────────────
  final List<FoodItem> customFoods;

  // ── Shared ────────────────────────────────────────────────────────────────
  final List<FoodItem> recentFoods;

  const FoodSearchState({
    this.localQuery = '',
    this.localCategory,
    this.localResults = const [],
    this.localHasSearched = false,
    this.usdaQuery = '',
    this.usdaResults = const [],
    this.usdaStatus = UsdaSearchStatus.idle,
    this.usdaError,
    this.usdaCooldownSeconds,
    this.customFoods = const [],
    this.recentFoods = const [],
  });

  bool get localHasResults => localResults.isNotEmpty;
  bool get usdaHasResults => usdaResults.isNotEmpty;
  bool get hasCustomFoods => customFoods.isNotEmpty;
}

class FoodSearchNotifier extends StateNotifier<FoodSearchState> {
  final UsdaApiService _apiService;
  final Map<String, _CacheEntry> _sessionCache = {};
  bool _disposed = false;

  FoodSearchNotifier(this._apiService) : super(const FoodSearchState()) {
    _loadInitial();
  }

  void _loadInitial() {
    if (!_disposed) {
      state = FoodSearchState(
        recentFoods: HiveStorage.getCachedFoods().take(10).toList(),
        customFoods: HiveStorage.getCustomFoods(),
      );
    }
  }

  // ── Section 1: Local ──────────────────────────────────────────────────────

  /// Explicit search — called when user taps the Search button.
  void searchLocal(String query) {
    if (_disposed) return;
    final q = query.trim().toLowerCase();
    final results = LocalFoodRepository.search(q, category: state.localCategory);
    if (!_disposed) {
      state = FoodSearchState(
        localQuery: query,
        localCategory: state.localCategory,
        localResults: results,
        localHasSearched: true,
        usdaQuery: state.usdaQuery,
        usdaResults: state.usdaResults,
        usdaStatus: state.usdaStatus,
        usdaError: state.usdaError,
        usdaCooldownSeconds: state.usdaCooldownSeconds,
        customFoods: state.customFoods,
        recentFoods: state.recentFoods,
      );
    }
  }

  /// Category chip tap — instant browse, no search button needed.
  void setLocalCategory(String? category) {
    if (_disposed) return;
    final newCat = category == state.localCategory ? null : category;
    final q = state.localQuery.trim().toLowerCase();
    final results = LocalFoodRepository.search(q, category: newCat);
    if (!_disposed) {
      state = FoodSearchState(
        localQuery: state.localQuery,
        localCategory: newCat,
        localResults: results,
        localHasSearched: state.localHasSearched || newCat != null,
        usdaQuery: state.usdaQuery,
        usdaResults: state.usdaResults,
        usdaStatus: state.usdaStatus,
        usdaError: state.usdaError,
        usdaCooldownSeconds: state.usdaCooldownSeconds,
        customFoods: state.customFoods,
        recentFoods: state.recentFoods,
      );
    }
  }

  void clearLocalSearch() {
    if (!_disposed) {
      state = FoodSearchState(
        localQuery: '',
        localCategory: null,
        localResults: const [],
        localHasSearched: false,
        usdaQuery: state.usdaQuery,
        usdaResults: state.usdaResults,
        usdaStatus: state.usdaStatus,
        usdaError: state.usdaError,
        usdaCooldownSeconds: state.usdaCooldownSeconds,
        customFoods: state.customFoods,
        recentFoods: state.recentFoods,
      );
    }
  }

  // ── Section 2: USDA ───────────────────────────────────────────────────────

  /// Explicit USDA search — called when user taps the USDA Search button.
  Future<void> searchUsda(String query) async {
    if (_disposed) return;
    final q = query.trim();
    if (q.isEmpty) return;
    final normalized = q.toLowerCase();

    // Session cache
    final cached = _sessionCache[normalized];
    if (cached != null && !cached.isExpired) {
      if (!_disposed) {
        state = FoodSearchState(
          localQuery: state.localQuery,
          localCategory: state.localCategory,
          localResults: state.localResults,
          localHasSearched: state.localHasSearched,
          usdaQuery: query,
          usdaResults: cached.results,
          usdaStatus: UsdaSearchStatus.success,
          customFoods: state.customFoods,
          recentFoods: state.recentFoods,
        );
      }
      _silentApiRefresh(q, normalized);
      return;
    }

    // Hive USDA cache
    final hiveResults = HiveStorage.searchLocalCache(normalized);
    if (hiveResults.isNotEmpty) {
      if (!_disposed) {
        state = FoodSearchState(
          localQuery: state.localQuery,
          localCategory: state.localCategory,
          localResults: state.localResults,
          localHasSearched: state.localHasSearched,
          usdaQuery: query,
          usdaResults: hiveResults,
          usdaStatus: UsdaSearchStatus.success,
          customFoods: state.customFoods,
          recentFoods: state.recentFoods,
        );
      }
      _silentApiRefresh(q, normalized);
      return;
    }

    // Live API call
    if (!_disposed) {
      state = FoodSearchState(
        localQuery: state.localQuery,
        localCategory: state.localCategory,
        localResults: state.localResults,
        localHasSearched: state.localHasSearched,
        usdaQuery: query,
        usdaResults: const [],
        usdaStatus: UsdaSearchStatus.loading,
        customFoods: state.customFoods,
        recentFoods: state.recentFoods,
      );
    }
    await _fetchFromApi(q, normalized);
  }

  Future<void> _fetchFromApi(String query, String normalized) async {
    try {
      final results = await _apiService.searchFoods(query);
      _sessionCache[normalized] = _CacheEntry(results);
      _evictOldest();
      for (final food in results.take(5)) {
        await HiveStorage.cacheFoodItem(food);
      }
      if (!_disposed) {
        state = FoodSearchState(
          localQuery: state.localQuery,
          localCategory: state.localCategory,
          localResults: state.localResults,
          localHasSearched: state.localHasSearched,
          usdaQuery: state.usdaQuery,
          usdaResults: results,
          usdaStatus: UsdaSearchStatus.success,
          customFoods: state.customFoods,
          recentFoods: state.recentFoods,
        );
      }
    } on RateLimitException catch (e) {
      if (!_disposed) {
        state = FoodSearchState(
          localQuery: state.localQuery,
          localCategory: state.localCategory,
          localResults: state.localResults,
          localHasSearched: state.localHasSearched,
          usdaQuery: state.usdaQuery,
          usdaStatus: UsdaSearchStatus.rateLimited,
          usdaError: e.message,
          usdaCooldownSeconds: e.cooldownSeconds,
          customFoods: state.customFoods,
          recentFoods: state.recentFoods,
        );
      }
    } catch (e) {
      if (_disposed) return;
      final msg = e.toString().replaceAll('Exception: ', '');
      final isOffline = msg.contains('No internet') ||
          msg.contains('Network timeout') ||
          msg.contains('No internet connection');
      state = FoodSearchState(
        localQuery: state.localQuery,
        localCategory: state.localCategory,
        localResults: state.localResults,
        localHasSearched: state.localHasSearched,
        usdaQuery: state.usdaQuery,
        usdaStatus:
            isOffline ? UsdaSearchStatus.offline : UsdaSearchStatus.error,
        usdaError: msg,
        customFoods: state.customFoods,
        recentFoods: state.recentFoods,
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
      if (!_disposed && state.usdaQuery.trim() == query.trim()) {
        state = FoodSearchState(
          localQuery: state.localQuery,
          localCategory: state.localCategory,
          localResults: state.localResults,
          localHasSearched: state.localHasSearched,
          usdaQuery: state.usdaQuery,
          usdaResults: results,
          usdaStatus: UsdaSearchStatus.success,
          customFoods: state.customFoods,
          recentFoods: state.recentFoods,
        );
      }
    }).catchError((_) {});
  }

  void _evictOldest() {
    if (_sessionCache.length <= AppConstants.maxSessionCacheEntries) return;
    final oldest = _sessionCache.entries
        .reduce((a, b) => a.value.cachedAt.isBefore(b.value.cachedAt) ? a : b)
        .key;
    _sessionCache.remove(oldest);
  }

  // ── Section 3: Custom foods ───────────────────────────────────────────────

  Future<void> addCustomFood(FoodItem food) async {
    await HiveStorage.saveCustomFood(food);
    _refreshCustomFoods();
  }

  Future<void> deleteCustomFood(String id) async {
    await HiveStorage.deleteCustomFood(id);
    _refreshCustomFoods();
  }

  void _refreshCustomFoods() {
    if (!_disposed) {
      state = FoodSearchState(
        localQuery: state.localQuery,
        localCategory: state.localCategory,
        localResults: state.localResults,
        localHasSearched: state.localHasSearched,
        usdaQuery: state.usdaQuery,
        usdaResults: state.usdaResults,
        usdaStatus: state.usdaStatus,
        usdaError: state.usdaError,
        usdaCooldownSeconds: state.usdaCooldownSeconds,
        customFoods: HiveStorage.getCustomFoods(),
        recentFoods: state.recentFoods,
      );
    }
  }

  @override
  void dispose() {
    _disposed = true;
    super.dispose();
  }
}

class _CacheEntry {
  final List<FoodItem> results;
  final DateTime cachedAt;
  _CacheEntry(this.results) : cachedAt = DateTime.now();
  bool get isExpired =>
      DateTime.now().difference(cachedAt).inMinutes >=
      AppConstants.searchCacheTtlMinutes;
}

final foodSearchProvider =
    StateNotifierProvider<FoodSearchNotifier, FoodSearchState>(
  (ref) => FoodSearchNotifier(UsdaApiService()),
);
