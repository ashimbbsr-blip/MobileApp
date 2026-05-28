import '../models/food_item.dart';
import 'local_food_repository.dart';

// Labels that carry zero food-specificity — filtered out before searching.
// Keep this list TIGHT. Over-filtering kills recall.
const _skipLabels = {
  // Absolute generics
  'food', 'dish', 'meal', 'ingredient', 'cuisine', 'recipe',
  // Tableware / props
  'tableware', 'plate', 'bowl', 'cup', 'glass', 'mug', 'container',
  'cutlery', 'fork', 'spoon', 'knife', 'chopstick',
  // Settings / context
  'table', 'kitchen', 'restaurant', 'dining', 'buffet',
  // Photography metadata
  'photography', 'still life', 'product', 'object', 'material', 'close-up', 'macro',
  // Purely abstract
  'serving', 'portion', 'cooking', 'baking',
  // Colours (not useful alone)
  'yellow', 'red', 'green', 'brown', 'white', 'orange', 'golden',
};

// Maps common ML Kit labels → one or more better local-DB search terms.
// This is the primary tool for bridging Western food terminology → South Asian DB.
const _synonyms = <String, List<String>>{
  // Bread / flatbread
  'flatbread':      ['roti', 'paratha', 'chapati', 'naan'],
  'bread':          ['bread', 'roti', 'pav'],
  'tortilla':       ['roti', 'chapati'],
  'pita':           ['roti', 'naan'],
  'lavash':         ['roti', 'paratha'],
  'crepe':          ['dosa'],
  'pancake':        ['dosa', 'uttapam', 'chilla'],

  // Rice / grain dishes
  'pilaf':          ['pulao', 'biryani'],
  'risotto':        ['khichdi', 'pulao'],
  'fried rice':     ['fried rice'],
  'rice dish':      ['biryani', 'pulao', 'khichdi'],
  'congee':         ['khichdi', 'congee'],
  'porridge':       ['khichdi', 'upma', 'oatmeal'],

  // Lentils / legumes
  'legume':         ['dal', 'lentil', 'chana', 'rajma'],
  'lentil':         ['dal', 'lentil'],
  'bean':           ['rajma', 'chana', 'beans'],
  'chickpea':       ['chana', 'chole'],
  'pulse':          ['dal', 'lentil', 'chana'],

  // Curry / stew
  'curry':          ['curry', 'sabzi', 'kosha', 'masala'],
  'stew':           ['curry', 'jhol', 'korma'],
  'gravy':          ['curry', 'sabzi', 'korma'],

  // Fried / street food
  'fritter':        ['pakora', 'bhajia', 'bonda'],
  'dumpling':       ['momo', 'modak', 'kozhukattai'],
  'pastry':         ['samosa', 'kachori', 'puff'],
  'spring roll':    ['spring roll', 'roll'],
  'puff':           ['puff', 'samosa'],
  'snack':          ['bhujia', 'namkeen', 'chakli', 'murukku'],

  // Noodle / pasta
  'noodle':         ['noodle', 'vermicelli', 'sevai'],
  'pasta':          ['pasta', 'noodle'],
  'noodles':        ['noodle', 'vermicelli'],

  // Meat
  'grilled meat':   ['kebab', 'tikka', 'tandoori'],
  'skewer':         ['kebab', 'seekh', 'satay'],
  'kebab':          ['kebab', 'seekh', 'shami'],
  'roasted meat':   ['roast', 'tandoori', 'kebab'],
  'meatball':       ['kofta', 'meatball'],

  // Seafood
  'seafood':        ['fish', 'prawn', 'shrimp', 'crab'],
  'fish dish':      ['fish curry', 'fish fry', 'machli'],
  'shellfish':      ['prawn', 'shrimp', 'crab'],

  // Dairy / paneer
  'cheese':         ['paneer', 'cheese'],
  'yogurt':         ['curd', 'raita', 'lassi', 'dahi'],
  'cottage cheese': ['paneer'],

  // Sweets / dessert
  'dessert':        ['halwa', 'kheer', 'barfi', 'ladoo', 'gulab jamun'],
  'pudding':        ['kheer', 'halwa', 'payesh'],
  'sweet':          ['halwa', 'barfi', 'ladoo', 'mithai'],
  'cake':           ['cake', 'barfi'],
  'cookie':         ['biscuit', 'nankhatai'],
  'biscuit':        ['biscuit', 'cookie'],

  // Beverage
  'coffee':         ['coffee', 'cafe'],
  'tea':            ['tea', 'chai'],
  'milkshake':      ['lassi', 'milkshake'],
  'smoothie':       ['lassi', 'smoothie'],

  // Breakfast
  'omelette':       ['egg', 'omelette', 'anda'],
  'scrambled egg':  ['egg', 'anda'],
  'boiled egg':     ['egg', 'anda boiled'],

  // Salad / sides
  'salad':          ['salad', 'raita', 'kachumber'],
  'pickle':         ['pickle', 'achar'],
  'chutney':        ['chutney', 'raita'],
  'dip':            ['chutney', 'raita', 'hummus'],

  // Soup
  'soup':           ['soup', 'shorba', 'rasam'],
  'broth':          ['soup', 'yakhni'],

  // Vegetable preparations
  'stir fry':       ['sabzi', 'bhaji', 'stir fry'],
  'sauté':          ['sabzi', 'bhaji'],
};

