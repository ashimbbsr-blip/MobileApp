import '../../models/food_item.dart';
import '../../services/gemini_food_scan_service.dart';
import '../../services/local_food_repository.dart';
import '../../storage/hive_storage.dart';

/// A detected dish paired with its database match (or AI-estimate fallback).
class ScannedItemMatch {
  final DetectedFoodItem detected;
  FoodItem selected;
  final List<FoodItem> alternates;
  final bool isFallback;
  double grams;

  ScannedItemMatch({
    required this.detected,
    required this.selected,
    required this.alternates,
    required this.isFallback,
    required this.grams,
  });
}

/// Pure matching logic: Gemini's detected dishes → local DB items.
class FoodMatchService {
  // Tier 4 ("substring in name") and above is trustworthy enough to
  // auto-select; anything below falls back to the AI estimate.
  static const int acceptThreshold = 500;
  static const int customFoodScore = 500;

  static List<ScannedItemMatch> matchAll(List<DetectedFoodItem> detected) {
    final out = <ScannedItemMatch>[];
    for (var i = 0; i < detected.length; i++) {
      out.add(_matchOne(detected[i], i));
    }
    return out;
  }

  static ScannedItemMatch _matchOne(DetectedFoodItem d, int index) {
    // Merge scored results across the English name and every alt name,
    // keeping the best score per food id.
    final best = <String, (FoodItem, int)>{};
    void absorb(List<(FoodItem, int)> results) {
      for (final (food, score) in results) {
        final prev = best[food.id];
        if (prev == null || score > prev.$2) best[food.id] = (food, score);
      }
    }

    absorb(LocalFoodRepository.searchScored(d.nameEn));
    for (final alt in d.altNames) {
      absorb(LocalFoodRepository.searchScored(alt));
    }

    // Custom foods: simple contains-match on either name.
    final queries = [d.nameEn, ...d.altNames].map((s) => s.toLowerCase());
    for (final custom in HiveStorage.getCustomFoods()) {
      final en = custom.name.toLowerCase();
      final bn = (custom.nameBn ?? '').toLowerCase();
      final hit = queries.any((q) =>
          q.isNotEmpty && (en.contains(q) || (bn.isNotEmpty && bn.contains(q))));
      if (hit) {
        final prev = best[custom.id];
        if (prev == null || customFoodScore > prev.$2) {
          best[custom.id] = (custom, customFoodScore);
        }
      }
    }

    final ranked = best.values.toList()..sort((a, b) => b.$2.compareTo(a.$2));
    final alternates = ranked.take(3).map((r) => r.$1).toList();

    final top = ranked.isNotEmpty ? ranked.first : null;
    if (top != null && top.$2 >= acceptThreshold) {
      return ScannedItemMatch(
        detected: d,
        selected: top.$1,
        alternates: alternates,
        isFallback: false,
        grams: d.estimatedGrams,
      );
    }

    return ScannedItemMatch(
      detected: d,
      selected: buildFallbackItem(d, index),
      alternates: alternates,
      isFallback: true,
      grams: d.estimatedGrams,
    );
  }

  /// Synthetic FoodItem carrying Gemini's own nutrition estimate for the
  /// detected portion. servingSize == estimatedGrams, so scaling by grams
  /// keeps the estimate proportional.
  static FoodItem buildFallbackItem(DetectedFoodItem d, int index) {
    return FoodItem(
      id: 'scan_${DateTime.now().millisecondsSinceEpoch}_$index',
      name: d.nameEn,
      servingSize: d.estimatedGrams,
      servingUnit: 'g',
      calories: d.kcal,
      proteinG: d.proteinG,
      carbsG: d.carbsG,
      fatG: d.fatG,
      fiberG: d.fiberG,
      isCustom: false,
      source: 'scan',
      category: 'restaurant_food',
    );
  }
}
