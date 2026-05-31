import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../localization/app_localizations.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../models/food_item.dart';
import '../../services/local_food_repository.dart';
import '../meal_tracking/providers/meal_provider.dart';
import '../dashboard/providers/dashboard_provider.dart';
import 'providers/scan_provider.dart';

// ─────────────────────────────────────────────────────────────────────────────
// Entry point
// ─────────────────────────────────────────────────────────────────────────────

class CameraScanScreen extends ConsumerStatefulWidget {
  final String mealType;
  const CameraScanScreen({super.key, required this.mealType});

  @override
  ConsumerState<CameraScanScreen> createState() => _CameraScanScreenState();
}

class _CameraScanScreenState extends ConsumerState<CameraScanScreen> {
  bool _sheetShown = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(scanProvider.notifier).reset();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(scanProvider);
    final l10n = ref.watch(appStringsProvider);

    ref.listen<ScanState>(scanProvider, (_, next) {
      if (next.phase == ScanPhase.done &&
          next.suggestions.isNotEmpty &&
          !_sheetShown) {
        _sheetShown = true;
        _showSuggestions(next.suggestions);
      }
      if (next.phase == ScanPhase.idle) _sheetShown = false;
    });

    return Scaffold(
      backgroundColor: const Color(0xFF0D1520),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        foregroundColor: Colors.white,
        title: Text(
          l10n.scanFood,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w600,
          ),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
        elevation: 0,
      ),
      body: _buildBody(context, state, l10n),
    );
  }

  Widget _buildBody(BuildContext context, ScanState state, AppStrings l10n) {
    return switch (state.phase) {
      ScanPhase.permissionDenied => _PermissionDeniedView(l10n: l10n),
      ScanPhase.error => _ErrorView(
          message: state.errorMessage,
          onRetry: _retry,
          l10n: l10n,
        ),
      ScanPhase.noResults => _NoResultsView(
          labels: state.detectedLabels,
          onRetry: _retry,
          mealType: widget.mealType,
          onFoodAdded: () => context.pop(),
          l10n: l10n,
        ),
      ScanPhase.analyzing => _ScanReadyView(
          onCapture: _capture,
          onManual: () => context.pop(),
          l10n: l10n,
          isAnalyzing: true,
        ),
      _ => _ScanReadyView(
          onCapture: _capture,
          onManual: () => context.pop(),
          l10n: l10n,
          isAnalyzing: false,
        ),
    };
  }

  void _capture() => ref.read(scanProvider.notifier).captureAndAnalyze();
  void _retry() => ref.read(scanProvider.notifier).reset();

  void _showSuggestions(List<FoodItem> suggestions) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _FoodSuggestionSheet(
        suggestions: suggestions,
        initialMealType: widget.mealType,
        onFoodAdded: () {
          Navigator.of(context).pop();
          context.pop();
        },
        onRetry: () {
          Navigator.of(context).pop();
          _retry();
        },
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Scan-ready view
// ─────────────────────────────────────────────────────────────────────────────

class _ScanReadyView extends StatelessWidget {
  final VoidCallback onCapture;
  final VoidCallback onManual;
  final AppStrings l10n;
  final bool isAnalyzing;

  const _ScanReadyView({
    required this.onCapture,
    required this.onManual,
    required this.l10n,
    required this.isAnalyzing,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const SizedBox(height: 16),
            _ViewfinderFrame(isAnalyzing: isAnalyzing, l10n: l10n),
            const SizedBox(height: 8),
            _TipBanner(l10n: l10n),
            const SizedBox(height: 24),
            _BottomControls(
              isAnalyzing: isAnalyzing,
              onCapture: onCapture,
              onManual: onManual,
              l10n: l10n,
            ),
            const SizedBox(height: 40),
          ],
        ),
      ],
    );
  }
}

class _ViewfinderFrame extends StatelessWidget {
  final bool isAnalyzing;
  final AppStrings l10n;
  const _ViewfinderFrame({required this.isAnalyzing, required this.l10n});

