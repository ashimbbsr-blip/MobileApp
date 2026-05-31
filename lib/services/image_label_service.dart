import 'package:flutter/foundation.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:google_mlkit_image_labeling/google_mlkit_image_labeling.dart';
import 'package:path_provider/path_provider.dart';

class ImageLabelService {
  static const _confidenceThreshold = 0.30;
  static const _lowConfidenceThreshold = 0.20;
  static const _jpegQuality = 72;
  static const _maxDimension = 800;
  static const _maxLowConfidenceLabels = 5;

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
    final inputImage = InputImage.fromFilePath(imagePath);

    final highOptions = ImageLabelerOptions(
      confidenceThreshold: _confidenceThreshold,
    );
    final highLabeler = ImageLabeler(options: highOptions);

    final lowOptions = ImageLabelerOptions(
      confidenceThreshold: _lowConfidenceThreshold,
    );
    final lowLabeler = ImageLabeler(options: lowOptions);

    try {
      final highResults = await highLabeler.processImage(inputImage);
      highResults.sort((a, b) => b.confidence.compareTo(a.confidence));

      final highLabels = highResults.map((l) => l.label).toList();
      final highLabelSet = highLabels.toSet();

      final lowResults = await lowLabeler.processImage(inputImage);
      lowResults.sort((a, b) => b.confidence.compareTo(a.confidence));

      // Append low-confidence labels not captured by the first pass.
      // The matcher weights them lower by virtue of positional index.
      final lowOnly = lowResults
          .where((l) => !highLabelSet.contains(l.label))
          .take(_maxLowConfidenceLabels)
          .map((l) => l.label)
          .toList();

      return [...highLabels, ...lowOnly];
    } finally {
      await highLabeler.close();
      await lowLabeler.close();
    }
  }
}
