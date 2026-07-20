import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../localization/app_localizations.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../storage/hive_storage.dart';
import '../../services/api_key_service.dart';
import '../../services/export_service.dart';
import '../../widgets/common/app_logo.dart';
import '../settings/providers/settings_provider.dart';
import '../profile/providers/profile_provider.dart';
import '../dashboard/providers/dashboard_provider.dart';
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

          // ── Custom Nutrition Goals ────────────────────────────────────────
          _CustomNutritionLimitsCard(l10n: l10n, theme: theme),

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

          // ── Weight & Backup ───────────────────────────────────────────────
          Card(
            child: Column(
              children: [
                _SettingsTile(
                  icon: Icons.monitor_weight_outlined,
                  title: l10n.isBengali ? 'ওজন ট্র্যাকার' : 'Weight Tracker',
                  onTap: () => context.push('/weight').then((_) {
                    ref.read(profileProvider.notifier).refresh();
                  }),
                ),
                const Divider(height: 1),
                _SettingsTile(
                  icon: Icons.shield_outlined,
                  title: l10n.isBengali ? 'ব্যাকআপ ও আর্কাইভ' : 'Backup & Archive',
                  onTap: () => context.push('/backup'),
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
                          content: Text(l10n.clearCache),
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

          // ── Advanced Settings (API Key) ────────────────────────────────────
          _ApiKeyCard(l10n: l10n, theme: theme),

          const SizedBox(height: 16),

          // ── Gemini API Key (photo food scan) ──────────────────────────────
          _GeminiKeyCard(l10n: l10n, theme: theme),

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
                  onTap: () => context.push('/legal/terms'),
                ),
                const Divider(height: 1),
                _SettingsTile(
                  icon: Icons.lock_outline,
                  title: l10n.legalPrivacy,
                  onTap: () => context.push('/legal/privacy'),
                ),
                const Divider(height: 1),
                _SettingsTile(
                  icon: Icons.health_and_safety_outlined,
                  title: l10n.legalHealth,
                  onTap: () => context.push('/legal/health'),
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
                  title: l10n.helpGuide,
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
        content: Text(l10n.resetDataConfirm),
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
        applicationVersion: AppConstants.currentAppVersion,
        applicationLegalese: '© 2026 Ashim Kumar Ghosh. All rights reserved.\n${l10n.tagline}',
        children: const [
          SizedBox(height: 16),
          Text(
            'A bilingual (English + Bengali) nutrition tracking app.\nFully offline-first. No data leaves your device.',
          ),
          SizedBox(height: 12),
          Text('Developer: Ashim Kumar Ghosh', style: TextStyle(fontWeight: FontWeight.w600)),
          SizedBox(height: 4),
          Text('Feedback & Support:\ntalktoashim27@gmail.com'),
        ],
      ),
    );
  }
}

// ── Custom Nutrition Limits ───────────────────────────────────────────────────

class _CustomNutritionLimitsCard extends ConsumerStatefulWidget {
  final AppStrings l10n;
  final ThemeData theme;
  const _CustomNutritionLimitsCard(
      {required this.l10n, required this.theme});

  @override
  ConsumerState<_CustomNutritionLimitsCard> createState() =>
      _CustomNutritionLimitsCardState();
}

