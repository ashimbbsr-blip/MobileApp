import 'package:hive/hive.dart';

/// Highest level of compression — one record per calendar year.
///
/// Produced by Archive Level 3 (monthly summaries older than 5 years are
/// collapsed into a yearly record). Preserves the long-term health trend while
/// occupying a few dozen bytes per year. TypeId 7.
@HiveType(typeId: 7)
class YearlySummary extends HiveObject {
  @HiveField(0)
  int year;

  @HiveField(1)
  double avgKcal;

  @HiveField(2)
  double avgProtein;

  @HiveField(3)
  double avgCarbs;

  @HiveField(4)
  double avgFat;

  @HiveField(5)
  double avgWater;

  @HiveField(6)
  double avgScore;

  /// Net weight change across the year (kg). Positive = gain.
  @HiveField(7)
  double weightChange;

  @HiveField(8)
  int daysLogged;

  YearlySummary({
    required this.year,
    required this.avgKcal,
    required this.avgProtein,
    required this.avgCarbs,
    required this.avgFat,
    required this.avgWater,
    required this.avgScore,
    required this.weightChange,
    required this.daysLogged,
  });

  @override
  String get key => year.toString();

  Map<String, dynamic> toJson() => {
        'year': year,
        'avgKcal': _r(avgKcal),
        'avgProtein': _r(avgProtein),
        'avgCarbs': _r(avgCarbs),
        'avgFat': _r(avgFat),
        'avgWater': _r(avgWater),
        'healthScore': _r(avgScore),
        'weightChange': _r(weightChange),
        'daysLogged': daysLogged,
      };

  factory YearlySummary.fromJson(Map<String, dynamic> m) => YearlySummary(
        year: (m['year'] as num?)?.toInt() ?? 0,
        avgKcal: (m['avgKcal'] as num?)?.toDouble() ?? 0,
        avgProtein: (m['avgProtein'] as num?)?.toDouble() ?? 0,
        avgCarbs: (m['avgCarbs'] as num?)?.toDouble() ?? 0,
        avgFat: (m['avgFat'] as num?)?.toDouble() ?? 0,
        avgWater: (m['avgWater'] as num?)?.toDouble() ?? 0,
        avgScore: (m['healthScore'] as num?)?.toDouble() ?? 0,
        weightChange: (m['weightChange'] as num?)?.toDouble() ?? 0,
        daysLogged: (m['daysLogged'] as num?)?.toInt() ?? 0,
      );

  static double _r(double v) => (v * 10).roundToDouble() / 10;
}

class YearlySummaryAdapter extends TypeAdapter<YearlySummary> {
  @override
  final int typeId = 7;

  @override
  YearlySummary read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return YearlySummary(
      year: (fields[0] as num).toInt(),
      avgKcal: (fields[1] as num).toDouble(),
      avgProtein: (fields[2] as num).toDouble(),
      avgCarbs: (fields[3] as num).toDouble(),
      avgFat: (fields[4] as num).toDouble(),
      avgWater: (fields[5] as num).toDouble(),
      avgScore: (fields[6] as num).toDouble(),
      weightChange: (fields[7] as num).toDouble(),
      daysLogged: (fields[8] as num).toInt(),
    );
  }

  @override
  void write(BinaryWriter writer, YearlySummary obj) {
    writer
      ..writeByte(9)
      ..writeByte(0)
      ..write(obj.year)
      ..writeByte(1)
      ..write(obj.avgKcal)
      ..writeByte(2)
      ..write(obj.avgProtein)
      ..writeByte(3)
      ..write(obj.avgCarbs)
      ..writeByte(4)
      ..write(obj.avgFat)
      ..writeByte(5)
      ..write(obj.avgWater)
      ..writeByte(6)
      ..write(obj.avgScore)
      ..writeByte(7)
      ..write(obj.weightChange)
      ..writeByte(8)
      ..write(obj.daysLogged);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is YearlySummaryAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
