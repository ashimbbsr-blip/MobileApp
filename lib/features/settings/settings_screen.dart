import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../localization/app_localizations.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../core/constants/app_constants.dart';
import '../../storage/hive_storage.dart';
import '../../services/api_key_service.dart';
import '../../services/export_service.dart';
import '../../widgets/common/app_logo.dart';
import '../settings/providers/settings_provider.dart';
import '../profile/providers/profile_provider.dart';
import '../legal/legal_content.dart';
import '../legal/legal_content_screen.dart';

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

          // ── USDA API Key ──────────────────────────────────────────────────
          _ApiKeyCard(l10n: l10n, theme: theme),

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
              '${l10n.version} 1.0.0',
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

// ── API Key Management Card ───────────────────────────────────────────────────

class _ApiKeyCard extends StatefulWidget {
  final AppStrings l10n;
  final ThemeData theme;
  const _ApiKeyCard({required this.l10n, required this.theme});

  @override
  State<_ApiKeyCard> createState() => _ApiKeyCardState();
}

class _ApiKeyCardState extends State<_ApiKeyCard> {
  bool _validating = false;
  String? _validationResult;

  Future<void> _showKeyDialog({bool isUpdate = false}) async {
    final ctrl = TextEditingController(
      text: isUpdate ? HiveStorage.getApiKey() ?? '' : '',
    );
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(isUpdate ? widget.l10n.apiKeyUpdate : widget.l10n.apiKeyAdd),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.l10n.apiKeyDialogHint,
              style: widget.theme.textTheme.bodySmall,
            ),
            const SizedBox(height: 12),
            TextField(
              controller: ctrl,
              autofocus: true,
              decoration: InputDecoration(
                hintText: widget.l10n.apiKeyPaste,
                prefixIcon: const Icon(Icons.vpn_key_outlined),
              ),
            ),
            const SizedBox(height: 8),
            TextButton.icon(
              icon: const Icon(Icons.open_in_browser_outlined, size: 16),
              label: Text(
                widget.l10n.apiKeyGetFree,
                style: const TextStyle(fontSize: 12),
              ),
              onPressed: () async {
                final uri = Uri.parse(AppConstants.usdaApiKeySignupUrl);
                if (await canLaunchUrl(uri)) {
                  await launchUrl(uri, mode: LaunchMode.externalApplication);
                }
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(widget.l10n.cancel),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
            child: Text(widget.l10n.save,
                style: const TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
    if (confirmed == true && ctrl.text.trim().isNotEmpty) {
      await ApiKeyService.instance.saveKey(ctrl.text.trim());
      if (mounted) setState(() => _validationResult = null);
    }
    ctrl.dispose();
  }

  Future<void> _validateKey() async {
    setState(() {
      _validating = true;
      _validationResult = null;
    });
    final key = HiveStorage.getApiKey() ?? '';
    final valid = await ApiKeyService.instance.validateKey(key);
    if (mounted) {
      setState(() {
        _validating = false;
        _validationResult = valid ? 'valid' : 'invalid';
      });
    }
  }

  Future<void> _removeKey() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(widget.l10n.apiKeyRemove),
        content: Text(widget.l10n.apiKeyRemoveConfirm),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text(widget.l10n.cancel),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: Text(widget.l10n.apiKeyRemove),
          ),
        ],
      ),
    );
    if (confirmed == true) {
      await ApiKeyService.instance.removeKey();
      if (mounted) setState(() => _validationResult = null);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = widget.l10n;
    final theme = widget.theme;
    final hasKey = HiveStorage.hasApiKey;
    final masked = ApiKeyService.instance.maskedKey;

    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
            child: Text(l10n.apiKeySection,
                style: theme.textTheme.bodySmall?.copyWith(
                    color: AppColors.primary, fontWeight: FontWeight.w700)),
          ),

          // Status row
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                Icon(
                  hasKey ? Icons.vpn_key : Icons.vpn_key_outlined,
                  size: 18,
                  color: hasKey ? AppColors.primary : Colors.orange,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        hasKey ? l10n.apiKeyLabel : l10n.apiKeyUsingDemo,
                        style: theme.textTheme.bodyMedium
                            ?.copyWith(fontWeight: FontWeight.w600),
                      ),
                      if (hasKey && masked != null)
                        Text(masked,
                            style: theme.textTheme.bodySmall?.copyWith(
                                fontFamily: 'monospace', color: Colors.grey)),
                      if (!hasKey)
                        Text(l10n.apiKeyDemoNote,
                            style: theme.textTheme.bodySmall
                                ?.copyWith(color: Colors.orange)),
                    ],
                  ),
                ),
              ],
            ),
          ),

          if (_validationResult != null)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
              child: Row(children: [
                Icon(
                  _validationResult == 'valid'
                      ? Icons.check_circle_outline
                      : Icons.error_outline,
                  size: 16,
                  color: _validationResult == 'valid' ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 6),
                Text(
                  _validationResult == 'valid'
                      ? l10n.apiKeyValid
                      : l10n.apiKeyInvalid,
                  style: TextStyle(
                    fontSize: 12,
                    color: _validationResult == 'valid' ? Colors.green : Colors.red,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ]),
            ),

          const Divider(height: 1),

          if (!hasKey)
            _SettingsTile(
              icon: Icons.add_circle_outline,
              title: l10n.apiKeyAdd,
              onTap: () => _showKeyDialog(),
            ),

          if (hasKey) ...[
            _SettingsTile(
              icon: Icons.edit_outlined,
              title: l10n.apiKeyUpdate,
              onTap: () => _showKeyDialog(isUpdate: true),
            ),
            const Divider(height: 1),
            _SettingsTile(
              icon: _validating ? Icons.hourglass_empty : Icons.verified_outlined,
              title: _validating ? l10n.apiKeyValidating : l10n.apiKeyValidate,
              onTap: _validating ? null : _validateKey,
            ),
            const Divider(height: 1),
            _SettingsTile(
              icon: Icons.delete_outline,
              title: l10n.apiKeyRemove,
              titleColor: Colors.red,
              onTap: _removeKey,
            ),
          ],
        ],
      ),
    );
  }
}