class _CustomNutritionLimitsCardState
    extends ConsumerState<_CustomNutritionLimitsCard> {
  bool _useCustom = false;
  final _formKey = GlobalKey<FormState>();
  final _calCtrl = TextEditingController();
  final _proCtrl = TextEditingController();
  final _carbCtrl = TextEditingController();
  final _fatCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _useCustom = HiveStorage.useCustomLimits;
    _calCtrl.text = HiveStorage.customCalories?.toStringAsFixed(0) ?? '';
    _proCtrl.text = HiveStorage.customProteinG?.toStringAsFixed(0) ?? '';
    _carbCtrl.text = HiveStorage.customCarbsG?.toStringAsFixed(0) ?? '';
    _fatCtrl.text = HiveStorage.customFatG?.toStringAsFixed(0) ?? '';
  }

  @override
  void dispose() {
    _calCtrl.dispose();
    _proCtrl.dispose();
    _carbCtrl.dispose();
    _fatCtrl.dispose();
    super.dispose();
  }

  Future<void> _saveAll() async {
    if (!(_formKey.currentState?.validate() ?? true)) return;
    await HiveStorage.setUseCustomLimits(_useCustom);
    await HiveStorage.saveCustomCalories(double.tryParse(_calCtrl.text.trim()));
    await HiveStorage.saveCustomProteinG(double.tryParse(_proCtrl.text.trim()));
    await HiveStorage.saveCustomCarbsG(double.tryParse(_carbCtrl.text.trim()));
    await HiveStorage.saveCustomFatG(double.tryParse(_fatCtrl.text.trim()));
    ref.read(profileProvider.notifier).refresh();
    ref.read(dashboardProvider.notifier).refresh();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(widget.l10n.isBengali
            ? 'পুষ্টির লক্ষ্যমাত্রা সংরক্ষিত হয়েছে'
            : 'Nutrition goals saved'),
        backgroundColor: AppColors.primary,
      ));
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = widget.l10n;
    final theme = widget.theme;
    final bn = l10n.isBengali;
    final isDark = theme.brightness == Brightness.dark;
    const accent = Color(0xFF8E44AD);

    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Section header ─────────────────────────────────────────────
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            child: Row(
              children: [
                const Icon(Icons.tune_rounded,
                    color: Color(0xFF8E44AD), size: 16),
                const SizedBox(width: 6),
                Text(
                  l10n.customNutritionLimits,
                  style: theme.textTheme.bodySmall?.copyWith(
                      color: accent, fontWeight: FontWeight.w700),
                ),
                if (_useCustom) ...[
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 7, vertical: 2),
                    decoration: BoxDecoration(
                      color: accent.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      l10n.customLimitsActive,
                      style: const TextStyle(
                          fontSize: 10,
                          color: AppColors.primary,
                          fontWeight: FontWeight.w700),
                    ),
                  ),
                ],
              ],
            ),
          ),

          // ── Toggle row ─────────────────────────────────────────────────
          ListTile(
            leading: const Icon(Icons.settings_applications_rounded,
                color: Color(0xFF8E44AD)),
            title: Text(l10n.customLimitsToggle),
            trailing: Switch(
              value: _useCustom,
              activeThumbColor: accent,
              activeTrackColor: accent.withValues(alpha: 0.4),
              onChanged: (v) async {
                setState(() => _useCustom = v);
                await HiveStorage.setUseCustomLimits(v);
                ref.read(profileProvider.notifier).refresh();
                ref.read(dashboardProvider.notifier).refresh();
              },
            ),
          ),

          if (_useCustom) ...[
            // ── Medical disclaimer ───────────────────────────────────────
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: isDark
                      ? Colors.orange.shade900.withValues(alpha: 0.3)
                      : Colors.amber.shade50,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                      color: Colors.orange.shade300, width: 1.2),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.medical_services_outlined,
                            color: Colors.orange.shade700, size: 17),
                        const SizedBox(width: 6),
                        Text(
                          l10n.customLimitsDisclaimer,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            color: Colors.orange.shade800,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      l10n.customLimitsDoctorNote,
                      style: TextStyle(
                          fontSize: 12, color: Colors.orange.shade800),
                    ),
                  ],
                ),
              ),
            ),

            // ── Input fields ─────────────────────────────────────────────
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 4),
              child: Form(
                key: _formKey,
                child: Column(
                children: [
                  _LimitField(
                    ctrl: _calCtrl,
                    label: l10n.customCalorieLimit,
                    hint: bn ? 'যেমন: ১৮০০' : 'e.g. 1800',
                    unit: 'kcal',
                    icon: Icons.local_fire_department_rounded,
                    color: AppColors.calories,
                    min: 800, max: 5000,
                  ),
                  const SizedBox(height: 10),
                  _LimitField(
                    ctrl: _proCtrl,
                    label: l10n.customProteinLimit,
                    hint: bn ? 'যেমন: ৮০' : 'e.g. 80',
                    unit: 'g',
                    icon: Icons.fitness_center_rounded,
                    color: AppColors.protein,
                    min: 10, max: 400,
                  ),
                  const SizedBox(height: 10),
                  _LimitField(
                    ctrl: _carbCtrl,
                    label: l10n.customCarbsLimit,
                    hint: bn ? 'যেমন: ২০০' : 'e.g. 200',
                    unit: 'g',
                    icon: Icons.grain_rounded,
                    color: AppColors.carbs,
                    min: 20, max: 700,
                  ),
                  const SizedBox(height: 10),
                  _LimitField(
                    ctrl: _fatCtrl,
                    label: l10n.customFatLimit,
                    hint: bn ? 'যেমন: ৬০' : 'e.g. 60',
                    unit: 'g',
                    icon: Icons.opacity_rounded,
                    color: AppColors.fat,
                    min: 10, max: 300,
                  ),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: _saveAll,
                      icon: const Icon(Icons.save_rounded, size: 16),
                      label: Text(l10n.save),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: accent,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ),
                  const SizedBox(height: 6),
                  TextButton(
                    onPressed: () async {
                      setState(() {
                        _useCustom = false;
                        _calCtrl.clear();
                        _proCtrl.clear();
                        _carbCtrl.clear();
                        _fatCtrl.clear();
                      });
                      await HiveStorage.setUseCustomLimits(false);
                      await HiveStorage.saveCustomCalories(null);
                      await HiveStorage.saveCustomProteinG(null);
                      await HiveStorage.saveCustomCarbsG(null);
                      await HiveStorage.saveCustomFatG(null);
                      ref.read(profileProvider.notifier).refresh();
                      ref.read(dashboardProvider.notifier).refresh();
                    },
                    child: Text(
                      l10n.useAutoCalculated,
                      style: TextStyle(
                          color: theme.colorScheme.onSurface
                              .withValues(alpha: 0.55)),
                    ),
                  ),
                ],
              ),
            ),
          ),
          ],
        ],
      ),
    );
  }
}

