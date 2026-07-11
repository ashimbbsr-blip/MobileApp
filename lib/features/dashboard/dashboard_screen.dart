import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../localization/strings_provider.dart';
import '../../localization/app_localizations.dart';
import '../../theme/app_colors.dart';
import '../../widgets/charts/macro_ring_chart.dart';
import '../../widgets/common/nutrition_progress_bar.dart';
import '../../models/meal_entry.dart';
import '../../models/nutrition_goals.dart';
import '../../core/constants/nutrition_constants.dart';
import '../../core/utils/extensions.dart';
import '../dashboard/providers/dashboard_provider.dart';
import '../meal_tracking/providers/meal_provider.dart';
import '../../services/recommendation_engine.dart';
import '../../services/energy_balance_service.dart';
import '../../services/backup/insights_service.dart';

class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({super.key});

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen>
    with WidgetsBindingObserver {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState lifecycle) {
    if (lifecycle == AppLifecycleState.resumed) {
      _syncDateIfChanged();
    }
  }

  void _syncDateIfChanged() {
    final today = DateTime.now().toLogKey();
    if (ref.read(dashboardProvider).selectedDateKey != today) {
      final now = DateTime.now();
      ref.read(dashboardProvider.notifier).selectDate(now);
      ref.read(mealProvider.notifier).setDate(now);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(dashboardProvider);
    final l10n = ref.watch(appStringsProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      body: CustomScrollView(
        physics: const BouncingScrollPhysics(),
        slivers: [
          SliverAppBar(
            toolbarHeight: 68,
            floating: true,
            pinned: false,
            automaticallyImplyLeading: false,
            centerTitle: false,
            titleSpacing: 0,
            backgroundColor: theme.scaffoldBackgroundColor,
            title: Padding(
              padding: const EdgeInsets.only(left: 4, right: 8),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  // Logo — natural 3:2 aspect ratio, no forced-square gaps
                  Image.asset(
                    'assets/images/infinitehealthtrackerlogo.png',
                    height: 44,
                    fit: BoxFit.fitHeight,
                  ),
                  const SizedBox(width: 10),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.appName,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w800,
                          color: AppColors.primary,
                          fontSize: 16,
                          letterSpacing: -0.3,
                        ),
                      ),
                      Text(
                        l10n.tagline,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: AppColors.primary.withValues(alpha: 0.70),
                          fontSize: 10,
                          fontWeight: FontWeight.w500,
                          letterSpacing: 0.2,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                _DateSelector(state: state),
                const SizedBox(height: 12),
                _WeeklyProgressPanel(state: state),
                const SizedBox(height: 16),
                _RecommendationCard(state: state),
                const SizedBox(height: 16),
                _CalorieCard(state: state),
                const SizedBox(height: 16),
                _ActivityCaloriesCard(state: state),
                const SizedBox(height: 16),
                _EnergyBalanceCard(state: state),
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
        : '${selected.day.toString().padLeft(2, '0')}/${selected.month.toString().padLeft(2, '0')}/${selected.year}';

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
                  style: const TextStyle(
                    color: AppColors.primary,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            )
          else
            Text(
              '${now.day.toString().padLeft(2, '0')}/${now.month.toString().padLeft(2, '0')}/${now.year}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Weekly Progress Panel — last 7 days calorie bars + streak counter
// ═══════════════════════════════════════════════════════════════════════════

class _WeeklyProgressPanel extends ConsumerWidget {
  final DashboardState state;
  const _WeeklyProgressPanel({required this.state});

  static const _dayLabelsEn = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  static const _dayLabelsBn = ['সো', 'মঙ', 'বু', 'বৃ', 'শু', 'শ', 'র'];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = ref.watch(appStringsProvider);
    final bn = l10n.isBengali;
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final calGoal = state.goals?.calories ?? 2000;

    // Last 7 calendar days (oldest → newest)
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final dates = List.generate(7, (i) => today.subtract(Duration(days: 6 - i)));

    final dayMap = {
      for (final s in InsightsService.allDailySummaries()) s.dateKey: s
    };

    final records = dates.map((d) {
      final key =
          '${d.year}_${d.month.toString().padLeft(2, '0')}_${d.day.toString().padLeft(2, '0')}';
      final s = dayMap[key];
      return (date: d, kcal: s?.kcal ?? 0.0, logged: (s?.mealCount ?? 0) > 0);
    }).toList();

    final streak = InsightsService.currentStreak();
    const maxBarH = 44.0;
    const orange = Color(0xFFFF6D00);

    final cardBg = isDark ? const Color(0xFF1E1E2E) : const Color(0xFFF8F9FF);
    final borderColor =
        isDark ? Colors.white.withValues(alpha: 0.08) : Colors.black.withValues(alpha: 0.07);

    return Container(
      decoration: BoxDecoration(
        color: cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor, width: 1),
      ),
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                bn ? 'সাপ্তাহিক অগ্রগতি' : 'Last 7 Days',
                style: theme.textTheme.titleSmall
                    ?.copyWith(fontWeight: FontWeight.w700),
              ),
              const Spacer(),
              if (streak > 0)
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: orange.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: orange.withValues(alpha: 0.3)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text('🔥', style: TextStyle(fontSize: 12)),
                      const SizedBox(width: 3),
                      Text(
                        bn ? '$streak দিন স্ট্রিক' : '$streak day streak',
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: orange,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
          const SizedBox(height: 10),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: records.asMap().entries.map((entry) {
              final i = entry.key;
              final r = entry.value;
              final pct =
                  calGoal > 0 ? (r.kcal / calGoal).clamp(0.0, 1.0) : 0.0;
              final isToday = i == 6;
              final barColor = _barColor(r.kcal, calGoal, r.logged);
              final barH = r.logged
                  ? (pct * maxBarH).clamp(4.0, maxBarH)
                  : 0.0;
              final dayIdx = r.date.weekday - 1; // 0=Mon…6=Sun
              final labels = bn ? _dayLabelsBn : _dayLabelsEn;

              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 2),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        r.logged ? '${r.kcal.round()}' : '',
                        style: TextStyle(
                          fontSize: 8,
                          color: barColor,
                          fontWeight: FontWeight.w600,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 2),
                      SizedBox(
                        height: maxBarH,
                        child: Align(
                          alignment: Alignment.bottomCenter,
                          child: AnimatedContainer(
                            duration: const Duration(milliseconds: 600),
                            curve: Curves.easeOut,
                            width: double.infinity,
                            height: r.logged ? barH : 3,
                            decoration: BoxDecoration(
                              color: r.logged
                                  ? barColor
                                  : (isDark
                                      ? Colors.white.withValues(alpha: 0.10)
                                      : Colors.black.withValues(alpha: 0.07)),
                              borderRadius: BorderRadius.circular(3),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        labels[dayIdx],
                        style: TextStyle(
                          fontSize: 9,
                          fontWeight:
                              isToday ? FontWeight.w800 : FontWeight.w500,
                          color: isToday
                              ? AppColors.primary
                              : theme.colorScheme.onSurface
                                  .withValues(alpha: 0.55),
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Color _barColor(double kcal, double goal, bool logged) {
    if (!logged || kcal == 0 || goal == 0) return Colors.grey;
    final pct = kcal / goal;
    if (pct >= 0.90 && pct <= 1.10) return const Color(0xFF27AE60);
    if (pct >= 0.75 && pct <= 1.25) return const Color(0xFFF39C12);
    return const Color(0xFFE74C3C);
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

  // Cached recommendation — only recomputed when meals, goals, or language change
  DailyRecommendation? _rec;
  List<MealEntry>? _lastMeals;
  NutritionGoals? _lastGoals;
  String? _lastLang;

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

  DailyRecommendation _getRecommendation(String lang) {
    final meals = widget.state.todaysMeals;
    final goals = widget.state.goals;
    if (_rec == null ||
        !identical(_lastMeals, meals) ||
        _lastGoals != goals ||
        _lastLang != lang) {
      _rec = RecommendationEngine.analyze(
        goals: goals ?? NutritionGoals.defaults,
        meals: meals,
        lang: lang,
        ironMg: widget.state.totalIron,
        calciumMg: widget.state.totalCalcium,
        vitaminDMcg: widget.state.totalVitaminD,
        vitaminB12Mcg: widget.state.totalVitaminB12,
        gender: widget.state.userProfile?.gender,
      );
      _lastMeals = meals;
      _lastGoals = goals;
      _lastLang = lang;
    }
    return _rec!;
  }

  @override
  Widget build(BuildContext context) {
    final l10n = ref.watch(appStringsProvider);
    final lang = l10n.language;
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final rec = _getRecommendation(lang);

    final bn = lang == 'bn';
    final stepsDisplay = ((rec.walkingSteps / 500).round() * 500);
    final minsDisplay  = ((rec.walkingMinutes / 5).round() * 5).clamp(10, 90);

    final cardBg = isDark
        ? const Color(0xFF1A2535)
        : const Color(0xFFF0F9F4);
    const accentColor = Color(0xFF27AE60);
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
                      child: const Icon(Icons.tips_and_updates_rounded,
                          color: Color(0xFF27AE60), size: 18),
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
                      child: const Icon(Icons.expand_more_rounded,
                          color: Color(0xFF27AE60), size: 20),
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
                      const Text('💡', style: TextStyle(fontSize: 16)),
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
                              const Icon(Icons.directions_walk_rounded,
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
    final bn = l10n.isBengali;
    final goals = state.goals;
    final calorieGoal = goals?.calories ?? 2000;

    final hasBurned = state.deductBurnedCalories && state.burnedCaloriesKcal > 0;
    final netCal = state.netCalories;
    final remaining = (calorieGoal - netCal).clamp(0.0, calorieGoal);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            MacroRingChart(
              calories: netCal,
              calorieGoal: calorieGoal,
              protein: state.totalProtein,
              carbs: state.totalCarbs,
              fat: state.totalFat,
              alcoholG: state.totalAlcohol,
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _StatRow(
                    label: l10n.consumed,
                    value: '${state.totalCalories.toStringAsFixed(0)} kcal',
                    color: AppColors.calories,
                  ),
                  if (hasBurned) ...[
                    const SizedBox(height: 6),
                    _StatRow(
                      label: l10n.activityBurned,
                      value: '−${state.burnedCaloriesKcal.toStringAsFixed(0)} kcal',
                      color: const Color(0xFF27AE60),
                    ),
                    const SizedBox(height: 6),
                    _StatRow(
                      label: l10n.netCalories,
                      value: '${netCal.toStringAsFixed(0)} kcal',
                      color: AppColors.primary,
                    ),
                  ],
                  const SizedBox(height: 8),
                  _StatRow(
                    label: l10n.goal,
                    value: '${calorieGoal.toStringAsFixed(0)} kcal',
                    color: AppColors.primary,
                  ),
                  const SizedBox(height: 8),
                  _StatRow(
                    label: l10n.remaining,
                    value: '${remaining.toStringAsFixed(0)} kcal',
                    color: AppColors.secondary,
                  ),
                  if (goals != null) ...[
                    const SizedBox(height: 10),
                    Text(
                      bn
                          ? 'বিএমআর: ${goals.bmr.toStringAsFixed(0)} kcal'
                          : 'BMR: ${goals.bmr.toStringAsFixed(0)} kcal',
                      style: theme.textTheme.bodySmall,
                    ),
                    Text(
                      bn
                          ? 'টিডিইই: ${goals.tdee.toStringAsFixed(0)} kcal'
                          : 'TDEE: ${goals.tdee.toStringAsFixed(0)} kcal',
                      style: theme.textTheme.bodySmall,
                    ),
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

// ═══════════════════════════════════════════════════════════════════════════════
// Activity Calories Card
// ═══════════════════════════════════════════════════════════════════════════════

class _ActivityCaloriesCard extends ConsumerWidget {
  final DashboardState state;
  const _ActivityCaloriesCard({required this.state});

  void _showInputDialog(BuildContext context, WidgetRef ref, AppStrings l10n) {
    final ctrl = TextEditingController(
      text: state.burnedCaloriesKcal > 0
          ? state.burnedCaloriesKcal.toStringAsFixed(0)
          : '',
    );
    final bn = l10n.isBengali;
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.directions_run_rounded,
                color: Color(0xFF27AE60), size: 20),
            const SizedBox(width: 8),
            Text(l10n.logActivityBurned),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              bn
                  ? 'আজকের কার্যকলাপে কত ক্যালোরি পুড়েছেন? (যেমন: হাঁটা, দৌড়, সাইকেল, যোগব্যায়াম)'
                  : 'How many calories did you burn through activity today? (e.g. walking, running, cycling, yoga)',
              style: const TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: ctrl,
              keyboardType: TextInputType.number,
              autofocus: true,
              decoration: InputDecoration(
                labelText: l10n.burnedKcalLabel,
                suffixText: 'kcal',
                border: const OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(l10n.cancel),
          ),
          if (state.burnedCaloriesKcal > 0)
            TextButton(
              onPressed: () {
                ref.read(dashboardProvider.notifier).setBurnedCalories(0);
                Navigator.pop(ctx);
              },
              child: Text(
                bn ? 'রিসেট' : 'Reset',
                style: const TextStyle(color: Colors.red),
              ),
            ),
          ElevatedButton(
            onPressed: () {
              final v = double.tryParse(ctrl.text.trim());
              if (v != null && v >= 0) {
                ref.read(dashboardProvider.notifier).setBurnedCalories(v);
              }
              Navigator.pop(ctx);
            },
            child: Text(l10n.save),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = ref.watch(appStringsProvider);
    final bn = l10n.isBengali;
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    const green = Color(0xFF27AE60);
    final burned = state.burnedCaloriesKcal;
    final deduct = state.deductBurnedCalories;

    final cardBg = isDark ? const Color(0xFF1A2A1F) : const Color(0xFFF0FFF4);
    final borderColor = isDark
        ? green.withValues(alpha: 0.3)
        : green.withValues(alpha: 0.3);

    return Container(
      decoration: BoxDecoration(
        color: cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor, width: 1.2),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Header ──────────────────────────────────────────────────
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(7),
                  decoration: BoxDecoration(
                    color: green.withValues(alpha: 0.15),
                    borderRadius: BorderRadius.circular(9),
                  ),
                  child: const Icon(Icons.directions_run_rounded,
                      color: green, size: 17),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        l10n.activityCalories,
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                          color: green,
                        ),
                      ),
                      if (burned > 0)
                        Text(
                          bn
                              ? '${burned.toStringAsFixed(0)} kcal পোড়া হয়েছে'
                              : '${burned.toStringAsFixed(0)} kcal burned today',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: green,
                            fontWeight: FontWeight.w600,
                          ),
                        )
                      else
                        Text(
                          bn
                              ? 'আজকের কার্যকলাপ লগ করুন'
                              : 'Log today\'s activity calories',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurface
                                .withValues(alpha: 0.55),
                          ),
                        ),
                    ],
                  ),
                ),
                // Log / Edit button
                OutlinedButton.icon(
                  onPressed: () => _showInputDialog(context, ref, l10n),
                  icon: Icon(
                    burned > 0 ? Icons.edit_rounded : Icons.add_rounded,
                    size: 14,
                  ),
                  label: Text(
                    burned > 0
                        ? (bn ? 'সম্পাদনা' : 'Edit')
                        : l10n.logActivityBurned,
                    style: const TextStyle(fontSize: 12),
                  ),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: green,
                    side: BorderSide(color: green.withValues(alpha: 0.5)),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 6),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8)),
                  ),
                ),
              ],
            ),

            if (burned > 0) ...[
              const SizedBox(height: 12),
              // Quick +/- buttons
              Row(
                children: [
                  _BurnButton(
                    label: bn ? '−৫০' : '−50',
                    kcal: -50,
                    color: Colors.red.shade400,
                    current: burned,
                  ),
                  const SizedBox(width: 6),
                  _BurnButton(
                    label: bn ? '−১০০' : '−100',
                    kcal: -100,
                    color: Colors.red.shade400,
                    current: burned,
                  ),
                  const SizedBox(width: 6),
                  _BurnButton(
                    label: bn ? '+৫০' : '+50',
                    kcal: 50,
                    color: green,
                    current: burned,
                  ),
                  const SizedBox(width: 6),
                  _BurnButton(
                    label: bn ? '+১০০' : '+100',
                    kcal: 100,
                    color: green,
                    current: burned,
                  ),
                ],
              ),
            ],

            const SizedBox(height: 10),
            // ── Deduct toggle ─────────────────────────────────────────────
            Row(
              children: [
                Expanded(
                  child: Text(
                    l10n.deductFromDaily,
                    style: theme.textTheme.bodySmall?.copyWith(
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                Transform.scale(
                  scale: 0.85,
                  child: Switch(
                    value: deduct,
                    activeThumbColor: green,
                    activeTrackColor: green.withValues(alpha: 0.4),
                    onChanged: (v) {
                      ref
                          .read(dashboardProvider.notifier)
                          .setDeductBurnedCalories(v);
                    },
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _BurnButton extends ConsumerWidget {
  final String label;
  final double kcal;
  final Color color;
  final double current;

  const _BurnButton({
    required this.label,
    required this.kcal,
    required this.color,
    required this.current,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Expanded(
      child: OutlinedButton(
        onPressed: () {
          final next = (current + kcal).clamp(0.0, 5000.0);
          ref.read(dashboardProvider.notifier).setBurnedCalories(next);
        },
        style: OutlinedButton.styleFrom(
          foregroundColor: color,
          side: BorderSide(color: color.withValues(alpha: 0.5)),
          padding: const EdgeInsets.symmetric(vertical: 6),
          shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8)),
          textStyle:
              const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
        ),
        child: Text(label),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Energy Balance Card
// ═══════════════════════════════════════════════════════════════════════════════

class _EnergyBalanceCard extends ConsumerStatefulWidget {
  final DashboardState state;
  const _EnergyBalanceCard({required this.state});

  @override
  ConsumerState<_EnergyBalanceCard> createState() =>
      _EnergyBalanceCardState();
}

class _EnergyBalanceCardState extends ConsumerState<_EnergyBalanceCard>
    with SingleTickerProviderStateMixin {
  bool _expanded = false;
  late final AnimationController _animCtrl;
  late final Animation<double> _expandAnim;

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 260));
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
    final bn = l10n.isBengali;
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final goals = widget.state.goals;
    if (goals == null) return const SizedBox.shrink();

    final balance = EnergyBalanceService.calculate(
      consumedKcal: widget.state.totalCalories,
      tdeeKcal: goals.tdee,
      targetKcal: goals.calories,
      goal: widget.state.userProfile?.fitnessGoal ?? 'maintain',
      profile: widget.state.userProfile,
    );

    final statusColor = _statusColor(balance.status);
    final cardBg = isDark ? const Color(0xFF1A2030) : const Color(0xFFF8F9FF);
    final borderColor = isDark
        ? statusColor.withValues(alpha: 0.3)
        : statusColor.withValues(alpha: 0.25);

    final balanceLabelFull = bn
        ? (balance.isDeficit
            ? '${balance.absBalance.round()} kcal ঘাটতি'
            : '+${balance.absBalance.round()} kcal উদ্বৃত্ত')
        : (balance.isDeficit
            ? '${balance.absBalance.round()} kcal deficit'
            : '+${balance.absBalance.round()} kcal surplus');

    return Container(
      decoration: BoxDecoration(
        color: cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor, width: 1.2),
        boxShadow: isDark
            ? null
            : [
                BoxShadow(
                  color: statusColor.withValues(alpha: 0.06),
                  blurRadius: 8,
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
                // ── Header ────────────────────────────────────────────────
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: statusColor.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(Icons.bolt_rounded,
                          color: statusColor, size: 18),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            bn ? 'এনার্জি ব্যালেন্স' : 'Energy Balance',
                            style: theme.textTheme.titleSmall?.copyWith(
                              fontWeight: FontWeight.w700,
                              color: statusColor,
                            ),
                          ),
                          if (balance.hasData)
                            Text(
                              balanceLabelFull,
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: statusColor,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                        ],
                      ),
                    ),
                    AnimatedRotation(
                      turns: _expanded ? 0.5 : 0.0,
                      duration: const Duration(milliseconds: 260),
                      child: Icon(Icons.expand_more_rounded,
                          color: statusColor, size: 20),
                    ),
                  ],
                ),

                const SizedBox(height: 12),

                // ── Progress bar: consumed vs target ──────────────────────
                _EnergyProgressBar(
                  consumed: balance.consumedKcal,
                  target: balance.targetKcal,
                  statusColor: statusColor,
                  bn: bn,
                  theme: theme,
                ),

                if (balance.hasData) ...[
                  const SizedBox(height: 10),

                  // ── Context message (always visible) ─────────────────────
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: statusColor.withValues(alpha: 0.08),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      bn ? balance.contextBn : balance.contextEn,
                      style: theme.textTheme.bodySmall?.copyWith(
                        height: 1.45,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ] else ...[
                  const SizedBox(height: 8),
                  Text(
                    bn
                        ? 'খাবার লগ করুন আপনার এনার্জি ব্যালেন্স দেখতে।'
                        : 'Log your meals to see your energy balance.',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                    ),
                  ),
                ],

                // ── Expanded: activity equivalents ────────────────────────
                SizeTransition(
                  sizeFactor: _expandAnim,
                  child: balance.hasData
                      ? Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 14),
                            _SectionLabel(
                              icon: Icons.directions_run_rounded,
                              label: bn
                                  ? 'কার্যকলাপ সমতুল্য'
                                  : 'Activity Equivalents',
                              color: statusColor,
                            ),
                            const SizedBox(height: 8),
                            Row(
                              children: [
                                _ActivityChip(
                                  icon: Icons.directions_walk_rounded,
                                  label: bn
                                      ? '${balance.walkingMins} মিনিট\nহাঁটা'
                                      : '${balance.walkingMins} min\nwalk',
                                  sub: '~${_fmtSteps(balance.walkingSteps)}',
                                  color: statusColor,
                                ),
                                const SizedBox(width: 8),
                                _ActivityChip(
                                  icon: Icons.directions_run_rounded,
                                  label: bn
                                      ? '${balance.runningMins} মিনিট\nদৌড়'
                                      : '${balance.runningMins} min\nrun',
                                  sub: '~9 km/h',
                                  color: statusColor,
                                ),
                                const SizedBox(width: 8),
                                _ActivityChip(
                                  icon: Icons.directions_bike_rounded,
                                  label: bn
                                      ? '${balance.cyclingMins} মিনিট\nসাইকেল'
                                      : '${balance.cyclingMins} min\ncycle',
                                  sub: '~15 km/h',
                                  color: statusColor,
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            Row(
                              children: [
                                Icon(Icons.info_outline,
                                    size: 12,
                                    color: theme.colorScheme.onSurface
                                        .withValues(alpha: 0.4)),
                                const SizedBox(width: 5),
                                Expanded(
                                  child: Text(
                                    bn
                                        ? 'TDEE: ${goals.tdee.round()} kcal · BMR: ${goals.bmr.round()} kcal · মানগুলো আনুমানিক।'
                                        : 'TDEE: ${goals.tdee.round()} kcal · BMR: ${goals.bmr.round()} kcal · Values are approximate.',
                                    style: theme.textTheme.bodySmall?.copyWith(
                                      fontSize: 10,
                                      color: theme.colorScheme.onSurface
                                          .withValues(alpha: 0.45),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                          ],
                        )
                      : const SizedBox.shrink(),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _statusColor(BalanceStatus s) {
    switch (s) {
      case BalanceStatus.deepDeficit:
        return const Color(0xFF27AE60);
      case BalanceStatus.deficit:
        return const Color(0xFF2ECC71);
      case BalanceStatus.onTarget:
        return AppColors.primary;
      case BalanceStatus.slightSurplus:
        return const Color(0xFFF39C12);
      case BalanceStatus.surplus:
        return const Color(0xFFE74C3C);
      case BalanceStatus.noData:
        return Colors.grey;
    }
  }

  String _fmtSteps(int steps) {
    final l10n = ref.read(appStringsProvider);
    final label = l10n.steps;
    if (steps >= 1000) {
      return '${(steps / 1000).toStringAsFixed(steps % 1000 == 0 ? 0 : 1)}k $label';
    }
    return '$steps $label';
  }
}

class _EnergyProgressBar extends StatelessWidget {
  final double consumed, target;
  final Color statusColor;
  final bool bn;
  final ThemeData theme;

  const _EnergyProgressBar({
    required this.consumed,
    required this.target,
    required this.statusColor,
    required this.bn,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    final pct = target > 0 ? (consumed / target).clamp(0.0, 1.5) : 0.0;
    final barPct = pct.clamp(0.0, 1.0);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              bn
                  ? '${consumed.round()} kcal খেয়েছেন'
                  : '${consumed.round()} kcal consumed',
              style: theme.textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.w500,
              ),
            ),
            Text(
              bn
                  ? 'লক্ষ্য: ${target.round()} kcal'
                  : 'Target: ${target.round()} kcal',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: Stack(
            children: [
              Container(
                height: 8,
                color: statusColor.withValues(alpha: 0.12),
              ),
              FractionallySizedBox(
                widthFactor: barPct,
                child: Container(
                  height: 8,
                  decoration: BoxDecoration(
                    color: statusColor,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ),
              // Target line at 100%
              Positioned(
                right: 0,
                top: 0,
                bottom: 0,
                child: Container(
                  width: 2,
                  color: statusColor.withValues(alpha: 0.5),
                ),
              ),
            ],
          ),
        ),
        if (pct > 1.0) ...[
          const SizedBox(height: 4),
          Align(
            alignment: Alignment.centerRight,
            child: Text(
              bn
                  ? '+${((pct - 1.0) * 100).toStringAsFixed(0)}% অতিরিক্ত'
                  : '+${((pct - 1.0) * 100).toStringAsFixed(0)}% over',
              style: TextStyle(
                fontSize: 10,
                color: statusColor,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ],
    );
  }
}

class _ActivityChip extends StatelessWidget {
  final IconData icon;
  final String label, sub;
  final Color color;

  const _ActivityChip({
    required this.icon,
    required this.label,
    required this.sub,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: color.withValues(alpha: 0.2)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: color, size: 18),
            const SizedBox(height: 4),
            Text(
              label,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: color,
                height: 1.3,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              sub,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 9,
                color: color.withValues(alpha: 0.7),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════

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
    final totalCals = entries.fold<double>(0, (sum, e) => sum + e.calories);
    return Consumer(builder: (context, ref, _) {
      final l10n = ref.watch(appStringsProvider);
      return Card(
        margin: const EdgeInsets.only(bottom: 8),
        child: ListTile(
          leading: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: AppColors.primary, size: 20),
          ),
          title: Text(label, style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600)),
          subtitle: Text(
            entries.isEmpty
                ? l10n.tapToAdd
                : '${entries.length} ${l10n.items}',
            style: Theme.of(context).textTheme.bodySmall,
          ),
          trailing: entries.isEmpty
              ? const Icon(Icons.add_circle_outline, color: AppColors.primary)
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

class _WaterFiberCard extends ConsumerWidget {
  final DashboardState state;
  const _WaterFiberCard({required this.state});

  void _showWaterInfoDialog(BuildContext context, AppStrings l10n, double waterGoal) {
    final bn = l10n.isBengali;
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.water_drop, color: Color(0xFF29B6F6), size: 20),
            const SizedBox(width: 8),
            Text(bn ? 'পানির লক্ষ্য কীভাবে?' : 'How is your goal set?'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              bn
                  ? 'আপনার লক্ষ্য: ${waterGoal.toStringAsFixed(0)} মিলি/দিন'
                  : 'Your goal: ${waterGoal.toStringAsFixed(0)} ml/day',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 10),
            Text(
              bn
                  ? '📐 সূত্র: আপনার ওজন (কেজি) × ৩৫ মিলি'
                  : '📐 Formula: body weight (kg) × 35 ml',
            ),
            const SizedBox(height: 4),
            Text(
              bn
                  ? '   + মাঝারি সক্রিয়: +২৫০ মিলি\n   + খুব সক্রিয়: +৫০০ মিলি'
                  : '   + moderately active: +250 ml\n   + very/extra active: +500 ml',
              style: const TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 10),
            Text(
              bn
                  ? 'ℹ️ ICMR রেফারেন্স: ৩৭০০ মিলি/দিন — এটি একজন ৭০ কেজি প্রাপ্তবয়স্কের জন্য। আপনার লক্ষ্য আপনার আসল ওজনের উপর ভিত্তি করে।'
                  : 'ℹ️ ICMR reference: 3700 ml/day — this is for a 70 kg adult. Your personalized goal is based on your actual weight.',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(l10n.done),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final goals = state.goals;
    final l10n = ref.watch(appStringsProvider);
    final bn = l10n.isBengali;
    final waterGoal = goals?.waterMl ?? 2450;
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Water ──────────────────────────────────────────────────────
            Row(
              children: [
                Text(
                  l10n.water,
                  style: theme.textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w500),
                ),
                const SizedBox(width: 4),
                GestureDetector(
                  onTap: () => _showWaterInfoDialog(context, l10n, waterGoal),
                  child: const Icon(Icons.info_outline, size: 15, color: Colors.grey),
                ),
                const Spacer(),
                Text(
                  '${state.waterIntakeMl.toStringAsFixed(0)}ml / ${waterGoal.toStringAsFixed(0)}ml',
                  style: theme.textTheme.bodySmall?.copyWith(color: const Color(0xFF29B6F6)),
                ),
              ],
            ),
            const SizedBox(height: 6),
            NutritionProgressBar(
              label: l10n.water,
              current: state.waterIntakeMl,
              goal: waterGoal,
              color: const Color(0xFF29B6F6),
              unit: 'ml',
              showValues: false,
            ),
            const SizedBox(height: 8),
            // Glass row: minus and plus side by side
            Row(
              children: [
                _WaterButton(
                  label: bn ? '−১ গ্লাস' : '−1 glass',
                  ml: -250,
                  isSubtract: true,
                ),
                const SizedBox(width: 8),
                _WaterButton(
                  label: bn ? '+১ গ্লাস' : '+1 glass',
                  ml: 250,
                ),
              ],
            ),
            const SizedBox(height: 6),
            // Bottle row: minus and plus side by side
            Row(
              children: [
                _WaterButton(
                  label: bn ? '−বোতল' : '−bottle',
                  ml: -500,
                  isSubtract: true,
                ),
                const SizedBox(width: 8),
                _WaterButton(
                  label: bn ? '+বোতল' : '+bottle',
                  ml: 500,
                ),
              ],
            ),
            const SizedBox(height: 6),
            // Reset — full width
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () => ref.read(dashboardProvider.notifier).setWater(0),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.grey,
                  side: BorderSide(color: Colors.grey.shade300),
                  padding: const EdgeInsets.symmetric(vertical: 7),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                ),
                child: Text(bn ? 'রিসেট' : 'Reset'),
              ),
            ),
            const SizedBox(height: 14),
            const Divider(height: 1),
            const SizedBox(height: 14),
            // ── Fiber ──────────────────────────────────────────────────────
            NutritionProgressBar(
              label: l10n.fiber,
              current: state.totalFiber,
              goal: goals?.fiberG ?? 40,
              color: AppColors.fiber,
            ),
          ],
        ),
      ),
    );
  }
}

class _WaterButton extends ConsumerWidget {
  final String label;
  final double ml;
  final bool isSubtract;

  const _WaterButton({
    required this.label,
    required this.ml,
    this.isSubtract = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    const waterBlue = Color(0xFF29B6F6);
    const subtractRed = Color(0xFFEF5350);

    final fgColor = isSubtract ? subtractRed : waterBlue;
    final borderColor = isSubtract
        ? subtractRed.withValues(alpha: 0.45)
        : waterBlue.withValues(alpha: 0.5);

    return Expanded(
      child: OutlinedButton(
        onPressed: () => ref.read(dashboardProvider.notifier).addWater(ml),
        style: OutlinedButton.styleFrom(
          foregroundColor: fgColor,
          side: BorderSide(color: borderColor),
          padding: const EdgeInsets.symmetric(vertical: 7),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
        ),
        child: Text(label),
      ),
    );
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
                  color: AppColors.primary.withValues(alpha: 0.1),
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
                    final parts = state.selectedDateKey.split('_');
                    if (parts.length == 3) {
                      return '${parts[2]}/${parts[1]}/${parts[0]}';
                    }
                    final now = DateTime.now();
                    return '${now.day.toString().padLeft(2, '0')}/${now.month.toString().padLeft(2, '0')}/${now.year}';
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
                // Micronutrient section: always shown to encourage tracking.
                // B12 is always displayed (deficiency affects ~47% of Indian vegetarians).
                _SummarySection(
                  title: l10n.micronutrients,
                  rows: [
                    if (state.totalVitaminA > 0)
                      _SummaryRow(label: l10n.vitaminA, consumed: state.totalVitaminA, goal: NutritionConstants.vitaminAForGender(state.userProfile?.gender ?? 'male'), unit: l10n.mcg, l10n: l10n),
                    _SummaryRow(
                      label: l10n.vitaminB,
                      consumed: state.totalVitaminB12,
                      goal: NutritionConstants.vitaminB12Mcg,
                      unit: l10n.mcg,
                      l10n: l10n,
                      forceWarning: state.totalVitaminB12 == 0,
                    ),
                    if (state.totalVitaminC > 0)
                      _SummaryRow(label: l10n.vitaminC, consumed: state.totalVitaminC, goal: NutritionConstants.vitaminCMg, unit: l10n.mg, l10n: l10n),
                    if (state.totalVitaminD > 0)
                      _SummaryRow(label: l10n.vitaminD, consumed: state.totalVitaminD, goal: NutritionConstants.vitaminDMcg, unit: l10n.mcg, l10n: l10n),
                    if (state.totalCalcium > 0)
                      _SummaryRow(label: l10n.calcium, consumed: state.totalCalcium, goal: NutritionConstants.calciumMg, unit: l10n.mg, l10n: l10n),
                    if (state.totalIron > 0)
                      _SummaryRow(
                        label: l10n.iron,
                        consumed: state.totalIron,
                        goal: NutritionConstants.ironForGender(state.userProfile?.gender ?? 'male'),
                        unit: l10n.mg,
                        l10n: l10n,
                        // ICMR 2020: females 19–50 need 29 mg/day; warn if below 60% (~17.4 mg)
                        forceWarning: state.userProfile?.gender == 'female' &&
                            state.totalIron < NutritionConstants.ironForGender('female') * 0.6,
                      ),
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
  final bool forceWarning;

  const _SummaryRow({
    required this.label,
    required this.consumed,
    required this.goal,
    required this.unit,
    required this.l10n,
    this.forceWarning = false,
  });

  @override
  Widget build(BuildContext context) {
    final pct = goal > 0 ? consumed / goal : 0.0;
    final (statusLabel, statusColor) = forceWarning
        ? (l10n.isBengali ? 'ট্র্যাক করুন' : 'Track it', Colors.red.shade600)
        : pct > 1.1
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
              color: statusColor.withValues(alpha: 0.12),
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

