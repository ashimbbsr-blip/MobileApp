import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../localization/app_localizations.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../widgets/common/loading_indicator.dart';
import '../../models/food_item.dart';
import '../../core/constants/app_constants.dart';
import '../food_search/providers/food_search_provider.dart';

class FoodSearchScreen extends ConsumerStatefulWidget {
  const FoodSearchScreen({super.key});

  @override
  ConsumerState<FoodSearchScreen> createState() => _FoodSearchScreenState();
}

class _FoodSearchScreenState extends ConsumerState<FoodSearchScreen> {
  final _searchController = TextEditingController();
  Timer? _debounceTimer;

  @override
  void initState() {
    super.initState();
    _searchController.addListener(_onSearchChanged);
  }

  void _onSearchChanged() {
    _debounceTimer?.cancel();
    final query = _searchController.text;
    // Update suffix icon without rebuilding the whole tree
    setState(() {});
    _debounceTimer = Timer(const Duration(milliseconds: 700), () {
      if (query.trim().length < AppConstants.minSearchQueryLength) {
        ref.read(foodSearchProvider.notifier).clearSearch();
      } else {
        ref.read(foodSearchProvider.notifier).search(query);
      }
    });
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(foodSearchProvider);
    final l10n = ref.watch(appStringsProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.foodSearch),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
            child: TextField(
              controller: _searchController,
              autofocus: false,
              decoration: InputDecoration(
                hintText: l10n.searchFood,
                prefixIcon: const Icon(Icons.search),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          ref.read(foodSearchProvider.notifier).clearSearch();
                        },
                      )
                    : null,
              ),
              onSubmitted: (q) {
                if (q.trim().length >= AppConstants.minSearchQueryLength) {
                  ref.read(foodSearchProvider.notifier).search(q);
                }
              },
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          // Cached-result banner — shown when displaying local cache hits
          if (state.fromCache && state.results.isNotEmpty)
            _CachedBanner(l10n: l10n),
          Expanded(child: _buildBody(context, state, l10n)),
        ],
      ),
    );
  }

  Widget _buildBody(BuildContext context, FoodSearchState state, AppStrings l10n) {
    switch (state.status) {
      case FoodSearchStatus.loading:
        return const Column(
          children: [SizedBox(height: 32), LoadingIndicator()],
        );

      case FoodSearchStatus.rateLimited:
        return _RateLimitedView(
          message: state.errorMessage,
          cachedFoods: state.recentFoods,
          l10n: l10n,
        );

      case FoodSearchStatus.error:
        return _ErrorView(
          message: state.errorMessage ?? l10n.error,
          onRetry: () => ref.read(foodSearchProvider.notifier).search(state.query),
        );

      case FoodSearchStatus.offline:
        return _OfflineView(cachedFoods: state.recentFoods, l10n: l10n);

      case FoodSearchStatus.success:
        if (state.results.isEmpty) {
          return Center(child: Text(l10n.noResults));
        }
        return _FoodList(foods: state.results);

      case FoodSearchStatus.idle:
        if (state.recentFoods.isNotEmpty) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                child: Text(
                  l10n.recent,
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ),
              Expanded(child: _FoodList(foods: state.recentFoods)),
            ],
          );
        }
        return Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.search, size: 64, color: AppColors.primary.withValues(alpha: 0.3)),
              const SizedBox(height: 16),
              Text(l10n.searchFood, style: Theme.of(context).textTheme.bodyLarge),
              const SizedBox(height: 8),
              Text(
                l10n.searchMinChars,
                style: Theme.of(context).textTheme.bodySmall,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        );
    }
  }
}

// ── Cached banner ─────────────────────────────────────────────────────────────

class _CachedBanner extends StatelessWidget {
  final AppStrings l10n;
  const _CachedBanner({required this.l10n});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      color: AppColors.primary.withValues(alpha: 0.08),
      child: Row(
        children: [
          const Icon(Icons.offline_bolt_outlined, size: 14, color: AppColors.primary),
          const SizedBox(width: 6),
          Text(
            l10n.cachedResults,
            style: const TextStyle(
              fontSize: 12,
              color: AppColors.primary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

// ── Rate-limited view ─────────────────────────────────────────────────────────

class _RateLimitedView extends StatelessWidget {
  final String? message;
  final List<FoodItem> cachedFoods;
  final AppStrings l10n;
  const _RateLimitedView({this.message, required this.cachedFoods, required this.l10n});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Colors.amber.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.amber.withValues(alpha: 0.4)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Icon(Icons.hourglass_top_rounded, color: Colors.amber, size: 22),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.rateLimitTitle,
                      style: const TextStyle(
                          color: Colors.amber,
                          fontWeight: FontWeight.w700,
                          fontSize: 14),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      message ?? l10n.rateLimitMessage,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        if (cachedFoods.isNotEmpty) ...[
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(l10n.recent,
                  style: Theme.of(context)
                      .textTheme
                      .titleSmall
                      ?.copyWith(fontWeight: FontWeight.w600)),
            ),
          ),
          Expanded(child: _FoodList(foods: cachedFoods)),
        ] else
          Expanded(child: Center(child: Text(l10n.noResults))),
      ],
    );
  }
}

// ── Food list ─────────────────────────────────────────────────────────────────

class _FoodList extends StatelessWidget {
  final List<FoodItem> foods;
  const _FoodList({required this.foods});

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      itemCount: foods.length,
      itemBuilder: (context, i) => _FoodTile(food: foods[i]),
    );
  }
}

class _FoodTile extends StatelessWidget {
  final FoodItem food;
  const _FoodTile({required this.food});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: AppColors.primary.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Icon(Icons.fastfood_outlined, color: AppColors.primary, size: 22),
        ),
        title: Text(
          food.name,
          style: Theme.of(context)
              .textTheme
              .titleSmall
              ?.copyWith(fontWeight: FontWeight.w600),
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          '${food.calories.toStringAsFixed(0)} kcal | '
          'P: ${food.proteinG.toStringAsFixed(1)}g | '
          'C: ${food.carbsG.toStringAsFixed(1)}g | '
          'F: ${food.fatG.toStringAsFixed(1)}g',
          style: Theme.of(context).textTheme.bodySmall,
        ),
        trailing: const Icon(Icons.chevron_right, size: 20),
        onTap: () => context.push('/food-search/detail', extra: food),
      ),
    );
  }
}

// ── Error view ────────────────────────────────────────────────────────────────

class _ErrorView extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;
  const _ErrorView({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, _) {
      final l10n = ref.watch(appStringsProvider);
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, size: 56, color: Colors.red),
              const SizedBox(height: 16),
              Text(message, textAlign: TextAlign.center),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                icon: const Icon(Icons.refresh),
                label: Text(l10n.retry),
                onPressed: onRetry,
              ),
            ],
          ),
        ),
      );
    });
  }
}

// ── Offline view ──────────────────────────────────────────────────────────────

class _OfflineView extends StatelessWidget {
  final List<FoodItem> cachedFoods;
  final AppStrings l10n;
  const _OfflineView({required this.cachedFoods, required this.l10n});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          margin: const EdgeInsets.all(16),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.orange.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            children: [
              const Icon(Icons.wifi_off, color: Colors.orange),
              const SizedBox(width: 8),
              Expanded(
                child: Text(l10n.offline,
                    style: const TextStyle(color: Colors.orange)),
              ),
            ],
          ),
        ),
        if (cachedFoods.isNotEmpty)
          Expanded(child: _FoodList(foods: cachedFoods))
        else
          Expanded(child: Center(child: Text(l10n.noResults))),
      ],
    );
  }
}
