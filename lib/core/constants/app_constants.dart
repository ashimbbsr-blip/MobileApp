class AppConstants {
  static const String appName = 'Infinite Nutrition Tracker';
  static const String appTagline = 'Better Health Every Day';

  // USDA Food Data Central API — built-in default key; override at build time via
  // flutter build apk --dart-define=USDA_API_KEY=your_key
  static const String usdaApiKey = String.fromEnvironment(
    'USDA_API_KEY',
    defaultValue: 'Bgn3gF9OaAKYl2OIGvjqv1WU1bbNekWmBblfH8Ne',
  );
  static const String usdaBaseUrl = 'https://api.nal.usda.gov/fdc/v1';

  // Google Gemini API (photo food scan) — no built-in default key; supply via
  // flutter build apk --dart-define=GEMINI_API_KEY=your_key or in Settings.
  static const String geminiApiKey = String.fromEnvironment(
    'GEMINI_API_KEY',
    defaultValue: '',
  );
  static const String geminiBaseUrl =
      'https://generativelanguage.googleapis.com/v1beta';
  static const String geminiModel = 'gemini-3.5-flash';
  static const int geminiCooldownSeconds = 60;

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
  static const String hiveMonthlySummaryBox = 'monthly_summary_box';
  static const String hiveLegalBox = 'legal_box';

  // Backup / Archive boxes (added v1.2 — long-term data lifecycle)
  static const String hiveWeightHistoryBox = 'weight_history_box';
  static const String hiveDailySummaryBox = 'daily_summary_box';   // archived daily summaries
  static const String hiveYearlySummaryBox = 'yearly_summary_box';

  // Backup / Archive constants
  static const int backupSchemaVersion = 1;
  static const String backupFileExtension = 'iht';
  static const String backupMagic = 'IHTBKP'; // header magic for .iht files

  // Data lifecycle thresholds (in days)
  static const int activeDataDays = 365;          // 0–12 months: full meal detail
  static const int archiveLevel1Days = 365;       // >12 months: meals → daily summary
  static const int archiveLevel2Days = 365 * 2;   // >24 months: daily → monthly
  static const int archiveLevel3Days = 365 * 5;   // >5 years: monthly → yearly

  // Settings keys for archive bookkeeping
  static const String keyLastBackupAt = 'last_backup_at';
  static const String keyLastArchiveAt = 'last_archive_at';
  static const String keyMeasurementUnit = 'measurement_unit'; // 'metric' | 'imperial'

  // Hive keys
  static const String keyUserProfile = 'user_profile';
  static const String keyThemeMode = 'theme_mode';
  static const String keyLanguage = 'language';
  static const String keyOnboardingDone = 'onboarding_done';
  static const String keyLegalAcceptance = 'legal_acceptance';
  static const String keyLocalDatasetLoaded = 'local_dataset_loaded';

  // USDA user-supplied API key (stored in settingsBox)
  static const String keyUserApiKey = 'user_usda_api_key';

  // Gemini user-supplied API key (stored in settingsBox)
  static const String keyUserGeminiApiKey = 'user_gemini_api_key';

  // Legal / policy versioning
  static const String currentPolicyVersion = '1.1.0';
  static const String currentAppVersion = '1.3.0';
}
