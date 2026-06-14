import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../widgets/common/loading_indicator.dart';
import '../../services/analytics_service.dart';
import '../../services/energy_balance_service.dart';
import 'providers/history_provider.dart';

class HistoryScreen extends ConsumerStatefulWidget {
  const HistoryScreen({super.key});

  @override
  ConsumerState<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends ConsumerState<HistoryScreen>
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
    final state = ref.watch(historyProvider);
    final l10n = ref.watch(appStringsProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.historyAnalytics),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(historyProvider.notifier).load(),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(text: l10n.days7),
            Tab(text: l10n.days30),
            Tab(text: l10n.monthly),
          ],
        ),
      ),
      body: state.isLoading
          ? const LoadingIndicator()
          : TabBarView(
              controller: _tabController,
              children: [
                _PeriodTab(
                  data: state.week,
                  goalCalories: state.goalCalories,
                  tdee: state.tdee,
                  streak: state.streak,
                  avgCompletion: state.weekAvgCompletion,
                  periodLabel: l10n.days7,
                ),
                _PeriodTab(
                  data: state.month,
                  goalCalories: state.goalCalories,
                  tdee: state.tdee,
                  streak: state.streak,
                  avgCompletion: state.monthAvgCompletion,
                  periodLabel: l10n.days30,
                ),
                _MonthlyTab(byMonth: state.byMonth),
              ],
            ),
    );
  }
}

// ── Period Tab (7 / 30 days) ──────────────────────────────────────────────────

class _PeriodTab extends StatelessWidget {
  final List<DailyNutrition> data;
  final double goalCalories;
  final double tdee;
  final int streak;
  final double avgCompletion;
  final String periodLabel;

  const _PeriodTab({
    required this.data,
    required this.goalCalories,
    required this.tdee,
    required this.streak,
    required this.avgCompletion,
    required this.periodLabel,
  });

  @override
  Widget build(BuildContext context) {
    final hasData = data.any((d) => d.hasData);

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _SummaryRow(streak: streak, avgCompletion: avgCompletion),
        const SizedBox(height: 16),
        if (hasData) ...[
          _CalorieChart(data: data, goalCalories: goalCalories),
          const SizedBox(height: 16),
          _WeeklyEnergyBalanceCard(data: data, targetKcal: goalCalories, tdee: tdee),
          const SizedBox(height: 16),
          _ActivityBurnedSummaryCard(data: data),
          const SizedBox(height: 16),
          _MacroAveragesCard(data: data),
          const SizedBox(height: 16),
          _NutritionStreakCard(data: data, goalCalories: goalCalories),
        ] else
          _EmptyState(),
        const SizedBox(height: 80),
      ],
    );
  }
}

// ── Summary Row ───────────────────────────────────────────────────────────────

class _SummaryRow extends StatelessWidget {
  final int streak;
  final double avgCompletion;
  const _SummaryRow({required this.streak, required this.avgCompletion});

  @override
  Widget build(BuildContext context) {
    return Row(children: [
      Expanded(
        child: _StatCard(
          icon: Icons.local_fire_department,
          iconColor: Colors.orange,
          value: '$streak',
          label: 'Day Streak',
        ),
      ),
      const SizedBox(width: 12),
      Expanded(
        child: _StatCard(
          icon: Icons.flag_outlined,
          iconColor: AppColors.primary,
          value: '${(avgCompletion * 100).toStringAsFixed(0)}%',
          label: 'Goal Avg',
        ),
      ),
    ]);
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String value, label;
  const _StatCard({required this.icon, required this.iconColor, required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: iconColor.withValues(alpha:0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 22),
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(value,
                  style: Theme.of(context)
                      .textTheme
                      .titleLarge
                      ?.copyWith(fontWeight: FontWeight.w800, color: iconColor)),
              Text(label, style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        ]),
      ),
    );
  }
}

// ── Calorie Line Chart ────────────────────────────────────────────────────────

class _CalorieChart extends StatelessWidget {
  final List<DailyNutrition> data;
  final double goalCalories;
  const _CalorieChart({required this.data, required this.goalCalories});

