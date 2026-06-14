class LegalSection {
  final String heading;
  final String body;
  const LegalSection(this.heading, this.body);
}

enum LegalDocType { terms, privacy, health }

class LegalContent {
  static List<LegalSection> getSections(LegalDocType type, String lang) {
    if (lang == 'bn') {
      switch (type) {
        case LegalDocType.terms:
          return _termsBn;
        case LegalDocType.privacy:
          return _privacyBn;
        case LegalDocType.health:
          return _healthBn;
      }
    }
    switch (type) {
      case LegalDocType.terms:
        return _termsEn;
      case LegalDocType.privacy:
        return _privacyEn;
      case LegalDocType.health:
        return _healthEn;
    }
  }

  // ── TERMS & CONDITIONS — ENGLISH ──────────────────────────────────────────

  static const List<LegalSection> _termsEn = [
    LegalSection(
      '1. General Use',
      'Infinite Nutrition Tracker ("the App") is provided "as is" for informational '
          'and personal wellness purposes only. By using the App, you acknowledge that '
          'you do so at your own discretion and risk.\n\n'
          'The App is designed to assist in tracking nutrition and wellness habits — not '
          'to replace professional health guidance. Features, data, and calculations are '
          'provided for general guidance and should be treated as estimates only.',
    ),
    LegalSection(
      '2. No Medical Advice',
      'The App is NOT a medical application. It does NOT provide:\n\n'
          '• Medical advice, diagnosis, or clinical assessment\n'
          '• Treatment plans for any medical condition\n'
          '• Recommendations to replace prescribed medication or therapy\n'
          '• Any form of dietitian or physician consultation\n\n'
          'Nutrition data, calorie estimates, and wellness insights are for general '
          'informational purposes only. Always consult a qualified physician, dietitian, '
          'or licensed healthcare professional before making significant changes to your '
          'diet, exercise routine, or health practices.',
    ),
    LegalSection(
      '3. Nutrition Information Disclaimer',
      'Nutrition data is sourced from third-party databases including the USDA '
          'FoodData Central. While we strive to present accurate information, '
          'nutritional values may vary due to:\n\n'
          '• Differences in food preparation methods\n'
          '• Regional and brand-specific product variations\n'
          '• Database inaccuracies or updates over time\n'
          '• Natural variation in whole foods\n\n'
          'The App should not be relied upon for medical nutrition therapy, clinical '
          'dietary management, or any health-critical dietary decision.',
    ),
    LegalSection(
      '4. Data Accuracy Disclaimer',
      'Nutritional data in the App is sourced from curated databases and may not '
          'precisely reflect every brand, preparation method, or regional variation. '
          'Factors that can affect accuracy include:\n\n'
          '• Differences in food preparation and cooking methods\n'
          '• Regional and brand-specific product variations\n'
          '• Natural variation in whole foods\n\n'
          'You are solely responsible for verifying all food quantities and serving '
          'sizes before logging them. Do not rely on the App for allergy management, '
          'medical diets, or clinical nutrition needs.',
    ),
    LegalSection(
      '5. User Responsibility',
      'By using the App, you accept sole responsibility for:\n\n'
          '• All dietary choices and decisions made using App data\n'
          '• Managing your own calorie intake and nutritional goals\n'
          '• Verifying food identification and serving sizes\n'
          '• Awareness of your food allergies and intolerances\n'
          '• Consulting appropriate professionals for any medical conditions\n'
          '• All fitness and exercise decisions influenced by App insights\n\n'
          'Children and individuals with medical conditions should use the App only '
          'under the supervision of a qualified healthcare provider.',
    ),
    LegalSection(
      '6. Limitation of Liability',
      'To the maximum extent permitted by applicable law, the developer of '
          'Infinite Nutrition Tracker shall NOT be liable for:\n\n'
          '• Any health issues arising directly or indirectly from App use\n'
          '• Adverse dietary or allergic reactions\n'
          '• Inaccurate food identification from manual entry errors\n'
          '• Inaccurate nutritional calculations or estimates\n'
          '• Fitness or wellness outcomes\n'
          '• Indirect, incidental, or consequential damages of any kind\n'
          '• Loss or corruption of data stored on your device\n'
          '• Third-party API (USDA) outages or data inaccuracies\n\n'
          'Your continued use of the App constitutes full acceptance of this '
          'limitation of liability.',
    ),
    LegalSection(
      '7. Acceptance of Risk',
      'By using the App, you voluntarily acknowledge that:\n\n'
          '• Nutrition and calorie estimation is inherently imprecise\n'
          '• Personal health decisions remain entirely your own responsibility\n'
          '• The App is a wellness tool, not a substitute for professional care\n'
          '• You use the App freely and at your own risk\n\n'
          'Users under the applicable legal age in their jurisdiction should use '
          'the App under parental or guardian guidance.',
    ),
    LegalSection(
      '8. Governing Terms & Updates',
      'These Terms & Conditions may be updated when significant changes are made '
          'to the App\'s features or legal obligations. You will be notified and '
          'asked to re-accept updated Terms before continuing to use the App.\n\n'
          'Policy Version: 1.0.0\n'
          'Effective Date: May 2026',
    ),
  ];

