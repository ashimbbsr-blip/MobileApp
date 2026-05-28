import 'package:flutter/foundation.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:google_mlkit_image_labeling/google_mlkit_image_labeling.dart';
import 'package:path_provider/path_provider.dart';

/// Compresses a captured image and runs Google ML Kit Image Labeling on it.
/// All processing is local — no network calls are made.
class ImageLabelService {
  static const _confidenceThreshold = 0.40;
  static const _jpegQuality = 72;
  // Target longest-edge dimension after compression (keeps RAM low).
  static const _maxDimension = 640;

  /// Returns a list of label strings sorted by confidence (highest first).
  /// May return an empty list if the model cannot identify anything above
  /// [_confidenceThreshold].
  static Future<List<String>> labelsFromFile(String originalPath) async {
    String pathToProcess = originalPath;

    try {
      final compressed = await _compress(originalPath);
      if (compressed != null) pathToProcess = compressed;
    } catch (e) {
      debugPrint('[ImageLabelService] compress failed, using original: $e');
    }

    return _runLabeling(pathToProcess);
  }

  // ── Private helpers ───────────────────────────────────────────────────────

  static Future<String?> _compress(String srcPath) async {
    final dir = await getTemporaryDirectory();
    final outPath = '${dir.path}/scan_compressed.jpg';

    final result = await FlutterImageCompress.compressAndGetFile(
      srcPath,
      outPath,
      minWidth: _maxDimension,
      minHeight: _maxDimension,
      quality: _jpegQuality,
      format: CompressFormat.jpeg,
    );
    return result?.path;
  }

  static Future<List<String>> _runLabeling(String imagePath) async {
    final options = ImageLabelerOptions(
      confidenceThreshold: _confidenceThreshold,
    );
    final labeler = ImageLabeler(options: options);

    try {
      final inputImage = InputImage.fromFilePath(imagePath);
      final results = await labeler.processImage(inputImage);

      // Sort by confidence descending so the matcher weights early labels higher.
      results.sort((a, b) => b.confidence.compareTo(a.confidence));

      return results.map((l) => l.label).toList();
    } finally {
      await labeler.close();
    }
  }
}
