import '../models/food_item.dart';
import 'local_food_repository.dart';

// Labels that carry zero food-specificity — filtered out before searching.
// Colors are NOT in this set; they are handled separately via _colorContextMap.
const _skipLabels = {
  'food', 'dish', 'meal', 'ingredient', 'cuisine', 'recipe',
  'tableware', 'plate', 'bowl', 'cup', 'glass', 'mug', 'container',
  'cutlery', 'fork', 'spoon', 'knife', 'chopstick',
  'table', 'kitchen', 'restaurant', 'dining', 'buffet',
  'photography', 'still life', 'product', 'object', 'material', 'close-up', 'macro',
  'serving', 'portion', 'cooking', 'baking',
};

// Pure color labels that are only useful when combined with another label.
const _colorLabels = {
  'yellow', 'red', 'green', 'brown', 'white', 'orange', 'golden',
  'dark', 'light', 'pale',
};

// When a color appears together with one of the co-labels (left), search the
// associated food terms. Keyed by color → map of co-label → search terms.
const _colorContextMap = <String, Map<String, List<String>>>{
  'yellow': {
    'liquid':   ['masoor dal', 'moong dal', 'dal'],
    'soup':     ['dal', 'moong dal'],
    'sauce':    ['dal', 'curry'],
    'rice':     ['moong khichdi', 'khichdi'],
    'drink':    ['lassi', 'mango lassi', 'turmeric milk'],
    'fruit':    ['mango', 'banana', 'pineapple'],
    'powder':   ['turmeric', 'besan'],
  },
  'orange': {
    'liquid':   ['masoor dal', 'tomato soup', 'shorba'],
    'sauce':    ['butter chicken', 'tikka masala', 'curry'],
    'fruit':    ['orange', 'mango'],
    'drink':    ['orange juice', 'mango lassi'],
  },
  'green': {
    'liquid':   ['palak soup', 'green chutney'],
    'sauce':    ['palak paneer', 'saag', 'green chutney'],
    'vegetable':['saag', 'palak', 'methi', 'beans'],
    'leaf':     ['palak', 'methi', 'saag', 'drumstick leaves'],
    'drink':    ['green tea', 'lassi'],
    'curry':    ['palak paneer', 'saag chicken'],
  },
  'brown': {
    'liquid':   ['kosha mangsho', 'mutton curry', 'beef curry'],
    'sauce':    ['kosha', 'korma', 'nihari'],
    'meat':     ['kosha mangsho', 'tandoori'],
    'bread':    ['roti', 'paratha', 'chapati'],
    'drink':    ['tea', 'coffee', 'chai'],
  },
  'white': {
    'liquid':   ['milk', 'raita', 'lassi'],
    'rice':     ['rice', 'steamed rice', 'bhat'],
    'cheese':   ['paneer', 'chhena'],
    'drink':    ['milk', 'doodh'],
    'grain':    ['rice', 'bhat'],
  },
  'golden': {
    'bread':    ['luchi', 'puri', 'paratha', 'naan'],
    'fried':    ['luchi', 'telebhaja', 'pakora', 'singara'],
    'sweet':    ['gulab jamun', 'jalebi', 'ladoo'],
  },
  'red': {
    'liquid':   ['tomato soup', 'rasam', 'tandoori'],
    'sauce':    ['tomato gravy', 'butter chicken', 'makhani'],
    'fruit':    ['tomato', 'watermelon', 'strawberry'],
    'meat':     ['tandoori chicken', 'seekh kebab'],
  },
};

