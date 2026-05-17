import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../storage/hive_storage.dart';

class SettingsState {
  final ThemeMode themeMode;
  final String language;

  const SettingsState({required this.themeMode, required this.language});

  SettingsState copyWith({ThemeMode? themeMode, String? language}) {
    return SettingsState(
      themeMode: themeMode ?? this.themeMode,
      language: language ?? this.language,
    );
  }
}

class SettingsNotifier extends StateNotifier<SettingsState> {
  SettingsNotifier() : super(_loadInitial());

  static SettingsState _loadInitial() {
    final themeModeStr = HiveStorage.themeMode;
    final themeMode = themeModeStr == 'light'
        ? ThemeMode.light
        : themeModeStr == 'dark'
            ? ThemeMode.dark
            : ThemeMode.system;
    return SettingsState(
      themeMode: themeMode,
      language: HiveStorage.language,
    );
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    final modeStr = mode == ThemeMode.light ? 'light' : mode == ThemeMode.dark ? 'dark' : 'system';
    await HiveStorage.saveThemeMode(modeStr);
    state = state.copyWith(themeMode: mode);
  }

  Future<void> setLanguage(String lang) async {
    await HiveStorage.saveLanguage(lang);
    state = state.copyWith(language: lang);
  }
}

final settingsProvider = StateNotifierProvider<SettingsNotifier, SettingsState>(
  (ref) => SettingsNotifier(),
);
