import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import '../../../models/food_item.dart';
import '../../../services/food_label_matcher.dart';
import '../../../services/image_label_service.dart';

enum ScanPhase {
  idle,
  capturing,
  analyzing,
  done,
  noResults,
  error,
  permissionDenied,
}

class ScanState {
  final ScanPhase phase;
  final List<String> detectedLabels;
  final List<FoodItem> suggestions;
  final String? capturedImagePath;
  final String? errorMessage;

  const ScanState({
    this.phase = ScanPhase.idle,
    this.detectedLabels = const [],
    this.suggestions = const [],
    this.capturedImagePath,
    this.errorMessage,
  });

  bool get isLoading =>
      phase == ScanPhase.capturing || phase == ScanPhase.analyzing;

  ScanState copyWith({
    ScanPhase? phase,
    List<String>? detectedLabels,
    List<FoodItem>? suggestions,
    String? capturedImagePath,
    String? errorMessage,
  }) {
    return ScanState(
      phase: phase ?? this.phase,
      detectedLabels: detectedLabels ?? this.detectedLabels,
      suggestions: suggestions ?? this.suggestions,
      capturedImagePath: capturedImagePath ?? this.capturedImagePath,
      errorMessage: errorMessage,
    );
  }
}

class ScanNotifier extends StateNotifier<ScanState> {
  ScanNotifier() : super(const ScanState());

  final _picker = ImagePicker();

  Future<void> captureAndAnalyze() async {
    // ── 1. Camera permission ──────────────────────────────────────────
    final camStatus = await Permission.camera.status;
    if (camStatus.isDenied) {
      final result = await Permission.camera.request();
      if (!result.isGranted) {
        state = state.copyWith(phase: ScanPhase.permissionDenied);
        return;
      }
    } else if (camStatus.isPermanentlyDenied) {
      state = state.copyWith(phase: ScanPhase.permissionDenied);
      return;
    }

    // ── 2. Open camera ────────────────────────────────────────────────
    state = state.copyWith(phase: ScanPhase.capturing);

    final XFile? picked = await _picker.pickImage(
      source: ImageSource.camera,
      maxWidth: 1280,
      maxHeight: 1280,
      imageQuality: 88,
      preferredCameraDevice: CameraDevice.rear,
    );

    if (picked == null) {
      // User cancelled — return to idle without error.
      state = state.copyWith(phase: ScanPhase.idle);
      return;
    }

    // ── 3. Compress + label ───────────────────────────────────────────
    state = state.copyWith(
      phase: ScanPhase.analyzing,
      capturedImagePath: picked.path,
    );

    try {
      final labels = await ImageLabelService.labelsFromFile(picked.path);

      if (labels.isEmpty) {
        state = state.copyWith(
          phase: ScanPhase.noResults,
          detectedLabels: const [],
        );
        return;
      }

      final suggestions = await FoodLabelMatcher.match(labels, maxResults: 6);

      if (suggestions.isEmpty) {
        state = state.copyWith(
          phase: ScanPhase.noResults,
          detectedLabels: labels,
        );
        return;
      }

      state = state.copyWith(
        phase: ScanPhase.done,
        detectedLabels: labels,
        suggestions: suggestions,
      );
    } catch (e) {
      state = state.copyWith(
        phase: ScanPhase.error,
        errorMessage: e.toString(),
      );
    }
  }

  void reset() {
    FoodLabelMatcher.clearCache();
    state = const ScanState();
  }
}

final scanProvider = StateNotifierProvider<ScanNotifier, ScanState>(
  (ref) => ScanNotifier(),
);
