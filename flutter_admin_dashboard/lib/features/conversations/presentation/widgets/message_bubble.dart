import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/utils/relative_time.dart';
import '../../domain/entities/message.dart';
import '../../domain/entities/message_sender.dart';

/// A single row in the chat thread. A [MessageSender.system] message (the
/// AI-escalation note) renders as a centered banner instead of a bubble -
/// it's not something either party said, so it shouldn't look like a
/// message from either side.
class MessageBubble extends StatelessWidget {
  const MessageBubble({super.key, required this.message});

  final Message message;

  @override
  Widget build(BuildContext context) {
    if (message.sender == MessageSender.system) {
      return _SystemBanner(text: message.text);
    }

    final isCustomer = message.sender == MessageSender.customer;

    final (background, border, labelColor, icon, label) = switch (message.sender) {
      MessageSender.ai => (
          const Color(0xFFEFF9FA),
          const Color(0xFFD3EEF1),
          AppColors.aiText,
          Icons.auto_awesome,
          'الذكاء الاصطناعي',
        ),
      MessageSender.agent => (
          const Color(0xFFF5F3FE),
          const Color(0xFFE4DFFC),
          AppColors.humanTookOverText,
          Icons.person,
          message.senderDisplayName ?? 'فريق الدعم',
        ),
      _ => (
          AppColors.surface,
          AppColors.border,
          AppColors.textPrimary,
          null,
          null,
        ),
    };

    return Column(
      crossAxisAlignment:
          isCustomer ? CrossAxisAlignment.start : CrossAxisAlignment.end,
      children: [
        if (label != null) ...[
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(icon, size: 12, color: labelColor),
                const SizedBox(width: 5),
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.bold,
                    color: labelColor,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 4),
        ],
        ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 380),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: background,
              border: Border.all(color: border),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Text(
              message.text,
              style: const TextStyle(
                fontSize: 14,
                height: 1.6,
                color: AppColors.textPrimary,
              ),
            ),
          ),
        ),
        const SizedBox(height: 4),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: Text(
            formatClockArabic(message.sentAt),
            style: const TextStyle(fontSize: 10, color: Color(0xFFB3B3C2)),
          ),
        ),
      ],
    );
  }
}

class _SystemBanner extends StatelessWidget {
  const _SystemBanner({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          const Expanded(child: Divider(color: Color(0xFFF0DCDC))),
          // Flexible (not a bare child) because this banner's sentence is
          // long enough that, at the chat panel's normal width, it needs to
          // wrap onto a second line rather than demanding its full one-line
          // width - which a plain Row child would do regardless of how
          // little space is actually left after the two dividers.
          Flexible(
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 8),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              decoration: BoxDecoration(
                color: AppColors.dangerLight,
                borderRadius: BorderRadius.circular(999),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.warning_amber_rounded,
                      size: 13, color: Color(0xFFB91C1C)),
                  const SizedBox(width: 6),
                  Flexible(
                    child: Text(
                      text,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFFB91C1C),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const Expanded(child: Divider(color: Color(0xFFF0DCDC))),
        ],
      ),
    );
  }
}
