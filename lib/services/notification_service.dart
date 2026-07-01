import 'dart:io';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/data/latest_all.dart' as tz_data;
import 'package:timezone/timezone.dart' as tz;
import '../storage/hive_storage.dart';

const int _kReminderId = 1001;
const String _kChannelId = 'infinite_meal_reminders';
const String _kChannelName = 'Meal Reminders';
const String _kChannelDesc = 'Daily reminders to log breakfast and dinner';

class NotificationService {
  NotificationService._();
  static final NotificationService instance = NotificationService._();

  final FlutterLocalNotificationsPlugin _plugin =
      FlutterLocalNotificationsPlugin();
  bool _initialized = false;

  // ── Init ─────────────────────────────────────────────────────────────────

  Future<void> init() async {
    if (_initialized) return;
    tz_data.initializeTimeZones();
    // Epoch values from DateTime.now() are already device-local, so UTC label
    // preserves the correct wall-clock time for matchDateTimeComponents.
    tz.setLocalLocation(tz.UTC);

    const androidInit = AndroidInitializationSettings('@mipmap/ic_launcher');
    await _plugin.initialize(
      const InitializationSettings(android: androidInit),
      onDidReceiveNotificationResponse: (_) {
        // Notification tapped — nothing to do; app opens via launcher intent.
      },
    );
    _initialized = true;
  }

  // ── Permission ────────────────────────────────────────────────────────────

  Future<bool> requestPermissions() async {
    if (!Platform.isAndroid) return true;
    final androidPlugin = _plugin
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>();
    if (androidPlugin == null) return false;
    return await androidPlugin.requestNotificationsPermission() ?? false;
  }

  Future<bool> requestExactAlarmPermission() async {
    if (!Platform.isAndroid) return true;
    final androidPlugin = _plugin
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>();
    if (androidPlugin == null) return false;
    return await androidPlugin.requestExactAlarmsPermission() ?? false;
  }

  // ── Schedule / Cancel ─────────────────────────────────────────────────────

  Future<bool> scheduleReminder({
    required int hour,
    required int minute,
    required String language,
  }) async {
    try {
      await _plugin.cancel(_kReminderId);
      final scheduled = _nextOccurrence(hour, minute);
      final details = _buildDetails(language);
      final mode = await _exactMode();
      await _plugin.zonedSchedule(
        _kReminderId,
        details.$1,
        details.$2,
        scheduled,
        _notificationDetails,
        androidScheduleMode: mode,
        uiLocalNotificationDateInterpretation:
            UILocalNotificationDateInterpretation.absoluteTime,
        matchDateTimeComponents: DateTimeComponents.time,
      );
      return true;
    } catch (_) {
      return false;
    }
  }

  // Returns exactAllowWhileIdle when permission is available, otherwise falls
  // back to inexact (still fires daily, just may be delayed a few minutes).
  Future<AndroidScheduleMode> _exactMode() async {
    if (!Platform.isAndroid) return AndroidScheduleMode.exactAllowWhileIdle;
    final ap = _plugin.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>();
    final canExact = await ap?.canScheduleExactNotifications() ?? false;
    return canExact
        ? AndroidScheduleMode.exactAllowWhileIdle
        : AndroidScheduleMode.inexactAllowWhileIdle;
  }

  Future<void> cancelReminder() async {
    await _plugin.cancel(_kReminderId);
  }

  // Reschedule for tomorrow (called when both breakfast + dinner are logged).
  Future<void> rescheduleForTomorrow() async {
    if (!HiveStorage.notificationEnabled) return;
    try {
      await _plugin.cancel(_kReminderId);

      final hour = HiveStorage.notificationHour;
      final minute = HiveStorage.notificationMinute;
      final lang = HiveStorage.language;

      final now = DateTime.now();
      final tomorrow = DateTime(now.year, now.month, now.day + 1, hour, minute);
      final scheduled = tz.TZDateTime.from(tomorrow, tz.UTC);
      final details = _buildDetails(lang);
      final mode = await _exactMode();

      await _plugin.zonedSchedule(
        _kReminderId,
        details.$1,
        details.$2,
        scheduled,
        _notificationDetails,
        androidScheduleMode: mode,
        uiLocalNotificationDateInterpretation:
            UILocalNotificationDateInterpretation.absoluteTime,
        matchDateTimeComponents: DateTimeComponents.time,
      );
    } catch (_) {
      // Best-effort reschedule — silently swallow
    }
  }

  // ── Smart check ───────────────────────────────────────────────────────────

  // Call after any meal is logged for today.
  Future<void> checkMealsAndMaybeReschedule(String dateKey) async {
    if (!HiveStorage.notificationEnabled) return;
    final meals = HiveStorage.getMealsForDate(dateKey);
    final hasBreakfast = meals.any((m) => m.mealType == 'breakfast');
    final hasDinner = meals.any((m) => m.mealType == 'dinner');
    if (hasBreakfast && hasDinner) {
      await rescheduleForTomorrow();
    }
  }

  // Call on app start — ensures the daily reminder is active if enabled.
  Future<void> ensureScheduled() async {
    if (!HiveStorage.notificationEnabled) {
      await cancelReminder();
      return;
    }
    await scheduleReminder(
      hour: HiveStorage.notificationHour,
      minute: HiveStorage.notificationMinute,
      language: HiveStorage.language,
    );
    // Ignore return value — best-effort on startup
  }

  // ── Helpers ───────────────────────────────────────────────────────────────

  tz.TZDateTime _nextOccurrence(int hour, int minute) {
    final now = DateTime.now();
    var local = DateTime(now.year, now.month, now.day, hour, minute);
    if (local.isBefore(now)) {
      local = local.add(const Duration(days: 1));
    }
    // tz.TZDateTime.from preserves the epoch value from the local DateTime,
    // so the notification fires at the correct device-local wall clock time.
    return tz.TZDateTime.from(local, tz.UTC);
  }

  (String, String) _buildDetails(String lang) {
    final bn = lang == 'bn';
    return (
      bn ? '🍽️ খাবারের রিমাইন্ডার' : '🍽️ Meal Reminder',
      bn
          ? 'আজকের নাস্তা ও রাতের খাবার লগ করতে ভুলবেন না!'
          : "Don't forget to log your breakfast and dinner today!",
    );
  }

  static const NotificationDetails _notificationDetails = NotificationDetails(
    android: AndroidNotificationDetails(
      _kChannelId,
      _kChannelName,
      channelDescription: _kChannelDesc,
      importance: Importance.high,
      priority: Priority.high,
      icon: '@mipmap/ic_launcher',
    ),
  );

  // ── Time display helpers ──────────────────────────────────────────────────

  static String formatTime(int hour, int minute) {
    final h = hour > 12
        ? hour - 12
        : hour == 0
            ? 12
            : hour;
    final m = minute.toString().padLeft(2, '0');
    final period = hour >= 12 ? 'PM' : 'AM';
    return '$h:$m $period';
  }
}