  @override
  Widget build(BuildContext context) {
    const size = 260.0;
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        fit: StackFit.expand,
        children: [
          Container(
            decoration: BoxDecoration(
              border: Border.all(
                color: isAnalyzing ? AppColors.secondary : AppColors.primary,
                width: 2.5,
              ),
              borderRadius: BorderRadius.circular(20),
            ),
          ),
          ..._corners(),
          if (isAnalyzing)
            Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const CircularProgressIndicator(
                    color: AppColors.secondary,
                    strokeWidth: 2.5,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    l10n.analysing,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          if (!isAnalyzing)
            Center(
              child: Icon(
                Icons.restaurant_outlined,
                size: 64,
                color: Colors.white.withValues(alpha: 0.2),
              ),
            ),
        ],
      ),
    );
  }

  List<Widget> _corners() {
    const thick = 3.5;
    const len = 24.0;
    final color = isAnalyzing ? AppColors.secondary : AppColors.primary;
    Widget corner(AlignmentGeometry align, BorderRadius br) => Align(
          alignment: align,
          child: Container(
            width: len,
            height: len,
            decoration: BoxDecoration(
              border: Border(
                top: br.topLeft != Radius.zero
                    ? BorderSide(color: color, width: thick)
                    : BorderSide.none,
                left: br.topLeft != Radius.zero
                    ? BorderSide(color: color, width: thick)
                    : BorderSide.none,
                bottom: br.bottomLeft != Radius.zero
                    ? BorderSide(color: color, width: thick)
                    : BorderSide.none,
                right: br.topRight != Radius.zero
                    ? BorderSide(color: color, width: thick)
                    : BorderSide.none,
              ),
              borderRadius: br,
            ),
          ),
        );

    return [
      corner(Alignment.topLeft,
          const BorderRadius.only(topLeft: Radius.circular(6))),
      corner(Alignment.topRight,
          const BorderRadius.only(topRight: Radius.circular(6))),
      corner(Alignment.bottomLeft,
          const BorderRadius.only(bottomLeft: Radius.circular(6))),
      corner(Alignment.bottomRight,
          const BorderRadius.only(bottomRight: Radius.circular(6))),
    ];
  }
}

