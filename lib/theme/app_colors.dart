import 'package:flutter/material.dart';

class AppColors {
  // Brand colors — Blue/Teal theme
  static const Color primary = Color(0xFF2979FF);
  static const Color primaryDark = Color(0xFF1565C0);
  static const Color secondary = Color(0xFF00BCD4);
  static const Color accent = Color(0xFF7C4DFF);

  // Nutrition macro colors (semantic — unchanged)
  static const Color calories = Color(0xFFFF5252);
  static const Color protein = Color(0xFF29B6F6);
  static const Color carbs = Color(0xFFFFA726);
  static const Color fat = Color(0xFFFF7043);
  static const Color fiber = Color(0xFF66BB6A);
  static const Color water = Color(0xFF26C6DA);
  static const Color alcohol = Color(0xFFAB8B2A);

  // Micronutrient colors (semantic — unchanged)
  static const Color vitaminA = Color(0xFFFF6B6B);
  static const Color vitaminB = Color(0xFFFFE66D);
  static const Color vitaminC = Color(0xFF4ECDC4);
  static const Color vitaminD = Color(0xFFFFD93D);
  static const Color vitaminE = Color(0xFF6BCB77);
  static const Color calcium = Color(0xFF4D96FF);
  static const Color iron = Color(0xFFFF6B6B);
  static const Color magnesium = Color(0xFF95E1D3);
  static const Color potassium = Color(0xFFF8B195);
  static const Color zinc = Color(0xFFA8E6CF);

  // Light theme
  static const Color lightBackground = Color(0xFFF0F4FF);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightCard = Color(0xFFFFFFFF);
  static const Color lightText = Color(0xFF0D1B3E);
  static const Color lightTextSecondary = Color(0xFF5A6A8A);
  static const Color lightDivider = Color(0xFFDDE3F0);

  // Dark theme
  static const Color darkBackground = Color(0xFF050D1A);
  static const Color darkSurface = Color(0xFF0F1728);
  static const Color darkCard = Color(0xFF111B2E);
  static const Color darkCardAlt = Color(0xFF162035);
  static const Color darkText = Color(0xFFE8F0FE);
  static const Color darkTextSecondary = Color(0xFF90A4AE);
  static const Color darkDivider = Color(0xFF1E2D45);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF2979FF), Color(0xFF00BCD4)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient splashGradient = LinearGradient(
    colors: [Color(0xFF050D1A), Color(0xFF0F1728), Color(0xFF162035)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient cardGradient = LinearGradient(
    colors: [Color(0xFF2979FF), Color(0xFF00BCD4)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient headerGradient = LinearGradient(
    colors: [Color(0xFF0F1728), Color(0xFF162035)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
}
