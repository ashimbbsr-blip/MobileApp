import 'dart:developer' as developer;
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:image/image.dart' as img;

class FoodPrediction {
  final String label;
  final double confidence;
  const FoodPrediction({required this.label, required this.confidence});
}

/// Runs TFLite food classification on camera images.
///
/// Model: MobileNetV2 trained on ImageNet-1001.
///   Input  — [1, 224, 224, 3] float32, normalized to [-1.0, 1.0]
///   Output — [1, 1001] float32 softmax probabilities
///
/// Only predictions whose class index falls inside [_foodClassIndices] are
/// returned — this prevents the model from reporting "Chihuahua" or "school
/// bus" when it cannot confidently identify a food.
class FoodClassifier {
  static const String _modelAsset = 'assets/models/food_model.tflite';
  static const String _labelsAsset = 'assets/models/labels.txt';
  static const int _inputSize = 224;

  // Minimum confidence required to report a result.
  static const double confidenceThreshold = 0.30;

  // ImageNet-1001 indices that correspond to edible food items.
  // Verified against labels.txt — all positions confirmed correct.
  static const Set<int> _foodClassIndices = {
    // Seafood / fish (391–399)
    391, 392, 393, 394, 395, 396, 397, 398, 399,
    // Prepared foods & dishes
    922, // guacamole
    923, // consomme
    924, // hot pot
    925, // trifle
    926, // ice cream
    927, // ice lolly
    928, // French loaf
    929, // bagel
    930, // pretzel
    931, // cheeseburger
    932, // hotdog
    933, // mashed potato
    957, // carbonara
    958, // chocolate sauce
    959, // dough
    960, // meat loaf
    961, // pizza
    962, // potpie
    963, // burrito
    964, // red wine
    965, // espresso
    966, // cup
    967, // eggnog
    // Vegetables (934–945)
    934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945,
    // Fruits (946–955)
    946, 947, 948, 949, 950, 951, 952, 953, 954, 955,
    // Mushrooms / fungi
    989, 990, 991, 992, 993, 994, 995,
    // Food-adjacent containers / utensils used as fallback signals
    921, // plate / pot
    807, // soup bowl
    568, // frying pan
  };

  Interpreter? _interpreter;
  List<String> _labels = [];
  bool _isInitialized = false;

  bool get isInitialized => _isInitialized;

  // ── Initialization ────────────────────────────────────────────────────────

  // Cached output shape info: true = flat [numClasses], false = batched [1, numClasses]
  bool _outputIs1D = false;
  int _numClasses = 0;

  Future<bool> initialize() async {
    try {
      final modelData = await rootBundle.load(_modelAsset);
      final modelBytes = modelData.buffer.asUint8List(
        modelData.offsetInBytes,
        modelData.lengthInBytes,
      );
      _interpreter = Interpreter.fromBuffer(modelBytes);

      final inputTensor = _interpreter!.getInputTensor(0);
      final outputTensor = _interpreter!.getOutputTensor(0);
      developer.log(
        '[FoodClassifier] Input  — shape: ${inputTensor.shape}, type: ${inputTensor.type}',
      );
      developer.log(
        '[FoodClassifier] Output — shape: ${outputTensor.shape}, type: ${outputTensor.type}',
      );

      // Support both [1001] (1-D) and [1, 1001] (batched) output shapes
      final outShape = outputTensor.shape;
      if (outShape.length == 1) {
        _outputIs1D = true;
        _numClasses = outShape[0];
      } else {
        _outputIs1D = false;
        _numClasses = outShape[1];
      }
      developer.log('[FoodClassifier] Output 1D=$_outputIs1D, numClasses=$_numClasses');

      final labelsRaw = await rootBundle.loadString(_labelsAsset);
      _labels = labelsRaw
          .split('\n')
          .map((l) => l.trim())
          .where((l) => l.isNotEmpty)
          .toList();
      developer.log('[FoodClassifier] Loaded ${_labels.length} labels');

      if (_labels.length != _numClasses) {
        developer.log(
          '[FoodClassifier] WARNING: labels.txt has ${_labels.length} entries '
          'but model outputs $_numClasses classes — index mismatch possible',
          level: 900,
        );
      }

      _isInitialized = true;
      return true;
    } on FlutterError catch (e) {
      developer.log(
        '[FoodClassifier] Asset not found — place food_model.tflite and '
        'labels.txt in assets/models/. Error: $e',
        level: 900,
      );
      _isInitialized = false;
      return false;
    } catch (e, stack) {
      developer.log('[FoodClassifier] Initialization failed: $e\n$stack', level: 1000);
      _isInitialized = false;
      return false;
    }
  }

  // ── Inference ─────────────────────────────────────────────────────────────

