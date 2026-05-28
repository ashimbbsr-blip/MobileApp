import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:uuid/uuid.dart';
import '../../../models/user_profile.dart';
import '../../../storage/hive_storage.dart';

class OnboardingState {
  final int currentStep;
  final String fullName;
  final String email;
  final DateTime? dateOfBirth;
  final String? profileImagePath;
  final String gender;
  final double heightCm;
  final double weightKg;
  final String activityLevel;
  final String fitnessGoal;
  final String? pregnancyStatus;
  final bool isComplete;

  const OnboardingState({
    this.currentStep = 0,
    this.fullName = '',
    this.email = '',
    this.dateOfBirth,
    this.profileImagePath,
    this.gender = 'male',
    this.heightCm = 170,
    this.weightKg = 70,
    this.activityLevel = 'moderately_active',
    this.fitnessGoal = 'healthy_fat_loss',
    this.pregnancyStatus,
    this.isComplete = false,
  });

  OnboardingState copyWith({
    int? currentStep,
    String? fullName,
    String? email,
    DateTime? dateOfBirth,
    String? profileImagePath,
    String? gender,
    double? heightCm,
    double? weightKg,
    String? activityLevel,
    String? fitnessGoal,
    String? pregnancyStatus,
    bool? isComplete,
    bool clearProfileImage = false,
    bool clearPregnancyStatus = false,
  }) {
    return OnboardingState(
      currentStep: currentStep ?? this.currentStep,
      fullName: fullName ?? this.fullName,
      email: email ?? this.email,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      profileImagePath: clearProfileImage ? null : (profileImagePath ?? this.profileImagePath),
      gender: gender ?? this.gender,
      heightCm: heightCm ?? this.heightCm,
      weightKg: weightKg ?? this.weightKg,
      activityLevel: activityLevel ?? this.activityLevel,
      fitnessGoal: fitnessGoal ?? this.fitnessGoal,
      pregnancyStatus: clearPregnancyStatus ? null : (pregnancyStatus ?? this.pregnancyStatus),
      isComplete: isComplete ?? this.isComplete,
    );
  }
}

class OnboardingNotifier extends StateNotifier<OnboardingState> {
  OnboardingNotifier() : super(const OnboardingState());

  void goToStep(int step) => state = state.copyWith(currentStep: step);
  void nextStep() => state = state.copyWith(currentStep: state.currentStep + 1);
  void previousStep() => state = state.copyWith(currentStep: state.currentStep - 1);

  void setFullName(String name) => state = state.copyWith(fullName: name);
  void setEmail(String email) => state = state.copyWith(email: email);
  void setDateOfBirth(DateTime dob) => state = state.copyWith(dateOfBirth: dob);
  void setGender(String gender) => state = state.copyWith(gender: gender);
  void setHeight(double height) => state = state.copyWith(heightCm: height);
  void setWeight(double weight) => state = state.copyWith(weightKg: weight);
  void setActivityLevel(String level) => state = state.copyWith(activityLevel: level);
  void setFitnessGoal(String goal) => state = state.copyWith(fitnessGoal: goal);
  void setPregnancyStatus(String? status) => state = status == null
      ? state.copyWith(clearPregnancyStatus: true)
      : state.copyWith(pregnancyStatus: status);

  Future<void> pickAndSaveProfileImage(ImageSource source) async {
    try {
      final picker = ImagePicker();
      final XFile? picked = await picker.pickImage(
        source: source,
        maxWidth: 800,
        maxHeight: 800,
        imageQuality: 90,
      );
      if (picked == null) return;

      final bytes = await FlutterImageCompress.compressWithFile(
        picked.path,
        minWidth: 200,
        minHeight: 200,
        quality: 85,
        keepExif: false,
      );
      if (bytes == null) return;

      final dir = await getApplicationDocumentsDirectory();
      final target = File('${dir.path}/profile_avatar.jpg');
      await target.writeAsBytes(bytes);
      state = state.copyWith(profileImagePath: target.path);
    } catch (_) {
      // Silently ignore — photo is optional
    }
  }

  void removeProfileImage() => state = state.copyWith(clearProfileImage: true);

  Future<void> complete() async {
    final dob = state.dateOfBirth;
    final age = dob != null ? _ageFromDob(dob) : 25;

    final profile = UserProfile(
      id: const Uuid().v4(),
      age: age,
      gender: state.gender,
      heightCm: state.heightCm,
      weightKg: state.weightKg,
      activityLevel: state.activityLevel,
      fitnessGoal: state.fitnessGoal,
      createdAt: DateTime.now(),
      fullName: state.fullName.trim().isEmpty ? null : state.fullName.trim(),
      email: state.email.trim().isEmpty ? null : state.email.trim(),
      dateOfBirth: state.dateOfBirth,
      profileImagePath: state.profileImagePath,
      pregnancyStatus: state.gender == 'female' ? state.pregnancyStatus : null,
    );
    await HiveStorage.saveUserProfile(profile);
    await HiveStorage.setOnboardingDone();
    state = state.copyWith(isComplete: true);
  }

  int _ageFromDob(DateTime dob) {
    final today = DateTime.now();
    int age = today.year - dob.year;
    if (today.month < dob.month ||
        (today.month == dob.month && today.day < dob.day)) {
      age--;
    }
    return age;
  }
}

final onboardingProvider =
    StateNotifierProvider<OnboardingNotifier, OnboardingState>(
  (ref) => OnboardingNotifier(),
);