  @override
  Widget build(BuildContext context) {
    final spots = <FlSpot>[];
    for (int i = 0; i < data.length; i++) {
      if (data[i].hasData) spots.add(FlSpot(i.toDouble(), data[i].calories));
    }
    if (spots.isEmpty) return const SizedBox.shrink();

    final maxY = ([...data.map((d) => d.calories), goalCalories]
          ..sort())
        .last * 1.2;

    return Card(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(8, 16, 16, 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.only(left: 8, bottom: 12),
              child: Text('Calorie Trend',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
            ),
            SizedBox(
              height: 180,
              child: LineChart(LineChartData(
                minY: 0,
                maxY: maxY > 0 ? maxY : 3000,
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  horizontalInterval: 500,
                  getDrawingHorizontalLine: (v) => FlLine(
                    color: Colors.grey.withValues(alpha:0.15),
                    strokeWidth: 1,
                  ),
                ),
                borderData: FlBorderData(show: false),
                titlesData: FlTitlesData(
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 42,
                      interval: 500,
                      getTitlesWidget: (v, _) => Text(
                        v.toInt().toString(),
                        style: const TextStyle(fontSize: 10),
                      ),
                    ),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 28,
                      interval: data.length <= 7 ? 1 : 5,
                      getTitlesWidget: (v, _) {
                        final idx = v.toInt();
                        if (idx < 0 || idx >= data.length) return const Text('');
                        final d = data[idx].date;
                        final label = data.length <= 7
                            ? ['M', 'T', 'W', 'T', 'F', 'S', 'S'][d.weekday - 1]
                            : d.day.toString();
                        return Text(label, style: const TextStyle(fontSize: 10));
                      },
                    ),
                  ),
                ),
                extraLinesData: ExtraLinesData(
                  horizontalLines: [
                    HorizontalLine(
                      y: goalCalories,
                      color: AppColors.primary.withValues(alpha:0.5),
                      strokeWidth: 1.5,
                      dashArray: [6, 4],
                      label: HorizontalLineLabel(
                        show: true,
                        alignment: Alignment.topRight,
                        labelResolver: (_) => 'Goal',
                        style: const TextStyle(
                          fontSize: 10,
                          color: AppColors.primary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
                lineBarsData: [
                  LineChartBarData(
                    spots: spots,
                    isCurved: true,
                    curveSmoothness: 0.3,
                    color: AppColors.calories,
                    barWidth: 2.5,
                    isStrokeCapRound: true,
                    dotData: FlDotData(
                      show: spots.length <= 7,
                      getDotPainter: (_, __, ___, ____) => FlDotCirclePainter(
                        radius: 3,
                        color: AppColors.calories,
                        strokeColor: Colors.white,
                        strokeWidth: 1.5,
                      ),
                    ),
                    belowBarData: BarAreaData(
                      show: true,
                      gradient: LinearGradient(
                        colors: [AppColors.calories.withValues(alpha:0.2), AppColors.calories.withValues(alpha:0.0)],
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                      ),
                    ),
                  ),
                ],
              )),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Weekly Energy Balance Card ────────────────────────────────────────────────

class _WeeklyEnergyBalanceCard extends StatelessWidget {
  final List<DailyNutrition> data;
  final double targetKcal;
  final double tdee;

  const _WeeklyEnergyBalanceCard({
    required this.data,
    required this.targetKcal,
    required this.tdee,
  });

  @override
  Widget build(BuildContext context) {
    final target = targetKcal > 0 ? targetKcal : tdee;
    if (target <= 0) return const SizedBox.shrink();

    final dailyInput = data
        .map((d) => (date: d.date, calories: d.calories))
        .toList();

    final weekly = EnergyBalanceService.weeklyBalance(
      dailyData: dailyInput,
      targetKcal: target,
    );

    if (!weekly.hasData) return const SizedBox.shrink();

    final theme = Theme.of(context);

    final totalSign = weekly.totalBalance >= 0 ? '+' : '';
    final totalColor = weekly.totalBalance > 0
        ? const Color(0xFFE67E22)
        : const Color(0xFF27AE60);
    final netLabel =
        '$totalSign${weekly.totalBalance.round()} kcal net ${weekly.totalBalance >= 0 ? 'surplus' : 'deficit'}';

    // Find max abs balance for scaling bars
    final maxAbs = weekly.dailyBalances
        .where((b) => b.hasData)
        .fold<double>(1, (m, b) => b.balance.abs() > m ? b.balance.abs() : m);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Header ─────────────────────────────────────────────────
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(7),
                  decoration: BoxDecoration(
                    color: AppColors.primary.withValues(alpha:0.12),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(Icons.bolt_rounded,
                      color: AppColors.primary, size: 16),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Energy Balance',
                    style: theme.textTheme.titleSmall
                        ?.copyWith(fontWeight: FontWeight.w700),
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: totalColor.withValues(alpha:0.12),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    netLabel,
                    style: TextStyle(
                      color: totalColor,
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // ── Per-day bars ──────────────────────────────────────────
            SizedBox(
              height: 90,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: weekly.dailyBalances.map((b) {
                  if (!b.hasData) {
                    return Expanded(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 2),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.end,
                          children: [
                            Container(
                              height: 4,
                              decoration: BoxDecoration(
                                color: Colors.grey.withValues(alpha:0.2),
                                borderRadius: BorderRadius.circular(2),
                              ),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              _dayLabel(b.date),
                              style: const TextStyle(fontSize: 9),
                            ),
                          ],
                        ),
                      ),
                    );
                  }

                  final isSurplus = b.balance > 0;
                  final barColor = isSurplus
                      ? const Color(0xFFE67E22)
                      : const Color(0xFF27AE60);
                  final heightFraction =
                      (b.balance.abs() / maxAbs).clamp(0.05, 1.0);
                  final barH = (heightFraction * 64).clamp(4.0, 64.0);

                  return Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 2),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          Text(
                            '${b.balance >= 0 ? '+' : ''}${(b.balance / 100).round() * 100 == 0 ? b.balance.round() : (b.balance / 100).round() * 100}',
                            style: TextStyle(
                              fontSize: 8,
                              color: barColor,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Container(
                            height: barH,
                            decoration: BoxDecoration(
                              color: barColor,
                              borderRadius: BorderRadius.circular(3),
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            _dayLabel(b.date),
                            style: TextStyle(
                              fontSize: 9,
                              color:
                                  theme.colorScheme.onSurface.withValues(alpha:0.6),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),
            ),

            const SizedBox(height: 14),
            const Divider(height: 1),
            const SizedBox(height: 10),

            // ── Summary stats ─────────────────────────────────────────
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _BalanceStat(
                  label: 'On Target',
                  value: '${weekly.onTargetDays}d',
                  color: AppColors.primary,
                ),
                _BalanceStat(
                  label: 'Deficit',
                  value: '${weekly.deficitDays}d',
                  color: const Color(0xFF27AE60),
                ),
                _BalanceStat(
                  label: 'Surplus',
                  value: '${weekly.surplusDays}d',
                  color: const Color(0xFFE67E22),
                ),
                _BalanceStat(
                  label: 'Avg/day',
                  value: '${weekly.avgBalance >= 0 ? '+' : ''}${weekly.avgBalance.round()}',
                  color: weekly.avgBalance > 0
                      ? const Color(0xFFE67E22)
                      : const Color(0xFF27AE60),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _dayLabel(DateTime d) {
    const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
    return days[d.weekday - 1];
  }
}

class _BalanceStat extends StatelessWidget {
  final String label, value;
  final Color color;
  const _BalanceStat(
      {required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Text(value,
          style: TextStyle(
              color: color, fontWeight: FontWeight.w800, fontSize: 15)),
      Text(label, style: Theme.of(context).textTheme.bodySmall),
    ]);
  }
}

// ── Macro Averages Card ───────────────────────────────────────────────────────

class _MacroAveragesCard extends StatelessWidget {
  final List<DailyNutrition> data;
  const _MacroAveragesCard({required this.data});

  @override
  Widget build(BuildContext context) {
    final logged = data.where((d) => d.hasData).toList();
    if (logged.isEmpty) return const SizedBox.shrink();
    final n = logged.length;
    final avgP = logged.fold<double>(0, (s, d) => s + d.protein) / n;
    final avgC = logged.fold<double>(0, (s, d) => s + d.carbs) / n;
    final avgF = logged.fold<double>(0, (s, d) => s + d.fat) / n;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Macro Averages (per day)',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _MacroBadge(label: 'Protein', value: avgP, color: AppColors.protein, unit: 'g'),
                _MacroBadge(label: 'Carbs', value: avgC, color: AppColors.carbs, unit: 'g'),
                _MacroBadge(label: 'Fat', value: avgF, color: AppColors.fat, unit: 'g'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _MacroBadge extends StatelessWidget {
  final String label, unit;
  final double value;
  final Color color;
  const _MacroBadge({required this.label, required this.value, required this.color, required this.unit});

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Container(
        width: 60,
        height: 60,
        decoration: BoxDecoration(shape: BoxShape.circle, color: color.withValues(alpha:0.12)),
        child: Center(
          child: Text(
            value.toStringAsFixed(0),
            style: TextStyle(color: color, fontWeight: FontWeight.w800, fontSize: 16),
          ),
        ),
      ),
      const SizedBox(height: 4),
      Text(label, style: Theme.of(context).textTheme.bodySmall),
      Text(unit, style: TextStyle(fontSize: 10, color: color)),
    ]);
  }
}

// ── Nutrition Streak Card ─────────────────────────────────────────────────────

class _NutritionStreakCard extends StatelessWidget {
  final List<DailyNutrition> data;
  final double goalCalories;
  const _NutritionStreakCard({required this.data, required this.goalCalories});

  @override
  Widget build(BuildContext context) {
    final logged = data.where((d) => d.hasData).toList();
    final total = data.length;
    final consistency = total > 0 ? logged.length / total : 0.0;
    final goodDays = logged.where((d) => d.goalCompletion(goalCalories) >= 0.85).length;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Nutrition Consistency',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 12),
            _ConsistencyBar(label: 'Days Logged', value: consistency, color: AppColors.secondary),
            const SizedBox(height: 8),
            _ConsistencyBar(
              label: 'Goal Hit Days',
              value: logged.isEmpty ? 0 : goodDays / logged.length,
              color: AppColors.primary,
            ),
            const SizedBox(height: 4),
            Text(
              '${logged.length}/$total days logged · $goodDays days hit goal',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}

class _ConsistencyBar extends StatelessWidget {
  final String label;
  final double value;
  final Color color;
  const _ConsistencyBar({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        Text('${(value * 100).toStringAsFixed(0)}%',
            style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600)),
      ]),
      const SizedBox(height: 4),
      ClipRRect(
        borderRadius: BorderRadius.circular(4),
        child: LinearProgressIndicator(
          value: value.clamp(0.0, 1.0),
          minHeight: 8,
          backgroundColor: color.withValues(alpha:0.12),
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      ),
    ]);
  }
}

// ── Monthly Tab ───────────────────────────────────────────────────────────────

class _MonthlyTab extends StatelessWidget {
  final List<MonthSummaryData> byMonth;
  const _MonthlyTab({required this.byMonth});

  @override
  Widget build(BuildContext context) {
    if (byMonth.isEmpty) return _EmptyState();
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: byMonth.length,
      itemBuilder: (_, i) => _MonthCard(data: byMonth[i]),
    );
  }
}

class _MonthCard extends StatelessWidget {
  final MonthSummaryData data;
  const _MonthCard({required this.data});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Text(data.label, style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha:0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text('${data.daysLogged} days',
                    style: const TextStyle(color: AppColors.primary, fontSize: 12, fontWeight: FontWeight.w600)),
              ),
            ]),
            const SizedBox(height: 8),
            _ConsistencyBar(
              label: 'Consistency',
              value: data.consistencyScore,
              color: data.consistencyScore >= 0.7 ? AppColors.primary : Colors.orange,
            ),
            const SizedBox(height: 10),
            Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              _MiniStat('Calories', data.avgCalories.toStringAsFixed(0), AppColors.calories),
              _MiniStat('Protein', '${data.avgProtein.toStringAsFixed(0)}g', AppColors.protein),
              _MiniStat('Carbs', '${data.avgCarbs.toStringAsFixed(0)}g', AppColors.carbs),
              _MiniStat('Fat', '${data.avgFat.toStringAsFixed(0)}g', AppColors.fat),
            ]),
          ],
        ),
      ),
    );
  }
}

