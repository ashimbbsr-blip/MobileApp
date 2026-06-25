import '../../models/food_item.dart';
import '../../models/meal_entry.dart';
import '../../models/monthly_summary.dart';
import '../../models/user_profile.dart';

/// Full-fidelity (loss-less) serialisers for the backup payload.
///
/// Unlike [FoodItem.toJson] — which is intentionally lossy for lightweight UI
/// export — these capture every field so a restore reproduces the original
/// records byte-for-byte. Keys are kept short to minimise pre-compression size.
class BackupSerializers {
  // ── FoodItem ───────────────────────────────────────────────────────────────

  static Map<String, dynamic> foodToJson(FoodItem f) {
    final m = <String, dynamic>{
      'id': f.id,
      'n': f.name,
      'ss': f.servingSize,
      'su': f.servingUnit,
      'k': f.calories,
      'p': f.proteinG,
      'c': f.carbsG,
      'ft': f.fatG,
      'fi': f.fiberG,
      'ic': f.isCustom,
    };
    void put(String key, Object? v) {
      if (v != null) m[key] = v;
    }

    put('nb', f.nameBn);
    put('br', f.brand);
    put('va', f.vitaminAMcg);
    put('vc', f.vitaminCMg);
    put('vd', f.vitaminDMcg);
    put('ca', f.calciumMg);
    put('fe', f.ironMg);
    put('pot', f.potassiumMg);
    put('mg', f.magnesiumMg);
    put('zn', f.zincMg);
    put('b12', f.vitaminB12Mcg);
    put('alc', f.alcoholG);
    put('na', f.sodiumMg);
    put('fdc', f.usdaFdcId);
    put('cat', f.category);
    put('src', f.source);
    put('kw', f.keywords);
    return m;
  }

  static FoodItem foodFromJson(Map m) {
    double? d(String k) => (m[k] as num?)?.toDouble();
    return FoodItem(
      id: (m['id'] as String?) ?? 'food_${DateTime.now().microsecondsSinceEpoch}',
      name: (m['n'] as String?) ?? '',
      nameBn: m['nb'] as String?,
      brand: m['br'] as String?,
      servingSize: d('ss') ?? 100,
      servingUnit: (m['su'] as String?) ?? 'g',
      calories: d('k') ?? 0,
      proteinG: d('p') ?? 0,
      carbsG: d('c') ?? 0,
      fatG: d('ft') ?? 0,
      fiberG: d('fi') ?? 0,
      vitaminAMcg: d('va'),
      vitaminCMg: d('vc'),
      vitaminDMcg: d('vd'),
      calciumMg: d('ca'),
      ironMg: d('fe'),
      potassiumMg: d('pot'),
      magnesiumMg: d('mg'),
      zincMg: d('zn'),
      vitaminB12Mcg: d('b12'),
      alcoholG: d('alc'),
      sodiumMg: d('na'),
      usdaFdcId: m['fdc'] as String?,
      isCustom: (m['ic'] as bool?) ?? false,
      category: m['cat'] as String?,
      source: m['src'] as String?,
      keywords: (m['kw'] as List?)?.cast<String>(),
    );
  }

  // ── MealEntry ────────────────────────────────────────────────────────────────

  static Map<String, dynamic> mealToJson(MealEntry m) => {
        'id': m.id,
        'mt': m.mealType,
        'q': m.quantityG,
        'at': m.loggedAt.toIso8601String(),
        'dk': m.dateKey,
        'food': foodToJson(m.foodItem),
      };

  static MealEntry mealFromJson(Map m) => MealEntry(
        id: (m['id'] as String?) ?? 'meal_${DateTime.now().microsecondsSinceEpoch}',
        mealType: (m['mt'] as String?) ?? 'snack',
        quantityG: (m['q'] as num?)?.toDouble() ?? 0,
        loggedAt: DateTime.tryParse((m['at'] as String?) ?? '') ?? DateTime.now(),
        dateKey: (m['dk'] as String?) ?? '',
        foodItem: foodFromJson((m['food'] as Map?) ?? const {}),
      );

  // ── UserProfile ──────────────────────────────────────────────────────────────

  static Map<String, dynamic> profileToJson(UserProfile p) => {
        'id': p.id,
        'age': p.age,
        'gender': p.gender,
        'heightCm': p.heightCm,
        'weightKg': p.weightKg,
        'activityLevel': p.activityLevel,
        'fitnessGoal': p.fitnessGoal,
        'createdAt': p.createdAt.toIso8601String(),
        'fullName': p.fullName,
        'dateOfBirth': p.dateOfBirth?.toIso8601String(),
        'profileImagePath': p.profileImagePath,
        'email': p.email,
        'pregnancyStatus': p.pregnancyStatus,
      };

  static UserProfile profileFromJson(Map m) => UserProfile(
        id: (m['id'] as String?) ?? 'profile',
        age: (m['age'] as num?)?.toInt() ?? 0,
        gender: (m['gender'] as String?) ?? 'other',
        heightCm: (m['heightCm'] as num?)?.toDouble() ?? 0,
        weightKg: (m['weightKg'] as num?)?.toDouble() ?? 0,
        activityLevel: (m['activityLevel'] as String?) ?? 'moderately_active',
        fitnessGoal: (m['fitnessGoal'] as String?) ?? 'maintain',
        createdAt: DateTime.tryParse((m['createdAt'] as String?) ?? '') ?? DateTime.now(),
        fullName: m['fullName'] as String?,
        dateOfBirth: DateTime.tryParse((m['dateOfBirth'] as String?) ?? ''),
        profileImagePath: m['profileImagePath'] as String?,
        email: m['email'] as String?,
        pregnancyStatus: m['pregnancyStatus'] as String?,
      );

  // ── MonthlySummary ───────────────────────────────────────────────────────────

  static Map<String, dynamic> monthlyToJson(MonthlySummary s) => {
        'year': s.year,
        'month': s.month,
        'avgCalories': s.avgCalories,
        'avgProtein': s.avgProtein,
        'avgCarbs': s.avgCarbs,
        'avgFat': s.avgFat,
        'avgFiber': s.avgFiber,
        'consistencyScore': s.consistencyScore,
        'daysLogged': s.daysLogged,
      };

  static MonthlySummary monthlyFromJson(Map m) => MonthlySummary(
        year: (m['year'] as num?)?.toInt() ?? 0,
        month: (m['month'] as num?)?.toInt() ?? 1,
        avgCalories: (m['avgCalories'] as num?)?.toDouble() ?? 0,
        avgProtein: (m['avgProtein'] as num?)?.toDouble() ?? 0,
        avgCarbs: (m['avgCarbs'] as num?)?.toDouble() ?? 0,
        avgFat: (m['avgFat'] as num?)?.toDouble() ?? 0,
        avgFiber: (m['avgFiber'] as num?)?.toDouble() ?? 0,
        consistencyScore: (m['consistencyScore'] as num?)?.toDouble() ?? 0,
        daysLogged: (m['daysLogged'] as num?)?.toInt() ?? 0,
      );
}