  // ── PRIVACY NOTICE — ENGLISH ──────────────────────────────────────────────

  static const List<LegalSection> _privacyEn = [
    LegalSection(
      '1. Local Storage Only',
      'All personal data you enter into the App — including your profile, meals, '
          'nutrition logs, body measurements, and preferences — is stored exclusively '
          'on your device using local on-device storage (Hive).\n\n'
          'No personal data is transmitted to, or stored on, any external server, '
          'cloud service, or third-party platform. Your data never leaves your device.',
    ),
    LegalSection(
      '2. No Account Required',
      'The App does not require account creation, login credentials, or any '
          'form of online registration.\n\n'
          'During setup, you may optionally enter an email address. If provided, '
          'it is stored only on your device and is never transmitted to the '
          'developer or any third party. You can use every feature of the App '
          'without providing an email address.',
    ),
    LegalSection(
      '3. No Tracking or Analytics',
      'The App does NOT include:\n\n'
          '• Usage analytics or behavioral tracking SDKs\n'
          '• Advertising networks or ad SDKs\n'
          '• Behavioral profiling or audience segmentation\n'
          '• Third-party crash reporting or telemetry services\n'
          '• Social login integrations\n\n'
          'Your usage patterns, habits, and personal data are never collected, '
          'analyzed, or shared with the developer or any third party.',
    ),
    LegalSection(
      '4. USDA API Usage',
      'The App connects directly to the USDA FoodData Central API '
          '(api.nal.usda.gov) to retrieve food nutrition data. Regarding this:\n\n'
          '• Food search queries are sent directly from your device to USDA servers\n'
          '• Your personal profile, body data, and meal logs are NOT sent to USDA\n'
          '• The developer does not store or intercept your API key\n'
          '• USDA\'s own privacy policy governs data processed by their servers\n\n'
          'Search results are cached locally on your device to reduce repeat API calls.',
    ),
    LegalSection(
      '5. User Data Control',
      'You have full and unconditional control over your data at all times:\n\n'
          '• Reset All Data: Permanently delete all locally stored data\n'
          '• Clear Cache: Remove cached food search results\n'
          '• Profile: Update or remove your personal profile anytime\n'
          '• Export: Generate and save a local CSV or JSON backup file\n\n'
          'Exported files are saved locally on your device only. The developer '
          'has no access to these files.',
    ),
    LegalSection(
      '6. Data Security',
      'Since all data is stored locally on your device, the security of your '
          'data depends on your device\'s own security configuration (screen lock, '
          'biometric authentication, device encryption, etc.).\n\n'
          'The developer is not responsible for unauthorized access to your data '
          'resulting from device compromise, loss, or theft. We recommend keeping '
          'your device secured with a strong PIN or biometric lock.',
    ),
    LegalSection(
      '7. Child Safety',
      'The App is designed for general wellness use and is intended for users '
          'who are of the applicable legal age in their jurisdiction.\n\n'
          'Users under the applicable legal age should use the App under parental '
          'or guardian guidance. We do not knowingly collect or process personal '
          'data from children.',
    ),
    LegalSection(
      '8. Privacy Policy Updates',
      'This Privacy Notice may be updated to reflect changes in App features or '
          'applicable law. You will be notified and asked to re-acknowledge updated '
          'notices before continuing to use the App.\n\n'
          'Policy Version: 1.0.0\n'
          'Effective Date: May 2026',
    ),
  ];

