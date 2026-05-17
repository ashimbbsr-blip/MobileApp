import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../localization/app_localizations.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../models/food_item.dart';
import '../../services/usda_api_service.dart';
import '../../widgets/common/loading_indicator.dart';
import '../dashboard/providers/dashboard_provider.dart';
import '../meal_tracking/providers/meal_provider.dart';
import 'package:uuid/uuid.dart';

class AddFoodScreen extends ConsumerStatefulWidget {
  final String mealType;
  const AddFoodScreen({super.key, required this.mealType});

  @override
  ConsumerState<AddFoodScreen> createState() => _AddFoodScreenState();
}

class _AddFoodScreenState extends ConsumerState<AddFoodScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _searchController = TextEditingController();
  final _apiService = UsdaApiService();

  List<FoodItem> _searchResults = [];
  bool _isSearching = false;
  String? _searchError;

  // Custom food form
  final _nameController = TextEditingController();
  final _caloriesController = TextEditingController();
  final _proteinController = TextEditingController();
  final _carbsController = TextEditingController();
  final _fatController = TextEditingController();
  final _servingController = TextEditingController(text: '100');

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    _nameController.dispose();
    _caloriesController.dispose();
    _proteinController.dispose();
    _carbsController.dispose();
    _fatController.dispose();
    _servingController.dispose();
    super.dispose();
  }

  Future<void> _search(String query) async {
    if (query.trim().isEmpty) return;
    setState(() { _isSearching = true; _searchError = null; });
    try {
      final results = await _apiService.searchFoods(query);
      setState(() { _searchResults = results; _isSearching = false; });
    } catch (e) {
      setState(() { _searchError = e.toString().replaceAll('Exception: ', ''); _isSearching = false; });
    }
  }

  Future<void> _addFood(FoodItem food, double quantity) async {
    await ref.read(mealProvider.notifier).addFood(food, widget.mealType, quantity);
    ref.read(dashboardProvider.notifier).refresh();
    if (mounted) context.pop();
  }

  Future<void> _addCustomFood() async {
    final name = _nameController.text.trim();
    if (name.isEmpty) return;
    final calories = double.tryParse(_caloriesController.text) ?? 0;
    final protein = double.tryParse(_proteinController.text) ?? 0;
    final carbs = double.tryParse(_carbsController.text) ?? 0;
    final fat = double.tryParse(_fatController.text) ?? 0;
    final serving = double.tryParse(_servingController.text) ?? 100;

    final food = FoodItem(
      id: const Uuid().v4(),
      name: name,
      servingSize: serving,
      servingUnit: 'g',
      calories: calories,
      proteinG: protein,
      carbsG: carbs,
      fatG: fat,
      fiberG: 0,
      isCustom: true,
    );
    await _addFood(food, serving);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = ref.watch(appStringsProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.addFood),
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: l10n.searchFood),
            Tab(text: l10n.customFood),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _SearchTab(
            controller: _searchController,
            results: _searchResults,
            isLoading: _isSearching,
            error: _searchError,
            onSearch: _search,
            onAdd: _addFood,
            l10n: l10n,
          ),
          _CustomFoodTab(
            nameController: _nameController,
            caloriesController: _caloriesController,
            proteinController: _proteinController,
            carbsController: _carbsController,
            fatController: _fatController,
            servingController: _servingController,
            onAdd: _addCustomFood,
            l10n: l10n,
          ),
        ],
      ),
    );
  }
}

class _SearchTab extends StatelessWidget {
  final TextEditingController controller;
  final List<FoodItem> results;
  final bool isLoading;
  final String? error;
  final void Function(String) onSearch;
  final Future<void> Function(FoodItem, double) onAdd;
  final AppStrings l10n;

  const _SearchTab({
    required this.controller, required this.results, required this.isLoading,
    required this.error, required this.onSearch, required this.onAdd, required this.l10n,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: TextField(
            controller: controller,
            decoration: InputDecoration(
              hintText: l10n.searchFood,
              prefixIcon: const Icon(Icons.search),
              suffixIcon: IconButton(
                icon: const Icon(Icons.send),
                onPressed: () => onSearch(controller.text),
              ),
            ),
            onSubmitted: onSearch,
          ),
        ),
        if (isLoading) const Expanded(child: LoadingIndicator()),
        if (error != null) Expanded(child: Center(child: Text(error!, textAlign: TextAlign.center))),
        if (!isLoading && error == null)
          Expanded(
            child: results.isEmpty
                ? Center(child: Text(l10n.searchFood))
                : ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    itemCount: results.length,
                    itemBuilder: (ctx, i) => _QuickAddTile(food: results[i], onAdd: onAdd),
                  ),
          ),
      ],
    );
  }
}

class _QuickAddTile extends StatefulWidget {
  final FoodItem food;
  final Future<void> Function(FoodItem, double) onAdd;
  const _QuickAddTile({required this.food, required this.onAdd});

  @override
  State<_QuickAddTile> createState() => _QuickAddTileState();
}

class _QuickAddTileState extends State<_QuickAddTile> {
  double _qty = 100;
  late final TextEditingController _qtyController;

  @override
  void initState() {
    super.initState();
    _qtyController = TextEditingController(text: '100');
  }

  @override
  void dispose() {
    _qtyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(widget.food.name, style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600), maxLines: 1, overflow: TextOverflow.ellipsis),
                  Text('${(widget.food.calories * _qty / widget.food.servingSize).toStringAsFixed(0)} kcal', style: TextStyle(color: AppColors.calories, fontSize: 12)),
                ],
              ),
            ),
            SizedBox(
              width: 70,
              child: TextField(
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(suffix: Text('g'), isDense: true, contentPadding: EdgeInsets.all(8)),
                controller: _qtyController,
                onChanged: (v) {
                  final parsed = double.tryParse(v);
                  if (parsed != null && parsed > 0) setState(() => _qty = parsed);
                },
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              icon: const Icon(Icons.add_circle, color: AppColors.primary),
              onPressed: () => widget.onAdd(widget.food, _qty),
            ),
          ],
        ),
      ),
    );
  }
}

class _CustomFoodTab extends StatelessWidget {
  final TextEditingController nameController, caloriesController, proteinController, carbsController, fatController, servingController;
  final VoidCallback onAdd;
  final AppStrings l10n;

  const _CustomFoodTab({
    required this.nameController, required this.caloriesController,
    required this.proteinController, required this.carbsController,
    required this.fatController, required this.servingController,
    required this.onAdd, required this.l10n,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(controller: nameController, decoration: InputDecoration(labelText: 'Food Name')),
          const SizedBox(height: 12),
          TextField(controller: servingController, keyboardType: TextInputType.number, decoration: const InputDecoration(labelText: 'Serving Size (g)')),
          const SizedBox(height: 12),
          TextField(controller: caloriesController, keyboardType: TextInputType.number, decoration: InputDecoration(labelText: '${l10n.calories} (kcal)')),
          const SizedBox(height: 12),
          TextField(controller: proteinController, keyboardType: TextInputType.number, decoration: InputDecoration(labelText: '${l10n.protein} (g)')),
          const SizedBox(height: 12),
          TextField(controller: carbsController, keyboardType: TextInputType.number, decoration: InputDecoration(labelText: '${l10n.carbs} (g)')),
          const SizedBox(height: 12),
          TextField(controller: fatController, keyboardType: TextInputType.number, decoration: InputDecoration(labelText: '${l10n.fat} (g)')),
          const SizedBox(height: 24),
          ElevatedButton(onPressed: onAdd, child: Text(l10n.addFood)),
        ],
      ),
    );
  }
}
