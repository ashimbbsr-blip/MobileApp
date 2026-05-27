import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:intl/intl.dart';
import '../../localization/strings_provider.dart';
import '../../theme/app_colors.dart';
import '../../core/utils/validators.dart';
import '../../widgets/common/app_logo.dart';
import 'providers/onboarding_provider.dart';

// Total page count (including welcome)
const _kTotalSteps = 5;

class OnboardingScreen extends ConsumerStatefulWidget {
  const OnboardingScreen({super.key});

  @override
  ConsumerState<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends ConsumerState<OnboardingScreen> {
  final _pageController = PageController();
  final _personalFormKey = GlobalKey<FormState>();
  final _bodyFormKey = GlobalKey<FormState>();

  final _nameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _heightCtrl = TextEditingController();
  final _weightCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    final s = ref.read(onboardingProvider);
    _nameCtrl.text = s.fullName;
    _emailCtrl.text = s.email;
    _heightCtrl.text = s.heightCm.toString();
    _weightCtrl.text = s.weightKg.toString();
  }

  @override
  void dispose() {
    _pageController.dispose();
    _nameCtrl.dispose();
    _emailCtrl.dispose();
    _heightCtrl.dispose();
    _weightCtrl.dispose();
    super.dispose();
  }

  void _animateNext() => _pageController.nextPage(
      duration: const Duration(milliseconds: 380), curve: Curves.easeInOut);

  void _animatePrev() => _pageController.previousPage(
      duration: const Duration(milliseconds: 380), curve: Curves.easeInOut);

  bool _validatePersonal() {
    return _personalFormKey.currentState?.validate() ?? false;
  }

  bool _validateBody() {
    return _bodyFormKey.currentState?.validate() ?? false;
  }

  Future<void> _complete() async {
    await ref.read(onboardingProvider.notifier).complete();
    if (mounted) context.go('/dashboard');
  }

  void _onPageChanged(int index) {
    ref.read(onboardingProvider.notifier).goToStep(index);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(onboardingProvider);

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Progress bar (hidden on welcome page)
            if (state.currentStep > 0)
              Padding(
                padding: const EdgeInsets.fromLTRB(24, 16, 24, 0),
                child: Row(
                  children: List.generate(_kTotalSteps - 1, (i) => Expanded(
                    child: Container(
                      height: 4,
                      margin: const EdgeInsets.symmetric(horizontal: 2),
                      decoration: BoxDecoration(
                        color: i < state.currentStep
                            ? AppColors.primary
                            : AppColors.primary.withOpacity(0.18),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  )),
                ),
              ),
            if (state.currentStep > 0) const SizedBox(height: 4),
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                onPageChanged: _onPageChanged,
                children: [
                  // Page 0: Welcome
                  _WelcomePage(onNext: _animateNext),

                  // Page 1: Personal Info
                  _PersonalInfoPage(
                    formKey: _personalFormKey,
                    nameCtrl: _nameCtrl,
                    emailCtrl: _emailCtrl,
                    onNext: () {
                      if (!_validatePersonal()) return;
                      ref.read(onboardingProvider.notifier)
                        ..setFullName(_nameCtrl.text)
                        ..setEmail(_emailCtrl.text);
                      _animateNext();
                    },
                    onBack: _animatePrev,
                  ),

                  // Page 2: Body measurements
                  _BodyPage(
                    formKey: _bodyFormKey,
                    heightCtrl: _heightCtrl,
                    weightCtrl: _weightCtrl,
                    onNext: () {
                      if (!_validateBody()) return;
                      final h = double.tryParse(_heightCtrl.text);
                      final w = double.tryParse(_weightCtrl.text);
                      if (h != null) ref.read(onboardingProvider.notifier).setHeight(h);
                      if (w != null) ref.read(onboardingProvider.notifier).setWeight(w);
                      _animateNext();
                    },
                    onBack: _animatePrev,
                  ),

                  // Page 3: Activity level
                  _ActivityPage(
                    selected: state.activityLevel,
                    onSelected: (v) => ref.read(onboardingProvider.notifier).setActivityLevel(v),
                    onNext: _animateNext,
                    onBack: _animatePrev,
                  ),

                  // Page 4: Fitness goal → completes onboarding
                  _GoalPage(
                    selected: state.fitnessGoal,
                    onSelected: (v) => ref.read(onboardingProvider.notifier).setFitnessGoal(v),
                    onNext: _complete,
                    onBack: _animatePrev,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ── Welcome Page ──────────────────────────────────────────────────────────────

class _WelcomePage extends StatelessWidget {
  final VoidCallback onNext;
  const _WelcomePage({required this.onNext});

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, _) {
      final l10n = ref.watch(appStringsProvider);
      return Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const AppLogo(size: 100),
            const SizedBox(height: 48),
            Text(
              l10n.welcomeTitle,
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.w700),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              l10n.welcomeSubtitle,
              style: Theme.of(context).textTheme.bodyLarge,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 48),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: onNext,
                child: Text(l10n.getStarted),
              ),
            ),
          ],
        ),
      );
    });
  }
}