  // ── HEALTH DISCLAIMER — ENGLISH ───────────────────────────────────────────

  static const List<LegalSection> _healthEn = [
    LegalSection(
      'General Health Disclaimer',
      'Infinite Nutrition Tracker provides general nutrition and wellness tracking '
          'tools. The information provided by the App is for general informational '
          'purposes only.\n\n'
          'It is NOT intended as:\n'
          '• Medical advice or clinical diagnosis\n'
          '• A substitute for professional healthcare consultation\n'
          '• A treatment plan for any disease or medical condition\n'
          '• Guidance for managing acute or chronic health conditions\n\n'
          'Do not make significant health or dietary decisions based solely on '
          'information provided by this App.',
    ),
    LegalSection(
      'Not for Emergency Use',
      'The App is NOT designed or intended for use in medical emergencies.\n\n'
          'If you are experiencing a health emergency, contact your local emergency '
          'services immediately (e.g., 999, 911, or your regional equivalent).\n\n'
          'Do not rely on the App for emergency nutrition guidance, medical '
          'instructions, or first aid information.',
    ),
    LegalSection(
      'Consult Healthcare Professionals',
      'Always consult a qualified healthcare professional before:\n\n'
          '• Starting a new diet or significantly changing eating habits\n'
          '• Beginning a new exercise or fitness program\n'
          '• Using nutrition data to manage a medical condition\n'
          '• Adjusting medications or supplements based on App data\n'
          '• Making dietary decisions if you have diabetes, cardiovascular disease, '
          'kidney disease, eating disorders, or any other diet-sensitive condition\n\n'
          'The App does not account for individual medical histories, '
          'contraindications, or prescribed treatment plans.',
    ),
    LegalSection(
      'No Guaranteed Health Outcomes',
      'The App makes no claims, promises, or guarantees regarding:\n\n'
          '• Weight loss or weight management results\n'
          '• Fat loss or muscle gain outcomes\n'
          '• Improvement in any health condition or biomarker\n'
          '• Achievement of any specific fitness goal\n'
          '• Increased energy, metabolism, or physical performance\n\n'
          'Individual results will vary significantly based on personal physiology, '
          'lifestyle, adherence, and many other factors outside App control.',
    ),
    LegalSection(
      'Manual Entry Accuracy',
      'The App relies on manual food logging. Nutritional data accuracy depends on:\n\n'
          '• Correct food selection from the database\n'
          '• Accurate portion size estimation by the user\n'
          '• Database coverage for specific regional or branded foods\n\n'
          'Always cross-check nutrition data with food labels for health-critical '
          'decisions. Never rely solely on App data for allergy management, medical '
          'diets, or clinical nutrition requirements.',
    ),
    LegalSection(
      'Export & Data Responsibility',
      'Users who export their data (CSV, JSON backup files) accept the following:\n\n'
          '• Exported files are stored locally on your device\n'
          '• You are responsible for keeping exported files secure\n'
          '• You are responsible for managing your own backups\n'
          '• You are responsible for preventing unauthorized access to exported files\n\n'
          'The developer is not responsible for lost, deleted, or corrupted exported '
          'files, nor for any failures of your device\'s local storage.',
    ),
  ];

  // ── TERMS & CONDITIONS — BENGALI ──────────────────────────────────────────

