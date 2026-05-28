import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../localization/strings_provider.dart';
import '../../localization/app_localizations.dart';
import '../../theme/app_colors.dart';
import '../../widgets/charts/macro_ring_chart.dart';
import '../../widgets/common/nutrition_progress_bar.dart';
import '../../models/nutrition_goals.dart';
import '../../core/constants/nutrition_constants.dart';
import '../dashboard/providers/dashboard_provider.dart';
import '../meal_tracking/providers/meal_provider.dart';
import '../../services/recommendation_engine.dart';

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(dashboardProvider);
    final l10n = ref.watch(appStringsProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      body: CustomScrollView(
        physics: const BouncingScrollPhysics(),
        slivers: [
          SliverAppBar(
            toolbarHeight: 72,
            floating: true,
            pinned: false,
            automaticallyImplyLeading: false,
            titleSpacing: 16,
            backgroundColor: theme.scaffoldBackgroundColor,
            title: Row(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Image.asset(
                  'assets/images/healthtrackerlogo.png',
                  width: 32,
                  height: 32,
                  fit: BoxFit.contain,
                ),
                const SizedBox(width: 9),
                Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.appName,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: AppColors.primary,
                        fontSize: 15,
                      ),
                    ),
                    Text(
                      l10n.tagline,
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: AppColors.primary.withValues(alpha: 0.65),
                        fontSize: 10,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                _DateSelector(state: state),
                const SizedBox(height: 16),
                _RecommendationCard(state: state),
                const SizedBox(height: 16),
                _CalorieCard(state: state),
                const SizedBox(height: 16),
                _MacrosRow(state: state),
                const SizedBox(height: 16),
                _MealSummarySection(state: state),
                const SizedBox(height: 16),
                _WaterFiberCard(state: state),
                const SizedBox(height: 16),
                _DailySummaryCard(state: state),
                const SizedBox(height: 80),
              ]),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.go('/meals'),
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add),
        label: Text(l10n.addFood),
      ),
    );
  }
}

class _DateSelector extends ConsumerWidget {
  final DashboardState state;
  const _DateSelector({required this.state});

