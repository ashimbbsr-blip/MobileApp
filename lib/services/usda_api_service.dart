import 'package:dio/dio.dart';
import '../core/constants/app_constants.dart';
import '../models/food_item.dart';
import '../services/api_key_service.dart';
import 'package:uuid/uuid.dart';

class RateLimitException implements Exception {
  final String message;
  final int cooldownSeconds;
  const RateLimitException(this.message, {this.cooldownSeconds = 120});

  @override
  String toString() => message;
}

class UsdaApiService {
  final Dio _dio;
  final _uuid = const Uuid();

  // In-flight deduplication: same query → same Future, one network request
  final Map<String, Future<List<FoodItem>>> _inFlight = {};

  // Rate-limit cooldown: after a 429, pause all requests for a period
  DateTime? _cooldownUntil;

  UsdaApiService()
      : _dio = Dio(BaseOptions(
          baseUrl: AppConstants.usdaBaseUrl,
          connectTimeout: const Duration(seconds: 10),
          receiveTimeout: const Duration(seconds: 15),
        ));

  bool get isRateLimited =>
      _cooldownUntil != null && DateTime.now().isBefore(_cooldownUntil!);

  int get cooldownSecondsRemaining {
    if (!isRateLimited) return 0;
    return _cooldownUntil!.difference(DateTime.now()).inSeconds.clamp(0, 99999);
  }

  Future<List<FoodItem>> searchFoods(String query) async {
    if (isRateLimited) {
      throw RateLimitException(
        'Food search is temporarily limited. Previously searched foods are still available.',
        cooldownSeconds: cooldownSecondsRemaining,
      );
    }

    // Return the same future if this exact query is already in-flight
    if (_inFlight.containsKey(query)) {
      return _inFlight[query]!;
    }

    final future = _doSearch(query);
    _inFlight[query] = future;
    try {
      return await future;
    } finally {
      _inFlight.remove(query);
    }
  }

  Future<List<FoodItem>> _doSearch(String query, {int attempt = 0}) async {
    try {
      final response = await _dio.get('/foods/search', queryParameters: {
        'query': query,
        'api_key': ApiKeyService.instance.activeKey,
        'pageSize': 20,
        'dataType': 'Foundation,SR Legacy,Branded',
      });

      if (response.statusCode == 200 && response.data != null) {
        final foods = response.data['foods'] as List? ?? [];
        return foods
            .map((food) => _parseFoodItem(food))
            .whereType<FoodItem>()
            .toList();
      }
      return [];
    } on DioException catch (e) {
      if (e.response?.statusCode == 429) {
        _cooldownUntil = DateTime.now().add(
          const Duration(seconds: AppConstants.rateLimitCooldownSeconds),
        );
        throw RateLimitException(
          'Food search is temporarily limited. Previously searched foods are still available.',
          cooldownSeconds: AppConstants.rateLimitCooldownSeconds,
        );
      }

      // Real network failure (airplane mode, no wifi, DNS failure, etc.)
      if (e.type == DioExceptionType.connectionError) {
        throw Exception('No internet connection. Check your network and try again.');
      }

      // Exponential backoff on timeout (attempt 0→1s, 1→2s, 2→4s)
      final isTimeout = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout;
      if (isTimeout && attempt < AppConstants.maxSearchRetries) {
        await Future.delayed(Duration(seconds: 1 << attempt));
        return _doSearch(query, attempt: attempt + 1);
      }

      if (isTimeout || e.type == DioExceptionType.receiveTimeout) {
        throw Exception('Network timeout. Check your connection and try again.');
      }

      // 403/401 → invalid or missing API key
      final status = e.response?.statusCode;
      if (status == 403 || status == 401) {
        throw Exception('USDA API key error (HTTP $status). The search service is temporarily unavailable.');
      }

      throw Exception('Search failed (HTTP ${status ?? 'unknown'}). Please try again.');
    }
  }

  Future<FoodItem?> getFoodDetails(String fdcId) async {
    if (isRateLimited) return null;
    try {
      final response = await _dio.get('/food/$fdcId', queryParameters: {
        'api_key': ApiKeyService.instance.activeKey,
      });
      if (response.statusCode == 200 && response.data != null) {
        return _parseFoodItem(response.data);
      }
      return null;
    } catch (_) {
      return null;
    }
  }

  FoodItem? _parseFoodItem(Map<String, dynamic> data) {
    try {
      final nutrients = _extractNutrients(data);
      final servingSize = (data['servingSize'] as num?)?.toDouble() ?? 100.0;
      final servingUnit = data['servingSizeUnit'] as String? ?? 'g';

      return FoodItem(
        id: _uuid.v4(),
        name: data['description'] as String? ?? 'Unknown Food',
        brand: data['brandOwner'] as String?,
        servingSize: servingSize,
        servingUnit: servingUnit,
        calories: nutrients['energy'] ?? 0,
        proteinG: nutrients['protein'] ?? 0,
        carbsG: nutrients['carbohydrate'] ?? 0,
        fatG: nutrients['fat'] ?? 0,
        fiberG: nutrients['fiber'] ?? 0,
        vitaminAMcg: nutrients['vitaminA'],
        vitaminCMg: nutrients['vitaminC'],
        vitaminDMcg: nutrients['vitaminD'],
        calciumMg: nutrients['calcium'],
        ironMg: nutrients['iron'],
        potassiumMg: nutrients['potassium'],
        magnesiumMg: nutrients['magnesium'],
        zincMg: nutrients['zinc'],
        usdaFdcId: data['fdcId']?.toString(),
        isCustom: false,
      );
    } catch (_) {
      return null;
    }
  }

  Map<String, double> _extractNutrients(Map<String, dynamic> data) {
    final result = <String, double>{};
    final nutrients = data['foodNutrients'] as List? ?? [];

    for (final nutrient in nutrients) {
      final rawNumber = nutrient['number'];
      final id = nutrient['nutrientId'] is int
          ? nutrient['nutrientId'] as int
          : (rawNumber is String
              ? int.tryParse(rawNumber) ?? 0
              : (rawNumber is int ? rawNumber : 0));
      final value = (nutrient['value'] as num?)?.toDouble() ??
          (nutrient['amount'] as num?)?.toDouble() ??
          0;
      final name = (nutrient['nutrientName'] ?? nutrient['name'] ?? '') as String;

      if (name.contains('Energy') || id == 1008) result['energy'] = value;
      else if (name.contains('Protein') || id == 1003) result['protein'] = value;
      else if (name.contains('Carbohydrate') || id == 1005) result['carbohydrate'] = value;
      else if (name.contains('Total lipid') || id == 1004) result['fat'] = value;
      else if (name.contains('Fiber') || id == 1079) result['fiber'] = value;
      else if (name.contains('Vitamin A') || id == 1106) result['vitaminA'] = value;
      else if (name.contains('Vitamin C') || id == 1162) result['vitaminC'] = value;
      else if (name.contains('Vitamin D') || id == 1114) result['vitaminD'] = value;
      else if (name.contains('Calcium') || id == 1087) result['calcium'] = value;
      else if (name.contains('Iron') || id == 1089) result['iron'] = value;
      else if (name.contains('Potassium') || id == 1092) result['potassium'] = value;
      else if (name.contains('Magnesium') || id == 1090) result['magnesium'] = value;
      else if (name.contains('Zinc') || id == 1095) result['zinc'] = value;
    }
    return result;
  }
}
