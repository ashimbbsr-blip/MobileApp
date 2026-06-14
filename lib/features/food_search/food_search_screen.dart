import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../models/food_item.dart';
import '../../services/local_food_repository.dart';
import 'providers/food_search_provider.dart';
import '../../core/utils/meal_time_utils.dart';

// ── Category metadata ─────────────────────────────────────────────────────────

// All normalised categories present in the dataset.
const _localCategories = [
  'rice', 'bread', 'vegetable', 'legume', 'fish', 'meat', 'egg', 'dairy',
  'fruit', 'snack', 'sweet', 'dessert', 'beverage', 'soup', 'breakfast',
  'grain', 'salad', 'noodle',
];

const _catIcons = <String, IconData>{
  'rice':      Icons.rice_bowl_outlined,
  'bread':     Icons.breakfast_dining_outlined,
  'vegetable': Icons.eco_outlined,
  'legume':    Icons.grass_outlined,
  'fruit':     Icons.apple_outlined,
  'fish':      Icons.set_meal_outlined,
  'meat':      Icons.lunch_dining_outlined,
  'egg':       Icons.egg_outlined,
  'dairy':     Icons.water_drop_outlined,
  'snack':     Icons.cookie_outlined,
  'sweet':     Icons.cake_outlined,
  'dessert':   Icons.icecream_outlined,
  'beverage':  Icons.local_drink_outlined,
  'soup':      Icons.soup_kitchen_outlined,
  'breakfast': Icons.free_breakfast_outlined,
  'grain':     Icons.grain_outlined,
  'salad':     Icons.local_florist_outlined,
  'noodle':    Icons.ramen_dining_outlined,
  'other':     Icons.fastfood_outlined,
};

Color _catColor(String? cat) {
  switch (cat) {
    case 'rice':      return const Color(0xFFFF8C42);
    case 'bread':     return const Color(0xFFE6A020);
    case 'legume':    return const Color(0xFFD4A017);
    case 'vegetable': return const Color(0xFF43A047);
    case 'fruit':     return const Color(0xFFD81B60);
    case 'fish':      return const Color(0xFF1E88E5);
    case 'meat':      return const Color(0xFFD32F2F);
    case 'egg':       return const Color(0xFFFF8F00);
    case 'dairy':     return const Color(0xFF0288D1);
    case 'snack':     return const Color(0xFF6D4C41);
    case 'sweet':     return const Color(0xFFC2185B);
    case 'dessert':   return const Color(0xFFAD1457);
    case 'beverage':  return const Color(0xFF00897B);
    case 'soup':      return const Color(0xFFEF6C00);
    case 'breakfast': return const Color(0xFFF9A825);
    case 'grain':     return const Color(0xFF8D6E63);
    case 'salad':     return const Color(0xFF2E7D32);
    case 'noodle':    return const Color(0xFFF57F17);
    default:          return const Color(0xFF546E7A);
  }
}

String _catLabel(String cat, String lang) {
  if (lang == 'bn') {
    const bn = <String, String>{
      'rice':      'ভাত',
      'bread':     'রুটি',
      'legume':    'ডাল',
      'vegetable': 'সবজি',
      'fruit':     'ফল',
      'fish':      'মাছ',
      'meat':      'মাংস',
      'egg':       'ডিম',
      'dairy':     'দুগ্ধ',
      'snack':     'স্ন্যাকস',
      'sweet':     'মিষ্টি',
      'dessert':   'ডেজার্ট',
      'beverage':  'পানীয়',
      'soup':      'স্যুপ',
      'breakfast': 'সকালের খাবার',
      'grain':     'শস্য',
      'salad':     'সালাদ',
      'noodle':    'নুডুলস',
    };
    return bn[cat] ?? cat;
  }
  return cat[0].toUpperCase() + cat.substring(1);
}

// ── Root screen with TabBar ───────────────────────────────────────────────────

class FoodSearchScreen extends ConsumerStatefulWidget {
  const FoodSearchScreen({super.key});

  @override
  ConsumerState<FoodSearchScreen> createState() => _FoodSearchScreenState();
}

class _FoodSearchScreenState extends ConsumerState<FoodSearchScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(foodSearchProvider);
    final lang = ref.watch(appStringsProvider).language;
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final topPad = MediaQuery.of(context).padding.top;
    final surfaceColor =
        isDark ? AppColors.darkBackground : AppColors.lightSurface;

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      body: Column(
        children: [
          // ── App bar ─────────────────────────────────────────────────────
          Container(
            color: surfaceColor,
            padding: EdgeInsets.fromLTRB(16, topPad + 12, 16, 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        lang == 'bn' ? 'খাবার খুঁজুন' : 'Food Search',
                        style: theme.textTheme.titleLarge
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 9, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.offline_bolt_rounded,
                              size: 11, color: AppColors.primary),
                          const SizedBox(width: 4),
                          Text(
                            '${LocalFoodRepository.itemCount} foods',
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppColors.primary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),

                // ── TabBar ──────────────────────────────────────────────
                TabBar(
                  controller: _tabController,
                  labelStyle: const TextStyle(
                      fontSize: 12, fontWeight: FontWeight.w700),
                  unselectedLabelStyle: const TextStyle(
                      fontSize: 12, fontWeight: FontWeight.w500),
                  indicatorSize: TabBarIndicatorSize.tab,
                  dividerColor: Colors.transparent,
                  tabs: [
                    Tab(
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.inventory_2_outlined, size: 16),
                          const SizedBox(width: 5),
                          Text(lang == 'bn' ? 'দেশি খাবার' : 'Local'),
                        ],
                      ),
                    ),
                    Tab(
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.travel_explore_rounded, size: 16),
                          const SizedBox(width: 5),
                          Text(lang == 'bn' ? 'আন্তর্জাতিক' : 'International'),
                        ],
                      ),
                    ),
                    Tab(
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.edit_note_rounded, size: 16),
                          const SizedBox(width: 5),
                          Text(lang == 'bn' ? 'কাস্টম' : 'My Foods'),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // ── Tab views ───────────────────────────────────────────────────
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _LocalTab(state: state, lang: lang, isDark: isDark),
                _UsdaTab(state: state, lang: lang, isDark: isDark),
                _CustomTab(state: state, lang: lang, isDark: isDark),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 1 — Indian & Bengali Food (local offline database)
