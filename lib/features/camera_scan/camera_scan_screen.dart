import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:camera/camera.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:go_router/go_router.dart';
import '../../localization/app_localizations.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../models/food_item.dart';
import '../../services/usda_api_service.dart';
import '../../services/food_classifier.dart';
import '../camera_scan/providers/scan_provider.dart';
import '../meal_tracking/providers/meal_provider.dart';
import '../dashboard/providers/dashboard_provider.dart';
import 'package:uuid/uuid.dart';

class CameraScanScreen extends ConsumerStatefulWidget {
  final String mealType;
  const CameraScanScreen({super.key, required this.mealType});

  @override
  ConsumerState<CameraScanScreen> createState() => _CameraScanScreenState();
}

class _CameraScanScreenState extends ConsumerState<CameraScanScreen> {
  CameraController? _cameraController;
  bool _isCameraInitialized = false;
  bool _isProcessing = false;
  List<CameraDescription> _cameras = [];
  final FoodClassifier _classifier = FoodClassifier();

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    final status = await Permission.camera.request();
    if (status.isDenied || status.isPermanentlyDenied) {
      ref.read(scanProvider.notifier).setPermissionDenied();
      return;
    }

    try {
      _cameras = await availableCameras();
      if (_cameras.isEmpty) {
        ref.read(scanProvider.notifier).setError('No camera found');
        return;
      }
      _cameraController = CameraController(
        _cameras.first,
        ResolutionPreset.medium,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.jpeg,
      );
      await _cameraController!.initialize();
      if (mounted) setState(() => _isCameraInitialized = true);
    } catch (e) {
      ref.read(scanProvider.notifier).setError('Camera initialization failed');
    }
  }

  Future<void> _captureAndAnalyze() async {
    if (_cameraController == null || !_cameraController!.value.isInitialized || _isProcessing) return;

    setState(() => _isProcessing = true);
    ref.read(scanProvider.notifier).setScanning();

    try {
      // Capture image
      final xFile = await _cameraController!.takePicture();

      // Lazy-initialize the classifier on first use
      if (!_classifier.isInitialized) {
        final ready = await _classifier.initialize();
        if (!ready) {
          final l10n = ref.read(appStringsProvider);
          ref.read(scanProvider.notifier).setError(l10n.modelNotAvailable);
          return;
        }
      }

      // Run TFLite inference
      final prediction = await _classifier.classify(xFile.path);

      if (prediction == null) {
        // Model returned no result above the confidence threshold
        final l10n = ref.read(appStringsProvider);
        ref.read(scanProvider.notifier).setError(l10n.unableToIdentify);
      } else {
        ref.read(scanProvider.notifier).setDetected(
          prediction.label,
          prediction.confidence,
        );
      }
    } catch (e) {
      ref.read(scanProvider.notifier).setError('Failed: ${e.runtimeType}');
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  Future<void> _confirmAndAdd(String foodName, double quantity) async {
    try {
      final apiService = UsdaApiService();
      final results = await apiService.searchFoods(foodName);
      FoodItem food;
      if (results.isNotEmpty) {
        food = results.first;
      } else {
        food = FoodItem(
          id: const Uuid().v4(),
          name: foodName,
          servingSize: quantity,
          servingUnit: 'g',
          calories: 52,
          proteinG: 0.3,
          carbsG: 14,
          fatG: 0.2,
          fiberG: 2.4,
          isCustom: true,
        );
      }
      await ref.read(mealProvider.notifier).addFood(food, widget.mealType, quantity);
      ref.read(dashboardProvider.notifier).refresh();
      if (mounted) context.pop();
    } catch (e) {
      ref.read(scanProvider.notifier).setError('Failed to add food');
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    _classifier.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final scanState = ref.watch(scanProvider);
    final l10n = ref.watch(appStringsProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        foregroundColor: Colors.white,
        title: Text(l10n.scanFood),
      ),
      body: _buildBody(context, scanState, l10n),
    );
  }

  Widget _buildBody(BuildContext context, ScanState state, AppStrings l10n) {
    if (state.status == ScanStatus.permissionDenied) {
      return _PermissionDeniedView(l10n: l10n);
    }

    if (state.status == ScanStatus.detected && state.result != null) {
      return _DetectedView(
        result: state.result!,
        l10n: l10n,
        onConfirm: (qty) => _confirmAndAdd(state.result!.foodName, qty),
        onRetry: () {
          ref.read(scanProvider.notifier).reset();
        },
      );
    }

    if (state.status == ScanStatus.error) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, color: Colors.red, size: 56),
            const SizedBox(height: 16),
            Text(state.errorMessage ?? l10n.error, style: const TextStyle(color: Colors.white)),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: () => ref.read(scanProvider.notifier).reset(), child: Text(l10n.tryAgain)),
          ],
        ),
      );
    }

    return Stack(
      children: [
        if (_isCameraInitialized && _cameraController != null)
          SizedBox.expand(child: CameraPreview(_cameraController!))
        else
          const Center(child: CircularProgressIndicator(color: Colors.white)),
        // Scan frame overlay
        Center(
          child: Container(
            width: 260,
            height: 260,
            decoration: BoxDecoration(
              border: Border.all(color: AppColors.primary, width: 3),
              borderRadius: BorderRadius.circular(16),
            ),
          ),
        ),
        // Bottom controls
        Positioned(
          bottom: 40,
          left: 0,
          right: 0,
          child: Column(
            children: [
              if (state.status == ScanStatus.scanning)
                Column(
                  children: [
                    const CircularProgressIndicator(color: AppColors.primary),
                    const SizedBox(height: 16),
                    Text(l10n.detectingFood, style: const TextStyle(color: Colors.white)),
                  ],
                )
              else
                GestureDetector(
                  onTap: _captureAndAnalyze,
                  child: Container(
                    width: 70,
                    height: 70,
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      shape: BoxShape.circle,
                      boxShadow: [BoxShadow(color: AppColors.primary.withOpacity(0.4), blurRadius: 16, spreadRadius: 4)],
                    ),
                    child: const Icon(Icons.camera_alt, color: Colors.white, size: 32),
                  ),
                ),
            ],
          ),
        ),
      ],
    );
  }
}

