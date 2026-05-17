import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:intl/intl.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../core/utils/validators.dart';
import '../../features/dashboard/providers/dashboard_provider.dart';
import 'providers/profile_provider.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _heightCtrl = TextEditingController();
  final _weightCtrl = TextEditingController();

  String _gender = 'male';
  String _activityLevel = 'moderately_active';
  String _fitnessGoal = 'maintain';
  DateTime? _dateOfBirth;
  bool _initialized = false;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _emailCtrl.dispose();
    _heightCtrl.dispose();
    _weightCtrl.dispose();
    super.dispose();
  }

  void _initFromProfile() {
    if (_initialized) return;
    final profile = ref.read(profileProvider).profile;
    if (profile == null) return;
    _nameCtrl.text = profile.fullName ?? '';
    _emailCtrl.text = profile.email ?? '';
    _heightCtrl.text = profile.heightCm.toStringAsFixed(0);
    _weightCtrl.text = profile.weightKg.toStringAsFixed(1);
    _gender = profile.gender;
    _activityLevel = profile.activityLevel;
    _fitnessGoal = profile.fitnessGoal;
    _dateOfBirth = profile.dateOfBirth;
    _initialized = true;
  }

  Future<void> _pickImage(BuildContext ctx) async {
    final source = await showModalBottomSheet<ImageSource>(
      context: ctx,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => _ImageSourceSheet(),
    );
    if (source == null || !mounted) return;
    final path =
        await ref.read(profileProvider.notifier).pickAndCompressImage(source);
    if (path != null) {
      ref.read(profileProvider.notifier).updateProfileImagePath(path);
    }
  }

  Future<void> _pickDob(BuildContext ctx) async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: ctx,
      initialDate: _dateOfBirth ?? DateTime(now.year - 25),
      firstDate: DateTime(now.year - 100),
      lastDate: DateTime(now.year - 5),
    );
    if (picked != null) setState(() => _dateOfBirth = picked);
  }

  Future<void> _save() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    final ok = await ref.read(profileProvider.notifier).saveProfile(
          fullName: _nameCtrl.text,
          email: _emailCtrl.text,
          dateOfBirth: _dateOfBirth,
          gender: _gender,
          heightCm: double.tryParse(_heightCtrl.text) ?? 170,
          weightKg: double.tryParse(_weightCtrl.text) ?? 70,
          activityLevel: _activityLevel,
          fitnessGoal: _fitnessGoal,
        );
    if (ok && mounted) {
      ref.read(dashboardProvider.notifier).refresh();
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(ref.read(appStringsProvider).profileUpdated),
        backgroundColor: AppColors.primary,
      ));
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(profileProvider);
    _initFromProfile();
    final l10n = ref.watch(appStringsProvider);
    final theme = Theme.of(context);
    final profile = state.profile;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.editProfile),
        actions: [
          if (state.isSaving)
            const Padding(
              padding: EdgeInsets.all(16),
              child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
            )
          else
            TextButton(
              onPressed: _save,
              child: Text(l10n.save, style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.w700)),
            ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Avatar
            Center(
              child: Stack(
                children: [
                  _ProfileAvatar(imagePath: profile?.profileImagePath),
                  Positioned(
                    bottom: 0,
                    right: 0,
                    child: GestureDetector(
                      onTap: () => _pickImage(context),
                      child: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: AppColors.primary,
                          shape: BoxShape.circle,
                          border: Border.all(color: theme.scaffoldBackgroundColor, width: 2),
                        ),
                        child: const Icon(Icons.camera_alt, size: 18, color: Colors.white),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
            Center(
              child: Text(l10n.profilePicture,
                  style: theme.textTheme.bodySmall?.copyWith(color: AppColors.primary)),
            ),
            const SizedBox(height: 24),

            // Personal Info
            _SectionHeader(l10n.personalInfo),
            const SizedBox(height: 12),
            TextFormField(
              controller: _nameCtrl,
              textCapitalization: TextCapitalization.words,
              decoration: InputDecoration(
                labelText: l10n.fullName,
                prefixIcon: const Icon(Icons.person_outline),
              ),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _emailCtrl,
              keyboardType: TextInputType.emailAddress,
              decoration: InputDecoration(
                labelText: l10n.emailAddress,
                prefixIcon: const Icon(Icons.email_outlined),
              ),
            ),
            const SizedBox(height: 12),
            InkWell(
              onTap: () => _pickDob(context),
              borderRadius: BorderRadius.circular(12),
              child: InputDecorator(
                decoration: InputDecoration(
                  labelText: l10n.dateOfBirth,
                  prefixIcon: const Icon(Icons.cake_outlined),
                ),
                child: Text(
                  _dateOfBirth != null
                      ? DateFormat('dd MMM yyyy').format(_dateOfBirth!)
                      : l10n.selectDate,
                  style: theme.textTheme.bodyLarge,
                ),
              ),
            ),
            const SizedBox(height: 12),
            _GenderSelector(
              value: _gender,
              onChanged: (v) => setState(() => _gender = v),
              l10n: l10n,
            ),
            const SizedBox(height: 24),

            // Body
            _SectionHeader(l10n.bodyMeasurements),
            const SizedBox(height: 12),
            Row(children: [
              Expanded(
                child: TextFormField(
                  controller: _heightCtrl,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    labelText: l10n.height,
                    suffixText: l10n.cm,
                    prefixIcon: const Icon(Icons.height),
                  ),
                  validator: Validators.validateHeight,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: TextFormField(
                  controller: _weightCtrl,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    labelText: l10n.weight,
                    suffixText: l10n.kg,
                    prefixIcon: const Icon(Icons.monitor_weight_outlined),
                  ),
                  validator: Validators.validateWeight,
                ),
              ),
            ]),
            const SizedBox(height: 24),

            // Fitness
            _SectionHeader(l10n.fitnessGoal),
            const SizedBox(height: 12),
            _DropdownField<String>(
              label: l10n.activityLevel,
              value: _activityLevel,
              items: {
                'sedentary': l10n.sedentary,
                'lightly_active': l10n.lightlyActive,
                'moderately_active': l10n.moderatelyActive,
                'very_active': l10n.veryActive,
                'extra_active': l10n.extraActive,
              },
              onChanged: (v) => setState(() => _activityLevel = v),
            ),
            const SizedBox(height: 12),
            _DropdownField<String>(
              label: l10n.fitnessGoal,
              value: _fitnessGoal,
              items: {
                'lose_weight': l10n.loseWeight,
                'maintain': l10n.maintain,
                'gain_muscle': l10n.gainMuscle,
                'healthy_fat_loss': l10n.healthyFatLoss,
              },
              onChanged: (v) => setState(() => _fitnessGoal = v),
            ),

            if (profile != null) ...[
              const SizedBox(height: 24),
              _SectionHeader(l10n.stats),
              const SizedBox(height: 12),
              _StatsCard(profile: profile),
            ],

            const SizedBox(height: 80),
          ],
        ),
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
      width: 100,
      height: 100,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AppColors.primary.withOpacity(0.1),
        border: Border.all(color: AppColors.primary.withOpacity(0.3), width: 2),
      ),
      child: ClipOval(
        child: hasImage
            ? Image.file(File(imagePath!), fit: BoxFit.cover, width: 100, height: 100,
                errorBuilder: (_, __, ___) => _placeholder())
            : _placeholder(),
      ),
    );
  }

  Widget _placeholder() => const Icon(Icons.person, size: 52, color: AppColors.primary);
}

