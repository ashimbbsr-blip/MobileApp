import 'dart:async';
import 'dart:convert';
import 'package:flutter/services.dart';

/// Loads search_index_v2.json into memory and provides fast candidate lookup.
///
/// v2 structure:
///   en_prefix     : Map<prefix, List<id>>
///   bn_prefix     : Map<prefix, List<id>>
///   alias_lookup  : Map<term,   List<id>>
///   family_index  : Map<family, List<id>>
///   top_foods     : List<id>
class LocalSearchService {
  static Map<String, List<int>>? _enPrefix;
  static Map<String, List<int>>? _bnPrefix;
  static Map<String, List<int>>? _aliasLookup;
  static Map<String, List<int>>? _familyIndex;
  static List<int> _topFoods = const [];

  static Completer<void>? _loadCompleter;

  static Future<void> ensureLoaded() async {
    if (_enPrefix != null) return;
    if (_loadCompleter != null) return _loadCompleter!.future;
    _loadCompleter = Completer<void>();
    try {
      final raw = await rootBundle.loadString('assets/data/search_index_v2.json');
      final map = json.decode(raw) as Map<String, dynamic>;
      _enPrefix    = _parseSection(map['en_prefix']);
      _bnPrefix    = _parseSection(map['bn_prefix']);
      _aliasLookup = _parseSection(map['alias_lookup']);
      _familyIndex = _parseSection(map['family_index']);
      _topFoods    = (map['top_foods'] as List?)?.cast<int>() ?? const [];
      _loadCompleter!.complete();
    } catch (e) {
      final c = _loadCompleter!;
      _loadCompleter = null;
      c.completeError(e);
      rethrow;
    }
  }

  static Map<String, List<int>> _parseSection(dynamic raw) {
    if (raw == null) return {};
    return (raw as Map<String, dynamic>)
        .map((k, v) => MapEntry(k, (v as List).cast<int>()));
  }

  /// Returns candidate food IDs for the given query.
  ///
  /// Strategy (in order, all additive):
  ///   1. Per-word prefix lookup (EN: 2/3/4-char; BN: 2/3/4-char)
  ///   2. Full-phrase alias lookup (any exact match in alias_lookup)
  ///   3. Per-word alias lookup (each word checked against alias_lookup)
  ///   4. Family index lookup when query matches a known family name
  ///   5. Bengali prefix via romanization table for EN queries
  static Set<int> candidateIds(String query) {
    if (_enPrefix == null) return {};
    final q = query.toLowerCase().trim();
    if (q.isEmpty) return {};

    final result = <int>{};
    final isBengali = _containsBengali(q);

    // ── 1. Per-word prefix lookup ──────────────────────────────────────────────
    final words = q.split(RegExp(r'[\s/\-]+'));
    for (final word in words) {
      if (word.length < 2) continue;

      if (isBengali) {
        // Normalize Bengali input (fix common independent-vowel after consonant)
        final normalized = _normalizeBengali(word);
        _addBnPrefixes(result, normalized);
        // Also try the raw word in case normalization changes something it shouldn't
        if (normalized != word) _addBnPrefixes(result, word);
      } else {
        result.addAll(_enPrefix?[word.substring(0, 2)] ?? const []);
        if (word.length >= 3) {
          result.addAll(_enPrefix?[word.substring(0, 3)] ?? const []);
        }
        if (word.length >= 4) {
          result.addAll(_enPrefix?[word.substring(0, 4)] ?? const []);
        }
      }
    }

    if (!isBengali) {
      // ── 2. Full-phrase alias lookup ──────────────────────────────────────────
      result.addAll(_aliasLookup?[q] ?? const []);

      // ── 3. Per-word alias lookup ─────────────────────────────────────────────
      for (final word in words) {
        if (word.length >= 3) {
          result.addAll(_aliasLookup?[word] ?? const []);
        }
      }

      // ── 4. Family index lookup ───────────────────────────────────────────────
      result.addAll(_familyIndex?[q] ?? const []);
      for (final word in words) {
        if (word.length >= 4) {
          result.addAll(_familyIndex?[word] ?? const []);
        }
      }

      // ── 5. Bengali prefix via romanization table ─────────────────────────────
      if (q.length <= 6) {
        for (final kv in _romanToBnPrefix.entries) {
          if (q.startsWith(kv.key) || kv.key.startsWith(q)) {
            result.addAll(_bnPrefix?[kv.value] ?? const []);
          }
        }
      } else {
        for (final kv in _romanToBnPrefix.entries) {
          if (q.startsWith(kv.key)) {
            result.addAll(_bnPrefix?[kv.value] ?? const []);
          }
        }
      }
    }

    return result;
  }

