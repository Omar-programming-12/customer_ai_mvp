import 'package:flutter/material.dart';

/// The dashboard's color palette. Centralized here so every widget draws
/// from the same set of values instead of inlining hex codes - the natural
/// place to swap in a real brand palette later.
abstract final class AppColors {
  static const background = Color(0xFFF7F7FB);
  static const surface = Color(0xFFFFFFFF);
  static const border = Color(0xFFECECF3);
  static const borderStrong = Color(0xFFDCDCE6);
  static const divider = Color(0xFFF1F1F6);

  static const textPrimary = Color(0xFF1B1B2C);
  static const textSecondary = Color(0xFF6B6B80);
  static const textMuted = Color(0xFF9999AC);

  static const brand = Color(0xFF4338CA);
  static const brandLight = Color(0xFFEEF0FD);

  static const success = Color(0xFF15803D);
  static const successLight = Color(0xFFE7F6EC);
  static const danger = Color(0xFFDC2626);
  static const dangerLight = Color(0xFFFEE2E2);

  // Per-status colors used by ConversationStatusStyle.
  static const aiText = Color(0xFF0E7C86);
  static const aiBg = Color(0xFFE3F6F8);
  static const aiDot = Color(0xFF14B8C4);

  static const needsHumanText = Color(0xFFDC2626);
  static const needsHumanBg = Color(0xFFFEE2E2);
  static const needsHumanDot = Color(0xFFEF4444);
  static const needsHumanRowTint = Color(0xFFFFF8F7);

  static const humanTookOverText = Color(0xFF6D28D9);
  static const humanTookOverBg = Color(0xFFEDE6FB);
  static const humanTookOverDot = Color(0xFF8B5CF6);

  static const resolvedText = Color(0xFF15803D);
  static const resolvedBg = Color(0xFFE7F6EC);
  static const resolvedDot = Color(0xFF22A55A);

  // A small rotation of tints for customer-initial avatars.
  static const avatarPalette = [
    (bg: Color(0xFFE0E4FD), fg: Color(0xFF4338CA)),
    (bg: Color(0xFFD7F3F1), fg: Color(0xFF0F766E)),
    (bg: Color(0xFFFDECD2), fg: Color(0xFFB45309)),
    (bg: Color(0xFFFCE1E7), fg: Color(0xFFBE185D)),
    (bg: Color(0xFFE4E4EC), fg: Color(0xFF3F3F52)),
  ];
}
