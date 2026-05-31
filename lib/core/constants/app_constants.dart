class AppConstants {
  static const String appName = 'Infinite Health Tracker';
  static const String appTagline = 'Better Health Every Day';

  // USDA Food Data Central API — managed key, not exposed to users
  static const String usdaApiKey = 'Bgn3gF9OaAKYl2OIGvjqv1WU1bbNekWmBblfH8Ne';
  static const String usdaBaseUrl = 'https://api.nal.usda.gov/fdc/v1';

  // Search & Cache
  static const int maxRecentSearches = 10;
  static const int maxCachedFoods = 200;
  static const int minSearchQueryLength = 1;
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
  static const String hiveLocalFoodBox = 'local_food_box';
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
  static const String keyLocalDatasetLoaded = 'local_dataset_loaded';

  // Notification settings keys
  static const String keyNotifEnabled = 'notif_enabled';
  static const String keyNotifHour = 'notif_hour';
  static const String keyNotifMinute = 'notif_minute';

  // Legal / policy versioning
  static const String currentPolicyVersion = '1.0.0';
  static const String currentAppVersion = '1.0';
}
