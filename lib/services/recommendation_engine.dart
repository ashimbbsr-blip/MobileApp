import '../models/meal_entry.dart';
import '../models/nutrition_goals.dart';

// ── Output model ──────────────────────────────────────────────────────────────

class DailyRecommendation {
  final double targetCalories;
  final double consumedCalories;
  final double proteinG;
  final double carbsG;
  final double fatG;
  final int walkingSteps;
  final int walkingMinutes;
  final List<String> insights;
  final List<String> recommendations;
  final String dailyTip;

  const DailyRecommendation({
    required this.targetCalories,
    required this.consumedCalories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.walkingSteps,
    required this.walkingMinutes,
    required this.insights,
    required this.recommendations,
    required this.dailyTip,
  });

  bool get hasData => consumedCalories > 50;
  bool get isOnTarget {
    final pct = targetCalories > 0 ? consumedCalories / targetCalories : 0.0;
    return pct >= 0.85 && pct <= 1.1;
  }
}

// ── Pattern struct ────────────────────────────────────────────────────────────

class _Pattern {
  final int fried;
  final int sweets;
  final int beverage;
  final int alcohol;
  final int beer;
  final int spirits; // whiskey, rum, vodka, gin
  final int wine;
  final int vegetables;
  final int proteinFoods;

  const _Pattern({
    this.fried = 0,
    this.sweets = 0,
    this.beverage = 0,
    this.alcohol = 0,
    this.beer = 0,
    this.spirits = 0,
    this.wine = 0,
    this.vegetables = 0,
    this.proteinFoods = 0,
  });

  String get dominantDrink {
    if (beer >= spirits && beer >= wine && beer > 0) return 'beer';
    if (spirits > 0) return 'spirits';
    if (wine > 0) return 'wine';
    return 'alcohol';
  }
}

// ── Engine ────────────────────────────────────────────────────────────────────