class _LimitField extends StatelessWidget {
  final TextEditingController ctrl;
  final String label, hint, unit;
  final IconData icon;
  final Color color;
  final double min;
  final double max;

  const _LimitField({
    required this.ctrl,
    required this.label,
    required this.hint,
    required this.unit,
    required this.icon,
    required this.color,
    this.min = 0,
    this.max = 9999,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: ctrl,
      keyboardType: const TextInputType.numberWithOptions(decimal: true),
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        suffixText: unit,
        prefixIcon: Icon(icon, color: color, size: 18),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: color, width: 1.5),
        ),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      ),
      validator: (v) {
        if (v == null || v.trim().isEmpty) return null;
        final n = double.tryParse(v.trim());
        if (n == null) return 'Enter a valid number';
        if (n < min || n > max) return 'Enter a value between ${min.toInt()} and ${max.toInt()}';
        return null;
      },
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
        color: AppColors.primary.withValues(alpha: 0.1),
        border: Border.all(color: AppColors.primary.withValues(alpha: 0.3), width: 1.5),
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

// ── Advanced Settings — USDA API Key ─────────────────────────────────────────

class _ApiKeyCard extends StatefulWidget {
  final AppStrings l10n;
  final ThemeData theme;
  const _ApiKeyCard({required this.l10n, required this.theme});

  @override
  State<_ApiKeyCard> createState() => _ApiKeyCardState();
}

class _ApiKeyCardState extends State<_ApiKeyCard> {
  bool _hasCustomKey = false;