  static const List<LegalSection> _termsBn = [
    LegalSection(
      '১. সাধারণ ব্যবহার',
      'ইনফিনিট নিউট্রিশন ট্র্যাকার ("অ্যাপ") "যেমন আছে" (as is) ভিত্তিতে শুধুমাত্র '
          'তথ্যগত ও ব্যক্তিগত সুস্বাস্থ্যের উদ্দেশ্যে প্রদান করা হয়েছে। অ্যাপটি '
          'ব্যবহার করে আপনি স্বীকার করছেন যে আপনি নিজের বিবেচনায় ও ঝুঁকিতে এটি ব্যবহার করছেন।\n\n'
          'অ্যাপটি পুষ্টি ও সুস্বাস্থ্য অভ্যাস ট্র্যাক করতে সহায়তার জন্য ডিজাইন করা হয়েছে — '
          'পেশাদার স্বাস্থ্যসেবার বিকল্প হিসেবে নয়।',
    ),
    LegalSection(
      '২. কোনো চিকিৎসা পরামর্শ নয়',
      'অ্যাপটি কোনো চিকিৎসা অ্যাপ্লিকেশন নয়। এটি প্রদান করে না:\n\n'
          '• চিকিৎসা পরামর্শ, রোগ নির্ণয় বা ক্লিনিক্যাল মূল্যায়ন\n'
          '• কোনো রোগের চিকিৎসা পরিকল্পনা\n'
          '• ওষুধ বা থেরাপি পরিবর্তনের সুপারিশ\n'
          '• ডাক্তার বা ডায়েটিশিয়ানের পরামর্শের বিকল্প\n\n'
          'খাদ্য ও পুষ্টি সংক্রান্ত বড় পরিবর্তনের আগে সর্বদা একজন যোগ্য '
          'চিকিৎসক, পুষ্টিবিদ বা স্বাস্থ্যসেবা পেশাদারের পরামর্শ নিন।',
    ),
    LegalSection(
      '৩. পুষ্টি তথ্য দাবিত্যাগ',
      'পুষ্টি তথ্য তৃতীয়-পক্ষের ডেটাবেস (USDA FoodData Central) থেকে নেওয়া। '
          'নিম্নলিখিত কারণে পুষ্টিমান ভিন্ন হতে পারে:\n\n'
          '• রান্নার পদ্ধতির পার্থক্য\n'
          '• অঞ্চল ও ব্র্যান্ডভেদে পণ্যের পার্থক্য\n'
          '• ডেটাবেসের অনির্ভুলতা বা আপডেট\n'
          '• প্রাকৃতিক খাদ্যে স্বাভাবিক পরিবর্তন\n\n'
          'চিকিৎসাগত পুষ্টি ব্যবস্থাপনা বা স্বাস্থ্য-সংকটজনক খাদ্য সিদ্ধান্তের '
          'জন্য শুধুমাত্র এই অ্যাপের উপর নির্ভর করবেন না।',
    ),
    LegalSection(
      '৪. তথ্যের নির্ভুলতা সম্পর্কিত দাবিত্যাগ',
      'অ্যাপের পুষ্টি তথ্য নির্বাচিত ডেটাবেস থেকে নেওয়া এবং প্রতিটি ব্র্যান্ড, '
          'রান্নার পদ্ধতি বা আঞ্চলিক বিভিন্নতা সঠিকভাবে প্রতিফলিত নাও হতে পারে। '
          'নির্ভুলতাকে প্রভাবিত করতে পারে এমন বিষয়সমূহ:\n\n'
          '• রান্নার পদ্ধতির পার্থক্য\n'
          '• অঞ্চল ও ব্র্যান্ডভেদে পণ্যের পার্থক্য\n'
          '• প্রাকৃতিক খাদ্যে স্বাভাবিক পরিবর্তন\n\n'
          'লগ করার আগে সমস্ত খাদ্যের পরিমাণ ও সার্ভিং সাইজ নিজে যাচাই করার '
          'দায়িত্ব সম্পূর্ণরূপে আপনার। অ্যালার্জি ব্যবস্থাপনা, চিকিৎসাগত ডায়েট '
          'বা ক্লিনিক্যাল পুষ্টির প্রয়োজনে শুধুমাত্র অ্যাপের উপর নির্ভর করবেন না।',
    ),
    LegalSection(
      '৫. ব্যবহারকারীর দায়িত্ব',
      'অ্যাপ ব্যবহার করে আপনি সম্পূর্ণ দায়িত্ব গ্রহণ করছেন:\n\n'
          '• অ্যাপ তথ্য ব্যবহার করে নেওয়া সমস্ত খাদ্য সিদ্ধান্তের\n'
          '• নিজের ক্যালোরি গ্রহণ ও পুষ্টি লক্ষ্য ব্যবস্থাপনার\n'
          '• খাবার শনাক্তকরণ ও সার্ভিং সাইজ যাচাই করার\n'
          '• নিজের খাদ্য অ্যালার্জি ও অসহিষ্ণুতা সম্পর্কে সচেতন থাকার\n'
          '• যেকোনো স্বাস্থ্য সমস্যার জন্য উপযুক্ত পেশাদারের পরামর্শ নেওয়ার\n\n'
          'শিশু এবং স্বাস্থ্যগত সমস্যায় থাকা ব্যক্তিরা শুধুমাত্র যোগ্য '
          'স্বাস্থ্যসেবা প্রদানকারীর তত্ত্বাবধানে অ্যাপটি ব্যবহার করবেন।',
    ),
    LegalSection(
      '৬. দায়বদ্ধতার সীমাবদ্ধতা',
      'প্রযোজ্য আইনের সর্বোচ্চ সীমার মধ্যে, ইনফিনিট নিউট্রিশন ট্র্যাকারের '
          'নির্মাতা দায়ী থাকবেন না:\n\n'
          '• অ্যাপ ব্যবহারের ফলে সৃষ্ট যেকোনো স্বাস্থ্যগত সমস্যার জন্য\n'
          '• খাদ্যাভ্যাসগত বা অ্যালার্জিক প্রতিক্রিয়ার জন্য\n'
          '• ম্যানুয়াল এন্ট্রিতে ভুল খাবার শনাক্তকরণের জন্য\n'
          '• অনির্ভুল পুষ্টি গণনার জন্য\n'
          '• পরোক্ষ বা আনুষঙ্গিক ক্ষতির জন্য\n'
          '• ডিভাইসে সংরক্ষিত ডেটা হারানোর জন্য\n\n'
          'অ্যাপের ক্রমাগত ব্যবহার এই দায়বদ্ধতার সীমাবদ্ধতার সম্পূর্ণ '
          'স্বীকৃতি হিসেবে গণ্য হবে।',
    ),
    LegalSection(
      '৭. ঝুঁকির স্বীকৃতি',
      'অ্যাপ ব্যবহার করে আপনি স্বেচ্ছায় স্বীকার করছেন যে:\n\n'
          '• পুষ্টি ও ক্যালোরি অনুমান স্বাভাবিকভাবেই অনির্ভুল হতে পারে\n'
          '• ব্যক্তিগত স্বাস্থ্য সিদ্ধান্ত সম্পূর্ণরূপে আপনার নিজের দায়িত্ব\n'
          '• অ্যাপটি একটি সুস্বাস্থ্য সহায়ক — পেশাদার সেবার বিকল্প নয়\n'
          '• আপনি স্বাধীনভাবে ও ব্যক্তিগত ঝুঁকিতে অ্যাপটি ব্যবহার করছেন',
    ),
    LegalSection(
      '৮. শর্তাবলী আপডেট',
      'অ্যাপের ফিচার বা আইনি বাধ্যবাধকতায় উল্লেখযোগ্য পরিবর্তন হলে এই '
          'শর্তাবলী আপডেট করা হতে পারে। আপডেট হলে আপনাকে নতুন শর্তাবলী '
          'পর্যালোচনা ও সম্মত হওয়ার জন্য অনুরোধ করা হবে।\n\n'
          'নীতি সংস্করণ: 1.0.0\n'
          'কার্যকর তারিখ: মে ২০২৬',
    ),
  ];