class _DetectedView extends StatefulWidget {
  final ScanResult result;
  final AppStrings l10n;
  final void Function(double) onConfirm;
  final VoidCallback onRetry;

  const _DetectedView({required this.result, required this.l10n, required this.onConfirm, required this.onRetry});

  @override
  State<_DetectedView> createState() => _DetectedViewState();
}

class _DetectedViewState extends State<_DetectedView> {
  final _qtyController = TextEditingController(text: '100');

  @override
  void dispose() {
    _qtyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = widget.l10n;
    final isLowConfidence = widget.result.confidence < 0.6;

    return Container(
      color: Colors.black87,
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.check_circle, color: AppColors.primary, size: 64),
              const SizedBox(height: 16),
              Text(l10n.foodDetected, style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              Text(
                widget.result.foodName,
                style: const TextStyle(color: Colors.white, fontSize: 20),
              ),
              const SizedBox(height: 8),
              Text(
                '${l10n.confidence}: ${(widget.result.confidence * 100).toStringAsFixed(0)}%',
                style: TextStyle(color: isLowConfidence ? Colors.orange : AppColors.primary),
              ),
              if (isLowConfidence) ...[
                const SizedBox(height: 4),
                Text(l10n.lowConfidence, style: const TextStyle(color: Colors.orange, fontSize: 12)),
              ],
              const SizedBox(height: 32),
              TextField(
                controller: _qtyController,
                keyboardType: TextInputType.number,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  labelText: '${l10n.quantity} (g)',
                  labelStyle: const TextStyle(color: Colors.white70),
                  enabledBorder: const OutlineInputBorder(borderSide: BorderSide(color: Colors.white30)),
                  focusedBorder: const OutlineInputBorder(borderSide: BorderSide(color: AppColors.primary)),
                ),
              ),
              const SizedBox(height: 24),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      style: OutlinedButton.styleFrom(foregroundColor: Colors.white, side: const BorderSide(color: Colors.white30)),
                      onPressed: widget.onRetry,
                      child: Text(l10n.tryAgain),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () => widget.onConfirm(double.tryParse(_qtyController.text) ?? 100),
                      child: Text(l10n.addToMeal),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _PermissionDeniedView extends StatelessWidget {
  final AppStrings l10n;
  const _PermissionDeniedView({required this.l10n});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.no_photography, color: Colors.white54, size: 64),
            const SizedBox(height: 16),
            Text(l10n.permissionDenied, style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            Text(l10n.cameraPermission, style: const TextStyle(color: Colors.white70), textAlign: TextAlign.center),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              icon: const Icon(Icons.settings),
              label: Text(l10n.openSettings),
              onPressed: openAppSettings,
            ),
          ],
        ),
      ),
    );
  }
}
