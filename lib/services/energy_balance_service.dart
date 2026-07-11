import '../models/user_profile.dart';

// ── MET values (Compendium of Physical Activities, Ainsworth 2011) ───────────
// kcal/min = MET × weightKg / 60
const double _walkMet = 3.5;   // moderate walking 5 km/h
const double _runMet = 9.8;    // running 9 km/h
const double _cycleMet = 8.0;  // cycling ~15 km/h
const double _stepsPerMin = 100.0;
const double _referenceWeightKg = 65.0; // Indian adult reference (ICMR 2020)

double _walkRate(double kg) => _walkMet * kg / 60.0;
double _runRate(double kg)  => _runMet  * kg / 60.0;
double _cycleRate(double kg)=> _cycleMet * kg / 60.0;

// ── Model ─────────────────────────────────────────────────────────────────────

class EnergyBalance {
  final double consumedKcal;
  final double tdeeKcal;
  final double targetKcal;    // goal-adjusted TDEE
  final double balanceKcal;   // consumed - target (positive = surplus)
  final bool isDeficit;
  final int walkingMins;
  final int walkingSteps;
  final int runningMins;
  final int cyclingMins;
  final String summaryEn;
  final String summaryBn;
  final String contextEn;
  final String contextBn;
  final BalanceStatus status;

  const EnergyBalance({
    required this.consumedKcal,
    required this.tdeeKcal,
    required this.targetKcal,
    required this.balanceKcal,
    required this.isDeficit,
    required this.walkingMins,
    required this.walkingSteps,
    required this.runningMins,
    required this.cyclingMins,
    required this.summaryEn,
    required this.summaryBn,
    required this.contextEn,
    required this.contextBn,
    required this.status,
  });

  bool get hasData => consumedKcal > 50;
  double get absBalance => balanceKcal.abs();

  // Percentage of target consumed (capped for display)
  double get percentOfTarget =>
      targetKcal > 0 ? (consumedKcal / targetKcal).clamp(0.0, 1.5) : 0.0;
}

enum BalanceStatus { noData, deepDeficit, deficit, onTarget, slightSurplus, surplus }

// ── Service ───────────────────────────────────────────────────────────────────

class EnergyBalanceService {
  static EnergyBalance calculate({
    required double consumedKcal,
    required double tdeeKcal,
    required double targetKcal,
    required String goal,
    UserProfile? profile,
  }) {
    if (consumedKcal < 50 || tdeeKcal == 0) {
      return EnergyBalance(
        consumedKcal: consumedKcal,
        tdeeKcal: tdeeKcal,
        targetKcal: targetKcal,
        balanceKcal: 0,
        isDeficit: false,
        walkingMins: 0,
        walkingSteps: 0,
        runningMins: 0,
        cyclingMins: 0,
        summaryEn: 'Log your meals to see your energy balance.',
        summaryBn: 'এনার্জি ব্যালেন্স দেখতে খাবার লগ করুন।',
        contextEn: '',
        contextBn: '',
        status: BalanceStatus.noData,
      );
    }

    final balance = consumedKcal - targetKcal;
    final isDeficit = balance < 0;
    final abs = balance.abs();

    // Activity equivalents — weight-personalized via MET × weightKg / 60
    final kg = profile?.weightKg ?? _referenceWeightKg;
    final walkMins = (abs / _walkRate(kg)).round().clamp(0, 240);
    final walkSteps = (walkMins * _stepsPerMin).round();
    final runMins = (abs / _runRate(kg)).round().clamp(0, 120);
    final cycleMins = (abs / _cycleRate(kg)).round().clamp(0, 180);

    final absRounded = abs.round();
    final balanceSign = balance > 0 ? '+' : '';
    final balanceStr = '$balanceSign${balance.round()}';

    final status = _status(balance, targetKcal);

    final summaryEn =
        'You consumed ${consumedKcal.round()} kcal against a target of '
        '${targetKcal.round()} kcal ($balanceStr kcal).';
    final summaryBn =
        'আপনি ${consumedKcal.round()} kcal খেয়েছেন। লক্ষ্য ছিল '
        '${targetKcal.round()} kcal ($balanceStr kcal)।';

    final contextEn = _contextEn(status, absRounded, walkMins, walkSteps);
    final contextBn = _contextBn(status, absRounded, walkMins, walkSteps);

    return EnergyBalance(
      consumedKcal: consumedKcal,
      tdeeKcal: tdeeKcal,
      targetKcal: targetKcal,
      balanceKcal: balance,
      isDeficit: isDeficit,
      walkingMins: walkMins,
      walkingSteps: walkSteps,
      runningMins: runMins,
      cyclingMins: cycleMins,
      summaryEn: summaryEn,
      summaryBn: summaryBn,
      contextEn: contextEn,
      contextBn: contextBn,
      status: status,
    );
  }

  static BalanceStatus _status(double balance, double target) {
    final pct = target > 0 ? balance / target : 0.0;
    if (pct < -0.20) return BalanceStatus.deepDeficit;
    if (pct < -0.05) return BalanceStatus.deficit;
    if (pct <= 0.05) return BalanceStatus.onTarget;
    if (pct <= 0.15) return BalanceStatus.slightSurplus;
    return BalanceStatus.surplus;
  }