  static void _addBnPrefixes(Set<int> result, String word) {
    result.addAll(_bnPrefix?[word.substring(0, 2)] ?? const []);
    if (word.length >= 3) {
      result.addAll(_bnPrefix?[word.substring(0, 3)] ?? const []);
    }
    if (word.length >= 4) {
      result.addAll(_bnPrefix?[word.substring(0, 4)] ?? const []);
    }
  }

  /// Returns IDs for a specific food family.
  static List<int> familyIds(String family) =>
      _familyIndex?[family] ?? const [];

  /// Top-200 food IDs by search_priority.
  static List<int> get topFoodIds => _topFoods;

  static bool _containsBengali(String text) =>
      text.codeUnits.any((c) => c >= 0x0980 && c <= 0x09FF);

  static bool get isLoaded => _enPrefix != null;

  // ── Bengali query normalization ──────────────────────────────────────────────
  // Applies the same conservative matra fix used to clean the dataset:
  // When a user types (or pastes) Bengali with an independent vowel between two
  // consonants (e.g. কইডস), convert it to the correct matra form (কিডস).
  // This improves recall for users who copied text from an uncorrected source.
  //
  // SAFE: only fires when prev char is a pure consonant (not a vowel matra),
  // so diphthongs like বাইক / লাইট / পাউরুটি are never touched.

  static const _bnConsonantRange = (0x0995, 0x09B9); // ক to হ
  static const _bnExtraConsonants = {0x09CE, 0x09DC, 0x09DD, 0x09DF}; // ৎ ড় ঢ় য়

  static bool _isBnConsonant(int cp) =>
      (cp >= _bnConsonantRange.$1 && cp <= _bnConsonantRange.$2) ||
      _bnExtraConsonants.contains(cp);

  // Characters that count as "consonant context" for prev-char check
  // (consonants, virama, nukta, anusvara, visarga, chandrabindu)
  // Crucially does NOT include vowel signs (matras) — so บา + ই + ค is safe.
  static bool _isBnConsonantContext(int cp) =>
      _isBnConsonant(cp) ||
      cp == 0x09CD || // virama ্
      cp == 0x09BC || // nukta ়
      cp == 0x0982 || // anusvara ং
      cp == 0x0983 || // visarga ঃ
      cp == 0x0981;   // chandrabindu ঁ

  static const _independentToMatra = <int, String>{
    0x0986: 'া',  // আ → া
    0x0987: 'ি',  // ই → ি
    0x0988: 'ী',  // ঈ → ী
    0x0989: 'ু',  // উ → ু
    0x098A: 'ূ',  // ঊ → ূ
    0x098F: 'ে',  // এ → ে
    0x0990: 'ৈ',  // ঐ → ৈ
    0x0993: 'ো',  // ও → ো
    0x0994: 'ৌ',  // ঔ → ৌ
  };

  static String _normalizeBengali(String word) {
    final runes = word.runes.toList();
    final n = runes.length;
    if (n < 3) return word;
    final result = List<String>.generate(n, (i) => String.fromCharCode(runes[i]));
    for (int i = 1; i < n - 1; i++) {
      final matra = _independentToMatra[runes[i]];
      if (matra == null) continue;
      final prev = runes[i - 1];
      final next = runes[i + 1];
      if (_isBnConsonantContext(prev) && _isBnConsonant(next)) {
        result[i] = matra;
      }
    }
    return result.join();
  }

