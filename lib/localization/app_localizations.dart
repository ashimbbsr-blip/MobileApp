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
  String get scanFood => _t('scanFood');
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
  String get cameraPermission => _t('cameraPermission');
  String get openSettings => _t('openSettings');
  String get detectingFood => _t('detectingFood');
  String get foodDetected => _t('foodDetected');
  String get confirmFood => _t('confirmFood');
  String get confidence => _t('confidence');
  String get lowConfidence => _t('lowConfidence');
  String get tryAgain => _t('tryAgain');
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
  String get fromCamera => _t('fromCamera');
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
  String get unableToIdentify => _t('unableToIdentify');
  String get modelNotAvailable => _t('modelNotAvailable');

  // Local dataset
  String get localDatasetReady => _t('localDatasetReady');
  String get searchBilingual => _t('searchBilingual');
  String get localResults => _t('localResults');
  String get searchUsda => _t('searchUsda');
  String get noLocalResults => _t('noLocalResults');

  // Camera scan UI
  String get analysing => _t('analysing');
  String get scanTip => _t('scanTip');
  String get searchManually => _t('searchManually');
  String get foodNotIdentified => _t('foodNotIdentified');
  String get tryBetterLighting => _t('tryBetterLighting');
  String get takeAnotherPhoto => _t('takeAnotherPhoto');
  String get searchFoodHint => _t('searchFoodHint');
  String get addTo => _t('addTo');
  String get didYouEat => _t('didYouEat');
  String get notYourFood => _t('notYourFood');
  String get searchHintSheet => _t('searchHintSheet');
  String get howMuch => _t('howMuch');
  String get portionSmall => _t('portionSmall');
  String get portionMedium => _t('portionMedium');
  String get portionLarge => _t('portionLarge');
  String get portionXl => _t('portionXl');
  String get portionCustom => _t('portionCustom');
  String get enterGrams => _t('enterGrams');

  String _t(String key) => _translations[language]?[key] ?? _translations['en']![key] ?? key;

  static const Map<String, Map<String, String>> _translations = {
    'en': {
      'appName': 'Infinite Health Tracker',
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
      'scanFood': 'Scan Food',
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
      'welcomeTitle': 'Welcome to\nInfinite Health Tracker',
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
      'cameraPermission': 'Camera permission is required to scan food.',
      'openSettings': 'Open Settings',
      'detectingFood': 'Detecting food...',
      'foodDetected': 'Food Detected',
      'confirmFood': 'Confirm Food',
      'confidence': 'Confidence',
      'lowConfidence': 'Low confidence. Try retaking.',
      'tryAgain': 'Try Again',
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
      'fromCamera': 'From Camera',
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
      'legalBullet4': 'AI food scanning may be inaccurate — always verify results.',
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
      'usdaSkipNote': 'Skipping uses the demo key (limited to 30 searches/hour). You can add your key anytime in Settings.',
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
      'apiKeyUsingDemo': 'Using demo key (limited)',
      'apiKeyDemoNote': '30 searches/hour — add your free key for more',
      'apiKeyAdd': 'Add My API Key',
      'apiKeyUpdate': 'Update API Key',
      'apiKeyValidate': 'Validate API Key',
      'apiKeyValidating': 'Validating...',
      'apiKeyRemove': 'Remove API Key',
      'apiKeyRemoveConfirm': 'Remove your API key? The app will switch to the demo key (limited searches).',
      'apiKeyValid': 'Key is valid and working',
      'apiKeyInvalid': 'Validation failed — check your key',
      'apiKeyDialogHint': 'Register at fdc.nal.usda.gov for a free key — it will be emailed to you.',
      'apiKeyPaste': 'Paste your API key here',
      'apiKeyGetFree': 'Get a free API key',
      // Food detection
      'unableToIdentify': 'Unable to confidently identify this food. Try again with better lighting.',
      'modelNotAvailable': 'Food detection model unavailable. Please install the model file.',
      // Local dataset
      'localDatasetReady': '1,057 foods available offline',
      'searchBilingual': 'Search in English or Bengali…',
      'localResults': 'Results from local dataset',
      'searchUsda': 'Search USDA Database',
      'noLocalResults': 'No local results — try USDA search',
      // Camera scan UI
      'analysing': 'Analysing…',
      'scanTip': 'Place food in frame, then tap the button',
      'searchManually': 'Search manually instead',
      'foodNotIdentified': 'Food not identified',
      'tryBetterLighting': 'Try better lighting or search below.',
      'takeAnotherPhoto': 'Take another photo',
      'searchFoodHint': 'e.g. dal, ilish, chicken curry…',
      'addTo': 'Add to',
      'didYouEat': 'Did you eat:',
      'notYourFood': 'Not your food? Search here',
      'searchHintSheet': 'e.g. ilish, paneer, dal…',
      'howMuch': 'How much?',
      'portionSmall': 'Small',
      'portionMedium': 'Medium',
      'portionLarge': 'Large',
      'portionXl': 'XL',
      'portionCustom': 'Custom',
      'enterGrams': 'Enter grams',
    },
    'bn': {
      'appName': 'ইনফিনিট হেলথ ট্র্যাকার',
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
      'scanFood': 'খাবার স্ক্যান',
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
      'welcomeTitle': 'ইনফিনিট হেলথ\nট্র্যাকারে স্বাগতম',
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
      'cameraPermission': 'খাবার স্ক্যান করতে ক্যামেরার অনুমতি প্রয়োজন।',
      'openSettings': 'সেটিংস খুলুন',
      'detectingFood': 'খাবার শনাক্ত করা হচ্ছে...',
      'foodDetected': 'খাবার শনাক্ত হয়েছে',
      'confirmFood': 'খাবার নিশ্চিত করুন',
      'confidence': 'নিশ্চিততা',
      'lowConfidence': 'কম নিশ্চিততা। আবার তুলুন।',
      'tryAgain': 'আবার চেষ্টা করুন',
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
      'fromCamera': 'ক্যামেরা থেকে',
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
      'legalBullet4': 'AI ফুড স্ক্যানিং ভুল হতে পারে — সর্বদা ফলাফল যাচাই করুন।',
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
      'usdaSkipNote': 'এড়িয়ে গেলে ডেমো কী ব্যবহার হবে (প্রতি ঘণ্টায় ৩০টি অনুসন্ধান সীমিত)। সেটিংসে যেকোনো সময় কী যোগ করতে পারবেন।',
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
      'apiKeyUsingDemo': 'ডেমো কী ব্যবহার হচ্ছে (সীমিত)',
      'apiKeyDemoNote': 'প্রতি ঘণ্টায় ৩০টি অনুসন্ধান — বেশির জন্য নিজের কী যোগ করুন',
      'apiKeyAdd': 'আমার API কী যোগ করুন',
      'apiKeyUpdate': 'API কী আপডেট করুন',
      'apiKeyValidate': 'API কী যাচাই করুন',
      'apiKeyValidating': 'যাচাই হচ্ছে...',
      'apiKeyRemove': 'API কী সরান',
      'apiKeyRemoveConfirm': 'API কী সরাবেন? অ্যাপ ডেমো কীতে ফিরে যাবে (সীমিত অনুসন্ধান)।',
      'apiKeyValid': 'কী সঠিক এবং কার্যকর',
      'apiKeyInvalid': 'যাচাই ব্যর্থ — কী পরীক্ষা করুন',
      'apiKeyDialogHint': 'বিনামূল্যে কীর জন্য fdc.nal.usda.gov-এ নিবন্ধন করুন — ইমেইলে পাঠানো হবে।',
      'apiKeyPaste': 'এখানে API কী পেস্ট করুন',
      'apiKeyGetFree': 'বিনামূল্যে API কী পান',
      // Food detection
      'unableToIdentify': 'এই খাবারটি আত্মবিশ্বাসের সাথে চিহ্নিত করা সম্ভব হয়নি। আরও ভালো আলোতে আবার চেষ্টা করুন।',
      'modelNotAvailable': 'ফুড ডিটেকশন মডেল পাওয়া যাচ্ছে না। মডেল ফাইলটি ইনস্টল করুন।',
      // Local dataset
      'localDatasetReady': '১,০৫৭টি খাবার অফলাইনে উপলব্ধ',
      'searchBilingual': 'বাংলা বা ইংরেজিতে খুঁজুন…',
      'localResults': 'স্থানীয় ডেটা থেকে ফলাফল',
      'searchUsda': 'USDA ডেটাবেজে খুঁজুন',
      'noLocalResults': 'স্থানীয় ডেটায় নেই — USDA খুঁজুন',
      // Camera scan UI
      'analysing': 'বিশ্লেষণ হচ্ছে…',
      'scanTip': 'খাবার ফ্রেমে রাখুন, তারপর বোতাম চাপুন',
      'searchManually': 'পরিবর্তে ম্যানুয়ালি অনুসন্ধান করুন',
      'foodNotIdentified': 'খাবার চিহ্নিত হয়নি',
      'tryBetterLighting': 'আরও ভালো আলোতে চেষ্টা করুন বা নিচে অনুসন্ধান করুন।',
      'takeAnotherPhoto': 'আরেকটি ছবি তুলুন',
      'searchFoodHint': 'যেমন: ডাল, ইলিশ, মুরগির তরকারি…',
      'addTo': 'যোগ করুন',
      'didYouEat': 'আপনি কি খেয়েছেন:',
      'notYourFood': 'আপনার খাবার নয়? এখানে খুঁজুন',
      'searchHintSheet': 'যেমন: ইলিশ, পনির, ডাল…',
      'howMuch': 'কতটুকু?',
      'portionSmall': 'ছোট',
      'portionMedium': 'মাঝারি',
      'portionLarge': 'বড়',
      'portionXl': 'অতিরিক্ত বড়',
      'portionCustom': 'কাস্টম',
      'enterGrams': 'গ্রাম লিখুন',
    },
  };
}