// ═══════════════════════════════════════════════════════════════════════════════

class _LocalTab extends ConsumerStatefulWidget {
  final FoodSearchState state;
  final String lang;
  final bool isDark;

  const _LocalTab(
      {required this.state, required this.lang, required this.isDark});

  @override
  ConsumerState<_LocalTab> createState() => _LocalTabState();
}

class _LocalTabState extends ConsumerState<_LocalTab>
    with AutomaticKeepAliveClientMixin {
  final _ctrl = TextEditingController();
  final _focus = FocusNode();
  List<FoodItem> _suggestions = [];
  bool _showSuggestions = false;
  // Prevents the focus-loss listener from hiding suggestions before a tap lands.
  bool _pointerDownOnSuggestions = false;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _focus.addListener(_onFocusChange);
  }

  void _onFocusChange() {
    if (!_focus.hasFocus && !_pointerDownOnSuggestions) {
      if (mounted) setState(() => _showSuggestions = false);
    }
  }

  @override
  void dispose() {
    _focus.removeListener(_onFocusChange);
    _ctrl.dispose();
    _focus.dispose();
    super.dispose();
  }

  void _onTextChanged(String value) {
    final q = value.trim();
    if (q.length >= 1) {
      final results = LocalFoodRepository.search(q, limit: 7);
      setState(() {
        _suggestions = results;
        _showSuggestions = results.isNotEmpty;
      });
    } else {
      setState(() {
        _suggestions = [];
        _showSuggestions = false;
      });
    }
  }

  void _pickSuggestion(FoodItem food) {
    _pointerDownOnSuggestions = false;
    _ctrl.text = food.name;
    setState(() {
      _suggestions = [];
      _showSuggestions = false;
    });
    FocusScope.of(context).unfocus();
    ref.read(foodSearchProvider.notifier).searchLocal(food.name);
  }

  void _doSearch() {
    setState(() => _showSuggestions = false);
    FocusScope.of(context).unfocus();
    ref.read(foodSearchProvider.notifier).searchLocal(_ctrl.text);
  }

  void _clear() {
    _ctrl.clear();
    setState(() {
      _suggestions = [];
      _showSuggestions = false;
    });
    ref.read(foodSearchProvider.notifier).clearLocalSearch();
    _focus.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final state = widget.state;
    final lang = widget.lang;
    final isDark = widget.isDark;
    final theme = Theme.of(context);
    final fieldFill = isDark ? AppColors.darkCard : AppColors.lightBackground;

    final dbError = LocalFoodRepository.initError;

    return Stack(
      fit: StackFit.expand,
      children: [
        // ── Main layout ──────────────────────────────────────────────────
        Column(
          children: [
            // ── Food-DB error banner ───────────────────────────────────
            if (dbError != null && !LocalFoodRepository.isReady)
              Container(
                width: double.infinity,
                color: Colors.red.shade700,
                padding: const EdgeInsets.symmetric(
                    horizontal: 16, vertical: 8),
                child: Row(
                  children: [
                    const Icon(Icons.warning_amber_rounded,
                        color: Colors.white, size: 16),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        lang == 'bn'
                            ? 'খাবার ডেটাবেস লোড হয়নি। অ্যাপটি পুনরায় চালু করুন।'
                            : 'Food database failed to load. Please restart the app.',
                        style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.w600),
                      ),
                    ),
                  ],
                ),
              ),

            // ── Search bar area ────────────────────────────────────────
            Container(
              color: isDark
                  ? AppColors.darkBackground
                  : AppColors.lightSurface,
              padding: const EdgeInsets.fromLTRB(16, 10, 16, 0),
              child: Column(
                children: [
                  // Text field
                  Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _ctrl,
                          focusNode: _focus,
                          autocorrect: false,
                          enableSuggestions: false,
                          textInputAction: TextInputAction.search,
                          onChanged: _onTextChanged,
                          onSubmitted: (_) => _doSearch(),
                          style: theme.textTheme.bodyLarge,
                          decoration: InputDecoration(
                            hintText: lang == 'bn'
                                ? 'ভাত, ডাল, মুরগি, rice…'
                                : 'rice, dal, chicken, paneer…',
                            hintStyle: TextStyle(
                                color: theme.hintColor, fontSize: 14),
                            prefixIcon: const Icon(Icons.search_rounded,
                                color: AppColors.primary, size: 20),
                            suffixIcon: _ctrl.text.isNotEmpty
                                ? GestureDetector(
                                    onTap: _clear,
                                    child: const Icon(Icons.cancel_rounded,
                                        size: 18, color: Colors.grey),
                                  )
                                : null,
                            filled: true,
                            fillColor: fieldFill,
                            contentPadding: const EdgeInsets.symmetric(
                                vertical: 12, horizontal: 14),
                            border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide.none),
                            enabledBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: BorderSide.none),
                            focusedBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(12),
                                borderSide: const BorderSide(
                                    color: AppColors.primary, width: 2)),
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      FilledButton(
                        onPressed: _doSearch,
                        style: FilledButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 13),
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12)),
                        ),
                        child: Text(
                          lang == 'bn' ? 'খুঁজুন' : 'Search',
                          style: const TextStyle(
                              fontWeight: FontWeight.w700, fontSize: 14),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 8),

                  // Category chips
                  SizedBox(
                    height: 32,
                    child: ListView.separated(
                      scrollDirection: Axis.horizontal,
                      padding: EdgeInsets.zero,
                      itemCount: _localCategories.length,
                      separatorBuilder: (_, __) => const SizedBox(width: 6),
                      itemBuilder: (context, i) {
                        final cat = _localCategories[i];
                        final sel = state.localCategory == cat;
                        final color = _catColor(cat);
                        return GestureDetector(
                          onTap: () => ref
                              .read(foodSearchProvider.notifier)
                              .setLocalCategory(cat),
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 180),
                            padding: const EdgeInsets.symmetric(horizontal: 10),
                            decoration: BoxDecoration(
                              color: sel
                                  ? color
                                  : color.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                  color: sel
                                      ? color
                                      : color.withValues(alpha: 0.4),
                                  width: 1.2),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                    _catIcons[cat] ??
                                        Icons.fastfood_outlined,
                                    size: 12,
                                    color: sel ? Colors.white : color),
                                const SizedBox(width: 4),
                                Text(
                                  _catLabel(cat, lang),
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                    color: sel ? Colors.white : color,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                  const SizedBox(height: 10),
                ],
              ),
            ),

            // ── Results ──────────────────────────────────────────────────
            Expanded(
              child: state.localHasSearched
                  ? _LocalResults(state: state, lang: lang)
                  : _LocalIdle(lang: lang, recentFoods: state.recentFoods),
            ),
          ],
        ),

        // ── Autocomplete overlay (floats above chips and results) ────────
        if (_showSuggestions && _suggestions.isNotEmpty)
          Positioned(
            // 10 (container top pad) + ~52 (TextField height) + 6 (gap)
            top: 68,
            left: 16,
            right: 16,
            child: Listener(
              // Mark pointer-down BEFORE focus-loss fires so the focus
              // listener doesn't hide the list before the tap lands.
              onPointerDown: (_) => _pointerDownOnSuggestions = true,
              onPointerUp: (_) => _pointerDownOnSuggestions = false,
              onPointerCancel: (_) => _pointerDownOnSuggestions = false,
              child: Material(
                elevation: 8,
                shadowColor: Colors.black26,
                borderRadius: BorderRadius.circular(12),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: _suggestions.asMap().entries.map((entry) {
                      final i = entry.key;
                      final food = entry.value;
                      final displayName =
                          lang == 'bn' && food.nameBn != null
                              ? food.nameBn!
                              : food.name;
                      final secondary =
                          lang == 'bn' ? food.name : food.nameBn;
                      return Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (i > 0)
                            const Divider(height: 1, indent: 44),
                          InkWell(
                            onTap: () => _pickSuggestion(food),
                            child: Padding(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 10),
                              child: Row(
                                children: [
                                  Icon(
                                    _catIcons[food.category] ??
                                        Icons.fastfood_outlined,
                                    size: 16,
                                    color: _catColor(food.category),
                                  ),
                                  const SizedBox(width: 10),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          displayName,
                                          style: Theme.of(context)
                                              .textTheme
                                              .bodyMedium
                                              ?.copyWith(
                                                  fontWeight: FontWeight.w600,
                                                  fontSize: 13),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                        if (secondary != null &&
                                            secondary.isNotEmpty)
                                          Text(
                                            secondary,
                                            style: Theme.of(context)
                                                .textTheme
                                                .bodySmall
                                                ?.copyWith(fontSize: 11),
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                      ],
                                    ),
                                  ),
                                  Text(
                                    '${food.calories.toStringAsFixed(0)} kcal',
                                    style: const TextStyle(
                                      fontSize: 11,
                                      color: AppColors.calories,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      );
                    }).toList(),
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}

class _LocalResults extends StatelessWidget {
  final FoodSearchState state;
  final String lang;

  const _LocalResults({required this.state, required this.lang});

  @override
  Widget build(BuildContext context) {
    if (state.localHasResults) {
      return ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 10, 16, 100),
        itemCount: state.localResults.length,
        itemBuilder: (_, i) =>
            _FoodCard(food: state.localResults[i], lang: lang),
      );
    }

    // No results
    return _CenteredMessage(
      icon: Icons.search_off_rounded,
      iconColor: Colors.grey,
      title: lang == 'bn' ? 'কোনো খাবার পাওয়া যায়নি' : 'No Results Found',
      subtitle: state.localCategory != null
          ? (lang == 'bn'
              ? '${_catLabel(state.localCategory!, lang)} বিভাগে "${state.localQuery}" পাওয়া যায়নি'
              : '"${state.localQuery}" not in ${state.localCategory} category')
          : (lang == 'bn'
              ? '"${state.localQuery}" স্থানীয় ডেটায় পাওয়া যায়নি'
              : '"${state.localQuery}" not in local database'),
      hint: lang == 'bn'
          ? 'ইংরেজি বা বাংলায় চেষ্টা করুন, অথবা আন্তর্জাতিক ট্যাবে খুঁজুন'
          : 'Try English or Bengali, or search the International tab',
    );
  }
}

class _LocalIdle extends StatelessWidget {
  final String lang;
  final List<FoodItem> recentFoods;

  const _LocalIdle({required this.lang, required this.recentFoods});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final count = LocalFoodRepository.itemCount;
    final isReady = LocalFoodRepository.isReady;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 100),
      children: [
        // Hero
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            gradient: AppColors.primaryGradient,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      lang == 'bn'
                          ? 'ভারতীয় ও বাংলাদেশি খাবার'
                          : 'Indian & Bengali Foods',
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      isReady
                          ? (lang == 'bn'
                              ? '$count টি খাবার — সম্পূর্ণ অফলাইনে কাজ করে'
                              : '$count foods — works 100% offline')
                          : (lang == 'bn'
                              ? 'ডেটা লোড হচ্ছে…'
                              : 'Loading food data…'),
                      style: const TextStyle(
                          color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.offline_bolt_rounded,
                  color: Colors.white30, size: 44),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // Tips
        _InfoCard(
          icon: Icons.tips_and_updates_outlined,
          color: AppColors.primary,
          title: lang == 'bn' ? 'কিভাবে ব্যবহার করবেন' : 'How to Search',
          items: lang == 'bn'
              ? [
                  'বাংলা বা ইংরেজিতে খাবারের নাম লিখুন',
                  '"খুঁজুন" বাটন চাপুন বা কীবোর্ডের Search চাপুন',
                  'অথবা উপরের ক্যাটাগরি চিপ ট্যাপ করুন',
                ]
              : [
                  'Type food name in English or Bengali',
                  'Tap "Search" button or press keyboard Search',
                  'Or tap a category chip above to browse',
                ],
        ),
        const SizedBox(height: 20),

        if (recentFoods.isNotEmpty) ...[
          Text(
            lang == 'bn' ? 'সম্প্রতি দেখা' : 'Recently Viewed',
            style: theme.textTheme.titleSmall
                ?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 8),
          ...recentFoods.map((f) => _FoodCard(food: f, lang: lang)),
        ],
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 2 — International Food (USDA API)
// ═══════════════════════════════════════════════════════════════════════════════

class _UsdaTab extends ConsumerStatefulWidget {
  final FoodSearchState state;
  final String lang;
  final bool isDark;

  const _UsdaTab(
      {required this.state, required this.lang, required this.isDark});

  @override
  ConsumerState<_UsdaTab> createState() => _UsdaTabState();
}

class _UsdaTabState extends ConsumerState<_UsdaTab>
    with AutomaticKeepAliveClientMixin {
  final _ctrl = TextEditingController();
  final _focus = FocusNode();

  @override
  bool get wantKeepAlive => true;

  @override
  void dispose() {
    _ctrl.dispose();
    _focus.dispose();
    super.dispose();
  }

  void _doSearch() {
    FocusScope.of(context).unfocus();
    ref.read(foodSearchProvider.notifier).searchUsda(_ctrl.text);
  }

  void _clear() {
    _ctrl.clear();
    setState(() {});
    _focus.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final state = widget.state;
    final lang = widget.lang;
    final isDark = widget.isDark;
    final theme = Theme.of(context);
    final fieldFill = isDark ? AppColors.darkCard : AppColors.lightBackground;

    return Column(
      children: [
        // ── Search bar ────────────────────────────────────────────────────
        Container(
          color: isDark
              ? AppColors.darkBackground
              : AppColors.lightSurface,
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 10),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _ctrl,
                  focusNode: _focus,
                  autocorrect: false,
                  enableSuggestions: false,
                  textInputAction: TextInputAction.search,
                  onChanged: (_) => setState(() {}),
                  onSubmitted: (_) => _doSearch(),
                  style: theme.textTheme.bodyLarge,
                  decoration: InputDecoration(
                    hintText: lang == 'bn'
                        ? 'যেমন: Coca-Cola, Oreo, Pizza…'
                        : 'e.g. Coca-Cola, Oreo, Pizza…',
                    hintStyle:
                        TextStyle(color: theme.hintColor, fontSize: 14),
                    prefixIcon: const Icon(Icons.travel_explore_rounded,
                        color: AppColors.secondary, size: 20),
                    suffixIcon: _ctrl.text.isNotEmpty
                        ? GestureDetector(
                            onTap: _clear,
                            child: const Icon(Icons.cancel_rounded,
                                size: 18, color: Colors.grey),
                          )
                        : null,
                    filled: true,
                    fillColor: fieldFill,
                    contentPadding: const EdgeInsets.symmetric(
                        vertical: 12, horizontal: 14),
                    border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none),
                    enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none),
                    focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: const BorderSide(
                            color: AppColors.secondary, width: 2)),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              FilledButton(
                onPressed: _ctrl.text.trim().isNotEmpty ? _doSearch : null,
                style: FilledButton.styleFrom(
                  backgroundColor: AppColors.secondary,
                  disabledBackgroundColor:
                      AppColors.secondary.withValues(alpha: 0.4),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 13),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12)),
                ),
                child: Text(
                  lang == 'bn' ? 'খুঁজুন' : 'Search',
                  style: const TextStyle(
                      fontWeight: FontWeight.w700, fontSize: 14),
                ),
              ),
            ],
          ),
        ),

        // ── Results ───────────────────────────────────────────────────────
        Expanded(child: _UsdaResults(state: state, lang: lang, onRetry: _doSearch)),
      ],
    );
  }
}

