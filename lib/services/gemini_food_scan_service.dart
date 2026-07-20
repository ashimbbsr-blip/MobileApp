import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart' show debugPrint;

import '../core/constants/app_constants.dart';
import '../services/api_key_service.dart';
import 'usda_api_service.dart' show RateLimitException;

/// One dish/food detected in a photo by Gemini.
class DetectedFoodItem {
  final String nameEn;
  final List<String> altNames;
  final String portionDescription;
  final double estimatedGrams;
  final double confidence; // 0..1
  // Nutrition for the estimated portion (not per 100 g) — fallback values
  // used when no local database match is found.
  final double kcal;
  final double proteinG;
  final double carbsG;
  final double fatG;
  final double fiberG;

  const DetectedFoodItem({
    required this.nameEn,
    required this.altNames,
    required this.portionDescription,
    required this.estimatedGrams,
    required this.confidence,
    required this.kcal,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.fiberG,
  });

  static DetectedFoodItem? fromJson(Map<String, dynamic> json) {
    final name = (json['name_en'] as String?)?.trim();
    if (name == null || name.isEmpty) return null;
    double num_(String key) => (json[key] as num?)?.toDouble() ?? 0;
    return DetectedFoodItem(
      nameEn: name,
      altNames: (json['alt_names'] as List? ?? [])
          .whereType<String>()
          .map((s) => s.trim())
          .where((s) => s.isNotEmpty)
          .toList(),
      portionDescription: (json['portion_description'] as String? ?? '').trim(),
      estimatedGrams: num_('estimated_grams').clamp(5, 2000),
      confidence: num_('confidence').clamp(0, 1),
      kcal: num_('kcal_per_serving').clamp(0, 5000),
      proteinG: num_('protein_g').clamp(0, 500),
      carbsG: num_('carbs_g').clamp(0, 1000),
      fatG: num_('fat_g').clamp(0, 500),
      fiberG: num_('fiber_g').clamp(0, 200),
    );
  }
}

class ScanApiKeyException implements Exception {
  final String message;
  const ScanApiKeyException(this.message);
  @override
  String toString() => message;
}

class ScanNothingRecognizedException implements Exception {
  const ScanNothingRecognizedException();
  @override
  String toString() => 'No food was recognized in the photo.';
}

class ScanModelUnavailableException implements Exception {
  const ScanModelUnavailableException();
  @override
  String toString() =>
      'The recognition model is unavailable. Check for an app update.';
}

/// Sends a meal photo to Gemini and returns the detected dishes with portion
/// and nutrition estimates. Mirrors the error-handling patterns of
/// [UsdaApiService].
class GeminiFoodScanService {
  final Dio _dio;
  DateTime? _cooldownUntil;

  GeminiFoodScanService()
      : _dio = Dio(BaseOptions(
          baseUrl: AppConstants.geminiBaseUrl,
          connectTimeout: const Duration(seconds: 10),
          // Vision inference is slower than a plain search API.
          receiveTimeout: const Duration(seconds: 60),
        ));

  bool get isRateLimited =>
      _cooldownUntil != null && DateTime.now().isBefore(_cooldownUntil!);

  int get cooldownSecondsRemaining {
    if (!isRateLimited) return 0;
    return _cooldownUntil!.difference(DateTime.now()).inSeconds.clamp(0, 99999);
  }

  static const String _prompt = '''
You are a nutrition assistant analyzing a photo of a meal, with special expertise in Indian cuisine (North Indian, South Indian, Bengali) as well as common international foods.

Identify each distinct dish or food item visible in the photo (at most 6 items). For each item:
- "name_en": the common Indian-English name, e.g. "dal tadka", "chole", "roti", "aloo bhaja", "plain rice", "chicken curry".
- "alt_names": 2-5 alternate names to help match a food database: Hindi/Bengali transliterations, alternate spellings, or more generic names (e.g. for "dal tadka": ["toor dal", "arhar dal", "yellow lentil curry", "dal fry"]).
- "portion_description": a human-friendly description of the visible portion, e.g. "1 medium bowl (~150 g)" or "2 rotis".
- "estimated_grams": your best estimate of the visible portion weight in grams.
- "confidence": 0-1 confidence that the identification is correct.
- "kcal_per_serving", "protein_g", "carbs_g", "fat_g", "fiber_g": estimated nutrition FOR THE VISIBLE PORTION (not per 100 g).

Only include actual food or drink. If nothing edible is visible, return {"items": []}.''';

