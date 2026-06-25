import 'package:hive/hive.dart';

part 'food_item.g.dart';

@HiveType(typeId: 1)
class FoodItem extends HiveObject {
  @HiveField(0)
  String id;

  @HiveField(1)
  String name;

  @HiveField(2)
  String? brand;

  @HiveField(3)
  double servingSize;

  @HiveField(4)
  String servingUnit;

  @HiveField(5)
  double calories;

  @HiveField(6)
  double proteinG;

  @HiveField(7)
  double carbsG;

  @HiveField(8)
  double fatG;

  @HiveField(9)
  double fiberG;

  @HiveField(10)
  double? vitaminAMcg;

  @HiveField(11)
  double? vitaminCMg;

  @HiveField(12)
  double? vitaminDMcg;

  @HiveField(13)
  double? calciumMg;

  @HiveField(14)
  double? ironMg;

  @HiveField(15)
  double? potassiumMg;

  @HiveField(16)
  double? magnesiumMg;

  @HiveField(17)
  double? zincMg;

  @HiveField(18)
  String? usdaFdcId;

  @HiveField(19)
  bool isCustom;

  // ── Bilingual & classification fields (added v2) ──────────────────────────

  @HiveField(20)
  String? nameBn;

  @HiveField(21)
  String? category;

  @HiveField(22)
  String? source; // 'local' | 'indb' | 'usda' | 'custom'

  @HiveField(23)
  List<String>? keywords;

  @HiveField(24)
  double? vitaminB12Mcg;

  @HiveField(25)
  double? alcoholG; // grams of ethanol per serving (7 kcal/g, Atwater)

  @HiveField(26)
  double? sodiumMg; // milligrams of sodium per serving

  // ── Search-pipeline fields (v8 dataset, not persisted to Hive) ───────────
  // These are populated from food_master_v8_0.json at load time and used only
  // for in-memory search ranking. Custom foods (isCustom=true) leave them null.

  String? family;          // food family cluster (e.g. "rice", "chicken")
  int?    searchPriority;  // 0-100 combined ranking signal
  int?    qualityScore;    // 0-100 data quality
  int?    popularityScore; // 0-100 food popularity
  List<String>? aliases;   // alternate search terms
  String? nutritionSource;     // ifct | brand_official | bd_fct | usda | ifct_recipe
  String? nutritionConfidence; // very_high | high | medium | low

  FoodItem({
    required this.id,
    required this.name,
    this.brand,
    required this.servingSize,
    required this.servingUnit,
    required this.calories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.fiberG,
    this.vitaminAMcg,
    this.vitaminCMg,
    this.vitaminDMcg,
    this.calciumMg,
    this.ironMg,
    this.potassiumMg,
    this.magnesiumMg,
    this.zincMg,
    this.usdaFdcId,
    this.isCustom = false,
    this.nameBn,
    this.category,
    this.source,
    this.keywords,
    this.vitaminB12Mcg,
    this.alcoholG,
    this.sodiumMg,
    this.family,
    this.searchPriority,
    this.qualityScore,
    this.popularityScore,
    this.aliases,
    this.nutritionSource,
    this.nutritionConfidence,
  });

  // ── Factory: compact local JSON schema ───────────────────────────────────

  factory FoodItem.fromLocalJson(Map<String, dynamic> m) {
    final (size, unit) = _parseServing((m['s'] as String?) ?? '100g');
    return FoodItem(
      id: 'local_${m['id']}',
      name: (m['en'] as String?) ?? '',
      nameBn: m['bn'] as String?,
      brand: null,
      servingSize: size,
      servingUnit: unit,
      calories: (m['k'] as num?)?.toDouble() ?? 0.0,
      proteinG: (m['p'] as num?)?.toDouble() ?? 0.0,
      carbsG: (m['c'] as num?)?.toDouble() ?? 0.0,
      fatG: (m['f'] as num?)?.toDouble() ?? 0.0,
      fiberG: (m['fi'] as num?)?.toDouble() ?? 0.0,
      vitaminAMcg: (m['va'] as num?)?.toDouble(),
      vitaminCMg:  (m['vc'] as num?)?.toDouble(),
      vitaminDMcg: (m['vd'] as num?)?.toDouble(),
      calciumMg:   (m['ca'] as num?)?.toDouble(),
      ironMg:      (m['fe'] as num?)?.toDouble(),
      zincMg:      (m['zn'] as num?)?.toDouble(),
      magnesiumMg:    (m['mg']  as num?)?.toDouble(),
      potassiumMg:    (m['pot'] as num?)?.toDouble(),
      vitaminB12Mcg:  (m['b12'] as num?)?.toDouble(),
      alcoholG:       (m['alc_g'] as num?)?.toDouble(),
      sodiumMg:       (m['na'] as num?)?.toDouble(),
      category: _normalizeCategory(m['cat'] as String?),
      keywords: (m['kw'] as List?)?.cast<String>(),
      source: m['src'] as String? ?? 'local',
      isCustom: false,
      family:              m['family'] as String?,
      searchPriority:      (m['search_priority'] as num?)?.toInt(),
      qualityScore:        (m['quality_score'] as num?)?.toInt(),
      popularityScore:     (m['popularity_score'] as num?)?.toInt(),
      aliases:             (m['aliases'] as List?)?.cast<String>(),
      nutritionSource:     m['nutrition_source'] as String?,
      nutritionConfidence: m['nutrition_confidence'] as String?,
    );
  }