class _TipBanner extends StatelessWidget {
  final AppStrings l10n;
  const _TipBanner({required this.l10n});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 32),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.tips_and_updates_outlined,
              size: 18, color: AppColors.primary),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              l10n.scanTip,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _BottomControls extends StatelessWidget {
  final bool isAnalyzing;
  final VoidCallback onCapture;
  final VoidCallback onManual;
  final AppStrings l10n;

  const _BottomControls({
    required this.isAnalyzing,
    required this.onCapture,
    required this.onManual,
    required this.l10n,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        GestureDetector(
          onTap: isAnalyzing ? null : onCapture,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: 76,
            height: 76,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isAnalyzing
                  ? Colors.white.withValues(alpha: 0.15)
                  : Colors.white,
              border: Border.all(
                color: isAnalyzing ? Colors.grey : AppColors.primary,
                width: 3,
              ),
            ),
            child: Icon(
              Icons.camera_alt,
              size: 32,
              color: isAnalyzing ? Colors.grey : AppColors.primary,
            ),
          ),
        ),
        const SizedBox(height: 20),
        TextButton(
          onPressed: onManual,
          child: Text(
            l10n.searchManually,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.6),
              fontSize: 13,
            ),
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Permission denied view
// ─────────────────────────────────────────────────────────────────────────────

class _PermissionDeniedView extends StatelessWidget {
  final AppStrings l10n;
  const _PermissionDeniedView({required this.l10n});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.no_photography_outlined,
                size: 64, color: Colors.white54),
            const SizedBox(height: 20),
            Text(
              l10n.permissionDenied,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              l10n.cameraPermission,
              style: const TextStyle(color: Colors.white60, fontSize: 14),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 28),
            ElevatedButton.icon(
              onPressed: openAppSettings,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                padding:
                    const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
              icon: const Icon(Icons.settings_outlined),
              label: Text(l10n.openSettings),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Error view
// ─────────────────────────────────────────────────────────────────────────────

class _ErrorView extends StatelessWidget {
  final String? message;
  final VoidCallback onRetry;
  final AppStrings l10n;

  const _ErrorView({this.message, required this.onRetry, required this.l10n});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.redAccent),
            const SizedBox(height: 20),
            Text(
              l10n.error,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              message ?? l10n.tryAgain,
              style: const TextStyle(color: Colors.white54, fontSize: 13),
              textAlign: TextAlign.center,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 28),
            ElevatedButton.icon(
              onPressed: onRetry,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                padding:
                    const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
              icon: const Icon(Icons.refresh),
              label: Text(l10n.tryAgain),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// No-results view — includes inline manual search
// ─────────────────────────────────────────────────────────────────────────────

// Labels we consider too generic to pre-populate the search field with.
const _genericLabels = {
  'food', 'dish', 'meal', 'ingredient', 'cuisine', 'recipe',
  'tableware', 'plate', 'bowl', 'cup', 'glass', 'mug', 'container',
  'table', 'kitchen', 'restaurant', 'dining',
  'photography', 'still life', 'product', 'object', 'material',
  'serving', 'portion', 'cooking', 'baking',
  'yellow', 'red', 'green', 'brown', 'white', 'orange', 'golden',
};

class _NoResultsView extends ConsumerStatefulWidget {
  final List<String> labels;
  final VoidCallback onRetry;
  final String mealType;
  final VoidCallback onFoodAdded;
  final AppStrings l10n;

  const _NoResultsView({
    required this.labels,
    required this.onRetry,
    required this.mealType,
    required this.onFoodAdded,
    required this.l10n,
  });

  @override
  ConsumerState<_NoResultsView> createState() => _NoResultsViewState();
}

class _NoResultsViewState extends ConsumerState<_NoResultsView> {
  late final TextEditingController _searchCtrl;
  List<FoodItem> _searchResults = [];
  FoodItem? _selected;
  late String _mealType;

  // Portion state
  double _multiplier = 1.0;
  bool _useCustom = false;
  final _customCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _mealType = widget.mealType;

    // Pre-populate with the first 1-2 meaningful detected labels.
    final meaningful = widget.labels
        .map((l) => l.toLowerCase().trim())
        .where((l) => l.isNotEmpty && !_genericLabels.contains(l))
        .take(2)
        .toList();
    final initialQuery = meaningful.join(' ');
    _searchCtrl = TextEditingController(text: initialQuery);

    if (initialQuery.isNotEmpty) {
      _runSearch(initialQuery);
    }
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    _customCtrl.dispose();
    super.dispose();
  }

  void _runSearch(String q) {
    final results = LocalFoodRepository.search(q.trim(), limit: 8);
    setState(() {
      _searchResults = results;
      _selected = null;
      _multiplier = 1.0;
      _useCustom = false;
      _customCtrl.clear();
    });
  }

  double get _quantityG {
    if (_selected == null) return 0;
    if (_useCustom) {
      return double.tryParse(_customCtrl.text) ?? _selected!.servingSize;
    }
    return (_selected!.servingSize * _multiplier).roundToDouble();
  }

  double get _scaledCalories {
    if (_selected == null) return 0;
    return _selected!.calories * (_quantityG / _selected!.servingSize);
  }

  Future<void> _addFood() async {
    if (_selected == null) return;
    final qty = _quantityG;
    if (qty <= 0) return;
    await ref
        .read(mealProvider.notifier)
        .addFood(_selected!, _mealType, qty);
    ref.read(dashboardProvider.notifier).refresh();
    widget.onFoodAdded();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = widget.l10n;
    final theme = Theme.of(context);

    final meals = [
      ('breakfast', l10n.breakfast, Icons.wb_sunny_outlined),
      ('lunch', l10n.lunch, Icons.lunch_dining_outlined),
      ('dinner', l10n.dinner, Icons.dinner_dining_outlined),
      ('snack', l10n.snack, Icons.cookie_outlined),
    ];

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 24, 24, 40),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          const Center(
            child: Icon(Icons.image_search_outlined,
                size: 56, color: Colors.white38),
          ),
          const SizedBox(height: 16),
          Center(
            child: Text(
              l10n.foodNotIdentified,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 6),
          Center(
            child: Text(
              l10n.tryBetterLighting,
              style: const TextStyle(color: Colors.white54, fontSize: 13),
              textAlign: TextAlign.center,
            ),
          ),
          if (widget.labels.isNotEmpty) ...[
            const SizedBox(height: 14),
            _DetectedLabelChips(labels: widget.labels),
          ],
          const SizedBox(height: 20),

          // Retry button
          Center(
            child: OutlinedButton.icon(
              onPressed: widget.onRetry,
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.white70,
                side: const BorderSide(color: Colors.white24),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
                padding: const EdgeInsets.symmetric(
                    horizontal: 20, vertical: 10),
              ),
              icon: const Icon(Icons.camera_alt_outlined, size: 16),
              label: Text(l10n.takeAnotherPhoto),
            ),
          ),
          const SizedBox(height: 28),

          // Search section
          Text(
            l10n.searchFood,
            style: theme.textTheme.titleSmall?.copyWith(
              color: Colors.white,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _searchCtrl,
            onChanged: _runSearch,
            style: const TextStyle(color: Colors.white),
            decoration: InputDecoration(
              hintText: l10n.searchFoodHint,
              hintStyle: const TextStyle(color: Colors.white38),
              prefixIcon:
                  const Icon(Icons.search, color: Colors.white38),
              filled: true,
              fillColor: Colors.white.withValues(alpha: 0.08),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
              contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16, vertical: 12),
            ),
          ),

          // Search results
          if (_searchResults.isNotEmpty) ...[
            const SizedBox(height: 8),
            ..._searchResults.map((food) {
              final isSelected = _selected?.id == food.id;
              final lang = l10n.language;
              return _FoodSuggestionTile(
                food: food,
                isSelected: isSelected,
                lang: lang,
                onTap: () => setState(() {
                  _selected = food;
                  _multiplier = 1.0;
                  _useCustom = false;
                  _customCtrl.clear();
                }),
              );
            }),
          ] else if (_searchCtrl.text.trim().isNotEmpty) ...[
            const SizedBox(height: 16),
            Center(
              child: Text(
                l10n.noResults,
                style: const TextStyle(color: Colors.white38, fontSize: 13),
              ),
            ),
          ],

          // Meal type + portion + confirm — shown once a food is selected
          if (_selected != null) ...[
            const SizedBox(height: 20),
            const Divider(color: Colors.white12),
            const SizedBox(height: 12),

            // Meal type chips
            Text(
              l10n.addTo,
              style: theme.textTheme.titleSmall?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: meals.map((m) {
                  final active = m.$1 == _mealType;
                  return Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      avatar: Icon(m.$3,
                          size: 16,
                          color: active ? Colors.white : AppColors.primary),
                      label: Text(m.$2),
                      selected: active,
                      selectedColor: AppColors.primary,
                      labelStyle: TextStyle(
                        color: active ? Colors.white : null,
                        fontSize: 12,
                      ),
                      visualDensity: VisualDensity.compact,
                      onSelected: (_) =>
                          setState(() => _mealType = m.$1),
                    ),
                  );
                }).toList(),
              ),
            ),
            const SizedBox(height: 16),

            // Portion selector
            _PortionSelector(
              food: _selected!,
              multiplier: _multiplier,
              useCustom: _useCustom,
              customCtrl: _customCtrl,
              scaledCalories: _scaledCalories,
              quantityG: _quantityG,
              l10n: l10n,
              onMultiplierChanged: (m) => setState(() {
                _multiplier = m;
                _useCustom = false;
                _customCtrl.clear();
              }),
              onCustomSelected: () => setState(() => _useCustom = true),
              onCustomChanged: (_) => setState(() {}),
            ),
            const SizedBox(height: 16),

            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _addFood,
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  foregroundColor: Colors.white,
                  padding:
                      const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14)),
                ),
                icon: const Icon(Icons.add_circle_outline),
                label: Text(
                  '${l10n.addToMeal}  •  '
                  '${_scaledCalories.toStringAsFixed(0)} kcal',
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _DetectedLabelChips extends StatelessWidget {
  final List<String> labels;
  const _DetectedLabelChips({required this.labels});

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 6,
      runSpacing: 6,
      alignment: WrapAlignment.center,
      children: labels.take(6).map((l) {
        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: Colors.white.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            l,
            style: const TextStyle(color: Colors.white60, fontSize: 12),
          ),
        );
      }).toList(),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Food suggestion bottom sheet
