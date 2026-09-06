import 'package:flutter/material.dart';

import '../../domain/entities/conversation_status.dart';
import 'conversation_status_style.dart';

class StatusBadge extends StatelessWidget {
  const StatusBadge({super.key, required this.status, this.compact = false});

  final ConversationStatus status;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final style = ConversationStatusStyle.of(status);

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: compact ? 9 : 10,
        vertical: compact ? 2 : 4,
      ),
      decoration: BoxDecoration(
        color: style.backgroundColor,
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: compact ? 5 : 6,
            height: compact ? 5 : 6,
            decoration: BoxDecoration(
              color: style.dotColor,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 5),
          // Flexible + ellipsis rather than a bare Text: this badge is used
          // in tight spots (the chat header, next to two action buttons)
          // where the longest label ("تولى الموظف المحادثة") can be asked
          // to fit in less space than it naturally needs - truncating
          // gracefully there beats a hard RenderFlex overflow.
          Flexible(
            child: Text(
              style.label,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: style.textColor,
                fontSize: compact ? 11 : 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
