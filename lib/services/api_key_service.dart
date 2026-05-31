import '../core/constants/app_constants.dart';

class ApiKeyService {
  const ApiKeyService._();
  static const ApiKeyService instance = ApiKeyService._();

  String get activeKey => AppConstants.usdaApiKey;
}
