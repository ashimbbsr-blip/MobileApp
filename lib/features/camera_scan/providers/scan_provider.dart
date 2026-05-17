import 'package:flutter_riverpod/flutter_riverpod.dart';

enum ScanStatus { idle, scanning, detected, error, permissionDenied }

class ScanResult {
  final String foodName;
  final double confidence;
  ScanResult({required this.foodName, required this.confidence});
}

class ScanState {
  final ScanStatus status;
  final ScanResult? result;
  final String? errorMessage;

  const ScanState({
    this.status = ScanStatus.idle,
    this.result,
    this.errorMessage,
  });

  ScanState copyWith({ScanStatus? status, ScanResult? result, String? errorMessage}) {
    return ScanState(
      status: status ?? this.status,
      result: result ?? this.result,
      errorMessage: errorMessage,
    );
  }
}

class ScanNotifier extends StateNotifier<ScanState> {
  ScanNotifier() : super(const ScanState());

  void setScanning() => state = const ScanState(status: ScanStatus.scanning);

  void setDetected(String foodName, double confidence) {
    state = ScanState(
      status: ScanStatus.detected,
      result: ScanResult(foodName: foodName, confidence: confidence),
    );
  }

  void setError(String message) {
    state = ScanState(status: ScanStatus.error, errorMessage: message);
  }

  void setPermissionDenied() {
    state = const ScanState(status: ScanStatus.permissionDenied);
  }

  void reset() => state = const ScanState();
}

final scanProvider = StateNotifierProvider<ScanNotifier, ScanState>(
  (ref) => ScanNotifier(),
);
