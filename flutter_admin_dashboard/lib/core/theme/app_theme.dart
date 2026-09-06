import 'package:flutter/material.dart';

import 'app_colors.dart';

/// The dashboard's single [ThemeData]. No custom font family is set: Flutter
/// resolves Arabic glyphs through its automatic Unicode fallback regardless
/// of the requested family, and bundling a specific Arabic typeface (e.g.
/// Cairo/IBM Plex Sans Arabic, to match the earlier product mockup) is a
/// cosmetic follow-up - drop the .ttf files under assets/fonts and register
/// them here once a brand typeface is chosen.
abstract final class AppTheme {
  static ThemeData light() {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: AppColors.brand,
      brightness: Brightness.light,
      primary: AppColors.brand,
      surface: AppColors.surface,
    );

    return ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: AppColors.background,
      dividerColor: AppColors.border,
      textTheme: const TextTheme(
        bodyMedium: TextStyle(color: AppColors.textPrimary, fontSize: 14),
      ).apply(
        bodyColor: AppColors.textPrimary,
        displayColor: AppColors.textPrimary,
      ),
      visualDensity: VisualDensity.standard,
    );
  }
}