  Future<void> _pickDate(BuildContext context, WidgetRef ref) async {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final parts = state.selectedDateKey.split('_');
    final current = parts.length == 3
        ? DateTime(int.parse(parts[0]), int.parse(parts[1]), int.parse(parts[2]))
        : today;

    final picked = await showDatePicker(
      context: context,
      initialDate: current,
      firstDate: DateTime(2020),
      lastDate: today,
      helpText: ref.read(appStringsProvider).isBengali
          ? 'তারিখ বেছে নিন'
          : 'Select Date',
    );
    if (picked == null) return;
    ref.read(dashboardProvider.notifier).selectDate(picked);
    ref.read(mealProvider.notifier).setDate(picked);
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final l10n = ref.watch(appStringsProvider);

    final parts = state.selectedDateKey.split('_');
    final selected = parts.length == 3
        ? DateTime(int.parse(parts[0]), int.parse(parts[1]), int.parse(parts[2]))
        : today;
    final isToday = selected.year == today.year &&
        selected.month == today.month &&
        selected.day == today.day;

    final label = isToday
        ? l10n.today
        : '${selected.day}/${selected.month}/${selected.year}';

    return GestureDetector(
      onTap: () => _pickDate(context, ref),
      child: Row(
        children: [
          Text(
            label,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.w700,
                  color: isToday ? null : AppColors.secondary,
                ),
          ),
          const SizedBox(width: 6),
          Icon(
            Icons.calendar_month_outlined,
            size: 18,
            color: isToday ? Colors.grey : AppColors.secondary,
          ),
          const Spacer(),
          if (!isToday)
            GestureDetector(
              onTap: () {
                ref.read(dashboardProvider.notifier).selectDate(today);
                ref.read(mealProvider.notifier).setDate(today);
              },
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  l10n.today,
                  style: TextStyle(
                    color: AppColors.primary,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            )
          else
            Text(
              '${now.day}/${now.month}/${now.year}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Recommendation Card
// ═══════════════════════════════════════════════════════════════════════════

class _RecommendationCard extends ConsumerStatefulWidget {
  final DashboardState state;
  const _RecommendationCard({required this.state});

  @override
  ConsumerState<_RecommendationCard> createState() => _RecommendationCardState();
}

class _RecommendationCardState extends ConsumerState<_RecommendationCard>
    with SingleTickerProviderStateMixin {
  bool _expanded = false;
  late final AnimationController _animCtrl;
  late final Animation<double> _expandAnim;

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 280));
    _expandAnim = CurvedAnimation(parent: _animCtrl, curve: Curves.easeInOut);
  }

  @override
  void dispose() {
    _animCtrl.dispose();
    super.dispose();
  }

  void _toggle() {
    setState(() => _expanded = !_expanded);
    _expanded ? _animCtrl.forward() : _animCtrl.reverse();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = ref.watch(appStringsProvider);
    final lang = l10n.language;
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final rec = RecommendationEngine.analyze(
      goals: widget.state.goals ?? NutritionGoals.defaults,
      meals: widget.state.todaysMeals,
      lang: lang,
    );

    final bn = lang == 'bn';
    final stepsDisplay = ((rec.walkingSteps / 500).round() * 500);
    final minsDisplay  = ((rec.walkingMinutes / 5).round() * 5).clamp(10, 90);

    final cardBg = isDark
        ? const Color(0xFF1A2535)
        : const Color(0xFFF0F9F4);
    final accentColor = const Color(0xFF27AE60);
    final borderColor = isDark
        ? const Color(0xFF2D4A3A)
        : const Color(0xFFB2DFCE);

    return Container(
      decoration: BoxDecoration(
        color: cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor, width: 1.2),
        boxShadow: isDark
            ? null
            : [
                BoxShadow(
                  color: accentColor.withValues(alpha: 0.08),
                  blurRadius: 10,
                  offset: const Offset(0, 3),
                ),
              ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          onTap: _toggle,
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Header row ─────────────────────────────────────────────
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: accentColor.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(Icons.tips_and_updates_rounded,
                          color: accentColor, size: 18),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        bn ? 'আজকের পরামর্শ' : 'Today\'s Insight',
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                          color: accentColor,
                        ),
                      ),
                    ),
                    AnimatedRotation(
                      turns: _expanded ? 0.5 : 0.0,
                      duration: const Duration(milliseconds: 280),
                      child: Icon(Icons.expand_more_rounded,
                          color: accentColor, size: 20),
                    ),
                  ],
                ),

                const SizedBox(height: 12),

                // ── Daily tip (always visible) ─────────────────────────────
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: accentColor.withValues(alpha: 0.08),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('💡', style: const TextStyle(fontSize: 16)),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          rec.dailyTip,
                          style: theme.textTheme.bodyMedium?.copyWith(
                            height: 1.45,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 10),

                // ── Compact stats row (always visible) ────────────────────
                Row(
                  children: [
                    _StatChip(
                      icon: Icons.local_fire_department_rounded,
                      color: AppColors.calories,
                      label: '${rec.consumedCalories.toStringAsFixed(0)}/'
                          '${rec.targetCalories.toStringAsFixed(0)} kcal',
                    ),
                    const SizedBox(width: 8),
                    if (rec.consumedCalories > 50)
                      _StatChip(
                        icon: Icons.directions_walk_rounded,
                        color: accentColor,
                        label: bn
                            ? '~$minsDisplay মিনিট'
                            : '~$minsDisplay min walk',
                      ),
                  ],
                ),

                // ── Expanded section ───────────────────────────────────────
                SizeTransition(
                  sizeFactor: _expandAnim,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (rec.insights.isNotEmpty) ...[
                        const SizedBox(height: 14),
                        _SectionLabel(
                          icon: Icons.bar_chart_rounded,
                          label: bn ? 'আজকের বিশ্লেষণ' : 'Today\'s Analysis',
                          color: accentColor,
                        ),
                        const SizedBox(height: 6),
                        ...rec.insights.map((ins) => _BulletRow(
                              text: ins,
                              theme: theme,
                              color: accentColor,
                            )),
                      ],
                      if (rec.recommendations.isNotEmpty) ...[
                        const SizedBox(height: 14),
                        _SectionLabel(
                          icon: Icons.lightbulb_outline_rounded,
                          label: bn ? 'পরামর্শসমূহ' : 'Recommendations',
                          color: AppColors.primary,
                        ),
                        const SizedBox(height: 6),
                        ...rec.recommendations.map((r) => _BulletRow(
                              text: r,
                              theme: theme,
                              color: AppColors.primary,
                            )),
                      ],
                      if (rec.consumedCalories > 50) ...[
                        const SizedBox(height: 14),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 12, vertical: 10),
                          decoration: BoxDecoration(
                            color: AppColors.primary.withValues(alpha: 0.07),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Row(
                            children: [
                              Icon(Icons.directions_walk_rounded,
                                  color: AppColors.primary, size: 18),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  bn
                                      ? 'প্রায় $minsDisplay মিনিট হাঁটা (~${_fmt(stepsDisplay)} স্টেপ) হজমে সাহায্য করতে পারে।'
                                      : 'Approximately $minsDisplay min walk (~${_fmt(stepsDisplay)} steps) may aid digestion.',
                                  style: theme.textTheme.bodySmall?.copyWith(
                                    color: AppColors.primary,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                      const SizedBox(height: 4),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  String _fmt(int n) {
    if (n >= 1000) return '${(n / 1000).toStringAsFixed(n % 1000 == 0 ? 0 : 1)}k';
    return n.toString();
  }
}

class _StatChip extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String label;
  const _StatChip({required this.icon, required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.25)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13, color: color),
          const SizedBox(width: 4),
          Text(label,
              style: TextStyle(
                  fontSize: 11,
                  color: color,
                  fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  const _SectionLabel(
      {required this.icon, required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 14, color: color),
        const SizedBox(width: 5),
        Text(label,
            style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                color: color)),
      ],
    );
  }
}

class _BulletRow extends StatelessWidget {
  final String text;
  final ThemeData theme;
  final Color color;
  const _BulletRow(
      {required this.text, required this.theme, required this.color});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 5),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 5),
            child: Container(
              width: 5,
              height: 5,
              decoration: BoxDecoration(
                  color: color, shape: BoxShape.circle),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(text,
                style: theme.textTheme.bodySmall?.copyWith(height: 1.45)),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════

class _CalorieCard extends ConsumerWidget {
  final DashboardState state;
  const _CalorieCard({required this.state});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = ref.watch(appStringsProvider);
    final theme = Theme.of(context);
    final goals = state.goals;
    final calorieGoal = goals?.calories ?? 2000;
    final remaining = (calorieGoal - state.totalCalories).clamp(0.0, calorieGoal);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            MacroRingChart(
              calories: state.totalCalories,
              calorieGoal: calorieGoal,
              protein: state.totalProtein,
              carbs: state.totalCarbs,
              fat: state.totalFat,
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _StatRow(label: l10n.consumed, value: '${state.totalCalories.toStringAsFixed(0)} ${l10n.kcal}', color: AppColors.calories),
                  const SizedBox(height: 8),
                  _StatRow(label: l10n.goal, value: '${calorieGoal.toStringAsFixed(0)} ${l10n.kcal}', color: AppColors.primary),
                  const SizedBox(height: 8),
                  _StatRow(label: l10n.remaining, value: '${remaining.toStringAsFixed(0)} ${l10n.kcal}', color: AppColors.secondary),
                  if (goals != null) ...[
                    const SizedBox(height: 12),
                    Text('BMR: ${goals.bmr.toStringAsFixed(0)} kcal', style: theme.textTheme.bodySmall),
                    Text('TDEE: ${goals.tdee.toStringAsFixed(0)} kcal', style: theme.textTheme.bodySmall),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatRow extends StatelessWidget {
  final String label, value;
  final Color color;
  const _StatRow({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        Text(value, style: Theme.of(context).textTheme.bodySmall?.copyWith(color: color, fontWeight: FontWeight.w600)),
      ],
    );
  }
}

class _MacrosRow extends StatelessWidget {
  final DashboardState state;
  const _MacrosRow({required this.state});

  @override
  Widget build(BuildContext context) {
    final goals = state.goals;
    return Consumer(builder: (context, ref, _) {
      final l10n = ref.watch(appStringsProvider);
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(l10n.dailyGoals, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
              const SizedBox(height: 16),
              NutritionProgressBar(
                label: l10n.protein,
                current: state.totalProtein,
                goal: goals?.proteinG ?? 120,
                color: AppColors.protein,
              ),
              const SizedBox(height: 12),
              NutritionProgressBar(
                label: l10n.carbs,
                current: state.totalCarbs,
                goal: goals?.carbsG ?? 225,
                color: AppColors.carbs,
              ),
              const SizedBox(height: 12),
              NutritionProgressBar(
                label: l10n.fat,
                current: state.totalFat,
                goal: goals?.fatG ?? 65,
                color: AppColors.fat,
              ),
            ],
          ),
        ),
      );
    });
  }
}

class _MealSummarySection extends StatelessWidget {
  final DashboardState state;
  const _MealSummarySection({required this.state});

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, _) {
      final l10n = ref.watch(appStringsProvider);
      final meals = [
        ('breakfast', l10n.breakfast, Icons.wb_sunny_outlined),
        ('lunch', l10n.lunch, Icons.lunch_dining_outlined),
        ('dinner', l10n.dinner, Icons.dinner_dining_outlined),
        ('snack', l10n.snack, Icons.cookie_outlined),
      ];

      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(l10n.meals, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 12),
          ...meals.map((m) => _MealCard(
            mealType: m.$1,
            label: m.$2,
            icon: m.$3,
            entries: state.mealsForType(m.$1),
          )),
        ],
      );
    });
  }
}

