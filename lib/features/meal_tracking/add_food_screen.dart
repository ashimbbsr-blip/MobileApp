import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../models/food_item.dart';
import '../../services/usda_api_service.dart';
import '../../services/local_food_repository.dart';
import '../../storage/hive_storage.dart';
import '../dashboard/providers/dashboard_provider.dart';
import '../meal_tracking/providers/meal_provider.dart';

// ── Category metadata (mirrors FoodSearchScreen) ─────────────────────────────

const _localCategories = [
  'rice', 'bread', 'bakery', 'vegetable', 'shaak', 'legume', 'fish', 'meat', 'egg', 'dairy',
  'fruit', 'juice', 'snack', 'sweet', 'beverage', 'soup', 'breakfast',
  'grain', 'salad', 'noodle', 'pizza', 'restaurant_food',
];

const _catIcons = <String, IconData>{
  'rice':      Icons.rice_bowl_outlined,
  'bread':     Icons.breakfast_dining_outlined,
  'bakery':    Icons.bakery_dining_outlined,
  'vegetable': Icons.eco_outlined,
  'shaak':     Icons.spa_outlined,
  'legume':    Icons.grass_outlined,
  'fruit':     Icons.apple_outlined,
  'fish':      Icons.set_meal_outlined,
  'meat':      Icons.lunch_dining_outlined,
  'egg':       Icons.egg_outlined,
  'dairy':     Icons.water_drop_outlined,
  'juice':     Icons.local_bar_outlined,
  'snack':     Icons.cookie_outlined,
  'sweet':     Icons.cake_outlined,
  'beverage':  Icons.local_drink_outlined,
  'soup':      Icons.soup_kitchen_outlined,
  'breakfast': Icons.free_breakfast_outlined,
  'grain':     Icons.grain_outlined,
  'salad':     Icons.local_florist_outlined,
  'noodle':           Icons.ramen_dining_outlined,
  'pizza':            Icons.local_pizza_outlined,
  'restaurant_food':  Icons.storefront_outlined,
  'other':            Icons.fastfood_outlined,
};

Color _catColor(String? cat) {
  switch (cat) {
    case 'rice':      return const Color(0xFFFF8C42);
    case 'bread':     return const Color(0xFFE6A020);
    case 'bakery':    return const Color(0xFFBF7A28);
    case 'legume':    return const Color(0xFFD4A017);
    case 'vegetable': return const Color(0xFF43A047);
    case 'shaak':     return const Color(0xFF1B5E20);
    case 'fruit':     return const Color(0xFFD81B60);
    case 'fish':      return const Color(0xFF1E88E5);
    case 'meat':      return const Color(0xFFD32F2F);
    case 'egg':       return const Color(0xFFFF8F00);
    case 'dairy':     return const Color(0xFF0288D1);
    case 'snack':     return const Color(0xFF6D4C41);
    case 'sweet':     return const Color(0xFFC2185B);
    case 'beverage':  return const Color(0xFF00897B);
    case 'soup':      return const Color(0xFFEF6C00);
    case 'breakfast': return const Color(0xFFF9A825);
    case 'grain':     return const Color(0xFF8D6E63);
    case 'salad':     return const Color(0xFF2E7D32);
    case 'juice':           return const Color(0xFFE65100);
    case 'noodle':          return const Color(0xFFF57F17);
    case 'pizza':           return const Color(0xFFE53935);
    case 'restaurant_food': return const Color(0xFF7B1FA2);
    default:                return const Color(0xFF546E7A);
  }
}

String _catLabel(String cat, String lang) {
  if (lang == 'bn') {
    const bn = <String, String>{
      'rice':      'ভাত',
      'bread':     'রুটি',
      'bakery':    'বেকারি',
      'legume':    'ডাল',
      'vegetable': 'সবজি',
      'shaak':     'শাক',
      'fruit':     'ফল',
      'fish':      'মাছ',
      'meat':      'মাংস',
      'egg':       'ডিম',
      'dairy':     'দুগ্ধ',
      'juice':     'জুস',
      'snack':     'স্ন্যাকস',
      'sweet':     'মিষ্টি/ডেজার্ট',
      'beverage':  'পানীয়',
      'soup':      'স্যুপ',
      'breakfast': 'সকালের খাবার',
      'grain':     'শস্য',
      'salad':     'সালাদ',
      'noodle':          'নুডুলস',
      'pizza':           'পিৎজা',
      'restaurant_food': 'রেস্তোরাঁ',
    };
    return bn[cat] ?? cat;
  }
  if (cat == 'sweet') return 'Sweet & Dessert';
  if (cat == 'shaak') return 'Leafy Greens';
  if (cat == 'restaurant_food') return 'Restaurant';
  return cat[0].toUpperCase() + cat.substring(1);
}

// ── Root screen ───────────────────────────────────────────────────────────────

class AddFoodScreen extends ConsumerStatefulWidget {
  final String mealType;
  const AddFoodScreen({super.key, required this.mealType});

  @override
  ConsumerState<AddFoodScreen> createState() => _AddFoodScreenState();
}

