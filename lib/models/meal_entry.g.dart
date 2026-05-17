// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'meal_entry.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class MealEntryAdapter extends TypeAdapter<MealEntry> {
  @override
  final int typeId = 2;

  @override
  MealEntry read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return MealEntry(
      id: fields[0] as String,
      mealType: fields[1] as String,
      foodItem: fields[2] as FoodItem,
      quantityG: fields[3] as double,
      loggedAt: fields[4] as DateTime,
      dateKey: fields[5] as String,
    );
  }

  @override
  void write(BinaryWriter writer, MealEntry obj) {
    writer
      ..writeByte(6)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.mealType)
      ..writeByte(2)
      ..write(obj.foodItem)
      ..writeByte(3)
      ..write(obj.quantityG)
      ..writeByte(4)
      ..write(obj.loggedAt)
      ..writeByte(5)
      ..write(obj.dateKey);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is MealEntryAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