// ─────────────────────────────────────────────────────────────────────────────

class _FoodSuggestionSheet extends ConsumerStatefulWidget {
  final List<FoodItem> suggestions;
  final String initialMealType;
  final VoidCallback onFoodAdded;
  final VoidCallback onRetry;

  const _FoodSuggestionSheet({
    required this.suggestions,
    required this.initialMealType,
    required this.onFoodAdded,
    required this.onRetry,
  });

  @override
  ConsumerState<_FoodSuggestionSheet> createState() =>
      _FoodSuggestionSheetState();
}

class _FoodSuggestionSheetState
    extends ConsumerState<_FoodSuggestionSheet> {
  FoodItem? _selected;
  String _mealType = 'snack';

  double _multiplier = 1.0;
  bool _useCustom = false;
  final _customCtrl = TextEditingController();

  // Inline search state
  bool _searchExpanded = false;
  final _searchCtrl = TextEditingController();
  List<FoodItem> _searchResults = [];

  @override
  void initState() {
    super.initState();
    _mealType = widget.initialMealType;
  }

  @override
  void dispose() {
    _customCtrl.dispose();
    _searchCtrl.dispose();
    super.dispose();
  }

  double get _quantityG {
    if (_selected == null) return 0;
    if (_useCustom) {
      return double.tryParse(_customCtrl.text) ?? _selected!.servingSize;
    }
    return (_selected!.servingSize * _multiplier).roundToDouble();
  }

  double get _scaledCalories {
    if (_selected == null) return 0;
    return _selected!.calories * (_quantityG / _selected!.servingSize);
  }

  Future<void> _confirm() async {
    if (_selected == null) return;
    final qty = _quantityG;
    if (qty <= 0) return;
    await ref.read(mealProvider.notifier).addFood(_selected!, _mealType, qty);
    ref.read(dashboardProvider.notifier).refresh();
    widget.onFoodAdded();
  }

  void _selectFood(FoodItem food) {
    setState(() {
      _selected = food;
      _multiplier = 1.0;
      _useCustom = false;
      _customCtrl.clear();
    });
  }

  void _runSearch(String q) {
    final results = LocalFoodRepository.search(q.trim(), limit: 8);
    setState(() => _searchResults = results);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = ref.watch(appStringsProvider);
    final theme = Theme.of(context);

    return DraggableScrollableSheet(
      initialChildSize: 0.65,
      minChildSize: 0.45,
      maxChildSize: 0.95,
      builder: (context, scrollCtrl) {
        return Container(
          decoration: BoxDecoration(
            color: theme.colorScheme.surface,
            borderRadius:
                const BorderRadius.vertical(top: Radius.circular(24)),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.3),
                blurRadius: 20,
              )
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const _SheetHandle(),
              _SheetHeader(
                mealType: _mealType,
                onMealTypeChanged: (m) => setState(() => _mealType = m),
                l10n: l10n,
                theme: theme,
              ),
              const Divider(height: 1),
              Expanded(
                child: ListView(
                  controller: scrollCtrl,
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                  children: [
                    // Suggestion tiles from ML Kit
                    ...widget.suggestions.map((food) {
                      final isSelected = _selected?.id == food.id;
                      return _FoodSuggestionTile(
                        food: food,
                        isSelected: isSelected,
                        lang: l10n.language,
                        onTap: () => _selectFood(food),
                      );
                    }),

                    // Retry button
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: TextButton.icon(
                        onPressed: widget.onRetry,
                        icon: const Icon(Icons.camera_alt_outlined, size: 16),
                        label: Text(l10n.takeAnotherPhoto),
                      ),
                    ),

                    // Collapsible inline search section
                    _InlineSearchSection(
                      expanded: _searchExpanded,
                      searchCtrl: _searchCtrl,
                      searchResults: _searchResults,
                      selected: _selected,
                      lang: l10n.language,
                      l10n: l10n,
                      onToggle: () => setState(
                          () => _searchExpanded = !_searchExpanded),
                      onSearch: _runSearch,
                      onFoodSelected: _selectFood,
                    ),

                    // Portion selector + confirm
                    if (_selected != null) ...[
                      const Divider(),
                      _PortionSelector(
                        food: _selected!,
                        multiplier: _multiplier,
                        useCustom: _useCustom,
                        customCtrl: _customCtrl,
                        scaledCalories: _scaledCalories,
                        quantityG: _quantityG,
                        l10n: l10n,
                        onMultiplierChanged: (m) => setState(() {
                          _multiplier = m;
                          _useCustom = false;
                          _customCtrl.clear();
                        }),
                        onCustomSelected: () =>
                            setState(() => _useCustom = true),
                        onCustomChanged: (_) => setState(() {}),
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: _confirm,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.primary,
                            foregroundColor: Colors.white,
                            padding:
                                const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14),
                            ),
                          ),
                          icon: const Icon(Icons.add_circle_outline),
                          label: Text(
                            '${l10n.addToMeal}  •  '
                            '${_scaledCalories.toStringAsFixed(0)} kcal',
                            style: const TextStyle(
                                fontWeight: FontWeight.w600),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Inline search section (collapsible, used inside suggestion sheet)
// ─────────────────────────────────────────────────────────────────────────────

class _InlineSearchSection extends StatelessWidget {
  final bool expanded;
  final TextEditingController searchCtrl;
  final List<FoodItem> searchResults;
  final FoodItem? selected;
  final String lang;
  final AppStrings l10n;
  final VoidCallback onToggle;
  final ValueChanged<String> onSearch;
  final ValueChanged<FoodItem> onFoodSelected;

  const _InlineSearchSection({
    required this.expanded,
    required this.searchCtrl,
    required this.searchResults,
    required this.selected,
    required this.lang,
    required this.l10n,
    required this.onToggle,
    required this.onSearch,
    required this.onFoodSelected,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Tappable header that expands/collapses the section
        InkWell(
          onTap: onToggle,
          borderRadius: BorderRadius.circular(10),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Row(
              children: [
                const Icon(Icons.search,
                    size: 18, color: AppColors.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    l10n.notYourFood,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: AppColors.primary,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Icon(
                  expanded
                      ? Icons.keyboard_arrow_up
                      : Icons.keyboard_arrow_down,
                  color: AppColors.primary,
                  size: 20,
                ),
              ],
            ),
          ),
        ),

        if (expanded) ...[
          const SizedBox(height: 6),
          TextField(
            controller: searchCtrl,
            onChanged: onSearch,
            decoration: InputDecoration(
              hintText: l10n.searchHintSheet,
              prefixIcon:
                  const Icon(Icons.search, size: 18),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              isDense: true,
              contentPadding: const EdgeInsets.symmetric(
                  horizontal: 14, vertical: 10),
            ),
          ),
          if (searchResults.isNotEmpty) ...[
            const SizedBox(height: 4),
            ...searchResults.map((food) {
              final isSelected = selected?.id == food.id;
              return _FoodSuggestionTile(
                food: food,
                isSelected: isSelected,
                lang: lang,
                onTap: () => onFoodSelected(food),
              );
            }),
          ] else if (searchCtrl.text.trim().isNotEmpty) ...[
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 10),
              child: Center(
                child: Text(
                  l10n.noResults,
                  style: const TextStyle(color: Colors.grey, fontSize: 13),
                ),
              ),
            ),
          ],
        ],
      ],
    );
  }
}

// ── Sheet sub-widgets ─────────────────────────────────────────────────────────

class _SheetHandle extends StatelessWidget {
  const _SheetHandle();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        margin: const EdgeInsets.only(top: 10, bottom: 4),
        width: 40,
        height: 4,
        decoration: BoxDecoration(
          color: Colors.grey.shade300,
          borderRadius: BorderRadius.circular(2),
        ),
      ),
    );
  }
}

