class AppConstants {
  static const String appName = 'Infinity Health Tracker';
  static const String appTagline = 'Better Health Every Day';

  static const String demoUsdaApiKey = 'DEMO_KEY';
  static const String usdaBaseUrl = 'https://api.nal.usda.gov/fdc/v1';

  static const String usdaApiKeySignupUrl =
      'https://fdc.nal.usda.gov/api-key-signup.html';

  // Search & Cache
  static const int maxRecentSearches = 10;
  static const int maxCachedFoods = 200;
  static const int minSearchQueryLength = 2;
  static const int searchCacheTtlMinutes = 10;
  static const int maxSessionCacheEntries = 50;

  // API rate-limit protection
  static const int rateLimitCooldownSeconds = 120;
  static const int maxSearchRetries = 2;

  // Calorie target
  static const double defaultCalorieTarget = 2000;

  // Hive box names
  static const String hiveUserBox = 'user_box';
  static const String hiveMealsBox = 'meals_box';
  static const String hiveFoodCacheBox = 'food_cache_box';
  static const String hiveSettingsBox = 'settings_box';
  static const String hiveDailyLogsBox = 'daily_logs_box';
  static const String hiveMonthlySummaryBox = 'monthly_summary_box';
  static const String hiveLegalBox = 'legal_box';

  // Hive keys
  static const String keyUserProfile = 'user_profile';
  static const String keyThemeMode = 'theme_mode';
  static const String keyLanguage = 'language';
  static const String keyOnboardingDone = 'onboarding_done';
  static const String keyLegalAcceptance = 'legal_acceptance';
  static const String keyApiKey = 'usda_api_key';

  // Legal / policy versioning
  static const String currentPolicyVersion = '1.0.0';
  static const String currentAppVersion = '1.0.0';
}