class RecommendationEngine {
  static DailyRecommendation analyze({
    required NutritionGoals goals,
    required List<MealEntry> meals,
    required String lang,
  }) {
    final bn = lang == 'bn';

    // ── Totals ────────────────────────────────────────────────────────────────
    final cal = meals.fold<double>(0, (s, m) => s + m.calories);
    final pro = meals.fold<double>(0, (s, m) => s + m.proteinG);
    final car = meals.fold<double>(0, (s, m) => s + m.carbsG);
    final fat = meals.fold<double>(0, (s, m) => s + m.fatG);

    // ── Activity suggestion ───────────────────────────────────────────────────
    // Burn off excess calories above goal at ~4 kcal/min (moderate walking).
    // Default to 30 min when on-target; cap at 60 min to stay actionable.
    final excess = (cal - goals.calories).clamp(0.0, 500.0);
    final walkMins = (excess > 0 ? excess / 4.0 : 30.0).clamp(15.0, 60.0).round();
    final walkSteps = walkMins * 95; // ~95 steps/min — Indian average moderate pace (WHO 2004)

    // ── Food-pattern detection ────────────────────────────────────────────────
    final p = _detectPatterns(meals);

    // ── Ratio helpers ─────────────────────────────────────────────────────────
    final calPct  = goals.calories > 0 ? cal / goals.calories : 0.0;
    final proPct  = goals.proteinG > 0 ? pro / goals.proteinG : 0.0;

    // ── Build insights (max 2) ─────────────────────────────────────────────────
    final insights = <String>[];

    if (cal > 50) {
      if (calPct >= 0.85 && calPct <= 1.1) {
        insights.add(bn
            ? 'আজকের ক্যালোরি লক্ষ্যমাত্রা একদম সঠিক আছে।'
            : 'Calorie intake is right on target today.');
      } else if (calPct > 1.1) {
        insights.add(bn
            ? 'আজ ক্যালোরি একটু বেশি হয়েছে।'
            : 'Calorie intake was a little high today.');
      }

      if (proPct >= 0.8) {
        insights.add(bn
            ? 'আজ প্রোটিনের পরিমাণ ভালো আছে।'
            : 'Protein intake looks balanced today.');
      } else if (proPct < 0.5 && insights.length < 2) {
        insights.add(bn
            ? 'আজ প্রোটিন একটু কম হয়েছে।'
            : 'Protein was a little low today.');
      }

      if (p.fried >= 2 && insights.length < 2) {
        insights.add(bn
            ? 'আজ ভাজাপোড়া একটু বেশি হয়েছে।'
            : 'Fried food was a bit high today.');
      } else if (p.vegetables >= 2 && insights.length < 2) {
        insights.add(bn
            ? 'আজ সবজি ও ফলের পরিমাণ ভালো ছিল!'
            : 'Good variety of vegetables and fruits today!');
      }

      if (p.alcohol >= 1 && insights.length < 2) {
        final drink = p.dominantDrink;
        final drinkName = bn
            ? (drink == 'beer' ? 'বিয়ার' : drink == 'spirits' ? 'স্পিরিট' : drink == 'wine' ? 'ওয়াইন' : 'অ্যালকোহল')
            : (drink == 'beer' ? 'beer' : drink == 'spirits' ? 'spirits' : drink == 'wine' ? 'wine' : 'alcohol');
        insights.add(bn
            ? 'আজ $drinkName খাওয়া হয়েছে — হাইড্রেশনের দিকে নজর রাখুন।'
            : '${drinkName[0].toUpperCase()}${drinkName.substring(1)} in today\'s log — stay hydrated.');
      }
    }

    // ── Build recommendations (max 3) ─────────────────────────────────────────
    final recs = <String>[];

    if (p.fried >= 2) {
      recs.add(bn
          ? 'কাল একটু হালকা রান্না ব্যবহার করুন — সিদ্ধ বা ভাপে রান্না ভালো বিকল্প।'
          : 'Consider lighter cooking tomorrow — steamed or boiled works great.');
    }
    if (proPct < 0.65) {
      recs.add(bn
          ? 'কাল একটু বেশি প্রোটিন যোগ করুন — ডাল, ডিম বা মাছ ভালো।'
          : 'Add a bit more protein tomorrow — dal, eggs, or fish are great choices.');
    }
    if (p.vegetables == 0 && cal > 200) {
      recs.add(bn
          ? 'পরের খাবারে একটা ছোট সবজির পদ বা ফল যোগ করুন।'
          : 'Try adding a vegetable side or some fruit to your next meal.');
    }
    if (p.sweets >= 2 && recs.length < 3) {
      recs.add(bn
          ? 'মিষ্টির পাশে তাজা ফল রাখলে ভালো ভারসাম্য হবে।'
          : 'Balance the sweet treats with some fresh fruit.');
    }
    if (p.alcohol >= 1 && recs.length < 3) {
      if (p.alcohol >= 3) {
        recs.add(bn
            ? 'অনেকটা পানীয় খাওয়া হয়েছে — ঘুমানোর আগে এক গ্লাস নারকেল জল বা ওআরএস পান করুন।'
            : 'That\'s a few rounds — your liver says hi. A glass of coconut water or ORS before bed helps a lot.');
      } else if (p.beer >= 1 && p.spirits == 0) {
        recs.add(bn
            ? 'বিয়ারের পরে হালকা খাবার খান — খালি পেটে থাকবেন না। ঘুমানোর আগে জল পান করুন।'
            : 'Beer night? Don\'t crash on an empty stomach — a light khichdi or toast keeps things smooth.');
      } else if (p.spirits >= 1) {
        recs.add(bn
            ? 'হুইস্কি/রামের পরে ইলেক্ট্রোলাইট দরকার — কলা বা ডাব জলে ম্যাজিক কাজ করবে।'
            : 'After those spirits, your body craves electrolytes — a banana or coconut water works wonders.');
      } else {
        recs.add(bn
            ? 'প্রচুর জল পান করুন এবং পরের খাবারটা হালকা রাখুন।'
            : 'Drink plenty of water and keep the next meal light.');
      }
    }
    if (recs.length < 3 && walkSteps > 0) {
      recs.add(bn
          ? 'একটা সন্ধ্যার হাঁটা হজমে সাহায্য করতে পারে।'
          : 'A short evening walk may help with digestion.');
    }

    // ── Determine single daily tip ─────────────────────────────────────────────
    final tip = _pickDailyTip(
      bn: bn,
      cal: cal,
      calPct: calPct,
      proPct: proPct,
      pattern: p,
      steps: walkSteps,
      mins: walkMins,
    );

    return DailyRecommendation(
      targetCalories: goals.calories,
      consumedCalories: cal,
      proteinG: pro,
      carbsG: car,
      fatG: fat,
      walkingSteps: walkSteps,
      walkingMinutes: walkMins,
      insights: insights,
      recommendations: recs,
      dailyTip: tip,
    );
  }

