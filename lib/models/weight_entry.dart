import 'package:hive/hive.dart';

/// A single weight measurement in the user's weight/BMI history.
///
/// Introduced with the long-term data lifecycle system (v1.2). The adapter is
/// hand-written (no build_runner step required) so the model can ship without
/// regenerating `.g.dart` files. TypeId 5 — must stay unique across the app.
@HiveType(typeId: 5)
class WeightEntry extends HiveObject {
  @HiveField(0)
  String id;

  @HiveField(1)
  DateTime recordedAt;

  @HiveField(2)
  double weightKg;

  /// Height at time of measurement — lets BMI be reconstructed historically
  /// even if the user later changes their height.
  @HiveField(3)
  double heightCm;

  @HiveField(4)
  String? note;

  WeightEntry({
    required this.id,
    required this.recordedAt,
    required this.weightKg,
    required this.heightCm,
    this.note,
  });

  /// 'yyyy_mm_dd' — used for de-duplication (one canonical entry per day).
  String get dateKey =>
      '${recordedAt.year}_${recordedAt.month.toString().padLeft(2, '0')}_${recordedAt.day.toString().padLeft(2, '0')}';

  double get bmi {
    if (heightCm <= 0) return 0;
    final m = heightCm / 100.0;
    return weightKg / (m * m);
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'recordedAt': recordedAt.toIso8601String(),
        'weightKg': weightKg,
        'heightCm': heightCm,
        if (note != null) 'note': note,
      };

  factory WeightEntry.fromJson(Map<String, dynamic> m) => WeightEntry(
        id: (m['id'] as String?) ?? '${m['recordedAt']}',
        recordedAt:
            DateTime.tryParse((m['recordedAt'] as String?) ?? '') ?? DateTime.now(),
        weightKg: (m['weightKg'] as num?)?.toDouble() ?? 0,
        heightCm: (m['heightCm'] as num?)?.toDouble() ?? 0,
        note: m['note'] as String?,
      );
}

class WeightEntryAdapter extends TypeAdapter<WeightEntry> {
  @override
  final int typeId = 5;

  @override
  WeightEntry read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return WeightEntry(
      id: fields[0] as String,
      recordedAt: fields[1] as DateTime,
      weightKg: (fields[2] as num).toDouble(),
      heightCm: (fields[3] as num).toDouble(),
      note: fields[4] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, WeightEntry obj) {
    writer
      ..writeByte(5)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.recordedAt)
      ..writeByte(2)
      ..write(obj.weightKg)
      ..writeByte(3)
      ..write(obj.heightCm)
      ..writeByte(4)
      ..write(obj.note);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WeightEntryAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
