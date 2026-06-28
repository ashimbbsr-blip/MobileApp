import '../core/constants/app_constants.dart';
import '../storage/hive_storage.dart';

class ApiKeyService {
  const ApiKeyService._();
  static const ApiKeyService instance = ApiKeyService._();

  /// Returns the user's custom key if set; otherwise falls back to the
  /// compile-time key (defaults to DEMO_KEY if built without --dart-define).
  String get activeKey {
    final stored = HiveStorage.userApiKey;
    if (stored != null && stored.isNotEmpty) return stored;
    return AppConstants.usdaApiKey;
  }

  bool get hasCustomKey => HiveStorage.userApiKey != null;
}
