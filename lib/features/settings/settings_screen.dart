import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../localization/app_localizations.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../storage/hive_storage.dart';
import '../../services/export_service.dart';
import '../../services/notification_service.dart';
import '../../widgets/common/app_logo.dart';
import '../settings/providers/settings_provider.dart';
import '../profile/providers/profile_provider.dart';
import '../legal/legal_content.dart';
import '../legal/legal_content_screen.dart';
import '../../core/constants/app_constants.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(settingsProvider);
    final l10n = ref.watch(appStringsProvider);
    final profileState = ref.watch(profileProvider);
    final profile = profileState.profile;
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.settings)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // ── Profile Card ──────────────────────────────────────────────────
          Card(
            child: InkWell(
              borderRadius: BorderRadius.circular(12),
              onTap: () => context.push('/profile').then((_) {
                ref.read(profileProvider.notifier).refresh();
              }),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    _ProfileAvatar(imagePath: profile?.profileImagePath),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            profile?.displayName ?? 'User',
                            style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700),
                          ),
                          const SizedBox(height: 2),
                          if (profile != null)
                            Text(
                              '${profile.weightKg.toStringAsFixed(0)} kg · '
                              '${profile.heightCm.toStringAsFixed(0)} cm · '
                              '${profile.computedAge} yrs',
                              style: theme.textTheme.bodySmall,
                            ),
                          if (profile != null)
                            Text(
                              'BMI: ${profile.bmi.toStringAsFixed(1)} (${profile.bmiCategory})',
                              style: theme.textTheme.bodySmall
                                  ?.copyWith(color: AppColors.primary),
                            ),
                        ],
                      ),
                    ),
                    const Icon(Icons.chevron_right, size: 20, color: Colors.grey),
                  ],
                ),
              ),
            ),
          ),

          const SizedBox(height: 16),

          // ── Appearance ────────────────────────────────────────────────────
          Card(
            child: Column(
              children: [
                _SettingsTile(
                  icon: Icons.palette_outlined,
                  title: l10n.theme,
                  trailing: DropdownButton<ThemeMode>(
                    value: settings.themeMode,
                    underline: const SizedBox(),
                    items: [
                      DropdownMenuItem(value: ThemeMode.system, child: Text(l10n.systemDefault)),
                      DropdownMenuItem(value: ThemeMode.light, child: Text(l10n.lightMode)),
                      DropdownMenuItem(value: ThemeMode.dark, child: Text(l10n.darkMode)),
                    ],
                    onChanged: (mode) {
                      if (mode != null) ref.read(settingsProvider.notifier).setThemeMode(mode);
                    },
                  ),
                ),
                const Divider(height: 1),
                _SettingsTile(
                  icon: Icons.language,
                  title: l10n.languageLabel,
                  trailing: DropdownButton<String>(
                    value: settings.language,
                    underline: const SizedBox(),
                    items: [
                      DropdownMenuItem(value: 'en', child: Text(l10n.english)),
                      DropdownMenuItem(value: 'bn', child: Text(l10n.bengali)),
                    ],
                    onChanged: (lang) {
                      if (lang != null) ref.read(settingsProvider.notifier).setLanguage(lang);
                    },
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // ── Data Export ───────────────────────────────────────────────────
          Card(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
                  child: Text(l10n.dataExport,
                      style: theme.textTheme.bodySmall?.copyWith(
                          color: AppColors.primary, fontWeight: FontWeight.w700)),
                ),
                _SettingsTile(
                  icon: Icons.table_chart_outlined,
                  title: l10n.exportCsv,
                  onTap: () => _export(context, ref, l10n, csv: true),
                ),
                const Divider(height: 1),
                _SettingsTile(
                  icon: Icons.backup_outlined,
                  title: l10n.exportJson,
                  onTap: () => _export(context, ref, l10n, csv: false),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // ── Notifications ─────────────────────────────────────────────────
          _NotificationCard(l10n: l10n, theme: theme),

          const SizedBox(height: 16),

          // ── Data Management ───────────────────────────────────────────────
          Card(
            child: Column(
              children: [
                _SettingsTile(
                  icon: Icons.cleaning_services_outlined,
                  title: l10n.clearCache,
                  onTap: () async {
                    await HiveStorage.clearCache();
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: const Text('Cache cleared'),
                          backgroundColor: AppColors.primary,
                        ),
                      );
                    }
                  },
                ),
                const Divider(height: 1),
                _SettingsTile(
                  icon: Icons.delete_outline,
                  title: l10n.resetData,
                  titleColor: Colors.red,
                  onTap: () => _showResetDialog(context, ref, l10n),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // ── Legal & Privacy ───────────────────────────────────────────────
          Card(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
                  child: Text(l10n.legalSection,
                      style: theme.textTheme.bodySmall?.copyWith(
                          color: AppColors.primary, fontWeight: FontWeight.w700)),
                ),
                _SettingsTile(
                  icon: Icons.description_outlined,
                  title: l10n.legalTerms,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) =>
                          const LegalContentScreen(type: LegalDocType.terms),
                    ),
                  ),
                ),
                const Divider(height: 1),
                _SettingsTile(
                  icon: Icons.lock_outline,
                  title: l10n.legalPrivacy,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) =>
                          const LegalContentScreen(type: LegalDocType.privacy),
                    ),
                  ),
                ),
                const Divider(height: 1),
                _SettingsTile(
                  icon: Icons.health_and_safety_outlined,
                  title: l10n.legalHealth,
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) =>
                          const LegalContentScreen(type: LegalDocType.health),
                    ),
                  ),
                ),
                const Divider(height: 1),
                _LegalAcceptanceInfo(l10n: l10n, theme: theme),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // ── About ─────────────────────────────────────────────────────────
          Card(
            child: Column(
              children: [
                _SettingsTile(
                  icon: Icons.help_outline_rounded,
                  title: 'Help & Guide',
                  onTap: () => context.push('/help'),
                ),
                const Divider(height: 1),
                _SettingsTile(
                  icon: Icons.science_outlined,
                  title: l10n.micronutrients,
                  onTap: () => context.push('/micronutrients'),
                ),
                const Divider(height: 1),
                _SettingsTile(
                  icon: Icons.info_outline,
                  title: l10n.about,
                  onTap: () => _showAboutDialog(context, l10n),
                ),
              ],
            ),
          ),

          const SizedBox(height: 32),
          const Center(child: AppLogo(size: 48, showTagline: true)),
          const SizedBox(height: 8),
          Center(
            child: Text(
              '${l10n.version} ${AppConstants.currentAppVersion}',
              style: theme.textTheme.bodySmall,
            ),
          ),
          const SizedBox(height: 80),
        ],
      ),
    );
  }

  Future<void> _export(
      BuildContext context, WidgetRef ref, AppStrings l10n, {required bool csv}) async {
    final messenger = ScaffoldMessenger.of(context);
    messenger.showSnackBar(SnackBar(
      content: Text(l10n.exporting),
      duration: const Duration(seconds: 1),
    ));
    final ok = csv
        ? await ExportService.exportCsv()
        : await ExportService.exportJsonBackup();
    if (!context.mounted) return;
    messenger.showSnackBar(SnackBar(
      content: Text(ok ? l10n.exportSuccess : l10n.exportFailed),
      backgroundColor: ok ? AppColors.primary : Colors.red,
    ));
  }

  void _showResetDialog(BuildContext context, WidgetRef ref, AppStrings l10n) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.resetData),
        content: const Text('This will delete all your data permanently. Are you sure?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text(l10n.cancel)),
          TextButton(
            onPressed: () async {
              Navigator.pop(ctx);
              await HiveStorage.resetAllData();
              if (context.mounted) context.go('/onboarding');
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: Text(l10n.resetData),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog(BuildContext context, AppStrings l10n) {
    showDialog(
      context: context,
      builder: (ctx) => AboutDialog(
        applicationName: l10n.appName,
        applicationVersion: '1.0.0',
        applicationLegalese: '© 2026 Infinity Health Tracker\n${l10n.tagline}',
        children: [
          const SizedBox(height: 16),
          const Text(
              'A bilingual (English + Bengali) nutrition tracking app.\nFully offline-first. No data leaves your device.'),
        ],
      ),
    );
  }
}

class _ProfileAvatar extends StatelessWidget {
  final String? imagePath;
  const _ProfileAvatar({this.imagePath});

  @override
  Widget build(BuildContext context) {
    final hasImage = imagePath != null && File(imagePath!).existsSync();
    return Container(
      width: 56,
      height: 56,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AppColors.primary.withOpacity(0.1),
        border: Border.all(color: AppColors.primary.withOpacity(0.3), width: 1.5),
      ),
      child: ClipOval(
        child: hasImage
            ? Image.file(File(imagePath!), fit: BoxFit.cover, width: 56, height: 56,
                errorBuilder: (_, __, ___) =>
                    const Icon(Icons.person, color: AppColors.primary, size: 28))
            : const Icon(Icons.person, color: AppColors.primary, size: 28),
      ),
    );
  }
}

class _LegalAcceptanceInfo extends StatelessWidget {
  final AppStrings l10n;
  final ThemeData theme;
  const _LegalAcceptanceInfo({required this.l10n, required this.theme});

  @override
  Widget build(BuildContext context) {
    final acceptance = HiveStorage.getLegalAcceptance();
    if (acceptance == null) return const SizedBox.shrink();

    final date = acceptance.acceptedAt;
    final formatted =
        '${date.day.toString().padLeft(2, '0')} / '
        '${date.month.toString().padLeft(2, '0')} / '
        '${date.year}';

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 10, 16, 14),
      child: Row(
        children: [
          const Icon(Icons.check_circle_outline,
              size: 16, color: AppColors.primary),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${l10n.legalAcceptedOn}: $formatted',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withValues(alpha: 0.65),
                  ),
                ),
                Text(
                  '${l10n.legalPolicyVersion}: ${acceptance.policyVersion}',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withValues(alpha: 0.45),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SettingsTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final Widget? trailing;
  final VoidCallback? onTap;
  final Color? titleColor;

  const _SettingsTile({
    required this.icon,
    required this.title,
    this.trailing,
    this.onTap,
    this.titleColor,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: AppColors.primary),
      title: Text(
        title,
        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: titleColor,
              fontWeight: FontWeight.w500,
            ),
      ),
      trailing: trailing ?? (onTap != null ? const Icon(Icons.chevron_right, size: 20) : null),
      onTap: onTap,
    );
  }
}