  // ── Pattern detection ─────────────────────────────────────────────────────

  static _Pattern _detectPatterns(List<MealEntry> meals) {
    int fried = 0, sweets = 0, bev = 0, alcohol = 0, beer = 0, spirits = 0, wine = 0, veg = 0, prot = 0;

    for (final m in meals) {
      final cat = m.foodItem.category ?? '';
      final name = m.foodItem.name.toLowerCase();
      final kws = (m.foodItem.keywords ?? []).join(' ').toLowerCase();
      final combined = '$name $kws';

      // Categories
      if (cat == 'sweets') sweets++;
      if (cat == 'beverage') bev++;
      if (cat == 'vegetable' || cat == 'fruit') veg++;
      if (cat == 'meat' || cat == 'fish' || cat == 'dairy' || cat == 'protein' ||
          cat == 'dal' || cat == 'egg' || cat == 'nut' || cat == 'grain') prot++;

      // Fried food detection
      if (kws.contains('fried') || kws.contains('fry') ||
          name.contains('fried') || name.contains(' fry') ||
          name.contains('bhaja') || name.contains('bhaji') ||
          name.contains('pakoda') || name.contains('vada') ||
          name.contains('samosa') || name.contains('puri')) {
        fried++;
      }

      // Alcohol detection — English (word-boundary) + Bengali Unicode keywords
      final nameBn = m.foodItem.nameBn?.toLowerCase() ?? '';
      final combinedBn = '$nameBn $kws';

      final isBeer = RegExp(r'\b(beer|lager|ale|stout|bira)\b').hasMatch(combined)
          || combinedBn.contains('বিয়ার') || combinedBn.contains('বিয়র')
          || combinedBn.contains('লাগার');
      final isSpirits = RegExp(r'\b(whisky|whiskey|rum|vodka|gin|brandy|tequila|baijiu)\b').hasMatch(combined)
          || combinedBn.contains('হুইস্কি') || combinedBn.contains('রাম')
          || combinedBn.contains('ভদকা') || combinedBn.contains('জিন');
      final isWine = RegExp(r'\b(wine|champagne|prosecco|sake)\b').hasMatch(combined)
          || combinedBn.contains('ওয়াইন') || combinedBn.contains('শ্যাম্পেন');
      final isAlcohol = isBeer || isSpirits || isWine ||
          combined.contains('alcohol') ||
          combined.contains('cocktail') ||
          combined.contains('liquor') ||
          combinedBn.contains('অ্যালকোহল') ||
          combinedBn.contains('মদ');

      if (isAlcohol) {
        alcohol++;
        if (isBeer) beer++;
        if (isSpirits) spirits++;
        if (isWine) wine++;
      }
    }

    return _Pattern(
      fried: fried,
      sweets: sweets,
      beverage: bev,
      alcohol: alcohol,
      beer: beer,
      spirits: spirits,
      wine: wine,
      vegetables: veg,
      proteinFoods: prot,
    );
  }

  // ── Single daily tip selection (priority ordered) ────────────────────────