class _MealCard extends StatelessWidget {
  final String mealType, label;
  final IconData icon;
  final List entries;

  const _MealCard({required this.mealType, required this.label, required this.icon, required this.entries});

  @override
  Widget build(BuildContext context) {
    final totalCals = entries.fold<double>(0, (sum, e) => sum + (e.calories as double));
    return Consumer(builder: (context, ref, _) {
      final l10n = ref.watch(appStringsProvider);
      return Card(
        margin: const EdgeInsets.only(bottom: 8),
        child: ListTile(
          leading: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: AppColors.primary, size: 20),
          ),
          title: Text(label, style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600)),
          subtitle: Text(
            entries.isEmpty ? l10n.tapToAdd : '${entries.length} items',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          trailing: entries.isEmpty
              ? Icon(Icons.add_circle_outline, color: AppColors.primary)
              : Text(
                  '${totalCals.toStringAsFixed(0)} kcal',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.calories,
                    fontWeight: FontWeight.w600,
                  ),
                ),
          onTap: () => context.go('/meals'),
        ),
      );
    });
  }
}

class _WaterFiberCard extends StatelessWidget {
  final DashboardState state;
  const _WaterFiberCard({required this.state});

  @override
  Widget build(BuildContext context) {
    final goals = state.goals;
    return Consumer(builder: (context, ref, _) {
      final l10n = ref.watch(appStringsProvider);
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              NutritionProgressBar(
                label: l10n.fiber,
                current: state.totalFiber,
                goal: goals?.fiberG ?? 38,
                color: AppColors.fiber,
              ),
            ],
          ),
        ),
      );
    });
  }
}

