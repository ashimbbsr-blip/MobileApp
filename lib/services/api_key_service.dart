import 'package:dio/dio.dart';
import '../core/constants/app_constants.dart';
import '../storage/hive_storage.dart';

class ApiKeyService {
  const ApiKeyService._();
  static const ApiKeyService instance = ApiKeyService._();

  String get activeKey => HiveStorage.getApiKey() ?? AppConstants.demoUsdaApiKey;

  bool get hasUserKey => HiveStorage.hasApiKey;

  String? get maskedKey {
    final key = HiveStorage.getApiKey();
    if (key == null || key.length < 8) return null;
    return '${key.substring(0, 4)}••••••••${key.substring(key.length - 4)}';
  }

  Future<void> saveKey(String key) => HiveStorage.saveApiKey(key.trim());

  Future<void> removeKey() => HiveStorage.removeApiKey();

  Future<bool> validateKey(String key) async {
    final trimmed = key.trim();
    if (trimmed.isEmpty) return false;
    try {
      final dio = Dio(BaseOptions(
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 10),
      ));
      final response = await dio.get(
        '${AppConstants.usdaBaseUrl}/foods/list',
        queryParameters: {'api_key': trimmed, 'pageSize': 1},
      );
      return response.statusCode == 200;
    } on DioException {
      return false;
    } catch (_) {
      return false;
    }
  }
}
