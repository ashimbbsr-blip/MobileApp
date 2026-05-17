import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app_localizations.dart';
import '../features/settings/providers/settings_provider.dart';

final appStringsProvider = Provider<AppStrings>((ref) {
  return AppStrings(ref.watch(settingsProvider).language);
});