class _MiniStat extends StatelessWidget {
  final String label, value;
  final Color color;
  const _MiniStat(this.label, this.value, this.color);

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Text(value, style: TextStyle(color: color, fontWeight: FontWeight.w700, fontSize: 14)),
      Text(label, style: Theme.of(context).textTheme.bodySmall),
    ]);
  }
}

// ── Activity Burned Summary ───────────────────────────────────────────────────

class _ActivityBurnedSummaryCard extends StatelessWidget {
  final List<DailyNutrition> data;
  const _ActivityBurnedSummaryCard({required this.data});

  @override
  Widget build(BuildContext context) {
    final totalBurned = data.fold<double>(0, (s, d) => s + d.burnedCalories);
    if (totalBurned <= 0) return const SizedBox.shrink();

    final daysWithActivity =
        data.where((d) => d.burnedCalories > 0).length;
    final avgBurned =
        daysWithActivity > 0 ? totalBurned / daysWithActivity : 0.0;
    const green = Color(0xFF27AE60);
    final theme = Theme.of(context);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: green.withValues(alpha:0.12),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.directions_run_rounded,
                    color: green, size: 18),
              ),
              const SizedBox(width: 10),
              Text(
                'Activity Burned',
                style: theme.textTheme.titleSmall
                    ?.copyWith(fontWeight: FontWeight.w700),
              ),
            ]),
            const SizedBox(height: 12),
            Row(children: [
              Expanded(
                child: _ActivityStat(
                  value: '${totalBurned.toStringAsFixed(0)}',
                  unit: 'kcal',
                  label: 'Total Burned',
                  color: green,
                ),
              ),
              Expanded(
                child: _ActivityStat(
                  value: '$daysWithActivity',
                  unit: 'days',
                  label: 'Active Days',
                  color: AppColors.primary,
                ),
              ),
              Expanded(
                child: _ActivityStat(
                  value: '${avgBurned.toStringAsFixed(0)}',
                  unit: 'kcal/day',
                  label: 'Avg Burned',
                  color: AppColors.secondary,
                ),
              ),
            ]),
          ],
        ),
      ),
    );
  }
}

class _ActivityStat extends StatelessWidget {
  final String value, unit, label;
  final Color color;
  const _ActivityStat(
      {required this.value,
      required this.unit,
      required this.label,
      required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      RichText(
        text: TextSpan(
          children: [
            TextSpan(
              text: value,
              style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  color: color),
            ),
            TextSpan(
              text: ' $unit',
              style: TextStyle(
                  fontSize: 11,
                  color: color.withValues(alpha:0.7)),
            ),
          ],
        ),
      ),
      const SizedBox(height: 2),
      Text(label,
          style: Theme.of(context)
              .textTheme
              .bodySmall
              ?.copyWith(fontSize: 11)),
    ]);
  }
}

// ── Empty State ───────────────────────────────────────────────────────────────

class _EmptyState extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.bar_chart, size: 64, color: AppColors.primary.withValues(alpha:0.3)),
            const SizedBox(height: 16),
            Text('No data yet',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.grey)),
            const SizedBox(height: 8),
            Text('Start logging meals to see your nutrition history.',
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodySmall),
          ],
        ),
      ),
    );
  }
}