class _DailySummaryCard extends ConsumerWidget {
  final DashboardState state;
  const _DailySummaryCard({required this.state});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = ref.watch(appStringsProvider);
    final goals = state.goals;
    if (goals == null && state.todaysMeals.isEmpty) return const SizedBox.shrink();

    final g = goals ?? NutritionGoals.defaults;
    final calPct = g.calories > 0 ? state.totalCalories / g.calories : 0.0;
    final proteinPct = g.proteinG > 0 ? state.totalProtein / g.proteinG : 0.0;
    final carbsPct = g.carbsG > 0 ? state.totalCarbs / g.carbsG : 0.0;
    final fatPct = g.fatG > 0 ? state.totalFat / g.fatG : 0.0;

    final overCount = [calPct, proteinPct, carbsPct, fatPct].where((p) => p > 1.1).length;
    final goodCount = [calPct, proteinPct, carbsPct, fatPct].where((p) => p >= 0.85 && p <= 1.1).length;

    final (statusText, statusColor) = overCount > 0
        ? (l10n.isBengali ? 'কিছু লক্ষ্য অতিক্রম করেছেন' : 'Some goals exceeded', Colors.orange)
        : goodCount >= 3
            ? (l10n.isBengali ? 'আজকের পুষ্টি চমৎকার!' : 'Great nutrition today!', Colors.green)
            : (l10n.isBengali ? 'লক্ষ্য পূরণ করতে খেতে থাকুন' : 'Keep eating to meet your goals', AppColors.primary);

    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _showSummary(context, l10n),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.bar_chart_rounded, color: AppColors.primary),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(l10n.dailySummary,
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 2),
                    Text(statusText,
                        style: TextStyle(color: statusColor, fontSize: 12)),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: Colors.grey),
            ],
          ),
        ),
      ),
    );
  }

  void _showSummary(BuildContext context, AppStrings l10n) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.7,
        maxChildSize: 0.95,
        minChildSize: 0.4,
        expand: false,
        builder: (_, controller) =>
            _DailySummarySheet(state: state, l10n: l10n, scrollController: controller),
      ),
    );
  }
}

