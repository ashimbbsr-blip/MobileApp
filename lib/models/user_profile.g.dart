// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_profile.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class UserProfileAdapter extends TypeAdapter<UserProfile> {
  @override
  final int typeId = 0;

  @override
  UserProfile read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return UserProfile(
      id: fields[0] as String,
      age: fields[1] as int,
      gender: fields[2] as String,
      heightCm: fields[3] as double,
      weightKg: fields[4] as double,
      activityLevel: fields[5] as String,
      fitnessGoal: fields[6] as String,
      createdAt: fields[7] as DateTime,
      fullName: fields[8] as String?,
      dateOfBirth: fields[9] as DateTime?,
      profileImagePath: fields[10] as String?,
      email: fields[11] as String?,
      pregnancyStatus: fields[12] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, UserProfile obj) {
    writer
      ..writeByte(13)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.age)
      ..writeByte(2)
      ..write(obj.gender)
      ..writeByte(3)
      ..write(obj.heightCm)
      ..writeByte(4)
      ..write(obj.weightKg)
      ..writeByte(5)
      ..write(obj.activityLevel)
      ..writeByte(6)
      ..write(obj.fitnessGoal)
      ..writeByte(7)
      ..write(obj.createdAt)
      ..writeByte(8)
      ..write(obj.fullName)
      ..writeByte(9)
      ..write(obj.dateOfBirth)
      ..writeByte(10)
      ..write(obj.profileImagePath)
      ..writeByte(11)
      ..write(obj.email)
      ..writeByte(12)
      ..write(obj.pregnancyStatus);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is UserProfileAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