// Maps generic ML Kit labels → LocalFoodRepository category values.
// Used as a last-resort fallback when direct search returns < 3 results.
const _categoryHints = <String, List<String>>{
  'fish':          ['fish'],
  'seafood':       ['fish'],
  'meat':          ['meat', 'chicken'],
  'chicken':       ['chicken'],
  'egg':           ['egg'],
  'rice':          ['rice'],
  'bread':         ['bread', 'roti'],
  'flatbread':     ['roti', 'bread'],
  'dal':           ['dal'],
  'lentil':        ['dal'],
  'vegetable':     ['vegetable'],
  'fruit':         ['fruit'],
  'dairy':         ['dairy'],
  'milk':          ['dairy'],
  'sweet':         ['sweets', 'dessert'],
  'dessert':       ['sweets', 'dessert'],
  'cake':          ['sweets', 'dessert'],
  'snack':         ['snack'],
  'noodle':        ['noodle'],
  'pasta':         ['noodle'],
  'soup':          ['soup'],
  'beverage':      ['beverage'],
  'drink':         ['beverage'],
  'curry':         ['curry', 'vegetable', 'meat'],
  'salad':         ['salad'],
  'pickle':        ['pickle'],
  'oil':           ['oil'],
};

const _synonyms = <String, List<String>>{
  // ── Breads / flatbread ───────────────────────────────────────────────────
  'flatbread':        ['roti', 'paratha', 'chapati', 'naan', 'luchi'],
  'bread':            ['bread', 'roti', 'pav'],
  'tortilla':         ['roti', 'chapati'],
  'pita':             ['roti', 'naan'],
  'lavash':           ['roti', 'paratha'],
  'crepe':            ['dosa'],
  'pancake':          ['dosa', 'uttapam', 'chilla'],
  'luchi':            ['luchi', 'puri'],
  'puri':             ['puri', 'luchi'],
  'paratha':          ['paratha', 'stuffed paratha'],
  'chapati':          ['chapati', 'roti'],
  'naan':             ['naan', 'kulcha'],

  // ── Rice / grain dishes ──────────────────────────────────────────────────
  'pilaf':            ['pulao', 'biryani'],
  'risotto':          ['khichdi', 'pulao'],
  'fried rice':       ['fried rice'],
  'rice dish':        ['biryani', 'pulao', 'khichdi', 'bhat'],
  'congee':           ['khichdi', 'panta bhat'],
  'porridge':         ['khichdi', 'upma', 'oatmeal'],
  'biryani':          ['biryani', 'chicken biryani', 'mutton biryani'],
  'pulao':            ['pulao', 'vegetable pulao'],
  'khichdi':          ['khichdi', 'moong khichdi'],
  'bhat':             ['steamed rice', 'bhat', 'rice'],
  'rice':             ['steamed rice', 'bhat', 'rice'],
  'panta bhat':       ['panta bhat', 'fermented rice'],
  'upma':             ['upma'],
  'idli':             ['idli'],
  'dosa':             ['dosa', 'masala dosa', 'plain dosa'],
  'uttapam':          ['uttapam'],

  // ── Dal varieties ────────────────────────────────────────────────────────
  'legume':           ['dal', 'lentil', 'chana', 'rajma'],
  'lentil':           ['dal', 'masoor dal', 'moong dal'],
  'bean':             ['rajma', 'chana', 'beans'],
  'chickpea':         ['chana', 'chole'],
  'pulse':            ['dal', 'lentil', 'chana'],
  'dal':              ['dal', 'masoor dal', 'moong dal', 'chana dal'],
  'masoor':           ['masoor dal'],
  'moong':            ['moong dal', 'moong khichdi'],
  'chana dal':        ['chana dal'],
  'toor dal':         ['toor dal', 'arhar dal'],
  'arhar':            ['toor dal', 'arhar dal'],
  'rajma':            ['rajma', 'kidney beans'],
  'chole':            ['chole', 'chana masala'],

  // ── Curry / stew ────────────────────────────────────────────────────────
  'curry':            ['curry', 'sabzi', 'kosha', 'masala'],
  'stew':             ['curry', 'jhol', 'korma'],
  'gravy':            ['curry', 'sabzi', 'korma', 'jhol'],
  'korma':            ['korma', 'chicken korma'],
  'masala':           ['masala', 'tikka masala', 'chana masala'],
  'jhol':             ['jhol', 'machher jhol'],
  'kosha':            ['kosha mangsho', 'kosha'],

  // ── Fish / Bengali fish dishes ───────────────────────────────────────────
  'fish':             ['fish', 'machh', 'rohu', 'katla', 'ilish'],
  'seafood':          ['fish', 'prawn', 'shrimp', 'crab', 'chingri'],
  'fish dish':        ['machher jhol', 'fish curry', 'fish fry', 'ilish'],
  'shellfish':        ['prawn', 'shrimp', 'crab', 'chingri'],
  'salmon':           ['hilsa', 'ilish', 'salmon'],
  'hilsa':            ['ilish', 'hilsa', 'ilish bhapa'],
  'ilish':            ['ilish', 'hilsa', 'ilish bhapa', 'sorshe ilish'],
  'rohu':             ['rohu', 'rui mach'],
  'katla':            ['katla', 'katla mach'],
  'prawn':            ['chingri', 'prawn', 'shrimp'],
  'chingri':          ['chingri malai curry', 'chingri bhuna', 'prawn'],
  'shrimp':           ['chingri', 'prawn', 'shrimp'],
  'crab':             ['crab', 'crab curry'],
  'tuna':             ['tuna', 'fish'],
  'mackerel':         ['mackerel', 'fish'],

  // ── Chicken / meat ───────────────────────────────────────────────────────
  'grilled meat':     ['kebab', 'tikka', 'tandoori'],
  'skewer':           ['kebab', 'seekh', 'satay'],
  'kebab':            ['kebab', 'seekh kebab', 'shami kebab'],
  'roasted meat':     ['roast', 'tandoori', 'kebab'],
  'meatball':         ['kofta', 'meatball'],
  'chicken':          ['chicken curry', 'murgi', 'murgi bhuna', 'chicken biryani'],
  'grilled chicken':  ['tandoori chicken', 'chicken tikka'],
  'fried chicken':    ['chicken fry', 'fried chicken'],
  'mutton':           ['mutton curry', 'kosha mangsho', 'mutton biryani'],
  'beef':             ['beef curry', 'beef bhuna'],
  'pork':             ['pork curry'],

  // ── Eggs ────────────────────────────────────────────────────────────────
  'omelette':         ['omelette', 'egg', 'anda'],
  'scrambled egg':    ['scrambled egg', 'anda bhurji', 'egg'],
  'boiled egg':       ['boiled egg', 'anda boiled'],
  'fried egg':        ['egg fry', 'dim fry', 'egg'],
  'egg':              ['egg', 'dim', 'anda'],
  'dim':              ['dim', 'egg curry', 'dimer curry'],

  // ── Bengali vegetables ───────────────────────────────────────────────────
  'vegetable':        ['sabzi', 'tarkari', 'saag', 'shukto'],
  'stir fry':         ['sabzi', 'bhaji', 'stir fry', 'tarkari'],
  'sauté':            ['sabzi', 'bhaji', 'posto'],
  'potato':           ['aloo', 'potato', 'aloo posto'],
  'aloo':             ['aloo curry', 'aloo posto', 'dum aloo'],
  'posto':            ['aloo posto', 'begun posto', 'posto'],
  'eggplant':         ['begun bhaja', 'begun', 'baingan bharta'],
  'aubergine':        ['begun bhaja', 'begun', 'eggplant'],
  'begun':            ['begun bhaja', 'begun bhaté', 'begun posto'],
  'shukto':           ['shukto'],
  'saag':             ['saag', 'palak', 'methi', 'sarson saag'],
  'spinach':          ['palak', 'saag', 'palak paneer'],
  'methi':            ['methi', 'methi thepla'],
  'pumpkin':          ['kumro', 'pumpkin curry', 'kaddu'],
  'kumro':            ['kumro', 'kumro chingri'],
  'cauliflower':      ['phulkopi', 'aloo gobi', 'gobi curry'],
  'cabbage':          ['bandha kopi', 'cabbage sabzi'],
  'bitter gourd':     ['karela', 'uchhe bhaja'],
  'okra':             ['bhindi', 'lady finger'],
  'drumstick':        ['sajina', 'drumstick curry', 'moringa'],
  'tomato':           ['tomato curry', 'tamatar'],
  'onion':            ['pyaz', 'onion', 'piyaj'],

  // ── Bengali sweets / desserts ────────────────────────────────────────────
  'dessert':          ['sandesh', 'mishti doi', 'rasogolla', 'payesh', 'ladoo', 'halwa'],
  'pudding':          ['payesh', 'kheer', 'halwa'],
  'sweet':            ['sandesh', 'mishti', 'barfi', 'ladoo', 'halwa'],
  'cake':             ['cake', 'sandesh'],
  'cookie':           ['biscuit', 'nankhatai'],
  'biscuit':          ['biscuit', 'cookie'],
  'sandesh':          ['sandesh'],
  'rasogolla':        ['rasogolla', 'rasgulla'],
  'payesh':           ['payesh', 'kheer payesh'],
  'mishti doi':       ['mishti doi', 'sweet curd'],
  'halwa':            ['halwa', 'suji halwa', 'gajar halwa'],
  'kheer':            ['kheer', 'payesh'],
  'ladoo':            ['ladoo', 'besan ladoo', 'motichur ladoo'],
  'barfi':            ['barfi', 'coconut barfi'],
  'jalebi':           ['jalebi'],
  'gulab jamun':      ['gulab jamun'],
  'rasgulla':         ['rasogolla', 'rasgulla'],
  'pitha':            ['pitha', 'puli pitha', 'chitoi pitha'],

  // ── Bengali snacks / street food ────────────────────────────────────────
  'fritter':          ['pakora', 'telebhaja', 'bhajia', 'bonda'],
  'dumpling':         ['momo', 'modak'],
  'pastry':           ['singara', 'samosa', 'kachori', 'puff'],
  'spring roll':      ['spring roll', 'roll'],
  'puff':             ['puff pastry', 'samosa'],
  'snack':            ['muri', 'bhujia', 'namkeen', 'telebhaja', 'nimki', 'chakli'],
  'singara':          ['singara', 'samosa'],
  'samosa':           ['samosa', 'singara'],
  'pakora':           ['pakora', 'telebhaja', 'bhajia'],
  'telebhaja':        ['telebhaja', 'pakora', 'fried snack'],
  'nimki':            ['nimki'],
  'muri':             ['muri', 'puffed rice', 'jhal muri'],
  'puffed rice':      ['muri', 'murmura'],
  'churmur':          ['churmur', 'muri'],
  'jhalmuri':         ['jhal muri', 'muri'],
  'chaat':            ['chaat', 'puchka', 'papri chaat'],
  'puchka':           ['puchka', 'pani puri', 'golgappa'],

  // ── Dairy / paneer ───────────────────────────────────────────────────────
  'cheese':           ['paneer', 'chhena', 'cheese'],
  'yogurt':           ['dahi', 'doi', 'curd', 'raita', 'lassi'],
  'cottage cheese':   ['paneer', 'chhena'],
  'paneer':           ['paneer', 'palak paneer', 'paneer curry', 'chena'],
  'chhena':           ['chhena', 'sandesh', 'chhena poda'],
  'dahi':             ['dahi', 'doi', 'curd'],
  'doi':              ['mishti doi', 'doi', 'dahi'],
  'milk':             ['milk', 'doodh', 'mishti doi'],
  'butter':           ['butter', 'makhan'],
  'ghee':             ['ghee', 'clarified butter'],
  'lassi':            ['lassi', 'sweet lassi', 'salty lassi'],

  // ── Soup / shorba ───────────────────────────────────────────────────────
  'soup':             ['soup', 'shorba', 'rasam', 'dal shorba'],
  'broth':            ['soup', 'yakhni', 'shorba'],
  'rasam':            ['rasam', 'tomato rasam'],

  // ── Beverages ────────────────────────────────────────────────────────────
  'coffee':           ['coffee', 'cafe'],
  'tea':              ['tea', 'chai', 'masala chai'],
  'milkshake':        ['lassi', 'milkshake'],
  'smoothie':         ['lassi', 'smoothie'],
  'juice':            ['juice', 'fruit juice'],
  'water':            ['water', 'coconut water'],
  'coconut water':    ['coconut water', 'daab'],

  // ── Condiments / sides ───────────────────────────────────────────────────
  'salad':            ['salad', 'raita', 'kachumber'],
  'pickle':           ['pickle', 'achar'],
  'chutney':          ['chutney', 'tomato chutney', 'green chutney'],
  'dip':              ['chutney', 'raita', 'hummus'],
  'raita':            ['raita', 'cucumber raita'],
  'achar':            ['achar', 'pickle'],

  // ── Pilaf / noodles ──────────────────────────────────────────────────────
  'noodle':           ['noodle', 'vermicelli', 'sevai'],
  'pasta':            ['pasta', 'noodle'],
  'noodles':          ['noodle', 'vermicelli', 'maggi'],
};