class _UsdaResults extends StatelessWidget {
  final FoodSearchState state;
  final String lang;
  final VoidCallback onRetry;

  const _UsdaResults(
      {required this.state, required this.lang, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    switch (state.usdaStatus) {
      case UsdaSearchStatus.idle:
        return _UsdaIdle(lang: lang);

      case UsdaSearchStatus.loading:
        return Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircularProgressIndicator(color: AppColors.secondary),
              const SizedBox(height: 16),
              Text(
                lang == 'bn'
                    ? 'USDA ডেটাবেজে খুঁজছে…'
                    : 'Searching USDA database…',
                style: const TextStyle(
                    color: AppColors.secondary, fontWeight: FontWeight.w500),
              ),
            ],
          ),
        );

      case UsdaSearchStatus.success:
        if (state.usdaHasResults) {
          return ListView.builder(
            padding: const EdgeInsets.fromLTRB(16, 10, 16, 100),
            itemCount: state.usdaResults.length,
            itemBuilder: (_, i) =>
                _FoodCard(food: state.usdaResults[i], lang: lang),
          );
        }
        return _CenteredMessage(
          icon: Icons.search_off_rounded,
          iconColor: Colors.grey,
          title: lang == 'bn' ? 'কোনো ফলাফল নেই' : 'No Results',
          subtitle: lang == 'bn'
              ? '"${state.usdaQuery}" USDA ডেটাবেজে পাওয়া যায়নি'
              : '"${state.usdaQuery}" not found in USDA database',
          hint: lang == 'bn'
              ? 'ভিন্ন শব্দ দিয়ে চেষ্টা করুন'
              : 'Try different keywords',
        );