class _AddFoodScreenState extends ConsumerState<AddFoodScreen>
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

  Future<void> _addFood(FoodItem food, double quantity) async {
    await ref.read(mealProvider.notifier).addFood(food, widget.mealType, quantity);
    ref.read(dashboardProvider.notifier).refresh();
    if (!mounted) return;
    final lang = ref.read(appStringsProvider).language;
    final name = food.displayName(lang);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.check_circle_rounded, color: Colors.white, size: 18),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                lang == 'bn' ? '"$name" যোগ হয়েছে!' : '"$name" added!',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        backgroundColor: AppColors.primary,
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(12),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
    Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final lang = ref.watch(appStringsProvider).language;
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final surfaceColor = isDark ? AppColors.darkBackground : AppColors.lightSurface;

    return Scaffold(
      appBar: AppBar(
        title: Text(lang == 'bn' ? 'খাবার যোগ করুন' : 'Add Food'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(48),
          child: Container(
            color: surfaceColor,
            child: TabBar(
              controller: _tabController,
              labelStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
              unselectedLabelStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
              indicatorSize: TabBarIndicatorSize.tab,
              tabs: [
                Tab(
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.inventory_2_outlined, size: 15),
                      const SizedBox(width: 4),
                      Text(lang == 'bn' ? 'দেশি' : 'Local'),
                    ],
                  ),
                ),
                Tab(
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.travel_explore_rounded, size: 15),
                      const SizedBox(width: 4),
                      Text(lang == 'bn' ? 'আন্তর্জাতিক' : 'USDA'),
                    ],
                  ),
                ),
                Tab(
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.edit_note_rounded, size: 15),
                      const SizedBox(width: 4),
                      Text(lang == 'bn' ? 'কাস্টম' : 'Custom'),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _LocalTab(lang: lang, isDark: isDark, mealType: widget.mealType, onAdd: _addFood),
          _UsdaTab(lang: lang, isDark: isDark, mealType: widget.mealType, onAdd: _addFood),
          _CustomTab(lang: lang, isDark: isDark, mealType: widget.mealType, onAdd: _addFood),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 1 — Local Indian & Bengali Foods
// ═══════════════════════════════════════════════════════════════════════════════

class _LocalTab extends StatefulWidget {
  final String lang;
  final bool isDark;
  final String mealType;
  final Future<void> Function(FoodItem, double) onAdd;

  const _LocalTab({required this.lang, required this.isDark, required this.mealType, required this.onAdd});

  @override
  State<_LocalTab> createState() => _LocalTabState();
}

class _LocalTabState extends State<_LocalTab> with AutomaticKeepAliveClientMixin {
  final _ctrl = TextEditingController();
  final _focus = FocusNode();
  String? _selectedCategory;
  List<FoodItem> _results = [];
  bool _hasSearched = false;

  Future<void> _handleEditCustom(FoodItem food) async {
    final updated = await showEditCustomFoodSheet(context, food, widget.lang);
    if (updated) _refreshResults();
  }