  static String _contextEn(BalanceStatus s, int abs, int wMins, int wSteps) {
    switch (s) {
      case BalanceStatus.deepDeficit:
        return 'You\'re significantly below your calorie target today. '
            'Make sure you\'re eating enough to feel energized — consistent under-eating can slow your metabolism.';
      case BalanceStatus.deficit:
        return 'Slightly under target — that\'s perfectly fine! '
            'A ~$abs kcal deficit is approximately $wMins min of walking (${_fmtSteps(wSteps)} steps).';
      case BalanceStatus.onTarget:
        return 'Right on target! Your energy intake is well-balanced for the day. Keep it up!';
      case BalanceStatus.slightSurplus:
        return 'Slightly above target by ~$abs kcal. '
            'A brisk $wMins-minute walk (~${_fmtSteps(wSteps)} steps) would easily balance this out.';
      case BalanceStatus.surplus:
        return 'You\'re ~$abs kcal above your target today. '
            'Consider a $wMins-min walk (~${_fmtSteps(wSteps)} steps) or lighter meals tomorrow.';
      case BalanceStatus.noData:
        return '';
    }
  }

  static String _contextBn(BalanceStatus s, int abs, int wMins, int wSteps) {
    switch (s) {
      case BalanceStatus.deepDeficit:
        return 'আজ ক্যালোরি লক্ষ্যমাত্রার থেকে অনেক কম খাওয়া হয়েছে। '
            'শক্তি বজায় রাখতে পর্যাপ্ত খাবার খান — নিয়মিত কম খেলে বিপাকক্রিয়া ধীর হয়ে যায়।';
      case BalanceStatus.deficit:
        return 'লক্ষ্যের থেকে সামান্য কম — এটা ঠিকই আছে! '
            '~$abs kcal ঘাটতি মানে প্রায় $wMins মিনিট হাঁটা (${_fmtSteps(wSteps)} স্টেপ)।';
      case BalanceStatus.onTarget:
        return 'একদম লক্ষ্যমাত্রায়! আজকের এনার্জি গ্রহণ সুষম। চালিয়ে যান!';
      case BalanceStatus.slightSurplus:
        return 'লক্ষ্যের থেকে ~$abs kcal বেশি। '
            '$wMins মিনিটের একটি হাঁটা (~${_fmtSteps(wSteps)} স্টেপ) এটি সহজেই ব্যালেন্স করতে পারে।';
      case BalanceStatus.surplus:
        return 'আজ লক্ষ্যের থেকে ~$abs kcal বেশি খাওয়া হয়েছে। '
            '$wMins মিনিট হাঁটুন (~${_fmtSteps(wSteps)} স্টেপ) বা কাল হালকা খান।';
      case BalanceStatus.noData:
        return '';
    }
  }

  static String _fmtSteps(int steps) {
    if (steps >= 1000) {
      return '${(steps / 1000).toStringAsFixed(steps % 1000 == 0 ? 0 : 1)}k';
    }
    return steps.toString();
  }

  // Weekly summary for history tab
  static WeeklyEnergyBalance weeklyBalance({
    required List<({DateTime date, double calories})> dailyData,
    required double targetKcal,
  }) {
    final logged = dailyData.where((d) => d.calories > 50).toList();
    if (logged.isEmpty) {
      return const WeeklyEnergyBalance(
        totalBalance: 0,
        avgBalance: 0,
        surplusDays: 0,
        deficitDays: 0,
        onTargetDays: 0,
        dailyBalances: [],
      );
    }

    final balances = dailyData.map((d) {
      if (d.calories < 50) return (date: d.date, balance: 0.0, hasData: false);
      return (date: d.date, balance: d.calories - targetKcal, hasData: true);
    }).toList();

    final loggedBalances = balances.where((b) => b.hasData).toList();
    final total = loggedBalances.fold<double>(0, (s, b) => s + b.balance);
    final avg = total / loggedBalances.length;

    int surplus = 0, deficit = 0, onTarget = 0;
    for (final b in loggedBalances) {
      final pct = targetKcal > 0 ? b.balance / targetKcal : 0.0;
      if (pct > 0.05) {
        surplus++;
      } else if (pct < -0.05) {
        deficit++;
      } else {
        onTarget++;
      }
    }

    return WeeklyEnergyBalance(
      totalBalance: total,
      avgBalance: avg,
      surplusDays: surplus,
      deficitDays: deficit,
      onTargetDays: onTarget,
      dailyBalances: balances,
    );
  }
}

class WeeklyEnergyBalance {
  final double totalBalance;
  final double avgBalance;
  final int surplusDays;
  final int deficitDays;
  final int onTargetDays;
  final List<({DateTime date, double balance, bool hasData})> dailyBalances;

  const WeeklyEnergyBalance({
    required this.totalBalance,
    required this.avgBalance,
    required this.surplusDays,
    required this.deficitDays,
    required this.onTargetDays,
    required this.dailyBalances,
  });

  bool get hasData => dailyBalances.any((b) => b.hasData);
}