  // ── PRIVACY NOTICE — BENGALI ──────────────────────────────────────────────

  static const List<LegalSection> _privacyBn = [
    LegalSection(
      '১. শুধুমাত্র স্থানীয় স্টোরেজ',
      'আপনার প্রবেশ করা সমস্ত ব্যক্তিগত তথ্য — প্রোফাইল, খাবারের তালিকা, '
          'পুষ্টি লগ, শারীরিক পরিমাপ এবং পছন্দ — সম্পূর্ণরূপে আপনার ডিভাইসে '
          'স্থানীয় স্টোরেজে (Hive) সংরক্ষিত হয়।\n\n'
          'কোনো ব্যক্তিগত তথ্য কোনো বাহ্যিক সার্ভার, ক্লাউড পরিষেবা বা '
          'তৃতীয়-পক্ষের প্ল্যাটফর্মে পাঠানো হয় না। আপনার ডেটা কখনই আপনার '
          'ডিভাইস ছেড়ে যায় না।',
    ),
    LegalSection(
      '২. কোনো অ্যাকাউন্টের প্রয়োজন নেই',
      'অ্যাপটি ব্যবহার করতে কোনো অ্যাকাউন্ট তৈরি, ইমেইল ঠিকানা, ফোন নম্বর '
          'বা কোনো লগইন তথ্যের প্রয়োজন নেই।\n\n'
          'আপনি নিজেকে নির্মাতা বা যেকোনো তৃতীয় পক্ষের কাছে পরিচয় না দিয়েই '
          'অ্যাপের সমস্ত ফিচার ব্যবহার করতে পারবেন।',
    ),
    LegalSection(
      '৩. কোনো ট্র্যাকিং বা অ্যানালিটিক্স নেই',
      'অ্যাপটিতে অন্তর্ভুক্ত নেই:\n\n'
          '• ব্যবহার বিশ্লেষণ বা আচরণ ট্র্যাকিং SDK\n'
          '• বিজ্ঞাপন নেটওয়ার্ক বা বিজ্ঞাপন SDK\n'
          '• আচরণগত প্রোফাইলিং বা দর্শক বিভাজন\n'
          '• তৃতীয়-পক্ষের ক্র্যাশ রিপোর্টিং বা টেলিমেট্রি\n'
          '• সোশ্যাল লগইন ইন্টিগ্রেশন\n\n'
          'আপনার ব্যবহারের ধরন, অভ্যাস এবং ব্যক্তিগত তথ্য কখনই সংগ্রহ, '
          'বিশ্লেষণ বা নির্মাতা বা যেকোনো তৃতীয় পক্ষের সাথে শেয়ার করা হয় না।',
    ),
    LegalSection(
      '৪. USDA API ব্যবহার',
      'খাদ্য পুষ্টির তথ্য পুনরুদ্ধারের জন্য অ্যাপটি সরাসরি USDA FoodData '
          'Central API (api.nal.usda.gov) ব্যবহার করে:\n\n'
          '• খাদ্য অনুসন্ধান প্রশ্ন সরাসরি আপনার ডিভাইস থেকে USDA সার্ভারে যায়\n'
          '• আপনার ব্যক্তিগত প্রোফাইল, শারীরিক তথ্য ও খাবারের লগ USDA-তে পাঠানো হয় না\n'
          '• নির্মাতা আপনার API কী সংরক্ষণ বা আটকায় না\n'
          '• USDA-র নিজস্ব গোপনীয়তা নীতি তাদের সার্ভারে প্রক্রিয়াকৃত ডেটার ক্ষেত্রে প্রযোজ্য\n\n'
          'বারবার API কল কমাতে অনুসন্ধান ফলাফল স্থানীয়ভাবে আপনার ডিভাইসে '
          'ক্যাশ করা হয়।',
    ),
    LegalSection(
      '৫. ডেটার নিয়ন্ত্রণ',
      'আপনার কাছে সবসময় আপনার তথ্যের সম্পূর্ণ নিয়ন্ত্রণ রয়েছে:\n\n'
          '• সব ডেটা রিসেট: স্থানীয়ভাবে সংরক্ষিত সমস্ত ডেটা স্থায়ীভাবে মুছুন\n'
          '• ক্যাশ পরিষ্কার: ক্যাশ করা খাদ্য অনুসন্ধান ফলাফল মুছুন\n'
          '• প্রোফাইল: যেকোনো সময় আপনার ব্যক্তিগত প্রোফাইল আপডেট বা মুছুন\n'
          '• ডেটা রপ্তানি: স্থানীয় CSV বা JSON ব্যাকআপ ফাইল তৈরি করুন\n\n'
          'রপ্তানিকৃত ফাইল শুধুমাত্র আপনার ডিভাইসে সংরক্ষিত হয়। নির্মাতার '
          'এই ফাইলে কোনো অ্যাক্সেস নেই।',
    ),
    LegalSection(
      '৬. ডেটা সুরক্ষা',
      'সমস্ত ডেটা স্থানীয়ভাবে আপনার ডিভাইসে সংরক্ষিত হওয়ায়, আপনার তথ্যের '
          'নিরাপত্তা নির্ভর করে আপনার ডিভাইসের নিজস্ব নিরাপত্তা কনফিগারেশনের '
          'উপর (স্ক্রিন লক, বায়োমেট্রিক, ডিভাইস এনক্রিপশন ইত্যাদি)।\n\n'
          'ডিভাইস হারানো, চুরি বা হ্যাকের ফলে অননুমোদিত তথ্য অ্যাক্সেসের জন্য '
          'নির্মাতা দায়ী নন। আমরা একটি শক্তিশালী PIN বা বায়োমেট্রিক লক দিয়ে '
          'ডিভাইস সুরক্ষিত রাখার পরামর্শ দিই।',
    ),
    LegalSection(
      '৭. শিশু সুরক্ষা',
      'অ্যাপটি সাধারণ সুস্বাস্থ্য ব্যবহারের জন্য ডিজাইন করা হয়েছে এবং '
          'ব্যবহারকারীর আইনগত বয়সের সীমার মধ্যে থাকা ব্যক্তিদের জন্য।\n\n'
          'আইনগত বয়সসীমার নিচে থাকা ব্যবহারকারীরা অভিভাবকের তত্ত্বাবধানে '
          'অ্যাপটি ব্যবহার করবেন। আমরা জেনেশুনে শিশুদের থেকে ব্যক্তিগত তথ্য '
          'সংগ্রহ বা প্রক্রিয়া করি না।',
    ),
    LegalSection(
      '৮. গোপনীয়তা নীতি আপডেট',
      'অ্যাপের ফিচার বা প্রযোজ্য আইনে পরিবর্তনের ক্ষেত্রে এই গোপনীয়তা '
          'বিজ্ঞপ্তি আপডেট করা হতে পারে। আপডেট হলে আপনাকে নতুন বিজ্ঞপ্তি '
          'পর্যালোচনা ও স্বীকৃতি দিতে বলা হবে।\n\n'
          'নীতি সংস্করণ: 1.0.0\n'
          'কার্যকর তারিখ: মে ২০২৬',
    ),
  ];