      case UsdaSearchStatus.offline:
        return _CenteredMessage(
          icon: Icons.wifi_off_rounded,
          iconColor: Colors.orange,
          title: lang == 'bn' ? 'ইন্টারনেট নেই' : 'No Internet Connection',
          subtitle: lang == 'bn'
              ? 'USDA সার্চের জন্য ইন্টারনেট প্রয়োজন'
              : 'Internet is required for USDA search',
          actionLabel: lang == 'bn' ? 'আবার চেষ্টা' : 'Retry',
          onAction: onRetry,
        );

      case UsdaSearchStatus.rateLimited:
        return _CenteredMessage(
          icon: Icons.hourglass_top_rounded,
          iconColor: Colors.amber,
          title: lang == 'bn' ? 'সাময়িকভাবে সীমাবদ্ধ' : 'Rate Limited',
          subtitle: lang == 'bn'
              ? 'কিছুক্ষণ পরে আবার চেষ্টা করুন'
              : 'Please try again in a few minutes',
          actionLabel: lang == 'bn' ? 'আবার চেষ্টা' : 'Retry',
          onAction: onRetry,
        );

      case UsdaSearchStatus.error:
        return _CenteredMessage(
          icon: Icons.error_outline_rounded,
          iconColor: Colors.redAccent,
          title: lang == 'bn' ? 'সংযোগ ব্যর্থ' : 'Search Failed',
          subtitle: state.usdaError ?? (lang == 'bn' ? 'একটি সমস্যা হয়েছে' : 'Something went wrong'),
          actionLabel: lang == 'bn' ? 'আবার চেষ্টা' : 'Retry',
          onAction: onRetry,
        );
    }
  }
}