class _SheetHeader extends StatelessWidget {
  final String mealType;
  final ValueChanged<String> onMealTypeChanged;
  final AppStrings l10n;
  final ThemeData theme;

  const _SheetHeader({
    required this.mealType,
    required this.onMealTypeChanged,
    required this.l10n,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    final meals = [
      ('breakfast', l10n.breakfast, Icons.wb_sunny_outlined),
      ('lunch', l10n.lunch, Icons.lunch_dining_outlined),
      ('dinner', l10n.dinner, Icons.dinner_dining_outlined),
      ('snack', l10n.snack, Icons.cookie_outlined),
    ];

    return Padding(
      padding: const EdgeInsets.fromLTRB(20, 8, 20, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.restaurant,
                  color: AppColors.primary, size: 20),
              const SizedBox(width: 8),
              Text(
                l10n.didYouEat,
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.w700),
              ),
            ],
          ),
          const SizedBox(height: 10),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: meals.map((m) {
                final active = m.$1 == mealType;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    avatar: Icon(m.$3,
                        size: 16,
                        color:
                            active ? Colors.white : AppColors.primary),
                    label: Text(m.$2),
                    selected: active,
                    selectedColor: AppColors.primary,
                    labelStyle: TextStyle(
                      color: active ? Colors.white : null,
                      fontSize: 12,
                    ),
                    visualDensity: VisualDensity.compact,
                    onSelected: (_) => onMealTypeChanged(m.$1),
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
}

class _FoodSuggestionTile extends StatelessWidget {
  final FoodItem food;
  final bool isSelected;
  final String lang;
  final VoidCallback onTap;

  const _FoodSuggestionTile({
    required this.food,
    required this.isSelected,
    required this.lang,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final displayName = food.displayName(lang);
    final subName =
        lang != 'bn' && food.nameBn != null && food.nameBn!.isNotEmpty
            ? food.nameBn!
            : null;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      margin: const EdgeInsets.symmetric(vertical: 4),
      decoration: BoxDecoration(
        color: isSelected
            ? AppColors.primary.withValues(alpha: 0.1)
            : theme.colorScheme.surfaceContainerHighest
                .withValues(alpha: 0.4),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isSelected ? AppColors.primary : Colors.transparent,
          width: 1.5,
        ),
      ),
      child: ListTile(
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 14, vertical: 4),
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: isSelected
                ? AppColors.primary.withValues(alpha: 0.2)
                : AppColors.primary.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            _categoryIcon(food.category),
            color: AppColors.primary,
            size: 22,
          ),
        ),
        title: Text(
          displayName,
          style: theme.textTheme.bodyMedium
              ?.copyWith(fontWeight: FontWeight.w600),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: subName != null
            ? Text(
                subName,
                style: theme.textTheme.bodySmall
                    ?.copyWith(color: Colors.grey),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              )
            : Text(
                food.category ?? '',
                style: theme.textTheme.bodySmall,
              ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              '${food.calories.toStringAsFixed(0)} kcal',
              style: theme.textTheme.bodySmall
                  ?.copyWith(color: AppColors.calories),
            ),
            const SizedBox(width: 6),
            Icon(
              isSelected
                  ? Icons.check_circle
                  : Icons.radio_button_unchecked,
              color: isSelected ? AppColors.primary : Colors.grey.shade400,
              size: 22,
            ),
          ],
        ),
        onTap: onTap,
      ),
    );
  }

  IconData _categoryIcon(String? cat) {
    return switch (cat) {
      'rice' => Icons.rice_bowl_outlined,
      'fish' => Icons.set_meal_outlined,
      'meat' || 'protein' => Icons.kebab_dining_outlined,
      'vegetable' => Icons.eco_outlined,
      'fruit' => Icons.apple_outlined,
      'dairy' => Icons.local_drink_outlined,
      'bread' || 'roti' => Icons.breakfast_dining_outlined,
      'sweets' || 'dessert' => Icons.cake_outlined,
      'beverage' => Icons.local_cafe_outlined,
      'snack' => Icons.cookie_outlined,
      'egg' => Icons.egg_outlined,
      'oil' => Icons.opacity_outlined,
      _ => Icons.restaurant_outlined,
    };
  }
}