  // ── HEALTH DISCLAIMER — BENGALI ───────────────────────────────────────────

  static const List<LegalSection> _healthBn = [
    LegalSection(
      'সাধারণ স্বাস্থ্য দাবিত্যাগ',
      'ইনফিনিট নিউট্রিশন ট্র্যাকার সাধারণ পুষ্টি ও সুস্বাস্থ্য ট্র্যাকিং সরঞ্জাম প্রদান করে। '
          'অ্যাপের তথ্য শুধুমাত্র সাধারণ তথ্যের উদ্দেশ্যে।\n\n'
          'এটি নিম্নলিখিত হিসেবে প্রদান করা হয় না:\n'
          '• চিকিৎসা পরামর্শ বা ক্লিনিক্যাল রোগ নির্ণয়\n'
          '• পেশাদার স্বাস্থ্যসেবার বিকল্প\n'
          '• কোনো রোগ বা চিকিৎসা অবস্থার চিকিৎসা পরিকল্পনা\n\n'
          'শুধুমাত্র এই অ্যাপের তথ্যের উপর নির্ভর করে উল্লেখযোগ্য স্বাস্থ্যগত '
          'বা খাদ্যাভ্যাসের সিদ্ধান্ত নেবেন না।',
    ),
    LegalSection(
      'জরুরি ব্যবহারের জন্য নয়',
      'অ্যাপটি চিকিৎসা জরুরি পরিস্থিতিতে ব্যবহারের জন্য নয়।\n\n'
          'স্বাস্থ্য জরুরি অবস্থায় অবিলম্বে স্থানীয় জরুরি সেবায় যোগাযোগ করুন '
          '(যেমন ৯৯৯, ৯৯১, বা আপনার অঞ্চলের সংশ্লিষ্ট নম্বর)।\n\n'
          'জরুরি পুষ্টি নির্দেশনা, চিকিৎসা নির্দেশনা বা প্রাথমিক চিকিৎসার '
          'জন্য অ্যাপের উপর নির্ভর করবেন না।',
    ),
    LegalSection(
      'স্বাস্থ্যসেবা পেশাদারের পরামর্শ',
      'নিম্নলিখিত ক্ষেত্রে সর্বদা একজন যোগ্য স্বাস্থ্যসেবা পেশাদারের পরামর্শ নিন:\n\n'
          '• নতুন ডায়েট শুরু বা খাদ্যাভ্যাসে উল্লেখযোগ্য পরিবর্তন\n'
          '• নতুন ব্যায়াম বা ফিটনেস প্রোগ্রাম শুরু\n'
          '• কোনো চিকিৎসা অবস্থা ব্যবস্থাপনায় পুষ্টি তথ্য ব্যবহার\n'
          '• অ্যাপ তথ্যের ভিত্তিতে ওষুধ বা সাপ্লিমেন্ট পরিবর্তন\n'
          '• ডায়াবেটিস, হৃদরোগ, কিডনি রোগ, খাওয়ার ব্যাধি বা অন্যান্য '
          'ডায়েট-সংবেদনশীল অবস্থায় খাদ্য সিদ্ধান্ত নেওয়া',
    ),
    LegalSection(
      'কোনো নিশ্চিত স্বাস্থ্যগত ফলাফল নেই',
      'অ্যাপটি কোনো দাবি, প্রতিশ্রুতি বা গ্যারান্টি দেয় না:\n\n'
          '• ওজন হ্রাস বা ওজন ব্যবস্থাপনার ফলাফল\n'
          '• চর্বি হ্রাস বা পেশী বৃদ্ধির ফলাফল\n'
          '• কোনো স্বাস্থ্যগত অবস্থা বা বায়োমার্কারের উন্নতি\n'
          '• যেকোনো নির্দিষ্ট ফিটনেস লক্ষ্য অর্জন\n\n'
          'ব্যক্তিগত শরীরবিদ্যা, জীবনধারা এবং অন্যান্য অনেক কারণের উপর '
          'নির্ভর করে ব্যক্তিগত ফলাফল উল্লেখযোগ্যভাবে ভিন্ন হতে পারে।',
    ),
    LegalSection(
      'ম্যানুয়াল এন্ট্রির যথার্থতা',
      'অ্যাপটি ম্যানুয়াল খাদ্য লগিংয়ের উপর নির্ভর করে। পুষ্টি তথ্যের নির্ভুলতা নির্ভর করে:\n\n'
          '• ডেটাবেস থেকে সঠিক খাবার নির্বাচনের উপর\n'
          '• ব্যবহারকারীর সঠিক পরিমাণ অনুমানের উপর\n'
          '• নির্দিষ্ট আঞ্চলিক বা ব্র্যান্ডেড খাবারের ডেটাবেস কভারেজের উপর\n\n'
          'স্বাস্থ্য-সংকটজনক সিদ্ধান্তের জন্য সর্বদা খাদ্য লেবেলের সাথে পুষ্টি তথ্য '
          'যাচাই করুন। অ্যালার্জি ব্যবস্থাপনা, চিকিৎসাগত ডায়েট বা ক্লিনিক্যাল পুষ্টির '
          'প্রয়োজনে শুধুমাত্র অ্যাপের তথ্যের উপর নির্ভর করবেন না।',
    ),
    LegalSection(
      'রপ্তানি ও ডেটার দায়িত্ব',
      'ডেটা রপ্তানি করা ব্যবহারকারীরা (CSV, JSON ব্যাকআপ ফাইল) নিম্নলিখিত গ্রহণ করেন:\n\n'
          '• রপ্তানিকৃত ফাইল আপনার ডিভাইসে স্থানীয়ভাবে সংরক্ষিত হয়\n'
          '• ফাইল সুরক্ষিত রাখার দায়িত্ব আপনার\n'
          '• নিজের ব্যাকআপ ব্যবস্থাপনার দায়িত্ব আপনার\n'
          '• রপ্তানিকৃত ফাইলে অননুমোদিত অ্যাক্সেস রোধ করার দায়িত্ব আপনার\n\n'
          'হারিয়ে যাওয়া, মুছে ফেলা বা নষ্ট হয়ে যাওয়া রপ্তানিকৃত ফাইল '
          'বা ডিভাইসের স্থানীয় স্টোরেজ ব্যর্থতার জন্য নির্মাতা দায়ী নন।',
    ),
  ];
}
