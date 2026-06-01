import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'storage/hive_storage.dart';
import 'services/analytics_service.dart';
import 'services/local_food_repository.dart';
import 'services/notification_service.dart';
import 'app.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
  ));

  await HiveStorage.init();
  await LocalFoodRepository.init();

  // Initialize notifications and ensure daily reminder is scheduled.
  await NotificationService.instance.init();
  if (HiveStorage.isOnboardingDone) {
    await NotificationService.instance.ensureScheduled();
  }

  WidgetsBinding.instance.addPostFrameCallback((_) {
    AnalyticsService.runCleanup(retainDays: 90);
  });

  runApp(
    const ProviderScope(
      child: InfinityHealthApp(),
    ),
  );
}claude