class _DailySummarySheet extends StatelessWidget {
  final DashboardState state;
  final AppStrings l10n;
  final ScrollController scrollController;

  const _DailySummarySheet(
      {required this.state, required this.l10n, required this.scrollController});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final g = state.goals ?? NutritionGoals.defaults;

    return Container(
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          Center(
            child: Container(
              margin: const EdgeInsets.only(top: 12, bottom: 4),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                  color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2)),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
            child: Row(
              children: [
                Text(l10n.dailySummary,
                    style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700)),
                const Spacer(),
                Text(
                  () {
                    final now = DateTime.now();
                    return '${now.day}/${now.month}/${now.year}';
                  }(),
                  style: theme.textTheme.bodySmall,
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: ListView(
              controller: scrollController,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              children: [
                _SummarySection(
                  title: l10n.dailyGoals,
                  rows: [
                    _SummaryRow(label: l10n.calories, consumed: state.totalCalories, goal: g.calories, unit: l10n.kcal, l10n: l10n),
                    _SummaryRow(label: l10n.protein, consumed: state.totalProtein, goal: g.proteinG, unit: l10n.grams, l10n: l10n),
                    _SummaryRow(label: l10n.carbs, consumed: state.totalCarbs, goal: g.carbsG, unit: l10n.grams, l10n: l10n),
                    _SummaryRow(label: l10n.fat, consumed: state.totalFat, goal: g.fatG, unit: l10n.grams, l10n: l10n),
                    _SummaryRow(label: l10n.fiber, consumed: state.totalFiber, goal: g.fiberG, unit: l10n.grams, l10n: l10n),
                  ],
                ),
                if (state.totalCalcium > 0 || state.totalIron > 0 || state.totalVitaminC > 0 || state.totalVitaminA > 0)
                  _SummarySection(
                    title: l10n.micronutrients,
                    rows: [
                      if (state.totalVitaminA > 0)
                        _SummaryRow(label: l10n.vitaminA, consumed: state.totalVitaminA, goal: NutritionConstants.vitaminAMcg, unit: l10n.mcg, l10n: l10n),
                      if (state.totalVitaminB12 > 0)
                        _SummaryRow(label: l10n.vitaminB, consumed: state.totalVitaminB12, goal: NutritionConstants.vitaminB12Mcg, unit: l10n.mcg, l10n: l10n),
                      if (state.totalVitaminC > 0)
                        _SummaryRow(label: l10n.vitaminC, consumed: state.totalVitaminC, goal: NutritionConstants.vitaminCMg, unit: l10n.mg, l10n: l10n),
                      if (state.totalVitaminD > 0)
                        _SummaryRow(label: l10n.vitaminD, consumed: state.totalVitaminD, goal: NutritionConstants.vitaminDMcg, unit: l10n.mcg, l10n: l10n),
                      if (state.totalCalcium > 0)
                        _SummaryRow(label: l10n.calcium, consumed: state.totalCalcium, goal: NutritionConstants.calciumMg, unit: l10n.mg, l10n: l10n),
                      if (state.totalIron > 0)
                        _SummaryRow(label: l10n.iron, consumed: state.totalIron, goal: NutritionConstants.ironForGender(state.userProfile?.gender ?? 'male'), unit: l10n.mg, l10n: l10n),
                      if (state.totalPotassium > 0)
                        _SummaryRow(label: l10n.potassium, consumed: state.totalPotassium, goal: NutritionConstants.potassiumMg, unit: l10n.mg, l10n: l10n),
                      if (state.totalMagnesium > 0)
                        _SummaryRow(label: l10n.magnesium, consumed: state.totalMagnesium, goal: NutritionConstants.magnesiumMg, unit: l10n.mg, l10n: l10n),
                      if (state.totalZinc > 0)
                        _SummaryRow(label: l10n.zinc, consumed: state.totalZinc, goal: NutritionConstants.zincForGender(state.userProfile?.gender ?? 'male'), unit: l10n.mg, l10n: l10n),
                    ],
                  ),
                const SizedBox(height: 16),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SummarySection extends StatelessWidget {
  final String title;
  final List<Widget> rows;
  const _SummarySection({required this.title, required this.rows});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(top: 16, bottom: 8),
          child: Text(title,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w700, color: AppColors.primary)),
        ),
        ...rows,
      ],
    );
  }
}

class _SummaryRow extends StatelessWidget {
  final String label, unit;
  final double consumed, goal;
  final AppStrings l10n;