  static String _pickDailyTip({
    required bool bn,
    required double cal,
    required double calPct,
    required double proPct,
    required _Pattern pattern,
    required int steps,
    required int mins,
  }) {
    // Nothing logged yet
    if (cal < 50) {
      return bn
          ? 'আজকের খাবার লগ করুন এবং ব্যক্তিগত পরামর্শ পান!'
          : 'Log your meals today to get personalized daily insights!';
    }

    // Very under calories (< 40% of target)
    if (calPct < 0.4) {
      return bn
          ? 'নিয়মিত খাওয়াদাওয়া করুন — শরীরকে সারাদিন শক্তি যোগাতে নিয়মিত খাবার দরকার।'
          : 'Don\'t skip meals — your body needs regular fuel to stay energized throughout the day.';
    }

    // Very low protein (< 40% of goal)
    if (proPct < 0.4 && cal > 200) {
      return bn
          ? 'আজ প্রোটিন অনেক কম হয়েছে। কাল ডাল, ডিম বা মুরগি খেলে অনেকক্ষণ পেট ভরা থাকবে।'
          : 'Protein is quite low today. Dal, eggs, or chicken tomorrow will keep you fuller for longer.';
    }

    // High fried food
    if (pattern.fried >= 2) {
      return bn
          ? 'আজ একটু ভাজাপোড়া বেশি হয়েছে! রাতের খাবারে ডাল বা স্যুপ রাখলে ভারসাম্য আসবে।'
          : 'Lots of fried food today! A light dinner with dal or soup will nicely balance it out.';
    }

    // No vegetables at all
    if (pattern.vegetables == 0 && cal > 300) {
      return bn
          ? 'আজ সবজি বা ফল খাওয়া হয়নি। পরের খাবারে একটু সবজি যোগ করার চেষ্টা করুন।'
          : 'No vegetables or fruit today — try adding a small portion to your next meal.';
    }

    // High sweets
    if (pattern.sweets >= 2) {
      return bn
          ? 'আজ মিষ্টি বেশি খাওয়া হয়েছে! এর পরে একটু তাজা ফল বা জল পান করুন।'
          : 'Sweet treats are great in moderation! Follow up with some fresh fruit or water.';
    }

    // Significantly over calories (> 125% of target)
    if (calPct > 1.25) {
      return bn
          ? 'আজ একটু বেশি খাওয়া হয়েছে — কিছু নেই! কাল হালকা খাবার দিয়ে শুরু করুন।'
          : 'A little over today — no worries! Start fresh with a lighter breakfast tomorrow.';
    }

    // Alcohol present
    if (pattern.alcohol >= 1) {
      if (pattern.alcohol >= 3) {
        return bn
            ? 'বেশ কয়েকটি পানীয় খাওয়া হয়েছে! ঘুমানোর আগে ওআরএস বা নারকেল জল পান করুন — সকালে অনেক ভালো লাগবে।'
            : 'Quite a few drinks today! ORS or coconut water before bed is your best friend right now — future you will be grateful.';
      }
      final drink = pattern.dominantDrink;
      if (drink == 'beer') {
        return bn
            ? 'বিয়ার রাতে হালকা খাবার সেরা — খিচুড়ি বা টোস্ট ভালো বিকল্প। প্রচুর জল পান করুন!'
            : 'Beer night done right — pair it with something light like khichdi or toast, and chase it with water!';
      } else if (drink == 'spirits') {
        return bn
            ? 'হুইস্কি/রামের পরে ঘুমানোর আগে একটা কলা আর ডাব জল খান — ইলেক্ট্রোলাইট যাদু করবে।'
            : 'Whiskey / rum evening? A banana and coconut water before bed keeps the morning much kinder.';
      } else if (drink == 'wine') {
        return bn
            ? 'ওয়াইনের পরে পরের খাবারটা হালকা রাখুন এবং প্রচুর জল পান করুন।'
            : 'After wine, keep the next meal light and make sure to hydrate well before sleeping.';
      }
      return bn
          ? 'প্রচুর জল পান করুন এবং পরের খাবারটা হালকা ও সহজে হজমযোগ্য রাখুন।'
          : 'Drink plenty of water and keep the next meal light and easy to digest.';
    }

    // Right on target — celebrate it
    if (calPct >= 0.85 && calPct <= 1.1) {
      return bn
          ? 'দারুণ! আজকের ক্যালোরি লক্ষ্যমাত্রা একদম সঠিকভাবে পূরণ হয়েছে।'
          : 'Excellent! You\'re right on track with your calorie goal today. Keep it up!';
    }

    // Moderately low protein
    if (proPct < 0.65) {
      return bn
          ? 'ঘুমানোর আগে এক মুঠো বাদাম বা এক গ্লাস দুধ প্রোটিন বাড়াতে সাহায্য করবে।'
          : 'A handful of nuts or a glass of milk before bed can give your protein a small boost.';
    }

    // Default — activity tip
    if (mins > 0) {
      final minsDisplay = ((mins / 5).round() * 5).clamp(10, 90);
      final stepsDisplay = ((steps / 500).round() * 500);
      return bn
          ? 'আজ প্রায় $minsDisplay মিনিট হাঁটলে (~${_formatNumber(stepsDisplay)} স্টেপ) হজম ভালো হবে।'
          : 'A walk of around $minsDisplay minutes (~${_formatNumber(stepsDisplay)} steps) may help with digestion today.';
    }

    return bn
        ? 'সুস্বাস্থ্যের জন্য প্রতিদিন পর্যাপ্ত জল পান করুন।'
        : 'Stay hydrated — drinking enough water is one of the easiest health wins.';
  }

  static String _formatNumber(int n) {
    if (n >= 1000) {
      return '${(n / 1000).toStringAsFixed(n % 1000 == 0 ? 0 : 1)}k';
    }
    return n.toString();
  }
}
