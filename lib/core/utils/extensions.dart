extension DoubleExt on double {
  String toNutritionString() => toStringAsFixed(1);
  String toCalorieString() => toStringAsFixed(0);
  double roundToDecimal(int places) {
    final factor = 10.0 * places;
    return (this * factor).round() / factor;
  }
}

extension IntExt on int {
  String toBengaliDigits() {
    const english = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
    const bengali = ['০', '১', '২', '৩', '৪', '৫', '৬', '৭', '৮', '৯'];
    String result = toString();
    for (int i = 0; i < english.length; i++) {
      result = result.replaceAll(english[i], bengali[i]);
    }
    return result;
  }
}

extension StringExt on String {
  String capitalize() {
    if (isEmpty) return this;
    return '${this[0].toUpperCase()}${substring(1)}';
  }
}

extension DateTimeExt on DateTime {
  String toLogKey() => '${year}_${month.toString().padLeft(2, '0')}_${day.toString().padLeft(2, '0')}';

  bool isSameDay(DateTime other) {
    return year == other.year && month == other.month && day == other.day;
  }
}
