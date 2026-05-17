// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'monthly_summary.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class MonthlySummaryAdapter extends TypeAdapter<MonthlySummary> {
  @override
  final int typeId = 3;

  @override
  MonthlySummary read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return MonthlySummary(
      year: fields[0] as int,
      month: fields[1] as int,
      avgCalories: fields[2] as double,
      avgProtein: fields[3] as double,
      avgCarbs: fields[4] as double,
      avgFat: fields[5] as double,
      avgFiber: fields[6] as double,
      consistencyScore: fields[7] as double,
      daysLogged: fields[8] as int,
    );
  }

  @override
  void write(BinaryWriter writer, MonthlySummary obj) {
    writer
      ..writeByte(9)
      ..writeByte(0)
      ..write(obj.year)
      ..writeByte(1)
      ..write(obj.month)
      ..writeByte(2)
      ..write(obj.avgCalories)
      ..writeByte(3)
      ..write(obj.avgProtein)
      ..writeByte(4)
      ..write(obj.avgCarbs)
      ..writeByte(5)
      ..write(obj.avgFat)
      ..writeByte(6)
      ..write(obj.avgFiber)
      ..writeByte(7)
      ..write(obj.consistencyScore)
      ..writeByte(8)
      ..write(obj.daysLogged);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is MonthlySummaryAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