  const _SummaryRow(
      {required this.label, required this.consumed, required this.goal, required this.unit, required this.l10n});

  @override
  Widget build(BuildContext context) {
    final pct = goal > 0 ? consumed / goal : 0.0;
    final (statusLabel, statusColor) = pct > 1.1
        ? (l10n.statusOver, Colors.red.shade400)
        : pct >= 0.85
            ? (l10n.statusGood, Colors.green.shade600)
            : pct >= 0.5
                ? (l10n.statusLow, Colors.orange.shade700)
                : (l10n.statusVeryLow, Colors.grey.shade500);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 7),
      child: Row(
        children: [
          Expanded(
            flex: 3,
            child: Text(label, style: Theme.of(context).textTheme.bodyMedium),
          ),
          Expanded(
            flex: 4,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${consumed.toStringAsFixed(consumed < 10 ? 1 : 0)} / ${goal.toStringAsFixed(goal < 10 ? 1 : 0)} $unit',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w500),
                ),
                const SizedBox(height: 4),
                ClipRRect(
                  borderRadius: BorderRadius.circular(3),
                  child: LinearProgressIndicator(
                    value: pct.clamp(0.0, 1.0),
                    minHeight: 5,
                    backgroundColor: Colors.grey.shade200,
                    valueColor: AlwaysStoppedAnimation<Color>(statusColor),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: statusColor.withOpacity(0.12),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              statusLabel,
              style: TextStyle(color: statusColor, fontSize: 11, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }
}

