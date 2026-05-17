import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'app_colors.dart';

class AppTheme {
  static ThemeData lightTheme(String language) {
    final textTheme = _buildTextTheme(language, Brightness.light);
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        brightness: Brightness.light,
        primary: AppColors.primary,
        secondary: AppColors.secondary,
        surface: AppColors.lightSurface,
        onSurface: AppColors.lightText,
      ),
      scaffoldBackgroundColor: AppColors.lightBackground,
      textTheme: textTheme,
      appBarTheme: AppBarTheme(
        backgroundColor: AppColors.lightSurface,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: textTheme.titleLarge?.copyWith(
          fontWeight: FontWeight.w600,
          color: AppColors.lightText,
        ),
        iconTheme: const IconThemeData(color: AppColors.lightText),
      ),
      cardTheme: CardThemeData(
        color: AppColors.lightCard,
        elevation: 2,
        shadowColor: Colors.black.withOpacity(0.08),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          elevation: 0,
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.lightBackground,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.lightDivider),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.lightDivider),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.primary, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
      dividerTheme: const DividerThemeData(
        color: AppColors.lightDivider,
        thickness: 1,
      ),
    );
  }

  static ThemeData darkTheme(String language) {
    final textTheme = _buildTextTheme(language, Brightness.dark);
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        brightness: Brightness.dark,
        primary: AppColors.primary,
        secondary: AppColors.secondary,
        surface: AppColors.darkSurface,
        onSurface: AppColors.darkText,
      ),
      scaffoldBackgroundColor: AppColors.darkBackground,
      textTheme: textTheme,
      appBarTheme: AppBarTheme(
        backgroundColor: AppColors.darkBackground,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: textTheme.titleLarge?.copyWith(
          fontWeight: FontWeight.w600,
          color: AppColors.darkText,
        ),
        iconTheme: const IconThemeData(color: AppColors.darkText),
      ),
      cardTheme: CardThemeData(
        color: AppColors.darkCard,
        elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          elevation: 0,
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.darkSurface,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.darkDivider),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.darkDivider),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.primary, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
      dividerTheme: const DividerThemeData(
        color: AppColors.darkDivider,
        thickness: 1,
      ),
    );
  }

  static TextTheme _buildTextTheme(String language, Brightness brightness) {
    final color = brightness == Brightness.light ? AppColors.lightText : AppColors.darkText;
    final secondaryColor = brightness == Brightness.light ? AppColors.lightTextSecondary : AppColors.darkTextSecondary;

    if (language == 'bn') {
      return TextTheme(
        displayLarge: TextStyle(fontFamily: 'HindSiliguri', fontSize: 57, fontWeight: FontWeight.w700, color: color),
        displayMedium: TextStyle(fontFamily: 'HindSiliguri', fontSize: 45, fontWeight: FontWeight.w600, color: color),
        displaySmall: TextStyle(fontFamily: 'HindSiliguri', fontSize: 36, fontWeight: FontWeight.w500, color: color),
        headlineLarge: TextStyle(fontFamily: 'HindSiliguri', fontSize: 32, fontWeight: FontWeight.w700, color: color),
        headlineMedium: TextStyle(fontFamily: 'HindSiliguri', fontSize: 28, fontWeight: FontWeight.w600, color: color),
        headlineSmall: TextStyle(fontFamily: 'HindSiliguri', fontSize: 24, fontWeight: FontWeight.w600, color: color),
        titleLarge: TextStyle(fontFamily: 'HindSiliguri', fontSize: 22, fontWeight: FontWeight.w600, color: color),
        titleMedium: TextStyle(fontFamily: 'HindSiliguri', fontSize: 16, fontWeight: FontWeight.w500, color: color),
        titleSmall: TextStyle(fontFamily: 'HindSiliguri', fontSize: 14, fontWeight: FontWeight.w500, color: color),
        bodyLarge: TextStyle(fontFamily: 'HindSiliguri', fontSize: 16, color: color),
        bodyMedium: TextStyle(fontFamily: 'HindSiliguri', fontSize: 14, color: secondaryColor),
        bodySmall: TextStyle(fontFamily: 'HindSiliguri', fontSize: 12, color: secondaryColor),
        labelLarge: TextStyle(fontFamily: 'HindSiliguri', fontSize: 14, fontWeight: FontWeight.w600, color: color),
        labelMedium: TextStyle(fontFamily: 'HindSiliguri', fontSize: 12, fontWeight: FontWeight.w500, color: secondaryColor),
        labelSmall: TextStyle(fontFamily: 'HindSiliguri', fontSize: 11, color: secondaryColor),
      );
    }

    return GoogleFonts.interTextTheme(TextTheme(
      displayLarge: TextStyle(fontSize: 57, fontWeight: FontWeight.w700, color: color),
      displayMedium: TextStyle(fontSize: 45, fontWeight: FontWeight.w600, color: color),
      displaySmall: TextStyle(fontSize: 36, fontWeight: FontWeight.w500, color: color),
      headlineLarge: TextStyle(fontSize: 32, fontWeight: FontWeight.w700, color: color),
      headlineMedium: TextStyle(fontSize: 28, fontWeight: FontWeight.w600, color: color),
      headlineSmall: TextStyle(fontSize: 24, fontWeight: FontWeight.w600, color: color),
      titleLarge: TextStyle(fontSize: 22, fontWeight: FontWeight.w600, color: color),
      titleMedium: TextStyle(fontSize: 16, fontWeight: FontWeight.w500, color: color),
      titleSmall: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: color),
      bodyLarge: TextStyle(fontSize: 16, color: color),
      bodyMedium: TextStyle(fontSize: 14, color: secondaryColor),
      bodySmall: TextStyle(fontSize: 12, color: secondaryColor),
      labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: color),
      labelMedium: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: secondaryColor),
      labelSmall: TextStyle(fontSize: 11, color: secondaryColor),
    ));
  }
}