  Future<void> _handleDeleteCustom(FoodItem food) async {
    final bn = widget.lang == 'bn';
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(bn ? 'মুছে ফেলবেন?' : 'Delete?'),
        content: Text('"${food.name}"'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: Text(bn ? 'বাতিল' : 'Cancel')),
          FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              style: FilledButton.styleFrom(backgroundColor: Colors.red),
              child: Text(bn ? 'মুছুন' : 'Delete')),
        ],
      ),
    );
    if (ok == true) {
      await HiveStorage.deleteCustomFood(food.id);
      _refreshResults();
    }
  }

  void _refreshResults() {
    final q = _ctrl.text.trim().toLowerCase();
    setState(() {
      _results = _mergedSearch(q, _selectedCategory);
    });
  }

  @override
  bool get wantKeepAlive => true;

  @override
  void dispose() {
    _ctrl.dispose();
    _focus.dispose();
    super.dispose();
  }

  List<FoodItem> _mergedSearch(String q, String? category) {
    final localResults = LocalFoodRepository.search(q, category: category);
    // Also search custom foods and prepend them so user's own entries rank first
    final customFoods = HiveStorage.getCustomFoods();
    final matchedCustom = customFoods.where((f) {
      final nameMatch = q.isEmpty ||
          f.name.toLowerCase().contains(q) ||
          (f.nameBn?.toLowerCase().contains(q) ?? false);
      final catMatch = category == null || f.category == category;
      return nameMatch && catMatch;
    }).toList();
    // Deduplicate by id in case a custom food was somehow duplicated
    final seen = <String>{};
    final merged = <FoodItem>[];
    for (final f in [...matchedCustom, ...localResults]) {
      if (seen.add(f.id)) merged.add(f);
    }
    return merged;
  }

  void _doSearch() {
    FocusScope.of(context).unfocus();
    final q = _ctrl.text.trim().toLowerCase();
    setState(() {
      _results = _mergedSearch(q, _selectedCategory);
      _hasSearched = true;
    });
  }

  void _setCategory(String cat) {
    final newCat = _selectedCategory == cat ? null : cat;
    final q = _ctrl.text.trim().toLowerCase();
    setState(() {
      _selectedCategory = newCat;
      _results = _mergedSearch(q, newCat);
      _hasSearched = _hasSearched || newCat != null;
    });
  }

  void _clear() {
    _ctrl.clear();
    setState(() {
      _selectedCategory = null;
      _results = [];
      _hasSearched = false;
    });
    _focus.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final lang = widget.lang;
    final isDark = widget.isDark;
    final theme = Theme.of(context);
    final fieldFill = isDark ? AppColors.darkCard : AppColors.lightBackground;

    return Column(
      children: [
        Container(
          color: isDark ? AppColors.darkBackground : AppColors.lightSurface,
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 0),
          child: Column(
            children: [
              Row(
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
                      decoration: InputDecoration(
                        hintText: lang == 'bn'
                            ? 'ভাত, ডাল, মুরগি, rice…'
                            : 'rice, dal, chicken, paneer…',
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
              if (_ctrl.text.isEmpty) ...[
                const SizedBox(height: 8),
                SizedBox(
                  height: 32,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    padding: EdgeInsets.zero,
                    itemCount: _localCategories.length,
                    separatorBuilder: (_, __) => const SizedBox(width: 6),
                    itemBuilder: (context, i) {
                      final cat = _localCategories[i];
                      final sel = _selectedCategory == cat;
                      final color = _catColor(cat);
                      return GestureDetector(
                        onTap: () => _setCategory(cat),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 180),
                          padding: const EdgeInsets.symmetric(horizontal: 10),
                          decoration: BoxDecoration(
                            color: sel ? color : color.withValues(alpha: 0.1),
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
                                  _catIcons[cat] ?? Icons.fastfood_outlined,
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
              ] else
                const SizedBox(height: 4),
            ],
          ),
        ),
        Expanded(
          child: _hasSearched
              ? (_results.isEmpty
                  ? _EmptyState(
                      icon: Icons.search_off_rounded,
                      title: lang == 'bn'
                          ? 'কোনো খাবার পাওয়া যায়নি'
                          : 'No Results Found',
                      subtitle: lang == 'bn'
                          ? 'আন্তর্জাতিক ট্যাবে খুঁজুন'
                          : 'Try the USDA tab',
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.fromLTRB(16, 10, 16, 20),
                      itemCount: _results.length,
                      itemBuilder: (_, i) {
                        final f = _results[i];
                        final isCustom = f.isCustom || f.source == 'custom';
                        return _AddFoodTile(
                          food: f,
                          lang: lang,
                          isDark: isDark,
                          mealType: widget.mealType,
                          onAdd: widget.onAdd,
                          trailing: isCustom
                              ? _CustomFoodActions(
                                  onEdit: () => _handleEditCustom(f),
                                  onDelete: () => _handleDeleteCustom(f),
                                )
                              : null,
                        );
                      },
                    ))
              : _LocalIdle(
                  lang: lang,
                  theme: theme,
                  mealType: widget.mealType,
                  onAdd: widget.onAdd,
                  isDark: isDark,
                  onEditCustom: _handleEditCustom,
                  onDeleteCustom: _handleDeleteCustom,
                ),
        ),
      ],
    );
  }
}

class _LocalIdle extends StatelessWidget {
  final String lang;
  final ThemeData theme;
  final String mealType;
  final Future<void> Function(FoodItem, double) onAdd;
  final bool isDark;
  final Future<void> Function(FoodItem)? onEditCustom;
  final Future<void> Function(FoodItem)? onDeleteCustom;

  const _LocalIdle({
    required this.lang,
    required this.theme,
    required this.mealType,
    required this.onAdd,
    required this.isDark,
    this.onEditCustom,
    this.onDeleteCustom,
  });

  @override
  Widget build(BuildContext context) {
    final count = LocalFoodRepository.itemCount;
    final customFoods = HiveStorage.getCustomFoods();
    final bn = lang == 'bn';

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 20),
      children: [
        // ── Dataset banner ────────────────────────────────────────────────
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
                      bn ? 'ভারতীয় ও বাঙালি খাবার' : 'Indian & Bengali Foods',
                      style: const TextStyle(
                          color: Colors.white, fontSize: 16, fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      bn ? '$count টি খাবার — সম্পূর্ণ অফলাইনে' : '$count foods — works offline',
                      style: const TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.offline_bolt_rounded, color: Colors.white30, size: 44),
            ],
          ),
        ),

        // ── My Custom Foods quick-access ──────────────────────────────────
        if (customFoods.isNotEmpty) ...[
          const SizedBox(height: 16),
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: const Color(0xFF7B61FF).withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.star_rounded, color: Color(0xFF7B61FF), size: 16),
              ),
              const SizedBox(width: 8),
              Text(
                bn ? 'আমার খাবার (${customFoods.length})' : 'My Foods (${customFoods.length})',
                style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
              ),
              const Spacer(),
              Text(
                bn ? 'সার্চে দেখা যাবে' : 'included in search',
                style: theme.textTheme.bodySmall?.copyWith(
                    color: const Color(0xFF7B61FF), fontSize: 11),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ...customFoods.take(3).map((food) => _AddFoodTile(
                food: food,
                lang: lang,
                isDark: isDark,
                mealType: mealType,
                onAdd: onAdd,
                trailing: (onEditCustom != null || onDeleteCustom != null)
                    ? _CustomFoodActions(
                        onEdit: onEditCustom != null
                            ? () => onEditCustom!(food)
                            : null,
                        onDelete: onDeleteCustom != null
                            ? () => onDeleteCustom!(food)
                            : null,
                      )
                    : null,
              )),
          if (customFoods.length > 3)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(
                bn
                    ? '+ আরও ${customFoods.length - 3}টি কাস্টম খাবার — সার্চ করুন'
                    : '+ ${customFoods.length - 3} more custom foods — use search',
                style: theme.textTheme.bodySmall?.copyWith(
                    color: const Color(0xFF7B61FF), fontStyle: FontStyle.italic),
              ),
            ),
        ],

        // ── Search tips ───────────────────────────────────────────────────
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.primary.withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.primary.withValues(alpha: 0.12)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.tips_and_updates_outlined, size: 14, color: AppColors.primary),
                  const SizedBox(width: 6),
                  Text(
                    bn ? 'কিভাবে ব্যবহার করবেন' : 'How to search',
                    style: theme.textTheme.titleSmall?.copyWith(
                        color: AppColors.primary, fontWeight: FontWeight.w700),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              for (final tip in (bn
                  ? [
                      'বাংলা বা ইংরেজিতে খাবারের নাম লিখুন',
                      '"খুঁজুন" বাটন চাপুন',
                      'ক্যাটাগরি চিপ ট্যাপ করে ব্রাউজ করুন',
                      'কাস্টম খাবারও সার্চে দেখা যাবে',
                    ]
                  : [
                      'Type food name in English or Bengali',
                      'Tap "Search" or press keyboard Search',
                      'Tap a category chip to browse by type',
                      'Your custom foods also appear in results',
                    ]))
                Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.circle, size: 5, color: AppColors.primary),
                      const SizedBox(width: 8),
                      Expanded(child: Text(tip, style: theme.textTheme.bodySmall)),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 2 — International (USDA API)
