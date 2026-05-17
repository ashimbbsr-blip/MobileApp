import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'storage/hive_storage.dart';
import 'services/analytics_service.dart';
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

  // Background cleanup: compress meal entries older than 90 days.
  // Runs after the first frame so it never delays startup.
  WidgetsBinding.instance.addPostFrameCallback((_) {
    AnalyticsService.runCleanup(retainDays: 90);
  });

  runApp(
    const ProviderScope(
      child: InfinityHealthApp(),
    ),
  );
}