class _UsdaIdle extends StatelessWidget {
  final String lang;
  const _UsdaIdle({required this.lang});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 100),
      children: [
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppColors.secondary.withValues(alpha: 0.85),
                AppColors.secondary,
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      lang == 'bn'
                          ? 'আন্তর্জাতিক ডেটাবেজ'
                          : 'International Database',
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      lang == 'bn'
                          ? 'USDA থেকে লক্ষাধিক খাবার — ইন্টারনেট প্রয়োজন'
                          : 'Millions of foods from USDA — requires internet',
                      style: const TextStyle(
                          color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.public_rounded,
                  color: Colors.white30, size: 44),
            ],
          ),
        ),
        const SizedBox(height: 14),
        _InfoCard(
          icon: Icons.info_outline_rounded,
          color: AppColors.secondary,
          title: lang == 'bn' ? 'এই ট্যাবে কী পাবেন' : 'What You Find Here',
          items: lang == 'bn'
              ? [
                  'প্যাকেজড ও ব্র্যান্ডেড খাবার (Coca-Cola, KitKat…)',
                  'আন্তর্জাতিক রেস্তোরাঁর খাবার',
                  'USDA FoodData Central ডেটাবেজ',
                ]
              : [
                  'Packaged & branded foods (Coca-Cola, KitKat…)',
                  'International restaurant dishes',
                  'USDA FoodData Central database',
                ],
        ),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 3 — Custom Food (user-created)
// ═══════════════════════════════════════════════════════════════════════════════

class _CustomTab extends ConsumerStatefulWidget {
  final FoodSearchState state;
  final String lang;
  final bool isDark;

  const _CustomTab(
      {required this.state, required this.lang, required this.isDark});

  @override
  ConsumerState<_CustomTab> createState() => _CustomTabState();
}