  // Normalise legacy/variant dataset category names to UI category names.
  static String? _normalizeCategory(String? cat) {
    switch (cat) {
      case 'veg':             return 'vegetable';
      case 'leafy_vegetable': return 'shaak';
      case 'drink':           return 'beverage';
      case 'fitness':         return 'other';
      case 'brand':           return 'snack';
      case 'condiment':       return 'snack';
      case 'diet':            return 'other';
      case 'meal':            return 'other';
      case 'dessert':         return 'sweet';
      default:          return cat;
    }
  }

  // Converts any serving string to (grams, 'g') or (ml, 'ml').
  // All dataset entries are pre-normalised to "Xg"/"Xml"; this also handles
  // legacy custom foods that may carry old descriptive serving strings.
  static (double, String) _parseServing(String s) {
    final raw = s.trim();

    // (Xg) in parentheses  →  "1 bowl (14g)"
    final pg = RegExp(r'\((\d+(?:\.\d+)?)\s*g\)', caseSensitive: false).firstMatch(raw);
    if (pg != null) {
      final g = double.tryParse(pg.group(1)!);
      if (g != null && g > 0) return (g, 'g');
    }

    // (Xml) in parentheses  →  "1 glass (200ml)"
    final pm = RegExp(r'\((\d+(?:\.\d+)?)\s*ml\)', caseSensitive: false).firstMatch(raw);
    if (pm != null) {
      final ml = double.tryParse(pm.group(1)!);
      if (ml != null && ml > 0) return (ml, 'ml');
    }

    // Leading "Xg"  →  "250g" or "250g serving"
    final gm = RegExp(r'^(\d+(?:\.\d+)?)\s*g\b', caseSensitive: false).firstMatch(raw);
    if (gm != null) return (double.tryParse(gm.group(1)!) ?? 100.0, 'g');

    // Leading "Xml"
    final mm = RegExp(r'^(\d+(?:\.\d+)?)\s*ml\b', caseSensitive: false).firstMatch(raw);
    if (mm != null) return (double.tryParse(mm.group(1)!) ?? 200.0, 'ml');

    // "X unit" with known unit → gram equivalent
    final um = RegExp(r'^(\d+(?:\.\d+)?)\s+(.+)$').firstMatch(raw);
    if (um != null) {
      final n = double.tryParse(um.group(1)!) ?? 1.0;
      final u = um.group(2)!.trim().toLowerCase();
      const unitMap = <String, double>{
        'bowl': 250, 'plate': 300, 'cup': 240, 'glass': 240,
        'serving': 100, 'portion': 150,
        'tablespoon': 15, 'tbsp': 15, 'teaspoon': 5, 'tsp': 5,
        'slice': 30, 'large slice': 50,
        'pc': 60, 'pcs': 60, 'piece': 60, 'pieces': 60,
        'oz': 28.35, 'kg': 1000,
        'small': 100, 'medium': 150, 'large': 200,
        'scoop': 30, 'handful': 30, 'sachet': 30,
      };
      for (final e in unitMap.entries) {
        if (u.startsWith(e.key)) return ((n * e.value).roundToDouble(), 'g');
      }
      // numeric-only fallback: treat the number as grams
      if (n >= 5) return (n, 'g');
    }

    // Bare number
    final num = double.tryParse(raw);
    if (num != null && num > 0) return (num, 'g');

    return (100.0, 'g');
  }

  // ── Display name (language-aware) ────────────────────────────────────────

  String displayName(String lang) =>
      lang == 'bn' && nameBn != null && nameBn!.isNotEmpty ? nameBn! : name;

  // ── Scaling ───────────────────────────────────────────────────────────────

  FoodItem scaledTo(double grams) {
    final factor = grams / servingSize;
    return FoodItem(
      id: id,
      name: name,
      nameBn: nameBn,
      brand: brand,
      servingSize: grams,
      servingUnit: servingUnit,
      calories: calories * factor,
      proteinG: proteinG * factor,
      carbsG: carbsG * factor,
      fatG: fatG * factor,
      fiberG: fiberG * factor,
      vitaminAMcg: vitaminAMcg != null ? vitaminAMcg! * factor : null,
      vitaminCMg: vitaminCMg != null ? vitaminCMg! * factor : null,
      vitaminDMcg: vitaminDMcg != null ? vitaminDMcg! * factor : null,
      calciumMg: calciumMg != null ? calciumMg! * factor : null,
      ironMg: ironMg != null ? ironMg! * factor : null,
      potassiumMg: potassiumMg != null ? potassiumMg! * factor : null,
      magnesiumMg: magnesiumMg != null ? magnesiumMg! * factor : null,
      zincMg: zincMg != null ? zincMg! * factor : null,
      vitaminB12Mcg: vitaminB12Mcg != null ? vitaminB12Mcg! * factor : null,
      alcoholG: alcoholG != null ? alcoholG! * factor : null,
      sodiumMg: sodiumMg != null ? sodiumMg! * factor : null,
      usdaFdcId: usdaFdcId,
      isCustom: isCustom,
      category: category,
      source: source,
      keywords: keywords,
      family: family,
      searchPriority: searchPriority,
      qualityScore: qualityScore,
      popularityScore: popularityScore,
      aliases: aliases,
      nutritionSource: nutritionSource,
      nutritionConfidence: nutritionConfidence,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'nameBn': nameBn,
    'brand': brand,
    'servingSize': servingSize,
    'servingUnit': servingUnit,
    'calories': calories,
    'proteinG': proteinG,
    'carbsG': carbsG,
    'fatG': fatG,
    'fiberG': fiberG,
    'usdaFdcId': usdaFdcId,
    'isCustom': isCustom,
    'category': category,
    'source': source,
  };
}