  @override
  void initState() {
    super.initState();
    _hasCustomKey = ApiKeyService.instance.hasCustomKey;
  }

  void _refresh() {
    if (mounted) setState(() => _hasCustomKey = ApiKeyService.instance.hasCustomKey);
  }

  Future<void> _openSheet() async {
    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _ApiKeySheet(
        l10n: widget.l10n,
        theme: widget.theme,
        hasCustomKey: _hasCustomKey,
        onChanged: _refresh,
      ),
    );
  }

  static const String _defaultKeyMasked = 'Bgn3gF9O••••••••••••H8Ne';

  @override
  Widget build(BuildContext context) {
    final l10n = widget.l10n;
    final theme = widget.theme;
    final bn = l10n.isBengali;
    final hasKey = _hasCustomKey;

    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            child: Text(
              bn ? 'উন্নত সেটিংস' : 'Advanced Settings',
              style: theme.textTheme.bodySmall?.copyWith(
                  color: AppColors.primary, fontWeight: FontWeight.w700),
            ),
          ),
          ListTile(
            leading: const Icon(Icons.vpn_key, color: Colors.green),
            title: Text(
              l10n.apiKeyLabel,
              style: theme.textTheme.bodyLarge?.copyWith(fontWeight: FontWeight.w500),
            ),
            subtitle: Text(
              hasKey
                  ? (bn ? 'আপনার কাস্টম API কী সক্রিয় ✓' : 'Your custom API key is active ✓')
                  : l10n.apiKeyUsingDemo,
              style: theme.textTheme.bodySmall?.copyWith(
                color: Colors.green,
                fontWeight: FontWeight.w500,
              ),
            ),
            trailing: const Icon(Icons.chevron_right, size: 20),
            onTap: _openSheet,
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(72, 0, 16, 12),
            child: Text(
              hasKey
                  ? (bn ? 'ডিফল্ট কী: $_defaultKeyMasked' : 'Default key: $_defaultKeyMasked')
                  : (bn ? 'কী: $_defaultKeyMasked' : 'Key: $_defaultKeyMasked'),
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.45),
                fontSize: 11,
                fontFamily: 'monospace',
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ApiKeySheet extends StatefulWidget {
  final AppStrings l10n;
  final ThemeData theme;
  final bool hasCustomKey;
  final VoidCallback onChanged;

  const _ApiKeySheet({
    required this.l10n,
    required this.theme,
    required this.hasCustomKey,
    required this.onChanged,
  });

  @override
  State<_ApiKeySheet> createState() => _ApiKeySheetState();
}

class _ApiKeySheetState extends State<_ApiKeySheet> {
  final _ctrl = TextEditingController();
  bool _validating = false;
  String? _error;
  bool _success = false;

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Future<void> _validateAndSave() async {
    final key = _ctrl.text.trim();
    final l10n = widget.l10n;
    final bn = l10n.isBengali;
    if (key.isEmpty) {
      setState(() => _error = bn ? 'API কী লিখুন' : 'Please enter an API key');
      return;
    }
    setState(() { _validating = true; _error = null; _success = false; });
    try {
      final dio = Dio(BaseOptions(
        baseUrl: AppConstants.usdaBaseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 15),
      ));
      final resp = await dio.get('/foods/search',
          queryParameters: {'query': 'apple', 'pageSize': 1, 'api_key': key});
      if (resp.statusCode == 200) {
        await HiveStorage.saveUserApiKey(key);
        if (!mounted) return;
        setState(() { _validating = false; _success = true; });
        widget.onChanged();
        await Future.delayed(const Duration(milliseconds: 700));
        if (mounted) Navigator.pop(context);
      } else {
        setState(() { _validating = false; _error = l10n.apiKeyInvalid; });
      }
    } on DioException catch (e) {
      final status = e.response?.statusCode;
      if (status == 403 || status == 401) {
        setState(() { _validating = false; _error = l10n.apiKeyInvalid; });
      } else {
        // Network unreachable — save anyway so user is not blocked
        await HiveStorage.saveUserApiKey(key);
        if (!mounted) return;
        setState(() { _validating = false; _success = true; });
        widget.onChanged();
        await Future.delayed(const Duration(milliseconds: 700));
        if (mounted) Navigator.pop(context);
      }
    } catch (_) {
      if (mounted) setState(() { _validating = false; _error = widget.l10n.apiKeyInvalid; });
    }
  }

  Future<void> _removeKey() async {
    final l10n = widget.l10n;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.apiKeyRemove),
        content: Text(l10n.apiKeyRemoveConfirm),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(l10n.cancel)),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: Text(l10n.apiKeyRemove),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      await HiveStorage.clearUserApiKey();
      if (mounted) {
        widget.onChanged();
        Navigator.pop(context);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = widget.l10n;
    final theme = widget.theme;
    final bn = l10n.isBengali;
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      padding: EdgeInsets.only(
        left: 20, right: 20, top: 12,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Drag handle
            Center(
              child: Container(
                width: 36, height: 4,
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),

            // Title
            Row(
              children: [
                const Icon(Icons.vpn_key, color: AppColors.primary, size: 20),
                const SizedBox(width: 8),
                Text(l10n.apiKeyLabel,
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              bn
                  ? 'অ্যাপটি বিল্ট-ইন ডিফল্ট কী ব্যবহার করে। চাইলে নিজের বিনামূল্যে USDA API কী যোগ করতে পারেন।'
                  : 'The app uses a built-in key by default. You can optionally add your own free USDA API key for dedicated access.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
              ),
            ),
            const SizedBox(height: 16),

            // Step-by-step instructions
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: isDark
                    ? Colors.blue.shade900.withValues(alpha: 0.25)
                    : Colors.blue.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                    color: isDark
                        ? Colors.blue.shade700.withValues(alpha: 0.4)
                        : Colors.blue.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.info_outline,
                          size: 14,
                          color: isDark
                              ? Colors.blue.shade300
                              : Colors.blue.shade800),
                      const SizedBox(width: 6),
                      Text(
                        bn ? 'বিনামূল্যে কী কীভাবে পাবেন:' : 'How to get a free API key:',
                        style: TextStyle(
                            fontWeight: FontWeight.w700,
                            fontSize: 12,
                            color: isDark
                                ? Colors.blue.shade300
                                : Colors.blue.shade800),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  _Step(
                    number: '1',
                    text: bn
                        ? 'fdc.nal.usda.gov ওয়েবসাইটে যান'
                        : 'Go to fdc.nal.usda.gov in your browser',
                    isDark: isDark,
                  ),
                  _Step(
                    number: '2',
                    text: bn
                        ? '"Get API Key" ক্লিক করুন'
                        : 'Click "Get API Key" at the top right',
                    isDark: isDark,
                  ),
                  _Step(
                    number: '3',
                    text: bn
                        ? 'নাম ও ইমেইল পূরণ করুন — একদম বিনামূল্যে, কোনো কার্ড নেই'
                        : 'Fill in your name & email — completely free, no card needed',
                    isDark: isDark,
                  ),
                  _Step(
                    number: '4',
                    text: bn
                        ? 'ইমেইল চেক করুন — কয়েক মিনিটে API কী আসবে'
                        : 'Check your email — your API key arrives within minutes',
                    isDark: isDark,
                  ),
                  _Step(
                    number: '5',
                    text: bn
                        ? 'নিচের ঘরে কী পেস্ট করুন এবং "যাচাই করুন" চাপুন'
                        : 'Paste the key in the field below and tap Validate & Save',
                    isDark: isDark,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Text field
            TextField(
              controller: _ctrl,
              autocorrect: false,
              enableSuggestions: false,
              decoration: InputDecoration(
                labelText: l10n.apiKeyLabel,
                hintText: l10n.apiKeyPaste,
                errorText: _error,
                prefixIcon: const Icon(Icons.vpn_key_outlined, size: 18),
                suffixIcon: _success
                    ? const Icon(Icons.check_circle, color: Colors.green)
                    : null,
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10)),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide:
                      const BorderSide(color: AppColors.primary, width: 1.5),
                ),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
              ),
            ),
            const SizedBox(height: 6),
            Text(
              l10n.apiKeyDialogHint,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
                fontSize: 11,
              ),
            ),
            const SizedBox(height: 16),

            // Action buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed:
                        _validating ? null : () => Navigator.pop(context),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                    child: Text(l10n.cancel),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: ElevatedButton.icon(
                    onPressed: _validating ? null : _validateAndSave,
                    icon: _validating
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: Colors.white))
                        : const Icon(Icons.check_rounded, size: 16),
                    label: Text(_validating
                        ? l10n.apiKeyValidating
                        : l10n.apiKeyValidate),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                ),
              ],
            ),

            if (widget.hasCustomKey) ...[
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: TextButton.icon(
                  onPressed: _validating ? null : _removeKey,
                  icon: const Icon(Icons.delete_outline,
                      size: 16, color: Colors.red),
                  label: Text(l10n.apiKeyRemove,
                      style: const TextStyle(color: Colors.red)),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _GeminiKeyCard extends StatefulWidget {
  final AppStrings l10n;
  final ThemeData theme;
  const _GeminiKeyCard({required this.l10n, required this.theme});

  @override
  State<_GeminiKeyCard> createState() => _GeminiKeyCardState();
}

class _GeminiKeyCardState extends State<_GeminiKeyCard> {
  bool _hasKey = false;
  bool _hasCustomKey = false;

  @override
  void initState() {
    super.initState();
    _hasKey = ApiKeyService.instance.hasGeminiKey;
    _hasCustomKey = ApiKeyService.instance.hasCustomGeminiKey;
  }

  void _refresh() {
    if (mounted) {
      setState(() {
        _hasKey = ApiKeyService.instance.hasGeminiKey;
        _hasCustomKey = ApiKeyService.instance.hasCustomGeminiKey;
      });
    }
  }

  Future<void> _openSheet() async {
    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _GeminiKeySheet(
        l10n: widget.l10n,
        theme: widget.theme,
        hasCustomKey: _hasCustomKey,
        onChanged: _refresh,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = widget.theme;
    final bn = widget.l10n.isBengali;

    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            child: Text(
              bn ? 'ফটো ফুড স্ক্যান' : 'Photo Food Scan',
              style: theme.textTheme.bodySmall?.copyWith(
                  color: AppColors.primary, fontWeight: FontWeight.w700),
            ),
          ),
          ListTile(
            leading: Icon(Icons.auto_awesome,
                color: _hasKey ? Colors.green : Colors.amber.shade700),
            title: Text(
              bn ? 'Gemini API কী' : 'Gemini API Key',
              style: theme.textTheme.bodyLarge
                  ?.copyWith(fontWeight: FontWeight.w500),
            ),
            subtitle: Text(
              _hasKey
                  ? (bn ? 'কী সক্রিয় — ফটো স্ক্যান চালু ✓' : 'Key active — photo scan enabled ✓')
                  : (bn
                      ? 'সেট করা নেই — ফটো স্ক্যানের জন্য প্রয়োজন'
                      : 'Not set — needed for photo food scan'),
              style: theme.textTheme.bodySmall?.copyWith(
                color: _hasKey ? Colors.green : Colors.amber.shade800,
                fontWeight: FontWeight.w500,
              ),
            ),
            trailing: const Icon(Icons.chevron_right, size: 20),
            onTap: _openSheet,
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(72, 0, 16, 12),
            child: Text(
              bn
                  ? 'বিনামূল্যে — aistudio.google.com থেকে নিন'
                  : 'Free — get one at aistudio.google.com',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.45),
                fontSize: 11,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _GeminiKeySheet extends StatefulWidget {
  final AppStrings l10n;
  final ThemeData theme;
  final bool hasCustomKey;
  final VoidCallback onChanged;

  const _GeminiKeySheet({
    required this.l10n,
    required this.theme,
    required this.hasCustomKey,
    required this.onChanged,
  });

  @override
  State<_GeminiKeySheet> createState() => _GeminiKeySheetState();
}

class _GeminiKeySheetState extends State<_GeminiKeySheet> {
  final _ctrl = TextEditingController();
  bool _validating = false;
  String? _error;
  bool _success = false;

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  Future<void> _validateAndSave() async {
    final key = _ctrl.text.trim();
    final l10n = widget.l10n;
    final bn = l10n.isBengali;
    if (key.isEmpty) {
      setState(() => _error = bn ? 'API কী লিখুন' : 'Please enter an API key');
      return;
    }
    setState(() { _validating = true; _error = null; _success = false; });
    try {
      final dio = Dio(BaseOptions(
        baseUrl: AppConstants.geminiBaseUrl,
        connectTimeout: const Duration(seconds: 10),
        receiveTimeout: const Duration(seconds: 20),
      ));
      final resp = await dio.post(
        '/models/${AppConstants.geminiModel}:generateContent',
        queryParameters: {'key': key},
        data: {
          'contents': [
            {'parts': [{'text': 'ping'}]}
          ],
          'generationConfig': {'maxOutputTokens': 1},
        },
      );
      if (resp.statusCode == 200) {
        await HiveStorage.saveUserGeminiApiKey(key);
        if (!mounted) return;
        setState(() { _validating = false; _success = true; });
        widget.onChanged();
        await Future.delayed(const Duration(milliseconds: 700));
        if (mounted) Navigator.pop(context);
      } else {
        setState(() { _validating = false; _error = l10n.apiKeyInvalid; });
      }
    } on DioException catch (e) {
      final status = e.response?.statusCode;
      if (status == 400 || status == 401 || status == 403) {
        setState(() { _validating = false; _error = widget.l10n.apiKeyInvalid; });
      } else {
        // Network unreachable — save anyway so user is not blocked
        await HiveStorage.saveUserGeminiApiKey(key);
        if (!mounted) return;
        setState(() { _validating = false; _success = true; });
        widget.onChanged();
        await Future.delayed(const Duration(milliseconds: 700));
        if (mounted) Navigator.pop(context);
      }
    } catch (_) {
      if (mounted) {
        setState(() { _validating = false; _error = widget.l10n.apiKeyInvalid; });
      }
    }
  }

  Future<void> _removeKey() async {
    final l10n = widget.l10n;
    final bn = l10n.isBengali;
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.apiKeyRemove),
        content: Text(bn
            ? 'Gemini কী মুছে ফেললে ফটো ফুড স্ক্যান বন্ধ হয়ে যাবে।'
            : 'Removing the Gemini key will disable photo food scan.'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: Text(l10n.cancel)),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: Text(l10n.apiKeyRemove),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      await HiveStorage.clearUserGeminiApiKey();
      if (mounted) {
        widget.onChanged();
        Navigator.pop(context);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = widget.l10n;
    final theme = widget.theme;
    final bn = l10n.isBengali;
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      padding: EdgeInsets.only(
        left: 20, right: 20, top: 12,
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Drag handle
            Center(
              child: Container(
                width: 36, height: 4,
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: theme.colorScheme.onSurface.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),

            // Title
            Row(
              children: [
                const Icon(Icons.auto_awesome,
                    color: AppColors.primary, size: 20),
                const SizedBox(width: 8),
                Text(bn ? 'Gemini API কী' : 'Gemini API Key',
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.w700)),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              bn
                  ? 'ফটো ফুড স্ক্যান Google Gemini ব্যবহার করে। একটি বিনামূল্যের API কী প্রয়োজন — কোনো কার্ড লাগে না।'
                  : 'Photo food scan uses Google Gemini. It needs a free API key — no card required.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
              ),
            ),
            const SizedBox(height: 16),

            // Step-by-step instructions
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: isDark
                    ? Colors.blue.shade900.withValues(alpha: 0.25)
                    : Colors.blue.shade50,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                    color: isDark
                        ? Colors.blue.shade700.withValues(alpha: 0.4)
                        : Colors.blue.shade200),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.info_outline,
                          size: 14,
                          color: isDark
                              ? Colors.blue.shade300
                              : Colors.blue.shade800),
                      const SizedBox(width: 6),
                      Text(
                        bn ? 'বিনামূল্যে কী কীভাবে পাবেন:' : 'How to get a free API key:',
                        style: TextStyle(
                            fontWeight: FontWeight.w700,
                            fontSize: 12,
                            color: isDark
                                ? Colors.blue.shade300
                                : Colors.blue.shade800),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  _Step(
                    number: '1',
                    text: bn
                        ? 'aistudio.google.com ওয়েবসাইটে যান'
                        : 'Go to aistudio.google.com in your browser',
                    isDark: isDark,
                  ),
                  _Step(
                    number: '2',
                    text: bn
                        ? 'Google অ্যাকাউন্ট দিয়ে সাইন ইন করুন'
                        : 'Sign in with your Google account',
                    isDark: isDark,
                  ),
                  _Step(
                    number: '3',
                    text: bn
                        ? '"Get API key" ক্লিক করে নতুন কী তৈরি করুন — একদম বিনামূল্যে'
                        : 'Click "Get API key" and create a new key — completely free',
                    isDark: isDark,
                  ),
                  _Step(
                    number: '4',
                    text: bn
                        ? 'নিচের ঘরে কী পেস্ট করুন এবং "যাচাই করুন" চাপুন'
                        : 'Paste the key in the field below and tap Validate & Save',
                    isDark: isDark,
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Text field
            TextField(
              controller: _ctrl,
              autocorrect: false,
              enableSuggestions: false,
              decoration: InputDecoration(
                labelText: bn ? 'Gemini API কী' : 'Gemini API Key',
                hintText: l10n.apiKeyPaste,
                errorText: _error,
                prefixIcon: const Icon(Icons.auto_awesome, size: 18),
                suffixIcon: _success
                    ? const Icon(Icons.check_circle, color: Colors.green)
                    : null,
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10)),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(10),
                  borderSide:
                      const BorderSide(color: AppColors.primary, width: 1.5),
                ),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
              ),
            ),
            const SizedBox(height: 16),

            // Action buttons
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed:
                        _validating ? null : () => Navigator.pop(context),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                    child: Text(l10n.cancel),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  flex: 2,
                  child: ElevatedButton.icon(
                    onPressed: _validating ? null : _validateAndSave,
                    icon: _validating
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: Colors.white))
                        : const Icon(Icons.check_rounded, size: 16),
                    label: Text(_validating
                        ? l10n.apiKeyValidating
                        : l10n.apiKeyValidate),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                ),
              ],
            ),

            if (widget.hasCustomKey) ...[
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: TextButton.icon(
                  onPressed: _validating ? null : _removeKey,
                  icon: const Icon(Icons.delete_outline,
                      size: 16, color: Colors.red),
                  label: Text(l10n.apiKeyRemove,
                      style: const TextStyle(color: Colors.red)),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _Step extends StatelessWidget {
  final String number;
  final String text;
  final bool isDark;

  const _Step(
      {required this.number, required this.text, required this.isDark});

  @override
  Widget build(BuildContext context) {
    final color = isDark ? Colors.blue.shade300 : Colors.blue.shade800;
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 20,
            height: 20,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.15),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(number,
                  style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: color)),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(text,
                style: TextStyle(fontSize: 12, color: color, height: 1.4)),
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

