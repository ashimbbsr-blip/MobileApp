import 'package:hive/hive.dart';

part 'user_profile.g.dart';

@HiveType(typeId: 0)
class UserProfile extends HiveObject {
  @HiveField(0)
  String id;

  @HiveField(1)
  int age;

  @HiveField(2)
  String gender;

  @HiveField(3)
  double heightCm;

  @HiveField(4)
  double weightKg;

  @HiveField(5)
  String activityLevel;

  @HiveField(6)
  String fitnessGoal;

  @HiveField(7)
  DateTime createdAt;

  @HiveField(8)
  String? fullName;

  @HiveField(9)
  DateTime? dateOfBirth;

  @HiveField(10)
  String? profileImagePath;

  @HiveField(11)
  String? email;

  @HiveField(12)
  String? pregnancyStatus; // null | 'pregnant_1st' | 'pregnant_2nd' | 'pregnant_3rd' | 'lactating'

  UserProfile({
    required this.id,
    required this.age,
    required this.gender,
    required this.heightCm,
    required this.weightKg,
    required this.activityLevel,
    required this.fitnessGoal,
    required this.createdAt,
    this.fullName,
    this.dateOfBirth,
    this.profileImagePath,
    this.email,
    this.pregnancyStatus,
  });

  int get computedAge {
    if (dateOfBirth != null) {
      final today = DateTime.now();
      int years = today.year - dateOfBirth!.year;
      if (today.month < dateOfBirth!.month ||
          (today.month == dateOfBirth!.month && today.day < dateOfBirth!.day)) {
        years--;
      }
      return years;
    }
    return age;
  }

  double get bmi => weightKg / ((heightCm / 100) * (heightCm / 100));

  // WHO 2004 / ICMR South Asian cutoffs: Normal < 23, Overweight < 27.5
  String get bmiCategory {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 23.0) return 'Normal';
    if (bmi < 27.5) return 'Overweight';
    return 'Obese';
  }

  String get displayName => (fullName != null && fullName!.isNotEmpty) ? fullName! : 'User';

  UserProfile copyWith({
    int? age,
    String? gender,
    double? heightCm,
    double? weightKg,
    String? activityLevel,
    String? fitnessGoal,
    String? fullName,
    DateTime? dateOfBirth,
    String? profileImagePath,
    String? email,
    String? pregnancyStatus,
    bool clearProfileImage = false,
    bool clearPregnancyStatus = false,
  }) {
    return UserProfile(
      id: id,
      age: age ?? this.age,
      gender: gender ?? this.gender,
      heightCm: heightCm ?? this.heightCm,
      weightKg: weightKg ?? this.weightKg,
      activityLevel: activityLevel ?? this.activityLevel,
      fitnessGoal: fitnessGoal ?? this.fitnessGoal,
      createdAt: createdAt,
      fullName: fullName ?? this.fullName,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      profileImagePath: clearProfileImage ? null : (profileImagePath ?? this.profileImagePath),
      email: email ?? this.email,
      pregnancyStatus: clearPregnancyStatus ? null : (pregnancyStatus ?? this.pregnancyStatus),
    );
  }
}