class FoodLabelMatcher {
  static const _perLabelLimit = 20;
  static const _maxLabelsToProcess = 12;
  static const _categoryFallbackLimit = 6;

  static String? _cacheKey;
  static List<FoodItem>? _cacheResult;

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

    // Step 1: separate colors from content labels
    final colors = normalized.where((l) => _colorLabels.contains(l)).toSet();
    final contentLabels = normalized.where((l) => !_colorLabels.contains(l)).toList();

    // Step 2: resolve color-context hints
    final colorSearchTerms = <_SearchTerm>[];
    for (final color in colors) {
      final colorMap = _colorContextMap[color];
      if (colorMap == null) continue;
      for (final coLabel in contentLabels) {
        final terms = colorMap[coLabel];
        if (terms != null) {
          for (final t in terms) {
            colorSearchTerms.add(_SearchTerm(t, 0.60));
          }
        }
      }
      // Generic fallback: color alone with no matching co-label
      if (colorSearchTerms.isEmpty) {
        for (final entry in colorMap.entries) {
          for (final t in entry.value) {
            colorSearchTerms.add(_SearchTerm(t, 0.40));
          }
        }
      }
    }

    // Step 3: build primary search terms from content labels
    final searchTerms = <_SearchTerm>[...colorSearchTerms];
    for (int i = 0; i < contentLabels.length; i++) {
      final label = contentLabels[i];
      if (label.isEmpty) continue;

      final posWeight = (1.0 - i * 0.1).clamp(0.3, 1.0);
      final isSkipped = _skipLabels.contains(label);

      final syns = _synonyms[label];
      if (syns != null) {
        for (final syn in syns) {
          searchTerms.add(_SearchTerm(syn, posWeight * 0.95));
        }
      } else if (!isSkipped) {
        searchTerms.add(_SearchTerm(label, posWeight));
      }
    }

