import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../domain/entities/conversation_status.dart';

/// How a [ConversationStatus] should look. Kept in the presentation layer
/// (not on the enum itself) so the domain stays free of `Color`/UI imports.
class ConversationStatusStyle {
  const ConversationStatusStyle({
    required this.label,
    required this.textColor,
    required this.backgroundColor,
    required this.dotColor,
  });

  final String label;
  final Color textColor;
  final Color backgroundColor;
  final Color dotColor;

  factory ConversationStatusStyle.of(ConversationStatus status) {
    return switch (status) {
      ConversationStatus.aiHandling => const ConversationStatusStyle(
          label: 'يديرها الذكاء الاصطناعي',
          textColor: AppColors.aiText,
          backgroundColor: AppColors.aiBg,
          dotColor: AppColors.aiDot,
        ),
      ConversationStatus.needsHuman => const ConversationStatusStyle(
          label: 'تحتاج تدخل بشري',
          textColor: AppColors.needsHumanText,
          backgroundColor: AppColors.needsHumanBg,
          dotColor: AppColors.needsHumanDot,
        ),
      ConversationStatus.humanTookOver => const ConversationStatusStyle(
          label: 'تولى الموظف المحادثة',
          textColor: AppColors.humanTookOverText,
          backgroundColor: AppColors.humanTookOverBg,
          dotColor: AppColors.humanTookOverDot,
        ),
      ConversationStatus.resolved => const ConversationStatusStyle(
          label: 'تم الحل',
          textColor: AppColors.resolvedText,
          backgroundColor: AppColors.resolvedBg,
          dotColor: AppColors.resolvedDot,
        ),
    };
  }
}