class _ImageSourceSheet extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.only(bottom: 12),
              decoration: BoxDecoration(
                  color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2)),
            ),
            ListTile(
              leading: const Icon(Icons.photo_library_outlined, color: AppColors.primary),
              title: const Text('From Gallery'),
              onTap: () => Navigator.pop(context, ImageSource.gallery),
            ),
            ListTile(
              leading: const Icon(Icons.camera_alt_outlined, color: AppColors.primary),
              title: const Text('From Camera'),
              onTap: () => Navigator.pop(context, ImageSource.camera),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String text;
  const _SectionHeader(this.text);

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: Theme.of(context).textTheme.titleSmall?.copyWith(
            fontWeight: FontWeight.w700,
            color: AppColors.primary,
          ),
    );
  }
}

class _GenderSelector extends StatelessWidget {
  final String value;
  final ValueChanged<String> onChanged;
  final dynamic l10n;
  const _GenderSelector({required this.value, required this.onChanged, required this.l10n});

  @override
  Widget build(BuildContext context) {
    return Row(children: [
      Expanded(child: _GenderOption(label: l10n.male, icon: Icons.male, selected: value == 'male', onTap: () => onChanged('male'))),
      const SizedBox(width: 12),
      Expanded(child: _GenderOption(label: l10n.female, icon: Icons.female, selected: value == 'female', onTap: () => onChanged('female'))),
    ]);
  }
}

class _GenderOption extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;
  const _GenderOption({required this.label, required this.icon, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 14),
        decoration: BoxDecoration(
          color: selected ? AppColors.primary : AppColors.primary.withOpacity(0.07),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: selected ? AppColors.primary : Colors.transparent),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: selected ? Colors.white : AppColors.primary, size: 20),
            const SizedBox(width: 6),
            Text(label,
                style: TextStyle(
                  color: selected ? Colors.white : AppColors.primary,
                  fontWeight: FontWeight.w600,
                )),
          ],
        ),
      ),
    );
  }
}

class _DropdownField<T> extends StatelessWidget {
  final String label;
  final T value;
  final Map<T, String> items;
  final ValueChanged<T> onChanged;
  const _DropdownField({required this.label, required this.value, required this.items, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return DropdownButtonFormField<T>(
      initialValue: value,
      decoration: InputDecoration(labelText: label),
      items: items.entries
          .map((e) => DropdownMenuItem(value: e.key, child: Text(e.value)))
          .toList(),
      onChanged: (v) { if (v != null) onChanged(v); },
    );
  }
}

class _StatsCard extends StatelessWidget {
  final dynamic profile;
  const _StatsCard({required this.profile});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _StatItem(label: 'BMI', value: profile.bmi.toStringAsFixed(1), sub: profile.bmiCategory),
            _StatItem(label: 'Height', value: '${profile.heightCm.toStringAsFixed(0)} cm'),
            _StatItem(label: 'Weight', value: '${profile.weightKg.toStringAsFixed(1)} kg'),
          ],
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label, value;
  final String? sub;
  const _StatItem({required this.label, required this.value, this.sub});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value, style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700, color: AppColors.primary)),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        if (sub != null) Text(sub!, style: const TextStyle(fontSize: 10, color: Colors.grey)),
      ],
    );
  }
}
