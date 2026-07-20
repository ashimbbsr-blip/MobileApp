import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

import '../../../models/food_item.dart';
import '../../../services/api_key_service.dart';
import '../../../services/gemini_food_scan_service.dart';
import '../../../services/usda_api_service.dart' show RateLimitException;
import '../food_match_service.dart';

enum ScanStatus { idle, analyzing, review, error }

enum ScanErrorKind {
  noApiKey,
  offline,
  rateLimited,
  invalidKey,
  nothingRecognized,
  generic,
}

class FoodScanState {
  final ScanStatus status;
  final String? imagePath;
  final List<ScannedItemMatch> items;
  final ScanErrorKind? errorKind;
  final String? errorMessage;

  const FoodScanState({
    this.status = ScanStatus.idle,
    this.imagePath,
    this.items = const [],
    this.errorKind,
    this.errorMessage,
  });

  FoodScanState copyWith({
    ScanStatus? status,
    String? imagePath,
    List<ScannedItemMatch>? items,
    ScanErrorKind? errorKind,
    String? errorMessage,
  }) {
    return FoodScanState(
      status: status ?? this.status,
      imagePath: imagePath ?? this.imagePath,
      items: items ?? this.items,
      errorKind: errorKind ?? this.errorKind,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  double get totalKcal => items.fold(
      0,
      (sum, it) =>
          sum + it.selected.calories * it.grams / it.selected.servingSize);
}

class FoodScanNotifier extends StateNotifier<FoodScanState> {
  FoodScanNotifier() : super(const FoodScanState());

  final GeminiFoodScanService _service = GeminiFoodScanService();

  /// Opens the OS picker; returns true when an image was selected.
  Future<bool> pickImage(ImageSource source) async {
    if (!ApiKeyService.instance.hasGeminiKey) {
      state = const FoodScanState(
        status: ScanStatus.error,
        errorKind: ScanErrorKind.noApiKey,
      );
      return false;
    }
    try {
      final picked = await ImagePicker().pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );
      if (picked == null) return false;
      state = FoodScanState(status: ScanStatus.idle, imagePath: picked.path);
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<void> analyze() async {
    final path = state.imagePath;
    if (path == null) return;
    state = state.copyWith(status: ScanStatus.analyzing);
    try {
      final detected = await _service.analyzeImage(File(path));
      final matches = FoodMatchService.matchAll(detected);
      if (!mounted) return;
      state = state.copyWith(status: ScanStatus.review, items: matches);
    } catch (e) {
      if (!mounted) return;
      state = state.copyWith(
        status: ScanStatus.error,
        errorKind: _classify(e),
        errorMessage: e.toString(),
      );
    }
  }

  static ScanErrorKind _classify(Object e) {
    if (e is ScanApiKeyException) return ScanErrorKind.invalidKey;
    if (e is RateLimitException) return ScanErrorKind.rateLimited;
    if (e is ScanNothingRecognizedException) {
      return ScanErrorKind.nothingRecognized;
    }
    final msg = e.toString().toLowerCase();
    if (msg.contains('internet') || msg.contains('timeout')) {
      return ScanErrorKind.offline;
    }
    return ScanErrorKind.generic;
  }

  void updateGrams(int index, double grams) {
    if (index < 0 || index >= state.items.length) return;
    state.items[index].grams = grams.clamp(1, 5000);
    state = state.copyWith(items: List.of(state.items));
  }

  void removeItem(int index) {
    if (index < 0 || index >= state.items.length) return;
    final items = List.of(state.items)..removeAt(index);
    state = state.copyWith(items: items);
  }

  void replaceSelection(int index, FoodItem food) {
    if (index < 0 || index >= state.items.length) return;
    final items = List.of(state.items);
    final old = items[index];
    items[index] = ScannedItemMatch(
      detected: old.detected,
      selected: food,
      alternates: old.alternates,
      isFallback: food.source == 'scan',
      grams: old.grams,
    );
    state = state.copyWith(items: items);
  }

  /// Restore the AI-estimate fallback for an item.
  void useAiEstimate(int index) {
    if (index < 0 || index >= state.items.length) return;
    final d = state.items[index].detected;
    replaceSelection(index, FoodMatchService.buildFallbackItem(d, index));
  }

  void reset() => state = const FoodScanState();
}

final foodScanProvider =
    StateNotifierProvider<FoodScanNotifier, FoodScanState>((ref) {
  return FoodScanNotifier();
});
