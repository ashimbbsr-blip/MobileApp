import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'storage/hive_storage.dart';
import 'services/analytics_service.dart';
import 'services/local_food_repository.dart';
import 'services/local_search_service.dart';
import 'app.dart';

void main() async {
  // Catch Flutter framework errors (widget build, layout, etc.) — prevents white-screen crash.
  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    debugPrint('[FlutterError] ${details.exceptionAsString()}');
  };

  // Catch async errors that escape the widget tree (Dart isolate top-level).
  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('[PlatformError] $error\n$stack');
    return true; // mark handled — prevents OS from killing the process
  };

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
  // Load search index in parallel with the rest of startup; search falls back
  // to full-scan until this completes (typically < 100ms after food data loads).
  LocalSearchService.ensureLoaded().ignore();

  WidgetsBinding.instance.addPostFrameCallback((_) {
    try {
      AnalyticsService.runCleanup(retainDays: 90);
    } catch (_) {}
  });

  runApp(
    const ProviderScope(
      child: InfinityHealthApp(),
    ),
  );
}