import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../storage/hive_storage.dart';
import '../../models/legal_acceptance.dart';
import '../../core/constants/app_constants.dart';
import 'legal_content.dart';
import 'legal_content_screen.dart';

class LegalAcceptanceScreen extends ConsumerStatefulWidget {
  const LegalAcceptanceScreen({super.key});

  @override
  ConsumerState<LegalAcceptanceScreen> createState() =>
      _LegalAcceptanceScreenState();
}

class _LegalAcceptanceScreenState extends ConsumerState<LegalAcceptanceScreen> {
  bool _termsChecked = false;
  bool _healthChecked = false;
  bool _isSaving = false;

  bool get _canAccept => _termsChecked && _healthChecked;

  bool get _isReAcceptance => HiveStorage.needsPolicyReAcceptance;

  Future<void> _accept() async {
    if (!_canAccept || _isSaving) return;
    setState(() => _isSaving = true);

    await HiveStorage.saveLegalAcceptance(LegalAcceptance(
      acceptedAt: DateTime.now(),
      policyVersion: AppConstants.currentPolicyVersion,
      appVersion: AppConstants.currentAppVersion,
    ));

    if (!mounted) return;
    if (!HiveStorage.isOnboardingDone) {
      context.go('/onboarding');
    } else {
      context.go('/dashboard');
    }
  }

  void _openDoc(LegalDocType type) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => LegalContentScreen(type: type),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = ref.watch(appStringsProvider);
    final theme = Theme.of(context);
    final isReAccept = _isReAcceptance;

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(24, 32, 24, 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // ── Header ─────────────────────────────────────────────
                    Center(
                      child: Container(
                        width: 72,
                        height: 72,
                        decoration: BoxDecoration(
                          color: AppColors.primary.withValues(alpha: 0.1),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.verified_user_outlined,
                          size: 36,
                          color: AppColors.primary,
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),
                    Center(
                      child: Text(
                        isReAccept ? l10n.legalUpdatedTitle : l10n.legalAcceptTitle,
                        style: theme.textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.w800,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Center(
                      child: Text(
                        isReAccept
                            ? l10n.legalUpdatedSubtitle
                            : l10n.legalAcceptSubtitle,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurface.withValues(alpha: 0.65),
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),

                    const SizedBox(height: 28),

                    // ── Quick Summary ───────────────────────────────────────
                    _SummaryCard(l10n: l10n, theme: theme),

                    const SizedBox(height: 20),

                    // ── Full Document Links ─────────────────────────────────
                    Text(
                      l10n.legalReadDocs,
                      style: theme.textTheme.labelLarge?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 10),
                    _DocLink(
                      icon: Icons.description_outlined,
                      label: l10n.legalTerms,
                      onTap: () => _openDoc(LegalDocType.terms),
                    ),
                    const SizedBox(height: 8),
                    _DocLink(
                      icon: Icons.lock_outline,
                      label: l10n.legalPrivacy,
                      onTap: () => _openDoc(LegalDocType.privacy),
                    ),
                    const SizedBox(height: 8),
                    _DocLink(
                      icon: Icons.health_and_safety_outlined,
                      label: l10n.legalHealth,
                      onTap: () => _openDoc(LegalDocType.health),
                    ),

                    const SizedBox(height: 28),

                    // ── Checkboxes ─────────────────────────────────────────
                    _ConsentCheck(
                      value: _termsChecked,
                      label: l10n.legalCheckTerms,
                      onChanged: (v) => setState(() => _termsChecked = v ?? false),
                      theme: theme,
                    ),
                    const SizedBox(height: 12),
                    _ConsentCheck(
                      value: _healthChecked,
                      label: l10n.legalCheckHealth,
                      onChanged: (v) => setState(() => _healthChecked = v ?? false),
                      theme: theme,
                    ),

                    const SizedBox(height: 8),
                  ],
                ),
              ),
            ),

            // ── Accept Button ───────────────────────────────────────────────
            Padding(
              padding: const EdgeInsets.fromLTRB(24, 8, 24, 24),
              child: SizedBox(
                width: double.infinity,
                height: 52,
                child: ElevatedButton(
                  onPressed: _canAccept ? _accept : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: Colors.white,
                    disabledBackgroundColor:
                        AppColors.primary.withValues(alpha: 0.3),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                    elevation: 0,
                  ),
                  child: _isSaving
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: Colors.white,
                          ),
                        )
                      : Text(
                          l10n.legalAcceptButton,
                          style: const TextStyle(
                            fontWeight: FontWeight.w700,
                            fontSize: 16,
                          ),
                        ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Quick Summary Card ────────────────────────────────────────────────────────

class _SummaryCard extends StatelessWidget {
  final dynamic l10n;
  final ThemeData theme;
  const _SummaryCard({required this.l10n, required this.theme});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.primary.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: AppColors.primary.withValues(alpha: 0.15),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.info_outline, size: 16, color: AppColors.primary),
              const SizedBox(width: 8),
              Text(
                l10n.legalQuickSummary,
                style: theme.textTheme.labelLarge?.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _Bullet(l10n.legalBullet1, theme),
          _Bullet(l10n.legalBullet2, theme),
          _Bullet(l10n.legalBullet3, theme),
          _Bullet(l10n.legalBullet4, theme),
          _Bullet(l10n.legalBullet5, theme),
        ],
      ),
    );
  }
}

class _Bullet extends StatelessWidget {
  final String text;
  final ThemeData theme;
  const _Bullet(this.text, this.theme);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.only(top: 5),
            child: Icon(Icons.check_circle_outline,
                size: 14, color: AppColors.primary),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: theme.textTheme.bodySmall?.copyWith(height: 1.5),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Document Link Button ──────────────────────────────────────────────────────

class _DocLink extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  const _DocLink({required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 13),
        decoration: BoxDecoration(
          color: theme.cardColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: theme.dividerColor,
          ),
        ),
        child: Row(
          children: [
            Icon(icon, size: 20, color: AppColors.primary),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                label,
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const Icon(Icons.chevron_right, size: 18, color: Colors.grey),
          ],
        ),
      ),
    );
  }
}

// ── Consent Checkbox ──────────────────────────────────────────────────────────

class _ConsentCheck extends StatelessWidget {
  final bool value;
  final String label;
  final ValueChanged<bool?> onChanged;
  final ThemeData theme;

  const _ConsentCheck({
    required this.value,
    required this.label,
    required this.onChanged,
    required this.theme,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () => onChanged(!value),
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.fromLTRB(4, 8, 12, 8),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
          color: value
              ? AppColors.primary.withValues(alpha: 0.06)
              : Colors.transparent,
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Checkbox(
              value: value,
              onChanged: onChanged,
              activeColor: AppColors.primary,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(4),
              ),
              materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
              visualDensity: VisualDensity.compact,
            ),
            const SizedBox(width: 4),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.only(top: 10),
                child: Text(
                  label,
                  style: theme.textTheme.bodySmall?.copyWith(
                    height: 1.55,
                    fontWeight:
                        value ? FontWeight.w600 : FontWeight.normal,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