// ── Portion selector ──────────────────────────────────────────────────────────

class _PortionSelector extends StatelessWidget {
  final FoodItem food;
  final double multiplier;
  final bool useCustom;
  final TextEditingController customCtrl;
  final double scaledCalories;
  final double quantityG;
  final ValueChanged<double> onMultiplierChanged;
  final VoidCallback onCustomSelected;
  final ValueChanged<String> onCustomChanged;
  final AppStrings l10n;

  const _PortionSelector({
    required this.food,
    required this.multiplier,
    required this.useCustom,
    required this.customCtrl,
    required this.scaledCalories,
    required this.quantityG,
    required this.onMultiplierChanged,
    required this.onCustomSelected,
    required this.onCustomChanged,
    required this.l10n,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    final portions = [
      (0.5, l10n.portionSmall, '½ serv'),
      (1.0, l10n.portionMedium, '1 serv'),
      (1.5, l10n.portionLarge, '1½ serv'),
      (2.0, l10n.portionXl, '2 serv'),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 12),
        Text(
          l10n.howMuch,
          style:
              theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            ...portions.map((p) {
              final active = !useCustom && multiplier == p.$1;
              final grams = (food.servingSize * p.$1).roundToDouble();
              return _PortionChip(
                label: p.$2,
                sublabel: '${grams.toStringAsFixed(0)}g',
                active: active,
                onTap: () => onMultiplierChanged(p.$1),
              );
            }),
            _PortionChip(
              label: l10n.portionCustom,
              sublabel:
                  useCustom ? '${quantityG.toStringAsFixed(0)}g' : '',
              active: useCustom,
              onTap: onCustomSelected,
            ),
          ],
        ),
        if (useCustom) ...[
          const SizedBox(height: 10),
          TextField(
            controller: customCtrl,
            keyboardType:
                const TextInputType.numberWithOptions(decimal: true),
            autofocus: true,
            onChanged: onCustomChanged,
            decoration: InputDecoration(
              labelText: l10n.enterGrams,
              suffixText: 'g',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              isDense: true,
              contentPadding: const EdgeInsets.symmetric(
                  horizontal: 14, vertical: 10),
            ),
          ),
        ],
        const SizedBox(height: 10),
        _NutritionPreview(food: food, quantityG: quantityG),
      ],
    );
  }
}