class _CustomTabState extends ConsumerState<_CustomTab>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;

  void _showAddSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _AddCustomFoodSheet(
        lang: widget.lang,
        onSave: (food) =>
            ref.read(foodSearchProvider.notifier).addCustomFood(food),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final state = widget.state;
    final lang = widget.lang;
    final isDark = widget.isDark;
    final theme = Theme.of(context);

    return Column(
      children: [
        // ── Top bar with Add button ───────────────────────────────────────
        Container(
          color: isDark
              ? AppColors.darkBackground
              : AppColors.lightSurface,
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 10),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      lang == 'bn' ? 'আমার কাস্টম খাবার' : 'My Custom Foods',
                      style: theme.textTheme.titleSmall
                          ?.copyWith(fontWeight: FontWeight.w700),
                    ),
                    Text(
                      state.hasCustomFoods
                          ? (lang == 'bn'
                              ? '${state.customFoods.length} টি কাস্টম খাবার সংরক্ষিত'
                              : '${state.customFoods.length} custom food(s) saved')
                          : (lang == 'bn'
                              ? 'কোনো কাস্টম খাবার নেই'
                              : 'No custom foods yet'),
                      style: theme.textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              FilledButton.icon(
                onPressed: _showAddSheet,
                icon: const Icon(Icons.add_rounded, size: 18),
                label: Text(
                  lang == 'bn' ? 'তৈরি করুন' : 'Create',
                  style: const TextStyle(
                      fontWeight: FontWeight.w700, fontSize: 13),
                ),
                style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFF7B61FF),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 10),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10)),
                ),
              ),
            ],
          ),
        ),

        // ── Custom food list ──────────────────────────────────────────────
        Expanded(
          child: state.hasCustomFoods
              ? ListView.builder(
                  padding: const EdgeInsets.fromLTRB(16, 10, 16, 100),
                  itemCount: state.customFoods.length,
                  itemBuilder: (_, i) => _CustomFoodCard(
                    food: state.customFoods[i],
                    lang: lang,
                    isDark: isDark,
                    onDelete: () => ref
                        .read(foodSearchProvider.notifier)
                        .deleteCustomFood(state.customFoods[i].id),
                  ),
                )
              : _CustomIdle(lang: lang, onAdd: _showAddSheet),
        ),
      ],
    );
  }
}

class _CustomIdle extends StatelessWidget {
  final String lang;
  final VoidCallback onAdd;

  const _CustomIdle({required this.lang, required this.onAdd});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 100),
      children: [
        Container(
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF7B61FF), Color(0xFF9C7BFF)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      lang == 'bn'
                          ? 'কাস্টম খাবার তৈরি করুন'
                          : 'Create Custom Foods',
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      lang == 'bn'
                          ? 'নিজের পুষ্টিমান দিয়ে যেকোনো খাবার যোগ করুন'
                          : 'Add any food with your own nutrition values',
                      style: const TextStyle(
                          color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.edit_note_rounded,
                  color: Colors.white30, size: 44),
            ],
          ),
        ),
        const SizedBox(height: 14),
        _InfoCard(
          icon: Icons.edit_note_rounded,
          color: const Color(0xFF7B61FF),
          title: lang == 'bn' ? 'কাস্টম খাবার কেন?' : 'Why Custom Food?',
          items: lang == 'bn'
              ? [
                  'ডেটাবেজে নেই এমন ঘরে তৈরি খাবার যোগ করুন',
                  'নিজের রেসিপির পুষ্টিমান হিসাব করুন',
                  'তৈরি করা খাবার মিল লগে যোগ করা যাবে',
                ]
              : [
                  'Add homemade dishes not in any database',
                  'Track nutrition of your own recipes',
                  'Custom foods can be logged in your meals',
                ],
        ),
        const SizedBox(height: 20),
        SizedBox(
          width: double.infinity,
          child: FilledButton.icon(
            onPressed: onAdd,
            icon: const Icon(Icons.add_rounded, size: 20),
            label: Text(
              lang == 'bn' ? 'প্রথম কাস্টম খাবার তৈরি করুন' : 'Create Your First Custom Food',
              style: const TextStyle(
                  fontWeight: FontWeight.w700, fontSize: 14),
            ),
            style: FilledButton.styleFrom(
              backgroundColor: const Color(0xFF7B61FF),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ),
      ],
    );
  }
}

class _CustomFoodCard extends StatelessWidget {
  final FoodItem food;
  final String lang;
  final bool isDark;
  final VoidCallback onDelete;