  // ── Romanization table ───────────────────────────────────────────────────────
  /// Maps common romanization prefixes to Bengali script 2-char prefixes.
  /// Allows typing "dal", "posto", "ilish" etc. to find Bengali-named foods.
  static const _romanToBnPrefix = <String, String>{
    // ── Staples / Rice / Bread ──────────────────────────────────────────────
    'bha':  'ভা',   // bhaja, bhat, bhapa → ভাজা, ভাত, ভাপা
    'bhe':  'ভে',   // bhetki → ভেটকি
    'bhi':  'ভি',   // bhindi → ভিন্ডি
    'bir':  'বি',   // biryani → বিরিয়ানি
    'cha':  'চা',   // chai/cha → চা
    'chi':  'চি',   // chicken, chips, chingri → চি
    'cho':  'চো',   // chorchori → চোরচোরি
    'dal':  'ডা',   // dal/daal → ডাল
    'daa':  'ডা',
    'dho':  'ধো',   // dhokar → ধোকার
    'gha':  'ঘা',   // ghee → ঘি (lookup ঘা too)
    'ghi':  'ঘি',   // ghee → ঘি
    'ghu':  'ঘু',   // ghugni → ঘুঘনি
    'gho':  'ঘো',   // ghonto → ঘোন্টো
    'kac':  'কা',   // kachori → কাচোরি
    'kal':  'কা',   // kalia → কালিয়া
    'kha':  'খা',   // kheer, khabar → খা
    'khi':  'খি',   // khichuri → খিচুড়ি
    'koc':  'কো',   // kochuri → কচুরি
    'kol':  'কল',   // kolkata → কলকাতা
    'kor':  'কো',   // korma, kosha → কোর্মা, কোষা
    'kum':  'কু',   // kumro → কুমড়ো
    'lan':  'লা',   // langcha → লাংচা
    'las':  'লা',   // lassi → লাচ্ছি
    'luc':  'লু',   // luchi → লুচি
    'mih':  'মি',   // mihidana → মিহিদানা
    'mis':  'মি',   // mishti → মিষ্টি
    'moc':  'মো',   // mocha → মোচা
    'mog':  'মো',   // moghlai → মোগলাই
    'moh':  'মো',   // mohanbhog → মোহনভোগ
    'mor':  'মো',   // mochar → মোচার
    'muc':  'মু',   // muri → মুড়ি
    'mug':  'মু',   // mughlai → মুঘলাই
    'mur':  'মু',   // muri → মুড়ি
    'mut':  'মু',   // mutton → মু
    'nol':  'নো',   // nolen gur → নোলেন গুড়
    'pak':  'পা',   // pakhala, pakora → পাখাল, পাকোড়া
    'pan':  'পা',   // paneer, panta → পানির, পান্তা
    'par':  'পা',   // paratha → পরোটা
    'pat':  'পা',   // patisapta, paturi → পাতিসাপ্তা
    'pay':  'পা',   // payesh → পায়েস
    'pho':  'ফু',   // phuchka → ফুচকা
    'phu':  'ফু',   // phuchka → ফুচকা
    'piy':  'পি',   // pithe → পিঠে
    'pok':  'পো',   // posto → পোস্ত
    'poh':  'পো',   // poha → পোহা
    'pos':  'পো',   // posto → পোস্ত
    'puc':  'ফু',   // phuchka variant
    'pui':  'পু',   // pui shaak → পুঁই শাক
    'pur':  'পু',   // puri → পুরি
    'ras':  'রস',   // rasmalai, rasgulla → রসমালাই
    'raj':  'রা',   // rasagola, rajma → রাজমা
    'res':  'রে',   // rezala → রেজালা
    'ros':  'রস',   // rosogolla → রসগোল্লা
    'rui':  'রু',   // rui/rohu → রুই
    'san':  'সন',   // sandesh → সন্দেশ
    'sar':  'সা',   // sarbhaja → সারভাজা
    'sat':  'সা',   // sattu → সাত্তু
    'sha':  'শা',   // shaak → শাক
    'sho':  'শো',   // shorshe → শোর্শে
    'sin':  'সি',   // singara → সিঙাড়া
    'sit':  'সি',   // sitabhog → সিতাভোগ
    'sor':  'সর',   // sorshe → সরষে
    'tho':  'থো',   // thor (banana stem) → থো
    'uch':  'উচ',   // uchhe → উচ্ছে
    // ── Fruits / Vegetables ─────────────────────────────────────────────────
    'aal':  'আল',   // aaloo → আলু
    'alu':  'আল',   // aloo → আলু
    'aam':  'আম',   // aam mango → আম
    'bai':  'বা',   // baingan → বাইগন / বেগুন
    'bat':  'বা',   // batasha → বাতাসা
    'beg':  'বে',   // begun → বেগুন
    'bes':  'বে',   // besara → বেসরা
    'ech':  'এচ',   // echor → এচড়
    'gan':  'গা',   // gandharaj → গান্ধারাজ
    'jhi':  'ঝি',   // jhinge → ঝিঙে
    'koi':  'কই',   // koi fish → কই মাছ
    // ── Fish / Protein ──────────────────────────────────────────────────────
    'ilu':  'ইল',   // ilish → ইলিশ
    'ili':  'ইল',   // ilish → ইলিশ
    'pab':  'পা',   // pabda → পাবদা
    // ── Sweets / Desserts ───────────────────────────────────────────────────
    'doi':  'দই',   // doi (curd) → দই
    'pah':  'পা',   // pahala rasgulla
    // ── Common cooking methods ───────────────────────────────────────────────
    'dam':  'দা',   // dalna → দালনা
    'kho':  'খো',   // khoi (puffed rice) → খই
  };
}