// ── Personal Info Page ────────────────────────────────────────────────────────

class _PersonalInfoPage extends ConsumerStatefulWidget {
  final GlobalKey<FormState> formKey;
  final TextEditingController nameCtrl;
  final TextEditingController emailCtrl;
  final VoidCallback onNext;
  final VoidCallback onBack;

  const _PersonalInfoPage({
    required this.formKey,
    required this.nameCtrl,
    required this.emailCtrl,
    required this.onNext,
    required this.onBack,
  });

  @override
  ConsumerState<_PersonalInfoPage> createState() => _PersonalInfoPageState();
}

class _PersonalInfoPageState extends ConsumerState<_PersonalInfoPage> {
  bool _pickingImage = false;

  Future<void> _pickDob() async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: ref.read(onboardingProvider).dateOfBirth ?? DateTime(now.year - 25),
      firstDate: DateTime(now.year - 100),
      lastDate: DateTime(now.year - 5),
    );
    if (picked != null) {
      ref.read(onboardingProvider.notifier).setDateOfBirth(picked);
    }
  }

  Future<void> _pickPhoto() async {
    final source = await showModalBottomSheet<ImageSource>(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => _PhotoSourceSheet(),
    );
    if (source == null || !mounted) return;
    setState(() => _pickingImage = true);
    await ref.read(onboardingProvider.notifier).pickAndSaveProfileImage(source);
    if (mounted) setState(() => _pickingImage = false);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = ref.watch(appStringsProvider);
    final state = ref.watch(onboardingProvider);
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(24, 12, 24, 24),
      child: Form(
        key: widget.formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(l10n.personalInfo,
                style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 4),
            Text('${l10n.step} 1 ${l10n.ofWord} 4',
                style: theme.textTheme.bodyMedium?.copyWith(color: AppColors.primary)),
            const SizedBox(height: 24),

            // Profile photo (optional)
            Center(
              child: GestureDetector(
                onTap: _pickingImage ? null : _pickPhoto,
                child: Stack(
                  children: [
                    _AvatarCircle(
                      imagePath: state.profileImagePath,
                      size: 90,
                      isLoading: _pickingImage,
                    ),
                    Positioned(
                      bottom: 0,
                      right: 0,
                      child: Container(
                        padding: const EdgeInsets.all(7),
                        decoration: BoxDecoration(
                          color: AppColors.primary,
                          shape: BoxShape.circle,
                          border: Border.all(
                              color: theme.scaffoldBackgroundColor, width: 2),
                        ),
                        child: const Icon(Icons.camera_alt,
                            size: 16, color: Colors.white),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Center(
              child: Padding(
                padding: const EdgeInsets.only(top: 6, bottom: 20),
                child: Text(
                  '${l10n.profilePicture} (${l10n.optional})',
                  style: theme.textTheme.bodySmall
                      ?.copyWith(color: AppColors.primary),
                ),
              ),
            ),

            // Full name (required)
            TextFormField(
              controller: widget.nameCtrl,
              textCapitalization: TextCapitalization.words,
              decoration: InputDecoration(
                labelText: l10n.fullName,
                prefixIcon: const Icon(Icons.person_outline),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'Full name is required';
                if (v.trim().length < 2) return 'Name must be at least 2 characters';
                return null;
              },
            ),
            const SizedBox(height: 14),

            // Date of birth (required)
            InkWell(
              onTap: _pickDob,
              borderRadius: BorderRadius.circular(12),
              child: InputDecorator(
                decoration: InputDecoration(
                  labelText: l10n.dateOfBirth,
                  prefixIcon: const Icon(Icons.cake_outlined),
                  suffixIcon: state.dateOfBirth != null
                      ? null
                      : const Icon(Icons.chevron_right, color: Colors.grey),
                  errorText: null,
                ),
                child: Text(
                  state.dateOfBirth != null
                      ? DateFormat('dd MMM yyyy').format(state.dateOfBirth!)
                      : l10n.selectDate,
                  style: theme.textTheme.bodyLarge?.copyWith(
                    color: state.dateOfBirth != null
                        ? null
                        : theme.hintColor,
                  ),
                ),
              ),
            ),
            if (state.dateOfBirth != null) ...[
              const SizedBox(height: 6),
              Padding(
                padding: const EdgeInsets.only(left: 12),
                child: Text(
                  'Age: ${_computeAge(state.dateOfBirth!)} years',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: AppColors.primary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
            const SizedBox(height: 14),

            // Email (required)
            TextFormField(
              controller: widget.emailCtrl,
              keyboardType: TextInputType.emailAddress,
              decoration: InputDecoration(
                labelText: l10n.emailAddress,
                prefixIcon: const Icon(Icons.email_outlined),
              ),
              validator: (v) {
                if (v == null || v.trim().isEmpty) return 'Email address is required';
                final emailRegex = RegExp(r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$');
                if (!emailRegex.hasMatch(v.trim())) return 'Enter a valid email address';
                return null;
              },
            ),

            const SizedBox(height: 32),

            // Navigation buttons
            Row(children: [
              Expanded(child: OutlinedButton(onPressed: widget.onBack, child: Text(l10n.back))),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: () {
                    if (ref.read(onboardingProvider).dateOfBirth == null) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Please select your date of birth'),
                          backgroundColor: Colors.red,
                        ),
                      );
                      return;
                    }
                    widget.onNext();
                  },
                  child: Text(l10n.next),
                ),
              ),
            ]),
          ],
        ),
      ),
    );
  }

  int _computeAge(DateTime dob) {
    final today = DateTime.now();
    int age = today.year - dob.year;
    if (today.month < dob.month ||
        (today.month == dob.month && today.day < dob.day)) {
      age--;
    }
    return age;
  }
}

// ── Body Measurements Page ────────────────────────────────────────────────────

class _BodyPage extends ConsumerWidget {
  final GlobalKey<FormState> formKey;
  final TextEditingController heightCtrl;
  final TextEditingController weightCtrl;
  final VoidCallback onNext;
  final VoidCallback onBack;

  const _BodyPage({
    required this.formKey,
    required this.heightCtrl,
    required this.weightCtrl,
    required this.onNext,
    required this.onBack,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = ref.watch(appStringsProvider);
    final state = ref.watch(onboardingProvider);

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Form(
        key: formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(l10n.bodyMeasurements,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 4),
            Text('${l10n.step} 2 ${l10n.ofWord} 4',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.primary)),
            const SizedBox(height: 28),

            // Gender
            Text(l10n.gender,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
            const SizedBox(height: 12),
            Row(children: [
              _GenderChip(
                label: l10n.male,
                selected: state.gender == 'male',
                onTap: () => ref.read(onboardingProvider.notifier).setGender('male'),
              ),
              const SizedBox(width: 12),
              _GenderChip(
                label: l10n.female,
                selected: state.gender == 'female',
                onTap: () => ref.read(onboardingProvider.notifier).setGender('female'),
              ),
            ]),
            const SizedBox(height: 20),

            // Height
            TextFormField(
              controller: heightCtrl,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: '${l10n.height} (${l10n.cm})',
                prefixIcon: const Icon(Icons.height),
              ),
              validator: Validators.validateHeight,
            ),
            const SizedBox(height: 14),

            // Weight
            TextFormField(
              controller: weightCtrl,
              keyboardType: const TextInputType.numberWithOptions(decimal: true),
              decoration: InputDecoration(
                labelText: '${l10n.weight} (${l10n.kg})',
                prefixIcon: const Icon(Icons.monitor_weight_outlined),
              ),
              validator: Validators.validateWeight,
            ),

            const Spacer(),
            Row(children: [
              Expanded(child: OutlinedButton(onPressed: onBack, child: Text(l10n.back))),
              const SizedBox(width: 12),
              Expanded(child: ElevatedButton(onPressed: onNext, child: Text(l10n.next))),
            ]),
          ],
        ),
      ),
    );
  }
}

