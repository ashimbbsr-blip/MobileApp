import 'package:flutter/material.dart';

String mealTypeForNow() {
  final h = TimeOfDay.now().hour;
  if (h >= 6 && h < 10) return 'breakfast';
  if (h >= 10 && h < 15) return 'lunch';
  if (h >= 15 && h < 18) return 'snack';
  if (h >= 18 && h < 22) return 'dinner';
  return 'snack';
}
