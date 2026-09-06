import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/app_avatar.dart';
import '../../../../core/widgets/transfer_dialog.dart';
import '../../domain/entities/conversation.dart';
import '../../domain/entities/conversation_status.dart';
import '../cubit/conversation_thread_cubit.dart';
import '../cubit/conversation_thread_state.dart';
import 'chat_input_bar.dart';
import 'message_bubble.dart';
import 'status_badge.dart';

class ChatThreadPanel extends StatelessWidget {
  const ChatThreadPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        decoration: const BoxDecoration(
          color: AppColors.surface,
          border: Border(left: BorderSide(color: AppColors.border)),
        ),
        child: BlocBuilder<ConversationThreadCubit, ConversationThreadState>(
          builder: (context, state) {
            final conversation = state.conversation;
            if (conversation == null) {
              return const Center(
                child: Text(
                  'اختر محادثة من القائمة لعرضها',
                  style: TextStyle(color: AppColors.textMuted),
                ),
              );
            }

            return Column(
              children: [
                _ThreadHeader(conversation: conversation),
                Expanded(
                  child: state.status == ConversationThreadStatus.loading
                      ? const Center(child: CircularProgressIndicator())
                      : ListView.separated(
                          padding: const EdgeInsets.all(24),
                          itemCount: state.messages.length,
                          separatorBuilder: (_, _) => const SizedBox(height: 16),
                          itemBuilder: (context, index) =>
                              MessageBubble(message: state.messages[index]),
                        ),
                ),
                _HandoffStrip(conversation: conversation),
                Container(
                  decoration: const BoxDecoration(
                    border: Border(top: BorderSide(color: AppColors.border)),
                  ),
                  child: ChatInputBar(
                    enabled: conversation.status == ConversationStatus.humanTookOver,
                    onSend: (text) =>
                        context.read<ConversationThreadCubit>().sendMessage(text),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}

class _ThreadHeader extends StatelessWidget {
  const _ThreadHeader({required this.conversation});

  final Conversation conversation;

  @override
  Widget build(BuildContext context) {
    final isResolved = conversation.status == ConversationStatus.resolved;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        children: [
          AppAvatar(name: conversation.customer.name, size: 40),
          const SizedBox(width: 12),
          Expanded(
            // Name, badge and channel are stacked (rather than sharing one
            // Row) so each gets the full column width to itself: a Row
            // gives its non-flex children their natural, unwrapped width
            // regardless of how little space is actually left once the two
            // header buttons claim theirs, which is exactly what was
            // overflowing here with a long name next to a long status
            // label like "تولى الموظف المحادثة".
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  conversation.customer.name,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 3),
                StatusBadge(status: conversation.status, compact: true),
                const SizedBox(height: 3),
                const Text(
                  'عبر Messenger',
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 11, color: AppColors.textMuted),
                ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          OutlinedButton.icon(
            onPressed: isResolved ? null : () => _showTransferDialog(context),
            icon: const Icon(Icons.sync_alt, size: 14),
            label: const Text('تحويل'),
            style: OutlinedButton.styleFrom(
              foregroundColor: AppColors.textPrimary,
              side: const BorderSide(color: AppColors.borderStrong),
              visualDensity: VisualDensity.compact,
              padding: const EdgeInsets.symmetric(horizontal: 10),
              textStyle: const TextStyle(fontSize: 12.5),
            ),
          ),
          const SizedBox(width: 8),
          FilledButton.icon(
            onPressed: isResolved
                ? null
                : () => context.read<ConversationThreadCubit>().resolve(),
            icon: const Icon(Icons.check, size: 14),
            label: const Text('إنهاء المحادثة'),
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.success,
              visualDensity: VisualDensity.compact,
              padding: const EdgeInsets.symmetric(horizontal: 12),
              textStyle: const TextStyle(fontSize: 12.5),
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _showTransferDialog(BuildContext context) async {
    final cubit = context.read<ConversationThreadCubit>();
    final agentName = await showTransferDialog(context);
    if (agentName != null) {
      await cubit.transfer(agentName);
    }
  }
}

/// The strip between the thread and the composer that surfaces whichever
/// human-handoff action is relevant to the conversation's current status -
/// this is the "تدخل والرد يدويًا" affordance the brief asked for.
class _HandoffStrip extends StatelessWidget {
  const _HandoffStrip({required this.conversation});

  final Conversation conversation;

  @override
  Widget build(BuildContext context) {
    switch (conversation.status) {
      case ConversationStatus.needsHuman:
        return _Strip(
          background: AppColors.dangerLight,
          foreground: AppColors.needsHumanText,
          icon: Icons.warning_amber_rounded,
          message: 'الذكاء الاصطناعي يحتاج مساعدتك في هذه المحادثة',
          actionLabel: 'تدخل والرد يدويًا',
          onAction: () => context.read<ConversationThreadCubit>().takeOver(),
        );
      case ConversationStatus.aiHandling:
        return _Strip(
          background: AppColors.aiBg,
          foreground: AppColors.aiText,
          icon: Icons.auto_awesome,
          message: 'الذكاء الاصطناعي يتولى الرد على هذه المحادثة حاليًا',
          actionLabel: 'تدخل والرد يدويًا',
          onAction: () => context.read<ConversationThreadCubit>().takeOver(),
        );
      case ConversationStatus.humanTookOver:
        return _Strip(
          background: AppColors.humanTookOverBg,
          foreground: AppColors.humanTookOverText,
          icon: Icons.person,
          message: 'أنتِ متصلة الآن وتراسلين العميل مباشرة',
          actionLabel: 'تسليم المحادثة للذكاء الاصطناعي مرة أخرى',
          onAction: () => context.read<ConversationThreadCubit>().handBackToAi(),
        );
      case ConversationStatus.resolved:
        return const _Strip(
          background: AppColors.resolvedBg,
          foreground: AppColors.resolvedText,
          icon: Icons.check_circle_outline,
          message: 'تم إغلاق هذه المحادثة',
        );
    }
  }
}

class _Strip extends StatelessWidget {
  const _Strip({
    required this.background,
    required this.foreground,
    required this.icon,
    required this.message,
    this.actionLabel,
    this.onAction,
  });

  final Color background;
  final Color foreground;
  final IconData icon;
  final String message;
  final String? actionLabel;
  final VoidCallback? onAction;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: background,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 9),
      child: Row(
        children: [
          Icon(icon, size: 15, color: foreground),
          const SizedBox(width: 7),
          Expanded(
            child: Text(
              message,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: foreground,
              ),
            ),
          ),
          if (actionLabel != null)
            TextButton(
              onPressed: onAction,
              style: TextButton.styleFrom(foregroundColor: foreground),
              child: Text(
                actionLabel!,
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
              ),
            ),
        ],
      ),
    );
  }
}
