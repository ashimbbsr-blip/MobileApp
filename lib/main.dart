import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'storage/hive_storage.dart';
import 'services/analytics_service.dart';
import 'services/local_food_repository.dart';
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

  // Load the bilingual food dataset into memory before the first frame so
  // every search returns results instantly with no race condition.
  await LocalFoodRepository.init();

  // Post-frame: background tasks that must not delay first render.
  WidgetsBinding.instance.addPostFrameCallback((_) {
    AnalyticsService.runCleanup(retainDays: 90);
  });

  runApp(
    const ProviderScope(
      child: InfinityHealthApp(),
    ),
  );
}