  static const Map<String, dynamic> _responseSchema = {
    'type': 'OBJECT',
    'properties': {
      'items': {
        'type': 'ARRAY',
        'items': {
          'type': 'OBJECT',
          'properties': {
            'name_en': {'type': 'STRING'},
            'alt_names': {
              'type': 'ARRAY',
              'items': {'type': 'STRING'},
            },
            'portion_description': {'type': 'STRING'},
            'estimated_grams': {'type': 'NUMBER'},
            'confidence': {'type': 'NUMBER'},
            'kcal_per_serving': {'type': 'NUMBER'},
            'protein_g': {'type': 'NUMBER'},
            'carbs_g': {'type': 'NUMBER'},
            'fat_g': {'type': 'NUMBER'},
            'fiber_g': {'type': 'NUMBER'},
          },
          'required': [
            'name_en',
            'alt_names',
            'portion_description',
            'estimated_grams',
            'confidence',
            'kcal_per_serving',
            'protein_g',
            'carbs_g',
            'fat_g',
            'fiber_g',
          ],
        },
      },
    },
    'required': ['items'],
  };

  Future<List<DetectedFoodItem>> analyzeImage(File image) async {
    if (isRateLimited) {
      throw RateLimitException(
        'Food scan is temporarily limited. Try again in a minute.',
        cooldownSeconds: cooldownSecondsRemaining,
      );
    }
    final key = ApiKeyService.instance.activeGeminiKey;
    if (key.isEmpty) {
      throw const ScanApiKeyException(
          'No Gemini API key configured. Add one in Settings.');
    }

    final b64 = base64Encode(await image.readAsBytes());
    return _doAnalyze(b64, key);
  }

  Future<List<DetectedFoodItem>> _doAnalyze(String b64, String key,
      {int attempt = 0}) async {
    try {
      final response = await _dio.post(
        '/models/${AppConstants.geminiModel}:generateContent',
        queryParameters: {'key': key},
        data: {
          'contents': [
            {
              'parts': [
                {
                  'inline_data': {'mime_type': 'image/jpeg', 'data': b64}
                },
                {'text': _prompt},
              ],
            },
          ],
          'generationConfig': {
            'temperature': 0.2,
            'response_mime_type': 'application/json',
            'response_schema': _responseSchema,
          },
        },
      );

      final items = _parseResponse(response.data);
      if (items.isEmpty) throw const ScanNothingRecognizedException();
      return items;
    } on DioException catch (e) {
      final status = e.response?.statusCode;

      if (status == 429) {
        _cooldownUntil = DateTime.now().add(
          const Duration(seconds: AppConstants.geminiCooldownSeconds),
        );
        throw const RateLimitException(
          'Food scan is temporarily limited (free quota). Try again in a minute.',
          cooldownSeconds: AppConstants.geminiCooldownSeconds,
        );
      }

      if (e.type == DioExceptionType.connectionError) {
        throw Exception(
            'No internet connection. Check your network and try again.');
      }

      final isTimeout = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout;
      if (isTimeout && attempt < 1) {
        await Future.delayed(Duration(seconds: 1 << attempt));
        return _doAnalyze(b64, key, attempt: attempt + 1);
      }
      if (isTimeout || e.type == DioExceptionType.receiveTimeout) {
        throw Exception(
            'Network timeout. Check your connection and try again.');
      }

      if (status == 404) throw const ScanModelUnavailableException();

      if (status == 400 || status == 401 || status == 403) {
        final body = e.response?.data;
        final msg = body is Map
            ? (body['error']?['message'] as String? ?? '')
            : '';
        debugPrint('[GeminiFoodScanService] HTTP $status: $msg');
        throw ScanApiKeyException(
            'Gemini API key error (HTTP $status). Check the key in Settings.');
      }

      throw Exception(
          'Scan failed (HTTP ${status ?? 'unknown'}). Please try again.');
    }
  }

  List<DetectedFoodItem> _parseResponse(dynamic data) {
    try {
      final candidates = data['candidates'] as List? ?? [];
      if (candidates.isEmpty) return [];
      final parts = candidates[0]['content']?['parts'] as List? ?? [];
      if (parts.isEmpty) return [];
      final text = parts[0]['text'] as String? ?? '';
      if (text.isEmpty) return [];
      final decoded = json.decode(text);
      final items = decoded is Map ? decoded['items'] as List? ?? [] : [];
      return items
          .whereType<Map>()
          .map((m) => DetectedFoodItem.fromJson(Map<String, dynamic>.from(m)))
          .whereType<DetectedFoodItem>()
          .toList();
    } catch (e) {
      debugPrint('[GeminiFoodScanService] parse failed: $e');
      return [];
    }
  }
}
