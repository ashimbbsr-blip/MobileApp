// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'food_item.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class FoodItemAdapter extends TypeAdapter<FoodItem> {
  @override
  final int typeId = 1;

  @override
  FoodItem read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return FoodItem(
      id: fields[0] as String,
      name: fields[1] as String,
      brand: fields[2] as String?,
      servingSize: fields[3] as double,
      servingUnit: fields[4] as String,
      calories: fields[5] as double,
      proteinG: fields[6] as double,
      carbsG: fields[7] as double,
      fatG: fields[8] as double,
      fiberG: fields[9] as double,
      vitaminAMcg: fields[10] as double?,
      vitaminCMg: fields[11] as double?,
      vitaminDMcg: fields[12] as double?,
      calciumMg: fields[13] as double?,
      ironMg: fields[14] as double?,
      potassiumMg: fields[15] as double?,
      magnesiumMg: fields[16] as double?,
      zincMg: fields[17] as double?,
      usdaFdcId: fields[18] as String?,
      isCustom: fields[19] as bool,
      nameBn: fields[20] as String?,
      category: fields[21] as String?,
      source: fields[22] as String?,
      keywords: (fields[23] as List?)?.cast<String>(),
    );
  }

  @override
  void write(BinaryWriter writer, FoodItem obj) {
    writer
      ..writeByte(24)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.name)
      ..writeByte(2)
      ..write(obj.brand)
      ..writeByte(3)
      ..write(obj.servingSize)
      ..writeByte(4)
      ..write(obj.servingUnit)
      ..writeByte(5)
      ..write(obj.calories)
      ..writeByte(6)
      ..write(obj.proteinG)
      ..writeByte(7)
      ..write(obj.carbsG)
      ..writeByte(8)
      ..write(obj.fatG)
      ..writeByte(9)
      ..write(obj.fiberG)
      ..writeByte(10)
      ..write(obj.vitaminAMcg)
      ..writeByte(11)
      ..write(obj.vitaminCMg)
      ..writeByte(12)
      ..write(obj.vitaminDMcg)
      ..writeByte(13)
      ..write(obj.calciumMg)
      ..writeByte(14)
      ..write(obj.ironMg)
      ..writeByte(15)
      ..write(obj.potassiumMg)
      ..writeByte(16)
      ..write(obj.magnesiumMg)
      ..writeByte(17)
      ..write(obj.zincMg)
      ..writeByte(18)
      ..write(obj.usdaFdcId)
      ..writeByte(19)
      ..write(obj.isCustom)
      ..writeByte(20)
      ..write(obj.nameBn)
      ..writeByte(21)
      ..write(obj.category)
      ..writeByte(22)
      ..write(obj.source)
      ..writeByte(23)
      ..write(obj.keywords);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FoodItemAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