    // Step 4: multi-label combinations for the top non-skipped labels
    final usable = contentLabels
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

    // Step 5: score accumulation
    final scores = <String, double>{};
    final foodMap = <String, FoodItem>{};

    for (final term in searchTerms) {
      final hits =
          LocalFoodRepository.search(term.query, limit: _perLabelLimit);
      for (int j = 0; j < hits.length; j++) {
        final food = hits[j];
        final rankWeight = (1.0 - j * 0.04).clamp(0.2, 1.0);
        final multiBonus = scores.containsKey(food.id) ? 1.7 : 1.0;
        scores[food.id] =
            (scores[food.id] ?? 0.0) + term.weight * rankWeight * multiBonus;
        foodMap[food.id] = food;
      }
    }

    var ranked = scores.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    var results =
        ranked.take(maxResults).map((e) => foodMap[e.key]!).toList();

    // Step 6: category fallback when we have too few results
    if (results.length < 3) {
      final seenIds = results.map((f) => f.id).toSet();
      final categories = <String>{};

      for (final label in normalized) {
        final cats = _categoryHints[label];
        if (cats != null) categories.addAll(cats);
      }

      for (final cat in categories) {
        if (results.length >= maxResults) break;
        final fallback = LocalFoodRepository.search('',
            category: cat, limit: _categoryFallbackLimit);
        for (final food in fallback) {
          if (!seenIds.contains(food.id)) {
            results.add(food);
            seenIds.add(food.id);
            if (results.length >= maxResults) break;
          }
        }
      }
    }

    return results.take(maxResults).toList();
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