// ── Activity Level Page ───────────────────────────────────────────────────────

class _ActivityPage extends StatelessWidget {
  final String selected;
  final void Function(String) onSelected;
  final VoidCallback onNext;
  final VoidCallback onBack;

  const _ActivityPage({
    required this.selected,
    required this.onSelected,
    required this.onNext,
    required this.onBack,
  });

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, _) {
      final l10n = ref.watch(appStringsProvider);
      final options = [
        ('sedentary', l10n.sedentary, 'Little or no exercise', Icons.chair),
        ('lightly_active', l10n.lightlyActive, '1-3 days/week', Icons.directions_walk),
        ('moderately_active', l10n.moderatelyActive, '3-5 days/week', Icons.directions_run),
        ('very_active', l10n.veryActive, '6-7 days/week', Icons.fitness_center),
        ('extra_active', l10n.extraActive, 'Physical job + exercise', Icons.sports),
      ];

      return Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(l10n.activityLevel,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 4),
            Text('${l10n.step} 3 ${l10n.ofWord} 4',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.primary)),
            const SizedBox(height: 20),
            Expanded(
              child: ListView(
                children: options.map((o) => _OptionTile(
                  value: o.$1, label: o.$2, subtitle: o.$3, icon: o.$4,
                  isSelected: selected == o.$1,
                  onTap: () => onSelected(o.$1),
                )).toList(),
              ),
            ),
            Row(children: [
              Expanded(child: OutlinedButton(onPressed: onBack, child: Text(l10n.back))),
              const SizedBox(width: 12),
              Expanded(child: ElevatedButton(onPressed: onNext, child: Text(l10n.next))),
            ]),
          ],
        ),
      );
    });
  }
}