// ═══════════════════════════════════════════════════════════════════════════════

enum _UsdaStatus { idle, loading, success, error, offline, rateLimited }

class _UsdaTab extends StatefulWidget {
  final String lang;
  final bool isDark;
  final String mealType;
  final Future<void> Function(FoodItem, double) onAdd;

  const _UsdaTab({required this.lang, required this.isDark, required this.mealType, required this.onAdd});

  @override
  State<_UsdaTab> createState() => _UsdaTabState();
}

class _UsdaTabState extends State<_UsdaTab> with AutomaticKeepAliveClientMixin {
  final _ctrl = TextEditingController();
  final _focus = FocusNode();
  final _apiService = UsdaApiService();
  List<FoodItem> _results = [];
  _UsdaStatus _status = _UsdaStatus.idle;
  String? _error;

  @override
  bool get wantKeepAlive => true;

  @override
  void dispose() {
    _ctrl.dispose();
    _focus.dispose();
    super.dispose();
  }

  Future<void> _doSearch() async {
    final q = _ctrl.text.trim();
    if (q.isEmpty) return;
    FocusScope.of(context).unfocus();
    setState(() {
      _status = _UsdaStatus.loading;
      _error = null;
    });
    try {
      final results = await _apiService.searchFoods(q);
      if (!mounted) return;
      setState(() {
        _results = results;
        _status = _UsdaStatus.success;
      });
    } on RateLimitException {
      if (!mounted) return;
      setState(() => _status = _UsdaStatus.rateLimited);
    } catch (e) {
      if (!mounted) return;
      final msg = e.toString().replaceAll('Exception: ', '');
      final isOffline = msg.contains('connection') ||
          msg.contains('network') || msg.contains('timeout');
      setState(() {
        _error = msg;
        _status = isOffline ? _UsdaStatus.offline : _UsdaStatus.error;
      });
    }
  }

  void _clear() {
    _ctrl.clear();
    setState(() {
      _results = [];
      _status = _UsdaStatus.idle;
      _error = null;
    });
    _focus.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final lang = widget.lang;
    final isDark = widget.isDark;
    final theme = Theme.of(context);
    final fieldFill = isDark ? AppColors.darkCard : AppColors.lightBackground;

    return Column(
      children: [
        Container(
          color: isDark ? AppColors.darkBackground : AppColors.lightSurface,
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
                  decoration: InputDecoration(
                    hintText: lang == 'bn'
                        ? 'যেমন: Coca-Cola, Oreo, Pizza…'
                        : 'e.g. Coca-Cola, Oreo, Pizza…',
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
        Expanded(child: _buildBody(lang, isDark, theme)),
      ],
    );
  }

  Widget _buildBody(String lang, bool isDark, ThemeData theme) {
    switch (_status) {
      case _UsdaStatus.idle:
        return _UsdaIdle(lang: lang, theme: theme);

      case _UsdaStatus.loading:
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

      case _UsdaStatus.success:
        if (_results.isEmpty) {
          return _EmptyState(
            icon: Icons.search_off_rounded,
            title: lang == 'bn' ? 'কোনো ফলাফল নেই' : 'No Results',
            subtitle: lang == 'bn'
                ? 'ভিন্ন শব্দ দিয়ে চেষ্টা করুন'
                : 'Try different keywords',
          );
        }
        return ListView.builder(
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 20),
          itemCount: _results.length,
          itemBuilder: (_, i) => _AddFoodTile(
            food: _results[i],
            lang: lang,
            isDark: isDark,
            mealType: widget.mealType,
            onAdd: widget.onAdd,
          ),
        );

      case _UsdaStatus.offline:
        return _EmptyState(
          icon: Icons.wifi_off_rounded,
          iconColor: Colors.orange,
          title: lang == 'bn' ? 'ইন্টারনেট নেই' : 'No Internet',
          subtitle: lang == 'bn'
              ? 'USDA সার্চের জন্য ইন্টারনেট প্রয়োজন'
              : 'Internet required for USDA search',
          actionLabel: lang == 'bn' ? 'আবার চেষ্টা' : 'Retry',
          onAction: _doSearch,
        );

      case _UsdaStatus.rateLimited:
        return _EmptyState(
          icon: Icons.hourglass_top_rounded,
          iconColor: Colors.amber,
          title: lang == 'bn' ? 'সাময়িক সীমাবদ্ধতা' : 'Rate Limited',
          subtitle: lang == 'bn'
              ? 'কিছুক্ষণ পরে আবার চেষ্টা করুন'
              : 'Please try again in a few minutes',
          actionLabel: lang == 'bn' ? 'আবার চেষ্টা' : 'Retry',
          onAction: _doSearch,
        );

      case _UsdaStatus.error:
        return _EmptyState(
          icon: Icons.error_outline_rounded,
          iconColor: Colors.redAccent,
          title: lang == 'bn' ? 'সংযোগ ব্যর্থ' : 'Search Failed',
          subtitle: _error ?? (lang == 'bn' ? 'একটি সমস্যা হয়েছে' : 'Something went wrong'),
          actionLabel: lang == 'bn' ? 'আবার চেষ্টা' : 'Retry',
          onAction: _doSearch,
        );
    }
  }
}

class _UsdaIdle extends StatelessWidget {
  final String lang;
  final ThemeData theme;
  const _UsdaIdle({required this.lang, required this.theme});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 20),
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
                      lang == 'bn' ? 'আন্তর্জাতিক ডেটাবেজ' : 'USDA Database',
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      lang == 'bn'
                          ? 'USDA — ইন্টারনেট প্রয়োজন'
                          : 'USDA FoodData Central — requires internet',
                      style: const TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.public_rounded, color: Colors.white30, size: 44),
            ],
          ),
        ),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// TAB 3 — Custom Food (inline form + saved list)
