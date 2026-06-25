import 'package:hive/hive.dart';

/// Compressed, meal-free representation of a single day's nutrition.
///
/// Produced by Archive Level 1 (meals older than 12 months are collapsed into
/// one of these and the underlying [MealEntry] records are deleted). Also used
/// as the canonical row shape for daily CSV/XLSX export. TypeId 6.
@HiveType(typeId: 6)
class DailySummary extends HiveObject {
  /// 'yyyy_mm_dd' — primary key in the daily-summary box.
  @HiveField(0)
  String dateKey;

  @HiveField(1)
  DateTime date;

  @HiveField(2)
  double kcal;

  @HiveField(3)
  double protein;

  @HiveField(4)
  double carbs;

  @HiveField(5)
  double fat;

  @HiveField(6)
  double fiber;

  @HiveField(7)
  double waterMl;

  /// Daily health score 0–100 (derived from goal completion + balance).
  @HiveField(8)
  double score;

  @HiveField(9)
  int mealCount;

  DailySummary({
    required this.dateKey,
    required this.date,
    required this.kcal,
    required this.protein,
    required this.carbs,
    required this.fat,
    required this.fiber,
    required this.waterMl,
    required this.score,
    required this.mealCount,
  });

  int get year => date.year;
  int get month => date.month;
  String get monthKey => '${date.year}_${date.month.toString().padLeft(2, '0')}';

  Map<String, dynamic> toJson() => {
        'date': dateKey,
        'kcal': _r(kcal),
        'protein': _r(protein),
        'carbs': _r(carbs),
        'fat': _r(fat),
        'fiber': _r(fiber),
        'waterMl': _r(waterMl),
        'score': _r(score),
        'meals': mealCount,
      };

  factory DailySummary.fromJson(Map<String, dynamic> m) {
    final key = (m['date'] as String?) ?? '';
    return DailySummary(
      dateKey: key,
      date: _parseKey(key),
      kcal: (m['kcal'] as num?)?.toDouble() ?? 0,
      protein: (m['protein'] as num?)?.toDouble() ?? 0,
      carbs: (m['carbs'] as num?)?.toDouble() ?? 0,
      fat: (m['fat'] as num?)?.toDouble() ?? 0,
      fiber: (m['fiber'] as num?)?.toDouble() ?? 0,
      waterMl: (m['waterMl'] as num?)?.toDouble() ?? 0,
      score: (m['score'] as num?)?.toDouble() ?? 0,
      mealCount: (m['meals'] as num?)?.toInt() ?? 0,
    );
  }

  static double _r(double v) => (v * 10).roundToDouble() / 10;

  static DateTime _parseKey(String key) {
    final p = key.split('_');
    if (p.length == 3) {
      return DateTime(
          int.tryParse(p[0]) ?? 2000, int.tryParse(p[1]) ?? 1, int.tryParse(p[2]) ?? 1);
    }
    return DateTime(2000);
  }
}

class DailySummaryAdapter extends TypeAdapter<DailySummary> {
  @override
  final int typeId = 6;

  @override
  DailySummary read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return DailySummary(
      dateKey: fields[0] as String,
      date: fields[1] as DateTime,
      kcal: (fields[2] as num).toDouble(),
      protein: (fields[3] as num).toDouble(),
      carbs: (fields[4] as num).toDouble(),
      fat: (fields[5] as num).toDouble(),
      fiber: (fields[6] as num).toDouble(),
      waterMl: (fields[7] as num).toDouble(),
      score: (fields[8] as num).toDouble(),
      mealCount: (fields[9] as num).toInt(),
    );
  }

  @override
  void write(BinaryWriter writer, DailySummary obj) {
    writer
      ..writeByte(10)
      ..writeByte(0)
      ..write(obj.dateKey)
      ..writeByte(1)
      ..write(obj.date)
      ..writeByte(2)
      ..write(obj.kcal)
      ..writeByte(3)
      ..write(obj.protein)
      ..writeByte(4)
      ..write(obj.carbs)
      ..writeByte(5)
      ..write(obj.fat)
      ..writeByte(6)
      ..write(obj.fiber)
      ..writeByte(7)
      ..write(obj.waterMl)
      ..writeByte(8)
      ..write(obj.score)
      ..writeByte(9)
      ..write(obj.mealCount);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DailySummaryAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
