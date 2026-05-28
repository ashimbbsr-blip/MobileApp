import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../localization/app_localizations.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../models/food_item.dart';
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

    // Show suggestion sheet exactly once when ML Kit returns results.
    ref.listen<ScanState>(scanProvider, (_, next) {
      if (next.phase == ScanPhase.done &&
          next.suggestions.isNotEmpty &&
          !_sheetShown) {
        _sheetShown = true;
        _showSuggestions(next.suggestions);
      }
      // Re-arm for a fresh scan after the user retries.
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

  // ── Body dispatcher ───────────────────────────────────────────────────────

  Widget _buildBody(
      BuildContext context, ScanState state, AppStrings l10n) {
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
          onManual: () => context.pop(),
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
          Navigator.of(context).pop(); // close sheet
          context.pop();              // close camera screen
        },
        onRetry: () {
          Navigator.of(context).pop(); // close sheet, return to scan
          _retry();
        },
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Scan-ready view (camera button + tips)
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
        // Background hint
        Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const SizedBox(height: 16),
            // Viewfinder frame
            _ViewfinderFrame(isAnalyzing: isAnalyzing),
            const SizedBox(height: 8),
            // Tips
            _TipBanner(l10n: l10n),
            const SizedBox(height: 24),
            // Shutter + manual search
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
  const _ViewfinderFrame({required this.isAnalyzing});

  @override
  Widget build(BuildContext context) {
    const size = 260.0;
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        fit: StackFit.expand,
        children: [
          // Darkened centre with rounded rect cutout
          Container(
            decoration: BoxDecoration(
              border: Border.all(
                color: isAnalyzing ? AppColors.secondary : AppColors.primary,
                width: 2.5,
              ),
              borderRadius: BorderRadius.circular(20),
            ),
          ),
          // Corner accents
          ..._corners(),
          // Analysing spinner
          if (isAnalyzing)
            const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(
                    color: AppColors.secondary,
                    strokeWidth: 2.5,
                  ),
                  SizedBox(height: 16),
                  Text(
                    'Analysing…',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ),
          // Food icon when idle
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
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.tips_and_updates_outlined,
              size: 18, color: AppColors.primary),
          SizedBox(width: 8),
          Flexible(
            child: Text(
              'Place food in frame, then tap the button',
              style: TextStyle(
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
        // Shutter button
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
            'Search manually instead',
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
                padding: const EdgeInsets.symmetric(
                    horizontal: 28, vertical: 14),
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
              message ?? 'Please try again.',
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
                padding: const EdgeInsets.symmetric(
                    horizontal: 28, vertical: 14),
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
// No-results view
// ─────────────────────────────────────────────────────────────────────────────

class _NoResultsView extends StatelessWidget {
  final List<String> labels;
  final VoidCallback onRetry;
  final VoidCallback onManual;
  final AppStrings l10n;

  const _NoResultsView({
    required this.labels,
    required this.onRetry,
    required this.onManual,
    required this.l10n,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.image_search_outlined,
                size: 64, color: Colors.white38),
            const SizedBox(height: 20),
            const Text(
              'Food not identified',
              style: TextStyle(
                color: Colors.white,
                fontSize: 20,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Try better lighting, closer framing, or search manually.',
              style: TextStyle(color: Colors.white54, fontSize: 13),
              textAlign: TextAlign.center,
            ),
            if (labels.isNotEmpty) ...[
              const SizedBox(height: 16),
              _DetectedLabelChips(labels: labels),
            ],
            const SizedBox(height: 28),
            ElevatedButton.icon(
              onPressed: onRetry,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.primary,
                foregroundColor: Colors.white,
                minimumSize: const Size(200, 48),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
              icon: const Icon(Icons.camera_alt),
              label: const Text('Take another photo'),
            ),
            const SizedBox(height: 12),
            TextButton(
              onPressed: onManual,
              child: const Text(
                'Search manually instead',
                style: TextStyle(color: Colors.white54),
              ),
            ),
          ],
        ),
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
          padding:
              const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
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

  // Portion state
  double _multiplier = 1.0;   // 1.0 = one base serving
  bool _useCustom = false;
  final _customCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _mealType = widget.initialMealType;
  }

  @override
  void dispose() {
    _customCtrl.dispose();
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
              // Handle
              const _SheetHandle(),
              // Header
              _SheetHeader(
                mealType: _mealType,
                onMealTypeChanged: (m) => setState(() => _mealType = m),
                l10n: l10n,
                theme: theme,
              ),
              const Divider(height: 1),
              // Scrollable body
              Expanded(
                child: ListView(
                  controller: scrollCtrl,
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                  children: [
                    // Food suggestion tiles
                    ...widget.suggestions.map((food) {
                      final isSelected = _selected?.id == food.id;
                      return _FoodSuggestionTile(
                        food: food,
                        isSelected: isSelected,
                        lang: l10n.language,
                        onTap: () => setState(() {
                          _selected = food;
                          _multiplier = 1.0;
                          _useCustom = false;
                          _customCtrl.clear();
                        }),
                      );
                    }),
                    // Retry if user doesn't see their food
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: TextButton.icon(
                        onPressed: widget.onRetry,
                        icon: const Icon(Icons.camera_alt_outlined, size: 16),
                        label: const Text('Take another photo'),
                      ),
                    ),
                    // Portion selector — shown only after selection
                    if (_selected != null) ...[
                      const Divider(),
                      _PortionSelector(
                        food: _selected!,
                        multiplier: _multiplier,
                        useCustom: _useCustom,
                        customCtrl: _customCtrl,
                        scaledCalories: _scaledCalories,
                        quantityG: _quantityG,
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
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(14),
                            ),
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
              ),
            ],
          ),
        );
      },
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
              const Icon(Icons.restaurant, color: AppColors.primary, size: 20),
              const SizedBox(width: 8),
              Text(
                'Did you eat:',
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.w700),
              ),
            ],
          ),
          const SizedBox(height: 10),
          // Meal type chips
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
                        color: active ? Colors.white : AppColors.primary),
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
    final subName = lang != 'bn' && food.nameBn != null && food.nameBn!.isNotEmpty
        ? food.nameBn!
        : null;

    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      margin: const EdgeInsets.symmetric(vertical: 4),
      decoration: BoxDecoration(
        color: isSelected
            ? AppColors.primary.withValues(alpha: 0.1)
            : theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.4),
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
              isSelected ? Icons.check_circle : Icons.radio_button_unchecked,
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
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // Predefined serving multiples with user-friendly labels
    const portions = [
      (0.5, 'Small', '½ serv'),
      (1.0, 'Medium', '1 serv'),
      (1.5, 'Large', '1½ serv'),
      (2.0, 'XL', '2 serv'),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 12),
        Text(
          'How much?',
          style: theme.textTheme.titleSmall
              ?.copyWith(fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 8),
        // Serving chips
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            ...portions.map((p) {
              final active = !useCustom && multiplier == p.$1;
              final grams =
                  (food.servingSize * p.$1).roundToDouble();
              return _PortionChip(
                label: p.$2,
                sublabel: '${grams.toStringAsFixed(0)}g',
                active: active,
                onTap: () => onMultiplierChanged(p.$1),
              );
            }),
            // Custom chip
            _PortionChip(
              label: 'Custom',
              sublabel: useCustom ? '${quantityG.toStringAsFixed(0)}g' : '',
              active: useCustom,
              onTap: onCustomSelected,
            ),
          ],
        ),
        // Custom text field — shown when custom is selected
        if (useCustom) ...[
          const SizedBox(height: 10),
          TextField(
            controller: customCtrl,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            autofocus: true,
            onChanged: onCustomChanged,
            decoration: InputDecoration(
              labelText: 'Enter grams',
              suffixText: 'g',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              isDense: true,
              contentPadding:
                  const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            ),
          ),
        ],
        // Live nutrition preview
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
        padding:
            const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: active
              ? AppColors.primary
              : AppColors.primary.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: active ? AppColors.primary : AppColors.primary.withValues(alpha: 0.3),
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
          _MacroPill('Cal', f.calories.toStringAsFixed(0), AppColors.calories),
          _MacroPill('P', '${f.proteinG.toStringAsFixed(1)}g', AppColors.protein),
          _MacroPill('C', '${f.carbsG.toStringAsFixed(1)}g', AppColors.carbs),
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