// ── Notification Settings Card ────────────────────────────────────────────────

class _NotificationCard extends StatefulWidget {
  final AppStrings l10n;
  final ThemeData theme;
  const _NotificationCard({required this.l10n, required this.theme});

  @override
  State<_NotificationCard> createState() => _NotificationCardState();
}

class _NotificationCardState extends State<_NotificationCard> {
  late bool _enabled;
  late int _hour;
  late int _minute;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    _enabled = HiveStorage.notificationEnabled;
    _hour = HiveStorage.notificationHour;
    _minute = HiveStorage.notificationMinute;
  }

  Future<void> _toggleEnabled(bool value) async {
    setState(() => _saving = true);
    await HiveStorage.setNotificationEnabled(value);
    if (value) {
      final granted =
          await NotificationService.instance.requestPermissions();
      if (granted) {
        await NotificationService.instance.scheduleReminder(
          hour: _hour,
          minute: _minute,
          language: HiveStorage.language,
        );
      }
    } else {
      await NotificationService.instance.cancelReminder();
    }
    if (mounted) setState(() { _enabled = value; _saving = false; });
  }

  Future<void> _pickTime() async {
    final picked = await showTimePicker(
      context: context,
      initialTime: TimeOfDay(hour: _hour, minute: _minute),
      helpText: widget.l10n.isBengali
          ? 'রিমাইন্ডারের সময় বেছে নিন'
          : 'Choose reminder time',
    );
    if (picked == null || !mounted) return;
    setState(() { _hour = picked.hour; _minute = picked.minute; _saving = true; });
    await HiveStorage.setNotificationTime(picked.hour, picked.minute);
    if (_enabled) {
      await NotificationService.instance.scheduleReminder(
        hour: picked.hour,
        minute: picked.minute,
        language: HiveStorage.language,
      );
    }
    if (mounted) setState(() => _saving = false);
  }

  @override
  Widget build(BuildContext context) {
    final theme = widget.theme;
    final l10n = widget.l10n;
    final bn = l10n.isBengali;
    final timeStr = NotificationService.formatTime(_hour, _minute);

    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            child: Text(
              bn ? 'মিল রিমাইন্ডার' : 'Meal Reminders',
              style: theme.textTheme.bodySmall?.copyWith(
                  color: AppColors.primary, fontWeight: FontWeight.w700),
            ),
          ),

          // Toggle row
          ListTile(
            leading: Icon(
              _enabled
                  ? Icons.notifications_active_outlined
                  : Icons.notifications_off_outlined,
              color: _enabled ? AppColors.primary : Colors.grey,
            ),
            title: Text(
              bn ? 'দৈনিক রিমাইন্ডার' : 'Daily reminder',
              style: theme.textTheme.bodyLarge
                  ?.copyWith(fontWeight: FontWeight.w500),
            ),
            subtitle: Text(
              bn
                  ? 'নাস্তা ও রাতের খাবার না লগ করলে রিমাইন্ড করবে'
                  : 'Reminds you to log breakfast & dinner',
              style: theme.textTheme.bodySmall,
            ),
            trailing: _saving
                ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Switch(
                    value: _enabled,
                    activeThumbColor: AppColors.primary,
                    activeTrackColor: AppColors.primary.withValues(alpha: 0.5),
                    onChanged: _toggleEnabled,
                  ),
          ),

          // Time picker row (only when enabled)
          if (_enabled) ...[
            const Divider(height: 1),
            ListTile(
              leading: const Icon(Icons.schedule_outlined,
                  color: AppColors.primary),
              title: Text(
                bn ? 'রিমাইন্ডারের সময়' : 'Reminder time',
                style: theme.textTheme.bodyLarge
                    ?.copyWith(fontWeight: FontWeight.w500),
              ),
              subtitle: Text(
                timeStr,
                style: theme.textTheme.bodySmall?.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
              trailing: const Icon(Icons.chevron_right, size: 20),
              onTap: _pickTime,
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
              child: Row(
                children: [
                  Icon(Icons.info_outline,
                      size: 14,
                      color: theme.colorScheme.onSurface.withValues(alpha: 0.45)),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      bn
                          ? 'উভয় মিল লগ করলে পরের দিনের জন্য স্বয়ংক্রিয়ভাবে সেট হবে।'
                          : 'Auto-reschedules to next day once both meals are logged.',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurface.withValues(alpha: 0.55),
                        fontSize: 11,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
