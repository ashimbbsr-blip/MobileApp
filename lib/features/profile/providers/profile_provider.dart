import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import '../../../models/user_profile.dart';
import '../../../models/weight_entry.dart';
import '../../../storage/hive_storage.dart';

class ProfileState {
  final UserProfile? profile;
  final bool isSaving;
  final bool isSaved;
  final String? error;

  const ProfileState({
    this.profile,
    this.isSaving = false,
    this.isSaved = false,
    this.error,
  });

  ProfileState copyWith({
    UserProfile? profile,
    bool? isSaving,
    bool? isSaved,
    String? error,
    bool clearError = false,
  }) {
    return ProfileState(
      profile: profile ?? this.profile,
      isSaving: isSaving ?? this.isSaving,
      isSaved: isSaved ?? this.isSaved,
      error: clearError ? null : (error ?? this.error),
    );
  }
}

class ProfileNotifier extends StateNotifier<ProfileState> {
  ProfileNotifier() : super(const ProfileState()) {
    _load();
  }

  void _load() {
    state = state.copyWith(profile: HiveStorage.getUserProfile());
  }

  void refresh() => _load();

  Future<String?> pickImage() async {
    try {
      final picker = ImagePicker();
      final XFile? picked = await picker.pickImage(
        source: ImageSource.gallery,
        maxWidth: 800,
        maxHeight: 800,
        imageQuality: 85,
      );
      if (picked == null) return null;
      final dir = await getApplicationDocumentsDirectory();
      final target = File('${dir.path}/profile_avatar.jpg');
      await File(picked.path).copy(target.path);
      return target.path;
    } catch (_) {
      return null;
    }
  }

  void updateProfileImagePath(String? path) {
    if (state.profile == null) return;
    state = state.copyWith(
      profile: state.profile!.copyWith(
        profileImagePath: path,
        clearProfileImage: path == null,
      ),
      isSaved: false,
    );
  }

  Future<bool> saveProfile({
    required String fullName,
    required String email,
    required DateTime? dateOfBirth,
    required String gender,
    required double heightCm,
    required double weightKg,
    required String activityLevel,
    required String fitnessGoal,
    String? pregnancyStatus,
    bool clearPregnancyStatus = false,
  }) async {
    if (state.profile == null) return false;
    state = state.copyWith(isSaving: true, isSaved: false, clearError: true);
    try {
      final updated = state.profile!.copyWith(
        fullName: fullName.trim().isEmpty ? null : fullName.trim(),
        email: email.trim().isEmpty ? null : email.trim(),
        dateOfBirth: dateOfBirth,
        gender: gender,
        heightCm: heightCm,
        weightKg: weightKg,
        activityLevel: activityLevel,
        fitnessGoal: fitnessGoal,
        age: dateOfBirth != null ? _ageFromDob(dateOfBirth) : state.profile!.age,
        pregnancyStatus: pregnancyStatus,
        clearPregnancyStatus: clearPregnancyStatus,
      );
      await HiveStorage.saveUserProfile(updated);
      // Capture the weight into the weight/BMI history (one canonical entry per
      // day — re-saving the same day updates it). Feeds the long-term trend,
      // weight charts, and the XLSX/CSV weight sheets.
      await _recordWeight(weightKg, heightCm);
      state = state.copyWith(profile: updated, isSaving: false, isSaved: true);
      return true;
    } catch (e) {
      state = state.copyWith(isSaving: false, error: e.toString());
      return false;
    }
  }

  Future<void> _recordWeight(double weightKg, double heightCm) async {
    if (weightKg <= 0) return;
    final now = DateTime.now();
    final dateKey =
        '${now.year}_${now.month.toString().padLeft(2, '0')}_${now.day.toString().padLeft(2, '0')}';
    await HiveStorage.saveWeightEntry(WeightEntry(
      id: dateKey,
      recordedAt: now,
      weightKg: weightKg,
      heightCm: heightCm,
    ));
  }

  int _ageFromDob(DateTime dob) {
    final today = DateTime.now();
    int age = today.year - dob.year;
    if (today.month < dob.month ||
        (today.month == dob.month && today.day < dob.day)) { age--; }
    return age;
  }
}

final profileProvider =
    StateNotifierProvider<ProfileNotifier, ProfileState>((ref) => ProfileNotifier());