  const _CustomFoodCard({
    required this.food,
    required this.lang,
    required this.isDark,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return GestureDetector(
      onTap: () => context.push('/food-search/detail', extra: {'food': food, 'mealType': mealTypeForNow()}),
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 11),
        decoration: BoxDecoration(
          color: isDark ? AppColors.darkCard : Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: isDark ? AppColors.darkDivider : const Color(0xFFEEEEEE),
          ),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Container(
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                color: const Color(0xFF7B61FF).withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.edit_note_rounded,
                  color: Color(0xFF7B61FF), size: 22),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    food.name,
                    style: theme.textTheme.titleSmall
                        ?.copyWith(fontWeight: FontWeight.w700, fontSize: 14),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      _MacroPill('P ${food.proteinG.toStringAsFixed(0)}g',
                          AppColors.protein),
                      const SizedBox(width: 4),
                      _MacroPill('C ${food.carbsG.toStringAsFixed(0)}g',
                          AppColors.carbs),
                      const SizedBox(width: 4),
                      _MacroPill(
                          'F ${food.fatG.toStringAsFixed(0)}g', AppColors.fat),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 8, vertical: 5),
                  decoration: BoxDecoration(
                    color: AppColors.calories.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    food.calories.toStringAsFixed(0),
                    style: const TextStyle(
                      color: AppColors.calories,
                      fontWeight: FontWeight.w800,
                      fontSize: 15,
                    ),
                  ),
                ),
                const SizedBox(height: 2),
                Text('kcal',
                    style: theme.textTheme.labelSmall
                        ?.copyWith(fontSize: 10)),
              ],
            ),
            const SizedBox(width: 4),
            GestureDetector(
              onTap: () async {
                final ok = await showDialog<bool>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: Text(
                        lang == 'bn' ? 'মুছে ফেলবেন?' : 'Delete?'),
                    content: Text('"${food.name}"'),
                    actions: [
                      TextButton(
                          onPressed: () => Navigator.pop(ctx, false),
                          child: Text(lang == 'bn' ? 'বাতিল' : 'Cancel')),
                      FilledButton(
                          onPressed: () => Navigator.pop(ctx, true),
                          style: FilledButton.styleFrom(
                              backgroundColor: Colors.red),
                          child: Text(lang == 'bn' ? 'মুছুন' : 'Delete')),
                    ],
                  ),
                );
                if (ok == true) onDelete();
              },
              child: Padding(
                padding: const EdgeInsets.all(6),
                child: Icon(Icons.delete_outline_rounded,
                    size: 20,
                    color: Colors.red.withValues(alpha: 0.7)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Add Custom Food bottom sheet ──────────────────────────────────────────────

class _AddCustomFoodSheet extends StatefulWidget {
  final String lang;
  final void Function(FoodItem food) onSave;

  const _AddCustomFoodSheet({required this.lang, required this.onSave});

  @override
  State<_AddCustomFoodSheet> createState() => _AddCustomFoodSheetState();
}

class _AddCustomFoodSheetState extends State<_AddCustomFoodSheet> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _servingCtrl = TextEditingController(text: '100');
  final _calCtrl = TextEditingController();
  final _proteinCtrl = TextEditingController(text: '0');
  final _carbCtrl = TextEditingController(text: '0');
  final _fatCtrl = TextEditingController(text: '0');
  String _unit = 'g';

  @override
  void dispose() {
    _nameCtrl.dispose();
    _servingCtrl.dispose();
    _calCtrl.dispose();
    _proteinCtrl.dispose();
    _carbCtrl.dispose();
    _fatCtrl.dispose();
    super.dispose();
  }

  void _save() {
    if (!_formKey.currentState!.validate()) return;
    final food = FoodItem(
      id: 'custom_${DateTime.now().millisecondsSinceEpoch}',
      name: _nameCtrl.text.trim(),
      servingSize: double.tryParse(_servingCtrl.text) ?? 100,
      servingUnit: _unit,
      calories: double.tryParse(_calCtrl.text) ?? 0,
      proteinG: double.tryParse(_proteinCtrl.text) ?? 0,
      carbsG: double.tryParse(_carbCtrl.text) ?? 0,
      fatG: double.tryParse(_fatCtrl.text) ?? 0,
      fiberG: 0,
      isCustom: true,
      source: 'custom',
    );
    widget.onSave(food);
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final bn = widget.lang == 'bn';
    final bottom = MediaQuery.of(context).viewInsets.bottom;

    return Container(
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      padding: EdgeInsets.fromLTRB(20, 0, 20, bottom + 20),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                margin: const EdgeInsets.symmetric(vertical: 12),
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: theme.dividerColor,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            Text(
              bn ? 'কাস্টম খাবার তৈরি করুন' : 'Create Custom Food',
              style: theme.textTheme.titleMedium
                  ?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 4),
            Text(
              bn
                  ? 'নিজের পুষ্টিমান দিয়ে খাবার যোগ করুন'
                  : 'Add food with your own nutritional values',
              style: theme.textTheme.bodySmall,
            ),
            const SizedBox(height: 16),
            Form(
              key: _formKey,
              child: Column(
                children: [
                  _SheetField(
                    controller: _nameCtrl,
                    label: bn ? 'খাবারের নাম *' : 'Food Name *',
                    hint: bn ? 'মায়ের হাতের ডাল' : "Mom's Dal",
                    validator: (v) => (v == null || v.trim().isEmpty)
                        ? (bn ? 'নাম দিন' : 'Required')
                        : null,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        flex: 3,
                        child: _SheetField(
                          controller: _servingCtrl,
                          label: bn ? 'পরিমাণ *' : 'Serving Size *',
                          hint: '100',
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          inputFormatters: [
                            FilteringTextInputFormatter.allow(
                                RegExp(r'^\d*\.?\d*'))
                          ],
                          validator: (v) =>
                              (double.tryParse(v ?? '') ?? 0) <= 0
                                  ? (bn ? 'পরিমাণ দিন' : 'Enter amount')
                                  : null,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        flex: 2,
                        child: DropdownButtonFormField<String>(
                          value: _unit,
                          decoration: InputDecoration(
                            labelText: bn ? 'একক' : 'Unit',
                            contentPadding: const EdgeInsets.symmetric(
                                horizontal: 12, vertical: 14),
                            border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10)),
                          ),
                          items: ['g', 'ml', 'pcs', 'oz', 'cup'].map((u) {
                            return DropdownMenuItem(value: u, child: Text(u));
                          }).toList(),
                          onChanged: (v) =>
                              setState(() => _unit = v ?? 'g'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  _SheetField(
                    controller: _calCtrl,
                    label: bn ? 'ক্যালোরি (kcal) *' : 'Calories (kcal) *',
                    hint: '250',
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    inputFormatters: [
                      FilteringTextInputFormatter.allow(
                          RegExp(r'^\d*\.?\d*'))
                    ],
                    validator: (v) =>
                        (double.tryParse(v ?? '') == null)
                            ? (bn ? 'ক্যালোরি দিন' : 'Required')
                            : null,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _SheetField(
                          controller: _proteinCtrl,
                          label: bn ? 'প্রোটিন (g)' : 'Protein (g)',
                          hint: '0',
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          inputFormatters: [
                            FilteringTextInputFormatter.allow(
                                RegExp(r'^\d*\.?\d*'))
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _SheetField(
                          controller: _carbCtrl,
                          label: bn ? 'কার্বস (g)' : 'Carbs (g)',
                          hint: '0',
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          inputFormatters: [
                            FilteringTextInputFormatter.allow(
                                RegExp(r'^\d*\.?\d*'))
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _SheetField(
                          controller: _fatCtrl,
                          label: bn ? 'ফ্যাট (g)' : 'Fat (g)',
                          hint: '0',
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          inputFormatters: [
                            FilteringTextInputFormatter.allow(
                                RegExp(r'^\d*\.?\d*'))
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      onPressed: _save,
                      style: FilledButton.styleFrom(
                        backgroundColor: const Color(0xFF7B61FF),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                      child: Text(
                        bn ? 'সংরক্ষণ করুন' : 'Save Custom Food',
                        style: const TextStyle(
                            fontWeight: FontWeight.w700, fontSize: 15),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SheetField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String hint;
  final TextInputType? keyboardType;
  final List<TextInputFormatter>? inputFormatters;
  final FormFieldValidator<String>? validator;

  const _SheetField({
    required this.controller,
    required this.label,
    required this.hint,
    this.keyboardType,
    this.inputFormatters,
    this.validator,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      inputFormatters: inputFormatters,
      validator: validator,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
        border:
            OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}

// ── Shared food card (local + USDA results) ───────────────────────────────────

class _FoodCard extends StatelessWidget {
  final FoodItem food;
  final String lang;

  const _FoodCard({required this.food, required this.lang});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final color = _catColor(food.category);
    final primary = food.displayName(lang);
    final alt = lang == 'bn' ? food.name : food.nameBn;

    return GestureDetector(
      onTap: () => context.push('/food-search/detail', extra: {'food': food, 'mealType': mealTypeForNow()}),
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 11),
        decoration: BoxDecoration(
          color: isDark ? AppColors.darkCard : Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(
            color: isDark ? AppColors.darkDivider : const Color(0xFFEEEEEE),
          ),
          boxShadow: isDark
              ? null
              : [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.04),
                    blurRadius: 6,
                    offset: const Offset(0, 2),
                  ),
                ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                _catIcons[food.category] ?? Icons.fastfood_outlined,
                color: color,
                size: 22,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    primary,
                    style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700, fontSize: 14),
                    maxLines: 3,
                    overflow: TextOverflow.visible,
                  ),
                  if (alt != null && alt.isNotEmpty) ...[
                    const SizedBox(height: 1),
                    Text(
                      alt,
                      style: theme.textTheme.bodySmall
                          ?.copyWith(fontSize: 11, height: 1.3),
                      maxLines: 2,
                      overflow: TextOverflow.visible,
                    ),
                  ],
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      _MacroPill('P ${food.proteinG.toStringAsFixed(0)}g',
                          AppColors.protein),
                      const SizedBox(width: 4),
                      _MacroPill('C ${food.carbsG.toStringAsFixed(0)}g',
                          AppColors.carbs),
                      const SizedBox(width: 4),
                      _MacroPill(
                          'F ${food.fatG.toStringAsFixed(0)}g', AppColors.fat),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                  decoration: BoxDecoration(
                    color: AppColors.calories.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    food.calories.toStringAsFixed(0),
                    style: const TextStyle(
                      color: AppColors.calories,
                      fontWeight: FontWeight.w800,
                      fontSize: 16,
                    ),
                  ),
                ),
                const SizedBox(height: 2),
                Text('kcal',
                    style: theme.textTheme.labelSmall
                        ?.copyWith(fontSize: 10, fontWeight: FontWeight.w500)),
                if (food.servingSize > 0)
                  Text(
                    'per ${food.servingSize.toStringAsFixed(0)}${food.servingUnit}',
                    style:
                        theme.textTheme.labelSmall?.copyWith(fontSize: 9),
                  ),
              ],
            ),
            const SizedBox(width: 2),
            Icon(Icons.chevron_right_rounded,
                size: 18, color: theme.hintColor),
          ],
        ),
      ),
    );
  }
}

class _MacroPill extends StatelessWidget {
  final String label;
  final Color color;
  const _MacroPill(this.label, this.color);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(label,
          style: TextStyle(
              fontSize: 10, color: color, fontWeight: FontWeight.w600)),
    );
  }
}

// ── Shared utility widgets ────────────────────────────────────────────────────

class _CenteredMessage extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;
  final String? hint;
  final String? actionLabel;
  final VoidCallback? onAction;

  const _CenteredMessage({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.subtitle,
    this.hint,
    this.actionLabel,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: iconColor.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, size: 36, color: iconColor),
            ),
            const SizedBox(height: 16),
            Text(title,
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.w700),
                textAlign: TextAlign.center),
            const SizedBox(height: 6),
            Text(subtitle,
                style: theme.textTheme.bodySmall
                    ?.copyWith(fontSize: 13),
                textAlign: TextAlign.center),
            if (hint != null) ...[
              const SizedBox(height: 4),
              Text(hint!,
                  style: theme.textTheme.bodySmall?.copyWith(
                      fontSize: 12,
                      color: theme.hintColor),
                  textAlign: TextAlign.center),
            ],
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: onAction,
                icon: const Icon(Icons.refresh_rounded, size: 16),
                label: Text(actionLabel!),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final List<String> items;

  const _InfoCard({
    required this.icon,
    required this.color,
    required this.title,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withValues(alpha: 0.12)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 15, color: color),
              const SizedBox(width: 7),
              Text(title,
                  style: theme.textTheme.titleSmall?.copyWith(
                      color: color, fontWeight: FontWeight.w700)),
            ],
          ),
          const SizedBox(height: 10),
          ...items.asMap().entries.map((e) => Padding(
                padding: EdgeInsets.only(
                    bottom: e.key < items.length - 1 ? 6 : 0),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 20,
                      height: 20,
                      margin: const EdgeInsets.only(top: 1, right: 8),
                      decoration: BoxDecoration(
                        color: color.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Center(
                        child: Text(
                          '${e.key + 1}',
                          style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              color: color),
                        ),
                      ),
                    ),
                    Expanded(
                        child: Text(e.value,
                            style: theme.textTheme.bodySmall)),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}
