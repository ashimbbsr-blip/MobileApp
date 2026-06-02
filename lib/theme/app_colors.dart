import 'package:flutter/material.dart';

class AppColors {
  // Brand colors
  static const Color primary = Color(0xFF2ECC71);
  static const Color primaryDark = Color(0xFF27AE60);
  static const Color secondary = Color(0xFF3498DB);
  static const Color accent = Color(0xFF9B59B6);

  // Nutrition colors
  static const Color calories = Color(0xFFE74C3C);
  static const Color protein = Color(0xFF3498DB);
  static const Color carbs = Color(0xFFF39C12);
  static const Color fat = Color(0xFFE67E22);
  static const Color fiber = Color(0xFF2ECC71);
  static const Color water = Color(0xFF1ABC9C);
  static const Color alcohol = Color(0xFFAB8B2A); // deep amber — distinct from fat's orange

  // Micronutrient colors
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
  static const Color lightBackground = Color(0xFFF8FAF9);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightCard = Color(0xFFFFFFFF);
  static const Color lightText = Color(0xFF1A1A2E);
  static const Color lightTextSecondary = Color(0xFF6B7280);
  static const Color lightDivider = Color(0xFFE5E7EB);

  // Dark theme
  static const Color darkBackground = Color(0xFF0F1923);
  static const Color darkSurface = Color(0xFF1A2535);
  static const Color darkCard = Color(0xFF1E2D3D);
  static const Color darkText = Color(0xFFF1F5F9);
  static const Color darkTextSecondary = Color(0xFF94A3B8);
  static const Color darkDivider = Color(0xFF2D3748);

  // Gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF2ECC71), Color(0xFF27AE60)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );

  static const LinearGradient splashGradient = LinearGradient(
    colors: [Color(0xFF0F1923), Color(0xFF1A2535), Color(0xFF1E3A5F)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );

  static const LinearGradient cardGradient = LinearGradient(
    colors: [Color(0xFF2ECC71), Color(0xFF1ABC9C)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
}
