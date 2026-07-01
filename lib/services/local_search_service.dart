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
  ///   1. Per-word prefix lookup (EN: 2/3/4-char; BN: 2/3-char)
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
        result.addAll(_bnPrefix?[word.substring(0, 2)] ?? const []);
        if (word.length >= 3) {
          result.addAll(_bnPrefix?[word.substring(0, 3)] ?? const []);
        }
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
      // Check if the full query or any meaningful word is a family cluster name
      result.addAll(_familyIndex?[q] ?? const []);
      for (final word in words) {
        if (word.length >= 4) {
          result.addAll(_familyIndex?[word] ?? const []);
        }
      }

      // ── 5. Bengali prefix via romanization table ─────────────────────────────
      // Activated for queries up to 6 chars to catch common romanizations
      if (q.length <= 6) {
        for (final kv in _romanToBnPrefix.entries) {
          if (q.startsWith(kv.key) || kv.key.startsWith(q)) {
            result.addAll(_bnPrefix?[kv.value] ?? const []);
          }
        }
      } else {
        // For longer queries, only exact romanization prefix match
        for (final kv in _romanToBnPrefix.entries) {
          if (q.startsWith(kv.key)) {
            result.addAll(_bnPrefix?[kv.value] ?? const []);
          }
        }
      }
    }

    return result;
  }

  /// Returns IDs for a specific food family.
  static List<int> familyIds(String family) =>
      _familyIndex?[family] ?? const [];

  /// Top-200 food IDs by search_priority.
  static List<int> get topFoodIds => _topFoods;

  static bool _containsBengali(String text) =>
      text.codeUnits.any((c) => c >= 0x0980 && c <= 0x09FF);

  static bool get isLoaded => _enPrefix != null;

  /// Maps common romanization prefixes to Bengali script 2-char prefixes.
  /// Allows typing "dal", "posto", "ilish" etc. to find Bengali-named foods.
  static const _romanToBnPrefix = <String, String>{
    // Common Bengali food terms
    'dal':  'ডা',   // dal/daal → ডাল
    'daa':  'ডা',
    'cha':  'চা',   // chai/cha → চা
    'chi':  'চি',   // chicken, chips
    'bha':  'ভা',   // bhaja, bhat, bhapa
    'bhe':  'ভে',   // bhetki → ভেটকি
    'sha':  'শা',   // shaak → শাক
    'kha':  'খা',   // kheer, khabar
    'gha':  'ঘা',   // ghee, ghanto
    'rui':  'রু',   // rui/rohu → রুই
    'ilu':  'ইল',   // ilish → ইলিশ
    'ili':  'ইল',   // ilish
    'ros':  'রস',   // rosogolla → রসগোল্লা
    'san':  'সন',   // sandesh → সন্দেশ
    'mis':  'মি',   // mishti → মিষ্টি
    'mut':  'মু',   // mutton, muri
    'mur':  'মু',   // muri → মুড়ি
    'bir':  'বি',   // biryani → বিরিয়ানি
    'kol':  'কল',   // kolkata
    'pos':  'পো',   // posto → পোস্ত
    'poh':  'পো',   // poha → পোহা
    'mor':  'মো',   // mochar → মোচার
    'moc':  'মো',   // mocha → মোচা
    'sin':  'সি',   // singara → সিঙাড়া
    'ghu':  'ঘু',   // ghugni → ঘুঘনি
    'sat':  'সা',   // sattu → সাত্তু
    'pho':  'ফু',   // phuchka → ফুচকা
    'phu':  'ফু',   // phuchka
    'pay':  'পা',   // payesh → পায়েস
    'pat':  'পা',   // patisapta, paturi
    'par':  'পা',   // paratha → পরোটা
    'pan':  'পা',   // paneer, panta
    'ras':  'রস',   // rasmalai → রসমালাই
    'khi':  'খি',   // khichuri, khichdi
    'puc':  'ফু',   // phuchka variant
    'pur':  'পু',   // puri → পুরি
    'luc':  'লু',   // luchi → লুচি
    'alu':  'আল',   // aloo → আলু
    'aam':  'আম',   // aam mango → আম
    'mog':  'মো',   // moghlai → মোগলাই
    'mug':  'মু',   // mughlai
    'lan':  'লা',   // langcha → লাংচা
    'mih':  'মি',   // mihidana → মিহিদানা
    'sit':  'সি',   // sitabhog → সিতাভোগ
    'kor':  'কো',   // korma → কোর্মা
    'kal':  'কা',   // kalia → কালিয়া
    'bes':  'বে',   // besara → বেসরা
    'sor':  'সর',   // sorshe → সরষে
    'sho':  'শো',   // shorshe
    'koc':  'কো',   // kochuri → কচুরি
    'kac':  'কা',   // kachori
    'pak':  'পা',   // pakhala, pakora
    'pok':  'পো',   // posta (poppy)
    'pui':  'পু',   // pui shaak → পুঁই শাক
    'beg':  'বে',   // begun → বেগুন
    'bai':  'বা',   // baingan
    'kum':  'কু',   // kumro → কুমড়ো
    'bat':  'বা',   // batasha → বাতাসা
    'doi':  'দই',   // doi (curd) → দই
    'raj':  'রা',   // rasagola
    'pah':  'পা',   // pahala
    'gan':  'গা',   // gandharaj
    'sar':  'সা',   // sarbhaja
    'moh':  'মো',   // mohanbhog
    'chn':  'চি',   // chingri
  };
}