// ═══════════════════════════════════════════════════════════════════════════════

class _CustomTab extends StatefulWidget {
  final String lang;
  final bool isDark;
  final String mealType;
  final Future<void> Function(FoodItem, double) onAdd;

  const _CustomTab({required this.lang, required this.isDark, required this.mealType, required this.onAdd});

  @override
  State<_CustomTab> createState() => _CustomTabState();
}

class _CustomTabState extends State<_CustomTab> with AutomaticKeepAliveClientMixin {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _servingCtrl = TextEditingController(text: '100');
  final _calCtrl = TextEditingController();
  final _proteinCtrl = TextEditingController(text: '0');
  final _carbCtrl = TextEditingController(text: '0');
  final _fatCtrl = TextEditingController(text: '0');
  final _fiberCtrl = TextEditingController(text: '0');
  String _unit = 'g';
  bool _saveForFuture = false;
  List<FoodItem> _customFoods = [];

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _reload();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _servingCtrl.dispose();
    _calCtrl.dispose();
    _proteinCtrl.dispose();
    _carbCtrl.dispose();
    _fatCtrl.dispose();
    _fiberCtrl.dispose();
    super.dispose();
  }

  void _reload() {
    setState(() => _customFoods = HiveStorage.getCustomFoods());
  }

  Future<void> _editFood(FoodItem food) async {
    final updated = await showEditCustomFoodSheet(context, food, widget.lang);
    if (updated) _reload();
  }

  void _clearForm() {
    _nameCtrl.clear();
    _servingCtrl.text = '100';
    _calCtrl.clear();
    _proteinCtrl.text = '0';
    _carbCtrl.text = '0';
    _fatCtrl.text = '0';
    _fiberCtrl.text = '0';
    setState(() {
      _unit = 'g';
      _saveForFuture = false;
    });
  }

  Future<void> _save() async {
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
      fiberG: double.tryParse(_fiberCtrl.text) ?? 0,
      isCustom: _saveForFuture,
      source: 'custom',
    );
    if (_saveForFuture) {
      await HiveStorage.saveCustomFood(food);
      _reload();
      if (mounted) {
        final bn = widget.lang == 'bn';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(bn ? 'সংরক্ষণ হয়েছে!' : 'Saved!'),
            duration: const Duration(seconds: 2),
            backgroundColor: const Color(0xFF7B61FF),
          ),
        );
      }
    }
    final serving = double.tryParse(_servingCtrl.text) ?? 100;
    _clearForm();
    await widget.onAdd(food, serving);
  }

  Future<void> _delete(String id) async {
    await HiveStorage.deleteCustomFood(id);
    _reload();
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final lang = widget.lang;
    final isDark = widget.isDark;
    final theme = Theme.of(context);
    final bn = lang == 'bn';

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Inline form ──────────────────────────────────────────────────
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isDark ? AppColors.darkCard : Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: const Color(0xFF7B61FF).withValues(alpha: 0.25),
              ),
              boxShadow: isDark
                  ? null
                  : [
                      BoxShadow(
                        color: Colors.black.withValues(alpha: 0.04),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ],
            ),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFF7B61FF).withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: const Icon(Icons.edit_note_rounded,
                            color: Color(0xFF7B61FF), size: 20),
                      ),
                      const SizedBox(width: 10),
                      Text(
                        bn ? 'কাস্টম খাবার তৈরি করুন' : 'Create Custom Food',
                        style: theme.textTheme.titleSmall
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  _SheetField(
                    controller: _nameCtrl,
                    label: bn ? 'খাবারের নাম *' : 'Food Name *',
                    hint: bn ? 'মায়ের হাতের ডাল' : "Mom's Dal",
                    validator: (v) => (v == null || v.trim().isEmpty)
                        ? (bn ? 'নাম দিন' : 'Required')
                        : null,
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        flex: 3,
                        child: _SheetField(
                          controller: _servingCtrl,
                          label: bn ? 'পরিমাণ *' : 'Serving *',
                          hint: '100',
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          inputFormatters: [
                            FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
                          ],
                          validator: (v) => (double.tryParse(v ?? '') ?? 0) <= 0
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
                          items: ['g', 'ml', 'pcs', 'oz', 'cup']
                              .map((u) => DropdownMenuItem(value: u, child: Text(u)))
                              .toList(),
                          onChanged: (v) => setState(() => _unit = v ?? 'g'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  _SheetField(
                    controller: _calCtrl,
                    label: bn ? 'ক্যালোরি (kcal) *' : 'Calories (kcal) *',
                    hint: '250',
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    inputFormatters: [
                      FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
                    ],
                    validator: (v) => double.tryParse(v ?? '') == null
                        ? (bn ? 'ক্যালোরি দিন' : 'Required')
                        : null,
                  ),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Expanded(
                        child: _SheetField(
                          controller: _proteinCtrl,
                          label: bn ? 'প্রোটিন (g)' : 'Protein (g)',
                          hint: '0',
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          inputFormatters: [
                            FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
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
                            FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
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
                            FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _SheetField(
                          controller: _fiberCtrl,
                          label: bn ? 'ফাইবার (g)' : 'Fiber (g)',
                          hint: '0',
                          keyboardType: const TextInputType.numberWithOptions(decimal: true),
                          inputFormatters: [
                            FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  // Save for future checkbox
                  GestureDetector(
                    onTap: () => setState(() => _saveForFuture = !_saveForFuture),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                      decoration: BoxDecoration(
                        color: _saveForFuture
                            ? const Color(0xFF7B61FF).withValues(alpha: 0.08)
                            : theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.4),
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(
                          color: _saveForFuture
                              ? const Color(0xFF7B61FF).withValues(alpha: 0.5)
                              : theme.dividerColor,
                        ),
                      ),
                      child: Row(
                        children: [
                          Checkbox(
                            value: _saveForFuture,
                            onChanged: (v) => setState(() => _saveForFuture = v ?? false),
                            activeColor: const Color(0xFF7B61FF),
                            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            visualDensity: VisualDensity.compact,
                          ),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  bn ? 'ভবিষ্যতে ব্যবহারের জন্য সংরক্ষণ করুন' : 'Save for future use',
                                  style: theme.textTheme.bodyMedium?.copyWith(
                                    fontWeight: FontWeight.w600,
                                    fontSize: 13,
                                  ),
                                ),
                                Text(
                                  bn
                                      ? 'চেক না করলে শুধু এবারের মিলে যোগ হবে'
                                      : 'Unchecked: add to this meal only, not saved',
                                  style: theme.textTheme.bodySmall?.copyWith(fontSize: 11),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      onPressed: _save,
                      icon: Icon(_saveForFuture ? Icons.save_rounded : Icons.add_rounded, size: 18),
                      label: Text(
                        _saveForFuture
                            ? (bn ? 'সংরক্ষণ করে যোগ করুন' : 'Save & Add to Meal')
                            : (bn ? 'মিলে যোগ করুন' : 'Add to Meal'),
                        style: const TextStyle(
                            fontWeight: FontWeight.w700, fontSize: 15),
                      ),
                      style: FilledButton.styleFrom(
                        backgroundColor: const Color(0xFF7B61FF),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 13),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),

          // ── Saved custom foods ───────────────────────────────────────────
          if (_customFoods.isNotEmpty) ...[
            const SizedBox(height: 20),
            Text(
              bn
                  ? 'সংরক্ষিত কাস্টম খাবার (${_customFoods.length})'
                  : 'Saved Custom Foods (${_customFoods.length})',
              style: theme.textTheme.titleSmall
                  ?.copyWith(fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 8),
            ..._customFoods.map((food) => _AddFoodTile(
              food: food,
              lang: lang,
              isDark: isDark,
              mealType: widget.mealType,
              onAdd: widget.onAdd,
              trailing: _CustomFoodActions(
                onEdit: () => _editFood(food),
                onDelete: () async {
                  final ok = await showDialog<bool>(
                    context: context,
                    builder: (ctx) => AlertDialog(
                      title: Text(bn ? 'মুছে ফেলবেন?' : 'Delete?'),
                      content: Text('"${food.name}"'),
                      actions: [
                        TextButton(
                            onPressed: () => Navigator.pop(ctx, false),
                            child: Text(bn ? 'বাতিল' : 'Cancel')),
                        FilledButton(
                            onPressed: () => Navigator.pop(ctx, true),
                            style: FilledButton.styleFrom(
                                backgroundColor: Colors.red),
                            child: Text(bn ? 'মুছুন' : 'Delete')),
                      ],
                    ),
                  );
                  if (ok == true) _delete(food.id);
                },
              ),
            )),
          ],
        ],
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
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Shared: food tile with inline quantity + add button
// ═══════════════════════════════════════════════════════════════════════════════

class _AddFoodTile extends StatefulWidget {
  final FoodItem food;
  final String lang;
  final bool isDark;
  final String mealType;
  final Future<void> Function(FoodItem, double) onAdd;
  final Widget? trailing;

  const _AddFoodTile({
    required this.food,
    required this.lang,
    required this.isDark,
    required this.mealType,
    required this.onAdd,
    this.trailing,
  });

  @override
  State<_AddFoodTile> createState() => _AddFoodTileState();
}

class _AddFoodTileState extends State<_AddFoodTile> {
  late double _qty;
  late final TextEditingController _qtyCtrl;
  bool _adding = false;

  @override
  void initState() {
    super.initState();
    _qty = widget.food.servingSize > 0 ? widget.food.servingSize : 100;
    _qtyCtrl = TextEditingController(text: _qty.toStringAsFixed(0));
  }

  @override
  void dispose() {
    _qtyCtrl.dispose();
    super.dispose();
  }

  Future<void> _add() async {
    if (_adding) return;
    setState(() => _adding = true);
    try {
      await widget.onAdd(widget.food, _qty);
    } finally {
      if (mounted) setState(() => _adding = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final food = widget.food;
    final lang = widget.lang;
    final isDark = widget.isDark;
    final theme = Theme.of(context);
    final color = _catColor(food.category);
    final scaledCal = food.calories * _qty / (food.servingSize > 0 ? food.servingSize : 100);

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top row: tappable food info → opens FoodDetailScreen
          Row(
            children: [
              Expanded(
                child: GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () => context.push(
                    '/food-search/detail',
                    extra: {'food': food, 'mealType': widget.mealType},
                  ),
                  child: Row(
                    children: [
                      Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.12),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Icon(
                          _catIcons[food.category] ?? Icons.fastfood_outlined,
                          color: color,
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              food.displayName(lang),
                              style: theme.textTheme.titleSmall?.copyWith(
                                  fontWeight: FontWeight.w700, fontSize: 13),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            if (lang == 'bn' && food.name.isNotEmpty)
                              Text(food.name,
                                  style: theme.textTheme.bodySmall
                                      ?.copyWith(fontSize: 10),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis)
                            else if (food.nameBn != null && food.nameBn!.isNotEmpty)
                              Text(food.nameBn!,
                                  style: theme.textTheme.bodySmall
                                      ?.copyWith(fontSize: 10),
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis),
                          ],
                        ),
                      ),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(
                            '${scaledCal.toStringAsFixed(0)} kcal',
                            style: const TextStyle(
                              color: AppColors.calories,
                              fontWeight: FontWeight.w800,
                              fontSize: 13,
                            ),
                          ),
                          Text(
                            'per ${_qty.toStringAsFixed(0)}${food.servingUnit}',
                            style: theme.textTheme.labelSmall?.copyWith(fontSize: 9),
                          ),
                        ],
                      ),
                      const SizedBox(width: 4),
                      Icon(Icons.chevron_right_rounded,
                          size: 16, color: theme.hintColor),
                    ],
                  ),
                ),
              ),
              if (widget.trailing != null) widget.trailing!,
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              // Macro pills
              _MacroPill('P ${(food.proteinG * _qty / (food.servingSize > 0 ? food.servingSize : 100)).toStringAsFixed(0)}g', AppColors.protein),
              const SizedBox(width: 4),
              _MacroPill('C ${(food.carbsG * _qty / (food.servingSize > 0 ? food.servingSize : 100)).toStringAsFixed(0)}g', AppColors.carbs),
              const SizedBox(width: 4),
              _MacroPill('F ${(food.fatG * _qty / (food.servingSize > 0 ? food.servingSize : 100)).toStringAsFixed(0)}g', AppColors.fat),
              const Spacer(),
              // Quantity input
              SizedBox(
                width: 72,
                child: TextField(
                  controller: _qtyCtrl,
                  keyboardType: TextInputType.number,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                  decoration: InputDecoration(
                    suffix: Text(food.servingUnit,
                        style: const TextStyle(fontSize: 11)),
                    isDense: true,
                    contentPadding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 7),
                    border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8)),
                  ),
                  onChanged: (v) {
                    final parsed = double.tryParse(v);
                    if (parsed != null && parsed > 0) {
                      setState(() => _qty = parsed);
                    }
                  },
                ),
              ),
              const SizedBox(width: 8),
              // Add button
              FilledButton(
                onPressed: _adding ? null : _add,
                style: FilledButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 9),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10)),
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
                child: _adding
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white))
                    : Text(
                        lang == 'bn' ? 'যোগ' : 'Add',
                        style: const TextStyle(
                            fontSize: 13, fontWeight: FontWeight.w700),
                      ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ── Custom food edit helpers ──────────────────────────────────────────────────

/// Shows the edit sheet for [food]. Returns true if the user saved changes.
Future<bool> showEditCustomFoodSheet(
    BuildContext context, FoodItem food, String lang) async {
  final result = await showModalBottomSheet<bool>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => _EditCustomFoodSheet(food: food, lang: lang),
  );
  return result == true;
}

class _CustomFoodActions extends StatelessWidget {
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const _CustomFoodActions({this.onEdit, this.onDelete});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (onEdit != null)
          GestureDetector(
            onTap: onEdit,
            child: Padding(
              padding: const EdgeInsets.all(6),
              child: Icon(Icons.edit_outlined,
                  size: 18,
                  color: AppColors.secondary.withValues(alpha: 0.8)),
            ),
          ),
        if (onDelete != null)
          GestureDetector(
            onTap: onDelete,
            child: Padding(
              padding: const EdgeInsets.all(6),
              child: Icon(Icons.delete_outline_rounded,
                  size: 18,
                  color: Colors.red.withValues(alpha: 0.7)),
            ),
          ),
      ],
    );
  }
}

