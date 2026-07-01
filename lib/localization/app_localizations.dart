class AppStrings {
  final String language;
  AppStrings(this.language);

  bool get isBengali => language == 'bn';

  String get appName => _t('appName');
  String get tagline => _t('tagline');
  String get dashboard => _t('dashboard');
  String get foodSearch => _t('foodSearch');
  String get meals => _t('meals');
  String get settings => _t('settings');
  String get micronutrients => _t('micronutrients');
  String get calories => _t('calories');
  String get protein => _t('protein');
  String get carbs => _t('carbs');
  String get fat => _t('fat');
  String get fiber => _t('fiber');
  String get water => _t('water');
  String get breakfast => _t('breakfast');
  String get lunch => _t('lunch');
  String get dinner => _t('dinner');
  String get snack => _t('snack');
  String get addFood => _t('addFood');
  String get searchFood => _t('searchFood');
  String get today => _t('today');
  String get goal => _t('goal');
  String get remaining => _t('remaining');
  String get consumed => _t('consumed');
  String get grams => _t('grams');
  String get mg => _t('mg');
  String get mcg => _t('mcg');
  String get ml => _t('ml');
  String get kcal => _t('kcal');
  String get age => _t('age');
  String get gender => _t('gender');
  String get height => _t('height');
  String get weight => _t('weight');
  String get activityLevel => _t('activityLevel');
  String get fitnessGoal => _t('fitnessGoal');
  String get male => _t('male');
  String get female => _t('female');
  String get sedentary => _t('sedentary');
  String get lightlyActive => _t('lightlyActive');
  String get moderatelyActive => _t('moderatelyActive');
  String get veryActive => _t('veryActive');
  String get extraActive => _t('extraActive');
  String get loseWeight => _t('loseWeight');
  String get maintain => _t('maintain');
  String get gainMuscle => _t('gainMuscle');
  String get healthyFatLoss => _t('healthyFatLoss');
  String get next => _t('next');
  String get back => _t('back');
  String get save => _t('save');
  String get cancel => _t('cancel');
  String get delete => _t('delete');
  String get edit => _t('edit');
  String get done => _t('done');
  String get search => _t('search');
  String get noResults => _t('noResults');
  String get offline => _t('offline');
  String get loading => _t('loading');
  String get error => _t('error');
  String get retry => _t('retry');
  String get theme => _t('theme');
  String get languageLabel => _t('language');
  String get lightMode => _t('lightMode');
  String get darkMode => _t('darkMode');
  String get systemDefault => _t('systemDefault');
  String get english => _t('english');
  String get bengali => _t('bengali');
  String get clearCache => _t('clearCache');
  String get resetData => _t('resetData');
  String get about => _t('about');
  String get version => _t('version');
  String get servingSize => _t('servingSize');
  String get quantity => _t('quantity');
  String get addToMeal => _t('addToMeal');
  String get selectMeal => _t('selectMeal');
  String get nutritionFacts => _t('nutritionFacts');
  String get vitamins => _t('vitamins');
  String get minerals => _t('minerals');
  String get welcomeTitle => _t('welcomeTitle');
  String get welcomeSubtitle => _t('welcomeSubtitle');
  String get getStarted => _t('getStarted');
  String get profile => _t('profile');
  String get bmr => _t('bmr');
  String get tdee => _t('tdee');
  String get bmi => _t('bmi');
  String get dailyGoals => _t('dailyGoals');
  String get weeklyProgress => _t('weeklyProgress');
  String get noFoodLogged => _t('noFoodLogged');
  String get tapToAdd => _t('tapToAdd');
  String get permissionDenied => _t('permissionDenied');
  String get openSettings => _t('openSettings');
  String get customFood => _t('customFood');
  String get recent => _t('recent');
  String get vitaminA => _t('vitaminA');
  String get vitaminB => _t('vitaminB');
  String get vitaminC => _t('vitaminC');
  String get vitaminD => _t('vitaminD');
  String get vitaminE => _t('vitaminE');
  String get calcium => _t('calcium');
  String get iron => _t('iron');
  String get magnesium => _t('magnesium');
  String get potassium => _t('potassium');
  String get zinc => _t('zinc');
  String get updateProfile => _t('updateProfile');
  String get calorieGoal => _t('calorieGoal');
  String get proteinGoal => _t('proteinGoal');
  String get carbsGoal => _t('carbsGoal');
  String get fatGoal => _t('fatGoal');
  String get step => _t('step');
  String get ofWord => _t('of');
  String get years => _t('years');
  String get cm => _t('cm');
  String get kg => _t('kg');
  String get dailySummary => _t('dailySummary');
  String get statusOver => _t('statusOver');
  String get statusGood => _t('statusGood');
  String get statusLow => _t('statusLow');
  String get statusVeryLow => _t('statusVeryLow');
  String get update => _t('update');

  // History & Analytics
  String get historyAnalytics => _t('historyAnalytics');
  String get days7 => _t('days7');
  String get days30 => _t('days30');
  String get monthly => _t('monthly');
  String get streak => _t('streak');
  String get goalCompletion => _t('goalCompletion');
  String get calorieTrend => _t('calorieTrend');
  String get macroBreakdown => _t('macroBreakdown');
  String get noHistory => _t('noHistory');
  String get loggedDays => _t('loggedDays');
  String get consistency => _t('consistency');
  String get noDataForPeriod => _t('noDataForPeriod');

  // Profile
  String get editProfile => _t('editProfile');
  String get profilePicture => _t('profilePicture');
  String get fromGallery => _t('fromGallery');
  String get fullName => _t('fullName');
  String get dateOfBirth => _t('dateOfBirth');
  String get profileUpdated => _t('profileUpdated');
  String get personalInfo => _t('personalInfo');
  String get bodyMeasurements => _t('bodyMeasurements');
  String get stats => _t('stats');
  String get selectDate => _t('selectDate');

  // Export
  String get dataExport => _t('dataExport');
  String get exportCsv => _t('exportCsv');
  String get exportJson => _t('exportJson');
  String get exportSuccess => _t('exportSuccess');
  String get exportFailed => _t('exportFailed');
  String get exporting => _t('exporting');

  // Food search — rate limit & cache
  String get rateLimitTitle => _t('rateLimitTitle');
  String get rateLimitMessage => _t('rateLimitMessage');
  String get cachedResults => _t('cachedResults');
  String get searchMinChars => _t('searchMinChars');

  // Legal & consent
  String get legalTerms => _t('legalTerms');
  String get legalPrivacy => _t('legalPrivacy');
  String get legalHealth => _t('legalHealth');
  String get legalSection => _t('legalSection');
  String get legalAcceptTitle => _t('legalAcceptTitle');
  String get legalAcceptSubtitle => _t('legalAcceptSubtitle');
  String get legalUpdatedTitle => _t('legalUpdatedTitle');
  String get legalUpdatedSubtitle => _t('legalUpdatedSubtitle');
  String get legalQuickSummary => _t('legalQuickSummary');
  String get legalBullet1 => _t('legalBullet1');
  String get legalBullet2 => _t('legalBullet2');
  String get legalBullet3 => _t('legalBullet3');
  String get legalBullet4 => _t('legalBullet4');
  String get legalBullet5 => _t('legalBullet5');
  String get legalReadDocs => _t('legalReadDocs');
  String get legalCheckTerms => _t('legalCheckTerms');
  String get legalCheckHealth => _t('legalCheckHealth');
  String get legalAcceptButton => _t('legalAcceptButton');
  String get legalAcceptedOn => _t('legalAcceptedOn');
  String get legalPolicyVersion => _t('legalPolicyVersion');

  // Registration & onboarding
  String get emailAddress => _t('emailAddress');
  String get optional => _t('optional');

  // USDA API setup
  String get usdaSetupTitle => _t('usdaSetupTitle');
  String get usdaSetupDesc => _t('usdaSetupDesc');
  String get usdaRegisterKey => _t('usdaRegisterKey');
  String get usdaEnterKeyLabel => _t('usdaEnterKeyLabel');
  String get usdaEnterKeyHint => _t('usdaEnterKeyHint');
  String get usdaPasteKey => _t('usdaPasteKey');
  String get usdaValidateAndSave => _t('usdaValidateAndSave');
  String get usdaSkip => _t('usdaSkip');
  String get usdaSkipNote => _t('usdaSkipNote');
  String get usdaKeyValid => _t('usdaKeyValid');
  String get usdaKeyInvalid => _t('usdaKeyInvalid');
  String get usdaBullet1 => _t('usdaBullet1');
  String get usdaBullet2 => _t('usdaBullet2');
  String get usdaBullet3 => _t('usdaBullet3');
  String get usdaBullet4 => _t('usdaBullet4');
  String get usdaBullet5 => _t('usdaBullet5');

  // API key management in settings
  String get apiKeySection => _t('apiKeySection');
  String get apiKeyLabel => _t('apiKeyLabel');
  String get apiKeyUsingDemo => _t('apiKeyUsingDemo');
  String get apiKeyDemoNote => _t('apiKeyDemoNote');
  String get apiKeyAdd => _t('apiKeyAdd');
  String get apiKeyUpdate => _t('apiKeyUpdate');
  String get apiKeyValidate => _t('apiKeyValidate');
  String get apiKeyValidating => _t('apiKeyValidating');
  String get apiKeyRemove => _t('apiKeyRemove');
  String get apiKeyRemoveConfirm => _t('apiKeyRemoveConfirm');
  String get apiKeyValid => _t('apiKeyValid');
  String get apiKeyInvalid => _t('apiKeyInvalid');
  String get apiKeyDialogHint => _t('apiKeyDialogHint');
  String get apiKeyPaste => _t('apiKeyPaste');
  String get apiKeyGetFree => _t('apiKeyGetFree');

  // Food detection
  // Local dataset
  String get localDatasetReady => _t('localDatasetReady');
  String get searchBilingual => _t('searchBilingual');
  String get localResults => _t('localResults');
  String get searchUsda => _t('searchUsda');
  String get noLocalResults => _t('noLocalResults');

  // Custom Nutrition Limits
  String get customNutritionLimits => _t('customNutritionLimits');
  String get customLimitsToggle => _t('customLimitsToggle');
  String get customLimitsDisclaimer => _t('customLimitsDisclaimer');
  String get customLimitsDoctorNote => _t('customLimitsDoctorNote');
  String get customCalorieLimit => _t('customCalorieLimit');
  String get customProteinLimit => _t('customProteinLimit');
  String get customCarbsLimit => _t('customCarbsLimit');
  String get customFatLimit => _t('customFatLimit');
  String get useAutoCalculated => _t('useAutoCalculated');
  String get customLimitsActive => _t('customLimitsActive');

  // Activity & Burned Calories
  String get activityCalories => _t('activityCalories');
  String get activityBurned => _t('activityBurned');
  String get deductFromDaily => _t('deductFromDaily');
  String get netCalories => _t('netCalories');
  String get burnedKcalLabel => _t('burnedKcalLabel');
  String get logActivityBurned => _t('logActivityBurned');
  String get enterBurnedKcal => _t('enterBurnedKcal');
  String get items => _t('items');
  String get steps => _t('steps');

  // Help
  String get helpGuide => _t('helpGuide');

  // Reset dialog
  String get resetDataConfirm => _t('resetDataConfirm');

  // Add-to-meal snackbar
  String get addedTo => _t('addedTo');
  String get quantityRequired => _t('quantityRequired');

  // Onboarding validators
  String get nameRequired => _t('nameRequired');
  String get nameTooShort => _t('nameTooShort');
  String get emailOptionalHint => _t('emailOptionalHint');
  String get emailInvalid => _t('emailInvalid');
  String get dobRequired => _t('dobRequired');

  // Activity level descriptions
  String get activitySedentaryDesc => _t('activitySedentaryDesc');
  String get activityLightlyDesc => _t('activityLightlyDesc');
  String get activityModeratelyDesc => _t('activityModeratelyDesc');
  String get activityVeryDesc => _t('activityVeryDesc');
  String get activityExtraDesc => _t('activityExtraDesc');

  // Fitness goal descriptions
  String get goalLoseWeightDesc => _t('goalLoseWeightDesc');
  String get goalFatLossDesc => _t('goalFatLossDesc');
  String get goalMaintainDesc => _t('goalMaintainDesc');
  String get goalGainMuscleDesc => _t('goalGainMuscleDesc');

  // Pregnancy page
  String get pregnancyTitle => _t('pregnancyTitle');
  String get pregnancySubtitle => _t('pregnancySubtitle');
  String get pregnancyNotApplicable => _t('pregnancyNotApplicable');
  String get pregnancyNotApplicableDesc => _t('pregnancyNotApplicableDesc');
  String get pregnancyFirst => _t('pregnancyFirst');
  String get pregnancyFirstDesc => _t('pregnancyFirstDesc');
  String get pregnancySecond => _t('pregnancySecond');
  String get pregnancySecondDesc => _t('pregnancySecondDesc');
  String get pregnancyThird => _t('pregnancyThird');
  String get pregnancyThirdDesc => _t('pregnancyThirdDesc');
  String get pregnancyLactating => _t('pregnancyLactating');
  String get pregnancyLactatingDesc => _t('pregnancyLactatingDesc');

  // Food card / search
  String get perServing => _t('perServing');
  String foodsCount(int n) => isBengali ? '$n টি খাবার' : '$n foods';

  // Nutrition education
  String get fiberGoalInfo => _t('fiberGoalInfo');
  String get sodiumLabel => _t('sodiumLabel');
  String get ironWarningFemale => _t('ironWarningFemale');

  // Custom food units
  String get unitKatori => _t('unitKatori');
  String get unitTbsp => _t('unitTbsp');
  String get unitTsp => _t('unitTsp');

  String _t(String key) => _translations[language]?[key] ?? _translations['en']![key] ?? key;

  static const Map<String, Map<String, String>> _translations = {
    'en': {
      'appName': 'Infinite Nutrition Tracker',
      'tagline': 'Better Health Every Day',
      'dashboard': 'Dashboard',
      'foodSearch': 'Food Search',
      'meals': 'Meals',
      'settings': 'Settings',
      'micronutrients': 'Micronutrients',
      'calories': 'Calories',
      'protein': 'Protein',
      'carbs': 'Carbs',
      'fat': 'Fat',
      'fiber': 'Fiber',
      'water': 'Water',
      'breakfast': 'Breakfast',
      'lunch': 'Lunch',
      'dinner': 'Dinner',
      'snack': 'Snack',
      'addFood': 'Add Food',
      'searchFood': 'Search Food',
      'today': 'Today',
      'goal': 'Goal',
      'remaining': 'Remaining',
      'consumed': 'Consumed',
      'grams': 'g',
      'mg': 'mg',
      'mcg': 'mcg',
      'ml': 'ml',
      'kcal': 'kcal',
      'age': 'Age',
      'gender': 'Gender',
      'height': 'Height',
      'weight': 'Weight',
      'activityLevel': 'Activity Level',
      'fitnessGoal': 'Fitness Goal',
      'male': 'Male',
      'female': 'Female',
      'sedentary': 'Sedentary',
      'lightlyActive': 'Lightly Active',
      'moderatelyActive': 'Moderately Active',
      'veryActive': 'Very Active',
      'extraActive': 'Extra Active',
      'loseWeight': 'Lose Weight',
      'maintain': 'Maintain Weight',
      'gainMuscle': 'Gain Muscle',
      'healthyFatLoss': 'Healthy Fat Loss',
      'next': 'Next',
      'back': 'Back',
      'save': 'Save',
      'cancel': 'Cancel',
      'delete': 'Delete',
      'edit': 'Edit',
      'done': 'Done',
      'search': 'Search',
      'noResults': 'No results found',
      'offline': 'You\'re offline',
      'loading': 'Loading...',
      'error': 'Something went wrong',
      'retry': 'Retry',
      'theme': 'Theme',
      'language': 'Language',
      'lightMode': 'Light Mode',
      'darkMode': 'Dark Mode',
      'systemDefault': 'System Default',
      'english': 'English',
      'bengali': 'বাংলা',
      'clearCache': 'Clear Cache',
      'resetData': 'Reset All Data',
      'about': 'About',
      'version': 'Version',
      'servingSize': 'Serving Size',
      'quantity': 'Quantity',
      'addToMeal': 'Add to Meal',
      'selectMeal': 'Select Meal',
      'nutritionFacts': 'Nutrition Facts',
      'vitamins': 'Vitamins',
      'minerals': 'Minerals',
      'welcomeTitle': 'Welcome to\nInfinite Nutrition Tracker',
      'welcomeSubtitle': 'Your personal nutrition companion.\nTrack calories, macros & vitamins.',
      'getStarted': 'Get Started',
      'profile': 'Profile',
      'bmr': 'BMR',
      'tdee': 'TDEE',
      'bmi': 'BMI',
      'dailyGoals': 'Daily Goals',
      'weeklyProgress': 'Weekly Progress',
      'noFoodLogged': 'No food logged yet',
      'tapToAdd': 'Tap + to add food',
      'permissionDenied': 'Permission Denied',
      'openSettings': 'Open Settings',
      'customFood': 'Custom Food',
      'recent': 'Recent',
      'vitaminA': 'Vitamin A',
      'vitaminB': 'Vitamin B12',
      'vitaminC': 'Vitamin C',
      'vitaminD': 'Vitamin D',
      'vitaminE': 'Vitamin E',
      'calcium': 'Calcium',
      'iron': 'Iron',
      'magnesium': 'Magnesium',
      'potassium': 'Potassium',
      'zinc': 'Zinc',
      'updateProfile': 'Update Profile',
      'calorieGoal': 'Calorie Goal',
      'proteinGoal': 'Protein Goal',
      'carbsGoal': 'Carbs Goal',
      'fatGoal': 'Fat Goal',
      'step': 'Step',
      'of': 'of',
      'years': 'years',
      'cm': 'cm',
      'kg': 'kg',
      'dailySummary': 'Daily Summary',
      'statusOver': 'Over',
      'statusGood': 'Good',
      'statusLow': 'Low',
      'statusVeryLow': 'Very Low',
      'update': 'Update',
      // History & Analytics
      'historyAnalytics': 'History & Analytics',
      'days7': '7 Days',
      'days30': '30 Days',
      'monthly': 'Monthly',
      'streak': 'Streak',
      'goalCompletion': 'Goal Completion',
      'calorieTrend': 'Calorie Trend',
      'macroBreakdown': 'Macro Breakdown',
      'noHistory': 'No history yet',
      'loggedDays': 'Logged Days',
      'consistency': 'Consistency',
      'noDataForPeriod': 'No data for this period',
      // Profile
      'editProfile': 'Edit Profile',
      'profilePicture': 'Tap to change photo',
      'fromGallery': 'From Gallery',
      'fullName': 'Full Name',
      'dateOfBirth': 'Date of Birth',
      'profileUpdated': 'Profile updated successfully',
      'personalInfo': 'Personal Info',
      'bodyMeasurements': 'Body Measurements',
      'stats': 'Stats',
      'selectDate': 'Select date',
      // Export
      'dataExport': 'Data Export',
      'exportCsv': 'Export CSV',
      'exportJson': 'Export Backup (JSON)',
      'exportSuccess': 'Export shared successfully',
      'exportFailed': 'Export failed. Try again.',
      'exporting': 'Exporting...',
      // Food search — rate limit & cache
      'rateLimitTitle': 'Search Temporarily Limited',
      'rateLimitMessage': 'Food search is temporarily limited. Previously searched foods are still available.',
      'cachedResults': 'Showing cached results',
      'searchMinChars': 'Type at least 2 characters to search',
      // Legal & consent
      'legalTerms': 'Terms & Conditions',
      'legalPrivacy': 'Privacy Notice',
      'legalHealth': 'Health Disclaimer',
      'legalSection': 'LEGAL & PRIVACY',
      'legalAcceptTitle': 'Before You Begin',
      'legalAcceptSubtitle': 'Please review our terms before using the app.',
      'legalUpdatedTitle': 'Terms Updated',
      'legalUpdatedSubtitle': 'Our terms have been updated. Please review and accept to continue.',
      'legalQuickSummary': 'Quick Summary',
      'legalBullet1': 'All your data stays on your device — nothing leaves it.',
      'legalBullet2': 'We don\'t collect, track, or share your personal data.',
      'legalBullet3': 'Nutrition data is for wellness guidance only, not medical advice.',
      'legalBullet4': 'Always verify nutrition data against food labels for accuracy.',
      'legalBullet5': 'This app is not a substitute for professional medical advice.',
      'legalReadDocs': 'Read the full documents:',
      'legalCheckTerms': 'I have read and agree to the Terms & Conditions and Privacy Notice.',
      'legalCheckHealth': 'I understand this app provides general nutrition and wellness information only and is not medical advice.',
      'legalAcceptButton': 'Accept & Continue',
      'legalAcceptedOn': 'Accepted on',
      'legalPolicyVersion': 'Policy version',
      // Registration & onboarding
      'emailAddress': 'Email Address',
      'optional': 'Optional',
      // USDA API setup
      'usdaSetupTitle': 'Connect USDA Food Database',
      'usdaSetupDesc': 'To search millions of foods and get accurate nutrition data, you need a free USDA FoodData Central API key.',
      'usdaRegisterKey': 'Register Free API Key',
      'usdaEnterKeyLabel': 'Enter Your API Key',
      'usdaEnterKeyHint': 'Check your email after registering — the key arrives within minutes.',
      'usdaPasteKey': 'Paste API key here',
      'usdaValidateAndSave': 'Validate & Save',
      'usdaSkip': 'Skip for now',
      'usdaSkipNote': 'Skipping uses the built-in default key. You can add your own key anytime in Settings.',
      'usdaKeyValid': 'API key validated and saved!',
      'usdaKeyInvalid': 'Invalid API key. Please check and try again.',
      'usdaBullet1': 'Completely free — no credit card needed',
      'usdaBullet2': 'Takes only 2–3 minutes to register',
      'usdaBullet3': 'API key is sent to your email',
      'usdaBullet4': 'Stored only on your device — never shared',
      'usdaBullet5': 'No backend server — your data stays private',
      // API key management in settings
      'apiKeySection': 'FOOD DATABASE',
      'apiKeyLabel': 'USDA API Key',
      'apiKeyUsingDemo': 'Built-in key active ✓',
      'apiKeyDemoNote': 'Optionally add your own USDA key for dedicated access',
      'apiKeyAdd': 'Add My API Key',
      'apiKeyUpdate': 'Update API Key',
      'apiKeyValidate': 'Validate & Save',
      'apiKeyValidating': 'Validating...',
      'apiKeyRemove': 'Remove Custom Key',
      'apiKeyRemoveConfirm': 'Remove your custom API key? The app will switch back to the built-in default key.',
      'apiKeyValid': 'Key is valid and working',
      'apiKeyInvalid': 'Validation failed — check your key',
      'apiKeyDialogHint': 'Register at fdc.nal.usda.gov for a free key — it will be emailed to you.',
      'apiKeyPaste': 'Paste your API key here',
      'apiKeyGetFree': 'Get a free API key',
      // Local dataset
      'localDatasetReady': '3,215 foods available offline',
      'searchBilingual': 'Search in English or Bengali…',
      'localResults': 'Results from local dataset',
      'searchUsda': 'Search USDA Database',
      'noLocalResults': 'No local results — try USDA search',
      // Custom Nutrition Limits
      'customNutritionLimits': 'Custom Nutrition Goals',
      'customLimitsToggle': 'Set My Own Goals',
      'customLimitsDisclaimer': '⚠️  Medical Conditions Detected',
      'customLimitsDoctorNote': 'If you have diabetes, pregnancy, kidney disease, or any other medical condition, please strictly consult a doctor or registered dietitian before setting custom nutrition goals. Incorrect limits can be harmful.',
      'customCalorieLimit': 'Daily Calorie Limit (kcal)',
      'customProteinLimit': 'Protein Goal (g)',
      'customCarbsLimit': 'Carbs Goal (g)',
      'customFatLimit': 'Fat Goal (g)',
      'useAutoCalculated': 'Use auto-calculated goals',
      'customLimitsActive': 'Custom goals active',
      // Activity & Burned Calories
      'activityCalories': 'Activity Calories',
      'activityBurned': 'Activity Burned',
      'deductFromDaily': 'Deduct from daily calorie total',
      'netCalories': 'Net Calories',
      'burnedKcalLabel': 'Burned (kcal)',
      'logActivityBurned': 'Log Activity',
      'enterBurnedKcal': 'Enter burned calories',
      'items': 'items',
      'steps': 'steps',
      // Help & Settings
      'helpGuide': 'Help & Guide',
      'resetDataConfirm': 'This will permanently delete all your logged meals, profile, and food data. This action cannot be undone. Continue?',
      // Add-to-meal
      'addedTo': 'Added to',
      'quantityRequired': 'Please enter a quantity greater than 0',
      // Onboarding validators
      'nameRequired': 'Name is required',
      'nameTooShort': 'Name must be at least 2 characters',
      'emailOptionalHint': 'Optional — for your reference only',
      'emailInvalid': 'Please enter a valid email address',
      'dobRequired': 'Date of birth is required',
      // Activity level descriptions
      'activitySedentaryDesc': 'Desk job or mostly sitting; little to no exercise',
      'activityLightlyDesc': 'Light exercise 1–3 days/week or office job with walking',
      'activityModeratelyDesc': 'Moderate exercise 3–5 days/week',
      'activityVeryDesc': 'Hard exercise 6–7 days/week or physical job',
      'activityExtraDesc': 'Very hard exercise daily or two-a-day training',
      // Fitness goal descriptions
      'goalLoseWeightDesc': 'Calorie deficit to reduce body weight',
      'goalFatLossDesc': 'Moderate deficit to reduce fat while preserving muscle',
      'goalMaintainDesc': 'Eat at maintenance to sustain current weight',
      'goalGainMuscleDesc': 'Calorie surplus with high protein to build muscle',
      // Pregnancy page
      'pregnancyTitle': 'Pregnancy / Lactation',
      'pregnancySubtitle': 'Select your current status for personalised nutrition targets (ICMR 2020)',
      'pregnancyNotApplicable': 'Not Applicable',
      'pregnancyNotApplicableDesc': 'Not pregnant or breastfeeding',
      'pregnancyFirst': 'First Trimester',
      'pregnancyFirstDesc': '+0 kcal/day · +1g protein/day',
      'pregnancySecond': 'Second Trimester',
      'pregnancySecondDesc': '+350 kcal/day · +7.5g protein/day',
      'pregnancyThird': 'Third Trimester',
      'pregnancyThirdDesc': '+350 kcal/day · +22.5g protein/day',
      'pregnancyLactating': 'Breastfeeding',
      'pregnancyLactatingDesc': '+600 kcal/day · +19g protein/day',
      // Food card / search
      'perServing': 'per serving',
      // Nutrition education
      'fiberGoalInfo': 'Fiber aids digestion, lowers cholesterol, and stabilises blood sugar. ICMR recommends 40 g/day for adults.',
      'sodiumLabel': 'Sodium',
      'ironWarningFemale': 'Iron intake is below recommended levels. Females aged 19–50 need 29 mg/day (ICMR 2020).',
      // Custom food units (Indian)
      'unitKatori': 'katori (150 ml)',
      'unitTbsp': 'tbsp (15 ml)',
      'unitTsp': 'tsp (5 ml)',
    },
    'bn': {
      'appName': 'ইনফিনিট নিউট্রিশন ট্র্যাকার',
      'tagline': 'প্রতিদিন সুস্বাস্থ্য',
      'dashboard': 'ড্যাশবোর্ড',
      'foodSearch': 'খাবার খুঁজুন',
      'meals': 'খাবার তালিকা',
      'settings': 'সেটিংস',
      'micronutrients': 'মাইক্রোনিউট্রিয়েন্ট',
      'calories': 'ক্যালোরি',
      'protein': 'প্রোটিন',
      'carbs': 'কার্বস',
      'fat': 'ফ্যাট',
      'fiber': 'ফাইবার',
      'water': 'জল',
      'breakfast': 'সকালের খাবার',
      'lunch': 'দুপুরের খাবার',
      'dinner': 'রাতের খাবার',
      'snack': 'স্ন্যাকস',
      'addFood': 'খাবার যোগ করুন',
      'searchFood': 'খাবার অনুসন্ধান',
      'today': 'আজকে',
      'goal': 'লক্ষ্য',
      'remaining': 'বাকি',
      'consumed': 'গ্রহণ করা',
      'grams': 'গ্রাম',
      'mg': 'মিগ্রা',
      'mcg': 'মাইক্রোগ্রাম',
      'ml': 'মিলি',
      'kcal': 'কিলোক্যালোরি',
      'age': 'বয়স',
      'gender': 'লিঙ্গ',
      'height': 'উচ্চতা',
      'weight': 'ওজন',
      'activityLevel': 'কার্যকলাপের স্তর',
      'fitnessGoal': 'ফিটনেস লক্ষ্য',
      'male': 'পুরুষ',
      'female': 'মহিলা',
      'sedentary': 'নিষ্ক্রিয়',
      'lightlyActive': 'সামান্য সক্রিয়',
      'moderatelyActive': 'মাঝারিভাবে সক্রিয়',
      'veryActive': 'খুব সক্রিয়',
      'extraActive': 'অতিরিক্ত সক্রিয়',
      'loseWeight': 'ওজন কমানো',
      'maintain': 'ওজন বজায় রাখা',
      'gainMuscle': 'পেশী বাড়ানো',
      'healthyFatLoss': 'স্বাস্থ্যকর চর্বি কমানো',
      'next': 'পরবর্তী',
      'back': 'পিছনে',
      'save': 'সংরক্ষণ',
      'cancel': 'বাতিল',
      'delete': 'মুছুন',
      'edit': 'সম্পাদনা',
      'done': 'সম্পন্ন',
      'search': 'অনুসন্ধান',
      'noResults': 'কোনো ফলাফল পাওয়া যায়নি',
      'offline': 'ইন্টারনেট সংযোগ নেই',
      'loading': 'লোড হচ্ছে...',
      'error': 'কিছু ভুল হয়েছে',
      'retry': 'আবার চেষ্টা করুন',
      'theme': 'থিম',
      'language': 'ভাষা',
      'lightMode': 'লাইট মোড',
      'darkMode': 'ডার্ক মোড',
      'systemDefault': 'সিস্টেম ডিফল্ট',
      'english': 'English',
      'bengali': 'বাংলা',
      'clearCache': 'ক্যাশ পরিষ্কার করুন',
      'resetData': 'সব ডেটা রিসেট করুন',
      'about': 'সম্পর্কে',
      'version': 'সংস্করণ',
      'servingSize': 'পরিবেশন আকার',
      'quantity': 'পরিমাণ',
      'addToMeal': 'খাবারে যোগ করুন',
      'selectMeal': 'খাবার নির্বাচন করুন',
      'nutritionFacts': 'পুষ্টির তথ্য',
      'vitamins': 'ভিটামিন',
      'minerals': 'খনিজ',
      'welcomeTitle': 'ইনফিনিট নিউট্রিশন\nট্র্যাকারে স্বাগতম',
      'welcomeSubtitle': 'আপনার ব্যক্তিগত পুষ্টি সহায়ক।\nক্যালোরি, ম্যাক্রো এবং ভিটামিন ট্র্যাক করুন।',
      'getStarted': 'শুরু করুন',
      'profile': 'প্রোফাইল',
      'bmr': 'বিএমআর',
      'tdee': 'টিডিইই',
      'bmi': 'বিএমআই',
      'dailyGoals': 'দৈনিক লক্ষ্যমাত্রা',
      'weeklyProgress': 'সাপ্তাহিক অগ্রগতি',
      'noFoodLogged': 'এখনো কোনো খাবার লগ করা হয়নি',
      'tapToAdd': 'খাবার যোগ করতে + চাপুন',
      'permissionDenied': 'অনুমতি অস্বীকৃত',
      'openSettings': 'সেটিংস খুলুন',
      'customFood': 'কাস্টম খাবার',
      'recent': 'সাম্প্রতিক',
      'vitaminA': 'ভিটামিন এ',
      'vitaminB': 'ভিটামিন বি১২',
      'vitaminC': 'ভিটামিন সি',
      'vitaminD': 'ভিটামিন ডি',
      'vitaminE': 'ভিটামিন ই',
      'calcium': 'ক্যালসিয়াম',
      'iron': 'আয়রন',
      'magnesium': 'ম্যাগনেসিয়াম',
      'potassium': 'পটাশিয়াম',
      'zinc': 'জিঙ্ক',
      'updateProfile': 'প্রোফাইল আপডেট',
      'calorieGoal': 'ক্যালোরি লক্ষ্য',
      'proteinGoal': 'প্রোটিন লক্ষ্য',
      'carbsGoal': 'কার্বস লক্ষ্য',
      'fatGoal': 'ফ্যাট লক্ষ্য',
      'step': 'ধাপ',
      'of': 'এর',
      'years': 'বছর',
      'cm': 'সেমি',
      'kg': 'কেজি',
      'dailySummary': 'দৈনিক সারসংক্ষেপ',
      'statusOver': 'বেশি',
      'statusGood': 'ভালো',
      'statusLow': 'কম',
      'statusVeryLow': 'অনেক কম',
      'update': 'আপডেট',
      // History & Analytics
      'historyAnalytics': 'ইতিহাস ও বিশ্লেষণ',
      'days7': '৭ দিন',
      'days30': '৩০ দিন',
      'monthly': 'মাসিক',
      'streak': 'ধারাবাহিকতা',
      'goalCompletion': 'লক্ষ্য পূরণ',
      'calorieTrend': 'ক্যালোরি প্রবণতা',
      'macroBreakdown': 'ম্যাক্রো বিভাজন',
      'noHistory': 'এখনো কোনো ইতিহাস নেই',
      'loggedDays': 'লগ করা দিন',
      'consistency': 'ধারাবাহিকতা',
      'noDataForPeriod': 'এই সময়ের জন্য ডেটা নেই',
      // Profile
      'editProfile': 'প্রোফাইল সম্পাদনা',
      'profilePicture': 'ছবি পরিবর্তন করতে চাপুন',
      'fromGallery': 'গ্যালারি থেকে',
      'fullName': 'পুরো নাম',
      'dateOfBirth': 'জন্ম তারিখ',
      'profileUpdated': 'প্রোফাইল সফলভাবে আপডেট হয়েছে',
      'personalInfo': 'ব্যক্তিগত তথ্য',
      'bodyMeasurements': 'শারীরিক পরিমাপ',
      'stats': 'পরিসংখ্যান',
      'selectDate': 'তারিখ নির্বাচন করুন',
      // Export
      'dataExport': 'ডেটা রপ্তানি',
      'exportCsv': 'CSV রপ্তানি',
      'exportJson': 'ব্যাকআপ রপ্তানি (JSON)',
      'exportSuccess': 'রপ্তানি সফল হয়েছে',
      'exportFailed': 'রপ্তানি ব্যর্থ হয়েছে। আবার চেষ্টা করুন।',
      'exporting': 'রপ্তানি হচ্ছে...',
      // Food search — rate limit & cache
      'rateLimitTitle': 'অনুসন্ধান সাময়িকভাবে সীমিত',
      'rateLimitMessage': 'খাবার অনুসন্ধান সাময়িকভাবে সীমিত। আগে খোঁজা খাবারগুলো এখনো দেখা যাচ্ছে।',
      'cachedResults': 'সংরক্ষিত ফলাফল দেখানো হচ্ছে',
      'searchMinChars': 'অনুসন্ধানের জন্য কমপক্ষে ২টি অক্ষর টাইপ করুন',
      // Legal & consent
      'legalTerms': 'শর্তাবলী',
      'legalPrivacy': 'গোপনীয়তা বিজ্ঞপ্তি',
      'legalHealth': 'স্বাস্থ্য দাবিত্যাগ',
      'legalSection': 'আইনি ও গোপনীয়তা',
      'legalAcceptTitle': 'শুরু করার আগে',
      'legalAcceptSubtitle': 'অ্যাপ ব্যবহারের আগে আমাদের শর্তাবলী পর্যালোচনা করুন।',
      'legalUpdatedTitle': 'শর্তাবলী আপডেট হয়েছে',
      'legalUpdatedSubtitle': 'আমাদের শর্তাবলী আপডেট হয়েছে। চালিয়ে যেতে পর্যালোচনা করুন ও সম্মত হন।',
      'legalQuickSummary': 'সংক্ষিপ্ত বিবরণ',
      'legalBullet1': 'আপনার সব তথ্য আপনার ডিভাইসেই থাকে — কোথাও যায় না।',
      'legalBullet2': 'আমরা আপনার ব্যক্তিগত তথ্য সংগ্রহ, ট্র্যাক বা শেয়ার করি না।',
      'legalBullet3': 'পুষ্টির তথ্য শুধুমাত্র সুস্বাস্থ্য নির্দেশনার জন্য, চিকিৎসা পরামর্শ নয়।',
      'legalBullet4': 'সঠিকতার জন্য সর্বদা খাবারের লেবেলের সাথে পুষ্টির তথ্য যাচাই করুন।',
      'legalBullet5': 'এই অ্যাপ পেশাদার চিকিৎসা পরামর্শের বিকল্প নয়।',
      'legalReadDocs': 'সম্পূর্ণ দলিল পড়ুন:',
      'legalCheckTerms': 'আমি শর্তাবলী ও গোপনীয়তা বিজ্ঞপ্তি পড়েছি এবং সম্মত হচ্ছি।',
      'legalCheckHealth': 'আমি বুঝতে পারছি যে এই অ্যাপ শুধুমাত্র সাধারণ পুষ্টি ও সুস্বাস্থ্য তথ্য প্রদান করে এবং এটি কোনো চিকিৎসা পরামর্শ নয়।',
      'legalAcceptButton': 'গ্রহণ করুন ও চালিয়ে যান',
      'legalAcceptedOn': 'গ্রহণের তারিখ',
      'legalPolicyVersion': 'নীতি সংস্করণ',
      // Registration & onboarding
      'emailAddress': 'ইমেইল ঠিকানা',
      'optional': 'ঐচ্ছিক',
      // USDA API setup
      'usdaSetupTitle': 'USDA ফুড ডেটাবেজ সংযুক্ত করুন',
      'usdaSetupDesc': 'লক্ষ লক্ষ খাবার অনুসন্ধান করতে এবং সঠিক পুষ্টির তথ্য পেতে আপনার একটি বিনামূল্যে USDA FoodData Central API কী প্রয়োজন।',
      'usdaRegisterKey': 'বিনামূল্যে API কী নিন',
      'usdaEnterKeyLabel': 'আপনার API কী লিখুন',
      'usdaEnterKeyHint': 'নিবন্ধনের পর আপনার ইমেইলে কী আসবে — কয়েক মিনিটের মধ্যেই।',
      'usdaPasteKey': 'এখানে API কী পেস্ট করুন',
      'usdaValidateAndSave': 'যাচাই করুন ও সংরক্ষণ করুন',
      'usdaSkip': 'এখন এড়িয়ে যান',
      'usdaSkipNote': 'এড়িয়ে গেলে বিল্ট-ইন ডিফল্ট কী ব্যবহার হবে। সেটিংসে যেকোনো সময় নিজের কী যোগ করতে পারবেন।',
      'usdaKeyValid': 'API কী যাচাই ও সংরক্ষণ হয়েছে!',
      'usdaKeyInvalid': 'অবৈধ API কী। আবার চেষ্টা করুন।',
      'usdaBullet1': 'সম্পূর্ণ বিনামূল্যে — কার্ড লাগবে না',
      'usdaBullet2': 'মাত্র ২-৩ মিনিটে নিবন্ধন',
      'usdaBullet3': 'API কী আপনার ইমেইলে পাঠানো হবে',
      'usdaBullet4': 'শুধু আপনার ডিভাইসে সংরক্ষিত — কোথাও শেয়ার হয় না',
      'usdaBullet5': 'কোনো সার্ভার নেই — আপনার ডেটা সম্পূর্ণ প্রাইভেট',
      // API key management in settings
      'apiKeySection': 'ফুড ডেটাবেজ',
      'apiKeyLabel': 'USDA API কী',
      'apiKeyUsingDemo': 'বিল্ট-ইন কী সক্রিয় ✓',
      'apiKeyDemoNote': 'ঐচ্ছিকভাবে নিজের USDA কী যোগ করতে পারেন',
      'apiKeyAdd': 'আমার API কী যোগ করুন',
      'apiKeyUpdate': 'API কী আপডেট করুন',
      'apiKeyValidate': 'যাচাই করুন ও সংরক্ষণ করুন',
      'apiKeyValidating': 'যাচাই হচ্ছে...',
      'apiKeyRemove': 'কাস্টম কী সরান',
      'apiKeyRemoveConfirm': 'কাস্টম API কী সরাবেন? অ্যাপ বিল্ট-ইন ডিফল্ট কীতে ফিরে যাবে।',
      'apiKeyValid': 'কী সঠিক এবং কার্যকর',
      'apiKeyInvalid': 'যাচাই ব্যর্থ — কী পরীক্ষা করুন',
      'apiKeyDialogHint': 'বিনামূল্যে কীর জন্য fdc.nal.usda.gov-এ নিবন্ধন করুন — ইমেইলে পাঠানো হবে।',
      'apiKeyPaste': 'এখানে API কী পেস্ট করুন',
      'apiKeyGetFree': 'বিনামূল্যে API কী পান',
      // Local dataset
      'localDatasetReady': '৩,২১৫টি খাবার অফলাইনে উপলব্ধ',
      'searchBilingual': 'বাংলা বা ইংরেজিতে খুঁজুন…',
      'localResults': 'স্থানীয় ডেটা থেকে ফলাফল',
      'searchUsda': 'আন্তর্জাতিক ডেটাবেজে খুঁজুন',
      'noLocalResults': 'স্থানীয় ডেটায় নেই — আন্তর্জাতিক খুঁজুন',
      // Custom Nutrition Limits
      'customNutritionLimits': 'কাস্টম পুষ্টির লক্ষ্যমাত্রা',
      'customLimitsToggle': 'নিজের লক্ষ্য নির্ধারণ করুন',
      'customLimitsDisclaimer': '⚠️  চিকিৎসাগত অবস্থা',
      'customLimitsDoctorNote': 'ডায়াবেটিস, গর্ভাবস্থা, কিডনি রোগ বা অন্য কোনো চিকিৎসাগত সমস্যা থাকলে কাস্টম পুষ্টির লক্ষ্যমাত্রা নির্ধারণের আগে অবশ্যই ডাক্তার বা রেজিস্টার্ড পুষ্টিবিদের পরামর্শ নিন। ভুল সীমা স্বাস্থ্যের জন্য ক্ষতিকর হতে পারে।',
      'customCalorieLimit': 'দৈনিক ক্যালোরি সীমা (kcal)',
      'customProteinLimit': 'প্রোটিন লক্ষ্য (গ্রাম)',
      'customCarbsLimit': 'কার্বস লক্ষ্য (গ্রাম)',
      'customFatLimit': 'ফ্যাট লক্ষ্য (গ্রাম)',
      'useAutoCalculated': 'স্বয়ংক্রিয় হিসাব ব্যবহার করুন',
      'customLimitsActive': 'কাস্টম লক্ষ্য সক্রিয়',
      // Activity & Burned Calories
      'activityCalories': 'কার্যকলাপ ক্যালোরি',
      'activityBurned': 'কার্যকলাপে পোড়া',
      'deductFromDaily': 'দৈনিক মোট থেকে বাদ দিন',
      'netCalories': 'নেট ক্যালোরি',
      'burnedKcalLabel': 'পোড়া (কিলোক্যালোরি)',
      'logActivityBurned': 'কার্যকলাপ লগ করুন',
      'enterBurnedKcal': 'পোড়া ক্যালোরি লিখুন',
      'items': 'আইটেম',
      'steps': 'স্টেপ',
      // Help & Settings
      'helpGuide': 'সাহায্য ও গাইড',
      'resetDataConfirm': 'এটি আপনার সমস্ত লগ করা খাবার, প্রোফাইল এবং খাবারের তথ্য স্থায়ীভাবে মুছে দেবে। এই কাজটি পূর্বাবস্থায় ফেরানো যাবে না। চালিয়ে যাবেন?',
      // Add-to-meal
      'addedTo': 'যোগ হয়েছে',
      'quantityRequired': 'অনুগ্রহ করে ০-এর বেশি পরিমাণ লিখুন',
      // Onboarding validators
      'nameRequired': 'নাম আবশ্যক',
      'nameTooShort': 'নাম কমপক্ষে ২ অক্ষরের হতে হবে',
      'emailOptionalHint': 'ঐচ্ছিক — শুধুমাত্র আপনার রেফারেন্সের জন্য',
      'emailInvalid': 'অনুগ্রহ করে একটি বৈধ ইমেইল ঠিকানা দিন',
      'dobRequired': 'জন্ম তারিখ আবশ্যক',
      // Activity level descriptions
      'activitySedentaryDesc': 'ডেস্ক জব বা বেশিরভাগ বসে থাকা; সামান্য বা কোনো ব্যায়াম নেই',
      'activityLightlyDesc': 'সপ্তাহে ১–৩ দিন হালকা ব্যায়াম বা হাঁটা-চলা',
      'activityModeratelyDesc': 'সপ্তাহে ৩–৫ দিন মাঝারি ব্যায়াম',
      'activityVeryDesc': 'সপ্তাহে ৬–৭ দিন কঠোর ব্যায়াম বা শারীরিক কাজ',
      'activityExtraDesc': 'প্রতিদিন অত্যন্ত কঠোর ব্যায়াম বা দিনে দুবার প্রশিক্ষণ',
      // Fitness goal descriptions
      'goalLoseWeightDesc': 'শরীরের ওজন কমাতে ক্যালোরি ঘাটতি',
      'goalFatLossDesc': 'পেশী রেখে চর্বি কমাতে মাঝারি ক্যালোরি ঘাটতি',
      'goalMaintainDesc': 'বর্তমান ওজন বজায় রাখতে রক্ষণাবেক্ষণ মাত্রায় খাওয়া',
      'goalGainMuscleDesc': 'পেশী গড়তে বেশি প্রোটিন সহ ক্যালোরি উদ্বৃত্ত',
      // Pregnancy page
      'pregnancyTitle': 'গর্ভাবস্থা / স্তন্যপান',
      'pregnancySubtitle': 'ব্যক্তিগত পুষ্টির লক্ষ্যমাত্রার জন্য বর্তমান অবস্থা নির্বাচন করুন (ICMR 2020)',
      'pregnancyNotApplicable': 'প্রযোজ্য নয়',
      'pregnancyNotApplicableDesc': 'গর্ভবতী বা স্তন্যদানকারী নন',
      'pregnancyFirst': 'প্রথম ত্রৈমাসিক',
      'pregnancyFirstDesc': '+০ কিলোক্যালোরি/দিন · +১ গ্রাম প্রোটিন/দিন',
      'pregnancySecond': 'দ্বিতীয় ত্রৈমাসিক',
      'pregnancySecondDesc': '+৩৫০ কিলোক্যালোরি/দিন · +৭.৫ গ্রাম প্রোটিন/দিন',
      'pregnancyThird': 'তৃতীয় ত্রৈমাসিক',
      'pregnancyThirdDesc': '+৩৫০ কিলোক্যালোরি/দিন · +২২.৫ গ্রাম প্রোটিন/দিন',
      'pregnancyLactating': 'বুকের দুধ খাওয়ানো',
      'pregnancyLactatingDesc': '+৬০০ কিলোক্যালোরি/দিন · +১৯ গ্রাম প্রোটিন/দিন',
      // Food card / search
      'perServing': 'প্রতি পরিবেশনে',
      // Nutrition education
      'fiberGoalInfo': 'ফাইবার হজম সহজ করে, কোলেস্টেরল কমায় এবং রক্তের শর্করা স্থিতিশীল রাখে। ICMR প্রাপ্তবয়স্কদের জন্য দৈনিক ৪০ গ্রাম সুপারিশ করে।',
      'sodiumLabel': 'সোডিয়াম',
      'ironWarningFemale': 'আয়রন গ্রহণ সুপারিশকৃত মাত্রার নিচে। ১৯–৫০ বছর বয়সী মহিলাদের দৈনিক ২৯ মিগ্রা আয়রন প্রয়োজন (ICMR 2020)।',
      // Custom food units (Indian)
      'unitKatori': 'কাটোরি (১৫০ মিলি)',
      'unitTbsp': 'টেবিল চামচ (১৫ মিলি)',
      'unitTsp': 'চা চামচ (৫ মিলি)',
    },
  };
}