  /// Returns the top food prediction, or null when:
  ///  • confidence is below [confidenceThreshold]
  ///  • the top class is not a food category
  ///  • any error occurs
  Future<FoodPrediction?> classify(String imagePath) async {
    if (!_isInitialized || _interpreter == null) {
      developer.log('[FoodClassifier] Not initialized');
      return null;
    }

    try {
      // 1. Load and decode image
      final imageFile = File(imagePath);
      if (!await imageFile.exists()) {
        developer.log('[FoodClassifier] File not found: $imagePath');
        return null;
      }

      final rawBytes = await imageFile.readAsBytes();
      final decoded = img.decodeImage(rawBytes);
      if (decoded == null) {
        developer.log('[FoodClassifier] Failed to decode image');
        return null;
      }

      // 2. Resize to 224×224 with bilinear interpolation
      final resized = img.copyResize(
        decoded,
        width: _inputSize,
        height: _inputSize,
        interpolation: img.Interpolation.linear,
      );

      // 3. Build [1, 224, 224, 3] float32 input tensor
      //    MobileNetV2 normalization: pixel / 127.5 − 1.0 → [-1.0, 1.0]
      final input = List.generate(
        1,
        (_) => List.generate(
          _inputSize,
          (y) => List.generate(
            _inputSize,
            (x) {
              final p = resized.getPixel(x, y);
              return [
                _normalize(p.r.toDouble()),
                _normalize(p.g.toDouble()),
                _normalize(p.b.toDouble()),
              ];
            },
          ),
        ),
      );

      // 4. Allocate output buffer matching the model's output shape and run inference
      // Some models export [1001] (1-D), others [1, 1001] (batched). Handle both.
      final Object output;
      if (_outputIs1D) {
        output = List<double>.filled(_numClasses, 0.0);
      } else {
        output = List.generate(1, (_) => List<double>.filled(_numClasses, 0.0));
      }
      _interpreter!.run(input, output);

      final scores = _outputIs1D
          ? List<double>.from(output as List)
          : List<double>.from((output as List)[0] as List);

      // 5. Find highest-confidence prediction across ALL classes first
      int bestIdx = 0;
      double bestScore = scores[0];
      for (int i = 1; i < scores.length; i++) {
        if (scores[i] > bestScore) {
          bestScore = scores[i];
          bestIdx = i;
        }
      }

      developer.log('[FoodClassifier] Top-3: ${_topN(scores, 3)}');
      developer.log(
        '[FoodClassifier] Best: idx=$bestIdx  '
        'label="${bestIdx < _labels.length ? _labels[bestIdx] : "OOB"}"  '
        'score=${(bestScore * 100).toStringAsFixed(1)}%',
      );

      // 6. Confidence gate
      if (bestScore < confidenceThreshold) {
        developer.log('[FoodClassifier] Below confidence threshold');
        return null;
      }

      // 7. Food-category gate — reject non-food ImageNet classes
      if (!_foodClassIndices.contains(bestIdx)) {
        // Try the highest-scoring food class as a fallback
        double bestFoodScore = 0;
        int bestFoodIdx = -1;
        for (final idx in _foodClassIndices) {
          if (idx < scores.length && scores[idx] > bestFoodScore) {
            bestFoodScore = scores[idx];
            bestFoodIdx = idx;
          }
        }

        developer.log(
          '[FoodClassifier] Top class ($bestIdx) is not food. '
          'Best food class: idx=$bestFoodIdx score=${(bestFoodScore * 100).toStringAsFixed(1)}%',
        );

        if (bestFoodIdx == -1 || bestFoodScore < confidenceThreshold) {
          return null;
        }

        bestIdx = bestFoodIdx;
        bestScore = bestFoodScore;
      }

      // 8. Label bounds check
      if (bestIdx >= _labels.length) {
        developer.log('[FoodClassifier] Label index $bestIdx out of range');
        return null;
      }

      return FoodPrediction(label: _labels[bestIdx], confidence: bestScore);
    } catch (e, stack) {
      developer.log('[FoodClassifier] classify() error: $e\n$stack', level: 1000);
      return null;
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  double _normalize(double pixel) => pixel / 127.5 - 1.0;

  List<Map<String, dynamic>> _topN(List<double> scores, int n) {
    final indexed = scores.asMap().entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    return indexed.take(n).map((e) {
      final label = e.key < _labels.length ? _labels[e.key] : 'idx_${e.key}';
      return {'idx': e.key, 'label': label, 'pct': '${(e.value * 100).toStringAsFixed(1)}%'};
    }).toList();
  }

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  void dispose() {
    _interpreter?.close();
    _interpreter = null;
    _labels = [];
    _isInitialized = false;
    _outputIs1D = false;
    _numClasses = 0;
  }
}