// ── Fitness Goal Page ─────────────────────────────────────────────────────────

class _GoalPage extends StatelessWidget {
  final String selected;
  final void Function(String) onSelected;
  final VoidCallback onNext;
  final VoidCallback onBack;

  const _GoalPage({
    required this.selected,
    required this.onSelected,
    required this.onNext,
    required this.onBack,
  });

  @override
  Widget build(BuildContext context) {
    return Consumer(builder: (context, ref, _) {
      final l10n = ref.watch(appStringsProvider);
      final options = [
        ('lose_weight', l10n.loseWeight, 'Calorie deficit approach', Icons.trending_down),
        ('healthy_fat_loss', l10n.healthyFatLoss, 'Preserve muscle, lose fat', Icons.local_fire_department),
        ('maintain', l10n.maintain, 'Balance intake & output', Icons.balance),
        ('gain_muscle', l10n.gainMuscle, 'Build lean mass', Icons.fitness_center),
      ];

      return Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(l10n.fitnessGoal,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 4),
            Text('${l10n.step} 4 ${l10n.ofWord} 4',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: AppColors.primary)),
            const SizedBox(height: 20),
            Expanded(
              child: ListView(
                children: options.map((o) => _OptionTile(
                  value: o.$1, label: o.$2, subtitle: o.$3, icon: o.$4,
                  isSelected: selected == o.$1,
                  onTap: () => onSelected(o.$1),
                )).toList(),
              ),
            ),
            Row(children: [
              Expanded(child: OutlinedButton(onPressed: onBack, child: Text(l10n.back))),
              const SizedBox(width: 12),
              Expanded(child: ElevatedButton(onPressed: onNext, child: Text(l10n.next))),
            ]),
          ],
        ),
      );
    });
  }
}


// ── Shared Widgets ────────────────────────────────────────────────────────────

class _GenderChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;
  const _GenderChip({required this.label, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            color: selected ? AppColors.primary : Colors.transparent,
            border: Border.all(
              color: selected ? AppColors.primary : AppColors.primary.withOpacity(0.3),
              width: 2,
            ),
            borderRadius: BorderRadius.circular(14),
          ),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                color: selected ? Colors.white : AppColors.primary,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _OptionTile extends StatelessWidget {
  final String value, label, subtitle;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;

  const _OptionTile({
    required this.value,
    required this.label,
    required this.subtitle,
    required this.icon,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected
              ? AppColors.primary.withOpacity(0.1)
              : Theme.of(context).cardTheme.color,
          border: Border.all(
            color: isSelected ? AppColors.primary : Colors.transparent,
            width: 2,
          ),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: isSelected ? AppColors.primary : AppColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: isSelected ? Colors.white : AppColors.primary, size: 20),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w600)),
                  Text(subtitle, style: Theme.of(context).textTheme.bodySmall),
                ],
              ),
            ),
            if (isSelected) const Icon(Icons.check_circle, color: AppColors.primary),
          ],
        ),
      ),
    );
  }
}

class _AvatarCircle extends StatelessWidget {
  final String? imagePath;
  final double size;
  final bool isLoading;
  const _AvatarCircle({this.imagePath, required this.size, this.isLoading = false});

  @override
  Widget build(BuildContext context) {
    final hasImage = imagePath != null && File(imagePath!).existsSync();
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AppColors.primary.withOpacity(0.1),
        border: Border.all(color: AppColors.primary.withOpacity(0.3), width: 2),
      ),
      child: ClipOval(
        child: isLoading
            ? const Center(
                child: SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
                ),
              )
            : hasImage
                ? Image.file(File(imagePath!),
                    fit: BoxFit.cover, width: size, height: size,
                    errorBuilder: (_, __, ___) => _icon())
                : _icon(),
      ),
    );
  }

  Widget _icon() => const Icon(Icons.person, size: 48, color: AppColors.primary);
}

class _PhotoSourceSheet extends StatelessWidget {
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
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
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
