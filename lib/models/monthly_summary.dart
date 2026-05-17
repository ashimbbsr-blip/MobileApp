import 'package:hive/hive.dart';

part 'monthly_summary.g.dart';

@HiveType(typeId: 3)
class MonthlySummary extends HiveObject {
  @HiveField(0)
  int year;

  @HiveField(1)
  int month;

  @HiveField(2)
  double avgCalories;

  @HiveField(3)
  double avgProtein;

  @HiveField(4)
  double avgCarbs;

  @HiveField(5)
  double avgFat;

  @HiveField(6)
  double avgFiber;

  @HiveField(7)
  double consistencyScore;

  @HiveField(8)
  int daysLogged;

  MonthlySummary({
    required this.year,
    required this.month,
    required this.avgCalories,
    required this.avgProtein,
    required this.avgCarbs,
    required this.avgFat,
    required this.avgFiber,
    required this.consistencyScore,
    required this.daysLogged,
  });

  @override
  String get key => '${year}_${month.toString().padLeft(2, '0')}';

  String get label {
    const months = [
      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return '${months[month - 1]} $year';
  }
}
