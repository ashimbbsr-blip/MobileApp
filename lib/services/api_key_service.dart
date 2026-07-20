import '../core/constants/app_constants.dart';
import '../storage/hive_storage.dart';

class ApiKeyService {
  const ApiKeyService._();
  static const ApiKeyService instance = ApiKeyService._();

  /// Returns the user's custom key if set; otherwise falls back to the built-in default key.
  String get activeKey {
    final stored = HiveStorage.userApiKey;
    if (stored != null && stored.isNotEmpty) return stored;
    return AppConstants.usdaApiKey;
  }

  bool get hasCustomKey => HiveStorage.userApiKey != null;

  /// Gemini key for photo food scan: user's custom key, else the build-time
  /// --dart-define default (empty when neither is set).
  String get activeGeminiKey {
    final stored = HiveStorage.userGeminiApiKey;
    if (stored != null && stored.isNotEmpty) return stored;
    return AppConstants.geminiApiKey;
  }

  bool get hasGeminiKey => activeGeminiKey.isNotEmpty;

  bool get hasCustomGeminiKey => HiveStorage.userGeminiApiKey != null;
}