class FoodLabelMatcher {
  static const _perLabelLimit = 20;
  static const _maxLabelsToProcess = 10;

  static String? _cacheKey;
  static List<FoodItem>? _cacheResult;

  /// Matches ML Kit [rawLabels] (confidence-sorted, highest first) against
  /// the local food database. Returns up to [maxResults] ranked [FoodItem]s.
  static Future<List<FoodItem>> match(
    List<String> rawLabels, {
    int maxResults = 6,
  }) async {
    if (!LocalFoodRepository.isReady || rawLabels.isEmpty) return [];

    final key = rawLabels.take(_maxLabelsToProcess).join('|');
    if (key == _cacheKey && _cacheResult != null) return _cacheResult!;

    final result = _doMatch(rawLabels, maxResults);
    _cacheKey = key;
    _cacheResult = result;
    return result;
  }

  static List<FoodItem> _doMatch(List<String> rawLabels, int maxResults) {
    final normalized = rawLabels
        .map((l) => l.toLowerCase().trim())
        .take(_maxLabelsToProcess)
        .toList();

    // Build effective search terms: original + synonyms, skipping pure noise.
    final searchTerms = <_SearchTerm>[];
    for (int i = 0; i < normalized.length; i++) {
      final label = normalized[i];
      if (label.isEmpty) continue;

      final posWeight = (1.0 - i * 0.1).clamp(0.3, 1.0);
      final isSkipped = _skipLabels.contains(label);

      // If we have synonyms, use them instead of (or in addition to) the raw label.
      final syns = _synonyms[label];
      if (syns != null) {
        for (final syn in syns) {
          searchTerms.add(_SearchTerm(syn, posWeight * 0.95));
        }
      } else if (!isSkipped) {
        searchTerms.add(_SearchTerm(label, posWeight));
      }
    }

    // Also try multi-label combinations for the top 3 non-skipped labels.
    // e.g. ["rice", "chicken"] → search "chicken rice"
    final usable = normalized
        .where((l) => !_skipLabels.contains(l) && l.length >= 3)
        .take(4)
        .toList();
    for (int a = 0; a < usable.length; a++) {
      for (int b = a + 1; b < usable.length; b++) {
        searchTerms.add(_SearchTerm('${usable[a]} ${usable[b]}', 0.85));
        searchTerms.add(_SearchTerm('${usable[b]} ${usable[a]}', 0.80));
      }
    }

    if (searchTerms.isEmpty) return [];

    // Score accumulator
    final scores = <String, double>{};
    final foodMap = <String, FoodItem>{};

    for (final term in searchTerms) {
      final hits = LocalFoodRepository.search(term.query, limit: _perLabelLimit);
      for (int j = 0; j < hits.length; j++) {
        final food = hits[j];
        final rankWeight = (1.0 - j * 0.04).clamp(0.2, 1.0);
        // Multi-label bonus: food matching several independent terms is more likely.
        final multiBonus = scores.containsKey(food.id) ? 1.7 : 1.0;
        scores[food.id] =
            (scores[food.id] ?? 0.0) + term.weight * rankWeight * multiBonus;
        foodMap[food.id] = food;
      }
    }

    final ranked = scores.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return ranked.take(maxResults).map((e) => foodMap[e.key]!).toList();
  }

  static void clearCache() {
    _cacheKey = null;
    _cacheResult = null;
  }
}

class _SearchTerm {
  final String query;
  final double weight;
  const _SearchTerm(this.query, this.weight);
}