class _EditCustomFoodSheet extends StatefulWidget {
  final FoodItem food;
  final String lang;
  const _EditCustomFoodSheet({required this.food, required this.lang});

  @override
  State<_EditCustomFoodSheet> createState() => _EditCustomFoodSheetState();
}

class _EditCustomFoodSheetState extends State<_EditCustomFoodSheet> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _nameCtrl;
  late final TextEditingController _servingCtrl;
  late final TextEditingController _calCtrl;
  late final TextEditingController _proteinCtrl;
  late final TextEditingController _carbCtrl;
  late final TextEditingController _fatCtrl;
  late String _unit;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    final f = widget.food;
    _nameCtrl    = TextEditingController(text: f.name);
    _servingCtrl = TextEditingController(text: f.servingSize.toStringAsFixed(0));
    _calCtrl     = TextEditingController(text: f.calories.toStringAsFixed(0));
    _proteinCtrl = TextEditingController(text: f.proteinG.toStringAsFixed(1));
    _carbCtrl    = TextEditingController(text: f.carbsG.toStringAsFixed(1));
    _fatCtrl     = TextEditingController(text: f.fatG.toStringAsFixed(1));
    _unit        = f.servingUnit;
  }

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

  Future<void> _save() async {
    if (!_formKey.currentState!.validate() || _saving) return;
    setState(() => _saving = true);
    final updated = FoodItem(
      id: widget.food.id,
      name: _nameCtrl.text.trim(),
      nameBn: widget.food.nameBn,
      servingSize: double.tryParse(_servingCtrl.text) ?? widget.food.servingSize,
      servingUnit: _unit,
      calories: double.tryParse(_calCtrl.text) ?? widget.food.calories,
      proteinG: double.tryParse(_proteinCtrl.text) ?? widget.food.proteinG,
      carbsG: double.tryParse(_carbCtrl.text) ?? widget.food.carbsG,
      fatG: double.tryParse(_fatCtrl.text) ?? widget.food.fatG,
      fiberG: widget.food.fiberG,
      isCustom: true,
      source: 'custom',
      category: widget.food.category,
      keywords: widget.food.keywords,
    );
    await HiveStorage.saveCustomFood(updated);
    if (mounted) Navigator.of(context).pop(true);
  }

  @override
  Widget build(BuildContext context) {
    final bn = widget.lang == 'bn';
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Padding(
      padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom),
      child: Container(
        decoration: BoxDecoration(
          color: isDark ? AppColors.darkCard : Colors.white,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(22)),
        ),
        child: SingleChildScrollView(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                // Handle
                Center(
                  child: Container(
                    width: 40, height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey.shade300,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: const Color(0xFF7B61FF).withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(Icons.edit_rounded,
                          color: Color(0xFF7B61FF), size: 20),
                    ),
                    const SizedBox(width: 10),
                    Text(
                      bn ? 'খাবার সম্পাদনা' : 'Edit Custom Food',
                      style: theme.textTheme.titleMedium
                          ?.copyWith(fontWeight: FontWeight.w800),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                _SheetField(
                  controller: _nameCtrl,
                  label: bn ? 'খাবারের নাম *' : 'Food Name *',
                  hint: '',
                  validator: (v) => (v == null || v.trim().isEmpty)
                      ? (bn ? 'নাম দিন' : 'Required')
                      : null,
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      flex: 3,
                      child: _SheetField(
                        controller: _servingCtrl,
                        label: bn ? 'পরিমাণ *' : 'Serving *',
                        hint: '100',
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        inputFormatters: [
                          FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
                        ],
                        validator: (v) => (double.tryParse(v ?? '') ?? 0) <= 0
                            ? (bn ? 'পরিমাণ দিন' : 'Enter amount')
                            : null,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      flex: 2,
                      child: DropdownButtonFormField<String>(
                        value: ['g', 'ml', 'pcs', 'oz', 'cup'].contains(_unit) ? _unit : 'g',
                        decoration: InputDecoration(
                          labelText: bn ? 'একক' : 'Unit',
                          contentPadding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 14),
                          border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(10)),
                        ),
                        items: ['g', 'ml', 'pcs', 'oz', 'cup']
                            .map((u) => DropdownMenuItem(value: u, child: Text(u)))
                            .toList(),
                        onChanged: (v) => setState(() => _unit = v ?? 'g'),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                _SheetField(
                  controller: _calCtrl,
                  label: bn ? 'ক্যালোরি (kcal) *' : 'Calories (kcal) *',
                  hint: '0',
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  inputFormatters: [
                    FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
                  ],
                  validator: (v) => double.tryParse(v ?? '') == null
                      ? (bn ? 'ক্যালোরি দিন' : 'Required')
                      : null,
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: _SheetField(
                        controller: _proteinCtrl,
                        label: bn ? 'প্রোটিন (g)' : 'Protein (g)',
                        hint: '0',
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        inputFormatters: [
                          FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
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
                          FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
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
                          FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: FilledButton.icon(
                    onPressed: _saving ? null : _save,
                    icon: _saving
                        ? const SizedBox(
                            width: 16, height: 16,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: Colors.white))
                        : const Icon(Icons.save_rounded, size: 18),
                    label: Text(
                      bn ? 'সংরক্ষণ করুন' : 'Save Changes',
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
                    ),
                    style: FilledButton.styleFrom(
                      backgroundColor: const Color(0xFF7B61FF),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ── Shared utility widgets ────────────────────────────────────────────────────

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

class _EmptyState extends StatelessWidget {
  final IconData icon;
  final Color? iconColor;
  final String title;
  final String subtitle;
  final String? actionLabel;
  final VoidCallback? onAction;

  const _EmptyState({
    required this.icon,
    this.iconColor,
    required this.title,
    required this.subtitle,
    this.actionLabel,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final color = iconColor ?? Colors.grey;
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
                color: color.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, size: 36, color: color),
            ),
            const SizedBox(height: 16),
            Text(title,
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.w700),
                textAlign: TextAlign.center),
            const SizedBox(height: 6),
            Text(subtitle,
                style: theme.textTheme.bodySmall?.copyWith(fontSize: 13),
                textAlign: TextAlign.center),
            if (actionLabel != null && onAction != null) ...[
              const SizedBox(height: 16),
              FilledButton.icon(
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
