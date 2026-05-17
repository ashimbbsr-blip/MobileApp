// GENERATED CODE - DO NOT MODIFY BY HAND
part of 'legal_acceptance.dart';

class LegalAcceptanceAdapter extends TypeAdapter<LegalAcceptance> {
  @override
  final int typeId = 4;

  @override
  LegalAcceptance read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return LegalAcceptance(
      acceptedAt: fields[0] as DateTime,
      policyVersion: fields[1] as String,
      appVersion: fields[2] as String,
      termsAccepted: fields[3] as bool? ?? true,
      healthDisclaimerAccepted: fields[4] as bool? ?? true,
    );
  }

  @override
  void write(BinaryWriter writer, LegalAcceptance obj) {
    writer
      ..writeByte(5)
      ..writeByte(0)
      ..write(obj.acceptedAt)
      ..writeByte(1)
      ..write(obj.policyVersion)
      ..writeByte(2)
      ..write(obj.appVersion)
      ..writeByte(3)
      ..write(obj.termsAccepted)
      ..writeByte(4)
      ..write(obj.healthDisclaimerAccepted);
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is LegalAcceptanceAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;

  @override
  int get hashCode => typeId.hashCode;
}