class _PortionChip extends StatelessWidget {
  final String label;
  final String sublabel;
  final bool active;
  final VoidCallback onTap;

  const _PortionChip({
    required this.label,
    required this.sublabel,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: active
              ? AppColors.primary
              : AppColors.primary.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: active
                ? AppColors.primary
                : AppColors.primary.withValues(alpha: 0.3),
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              label,
              style: TextStyle(
                color: active ? Colors.white : AppColors.primary,
                fontWeight: FontWeight.w600,
                fontSize: 13,
              ),
            ),
            if (sublabel.isNotEmpty)
              Text(
                sublabel,
                style: TextStyle(
                  color: active
                      ? Colors.white.withValues(alpha: 0.8)
                      : AppColors.primary.withValues(alpha: 0.7),
                  fontSize: 11,
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _NutritionPreview extends StatelessWidget {
  final FoodItem food;
  final double quantityG;

  const _NutritionPreview({required this.food, required this.quantityG});

  @override
  Widget build(BuildContext context) {
    if (quantityG <= 0) return const SizedBox.shrink();
    final f = food.scaledTo(quantityG);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.primary.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _MacroPill(
              'Cal', f.calories.toStringAsFixed(0), AppColors.calories),
          _MacroPill(
              'P', '${f.proteinG.toStringAsFixed(1)}g', AppColors.protein),
          _MacroPill(
              'C', '${f.carbsG.toStringAsFixed(1)}g', AppColors.carbs),
          _MacroPill('F', '${f.fatG.toStringAsFixed(1)}g', AppColors.fat),
        ],
      ),
    );
  }
}

class _MacroPill extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _MacroPill(this.label, this.value, this.color);

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          value,
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.w700,
            fontSize: 14,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.grey,
            fontSize: 11,
          ),
        ),
      ],
    );
  }
}
