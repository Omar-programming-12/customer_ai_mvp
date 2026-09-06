import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/widgets/app_avatar.dart';
import '../../../../core/widgets/transfer_dialog.dart';
import '../../domain/entities/conversation.dart';
import '../../domain/entities/customer.dart';
import '../cubit/conversation_thread_cubit.dart';
import '../cubit/conversation_thread_state.dart';

class CustomerDetailsPanel extends StatelessWidget {
  const CustomerDetailsPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 300,
      color: AppColors.surface,
      child: BlocBuilder<ConversationThreadCubit, ConversationThreadState>(
        builder: (context, state) {
          final conversation = state.conversation;
          if (conversation == null) return const SizedBox.shrink();

          return SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 22),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _CustomerHeader(customer: conversation.customer),
                const SizedBox(height: 20),
                Row(
                  children: [
                    Expanded(
                      child: _MiniStat(
                        label: 'محادثات سابقة',
                        value: '${conversation.customer.previousConversationsCount} محادثات',
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: _MiniStat(
                        label: 'عميل منذ',
                        value: _formatMonthYear(conversation.customer.customerSince),
                      ),
                    ),
                  ],
                ),
                if (conversation.customer.tags.isNotEmpty) ...[
                  const SizedBox(height: 20),
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: [
                      for (final tag in conversation.customer.tags) _TagChip(label: tag),
                    ],
                  ),
                ],
                if (conversation.customer.lastPurchaseProductName != null) ...[
                  const SizedBox(height: 20),
                  const Text(
                    'آخر عملية شراء',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  _LastPurchaseCard(customer: conversation.customer),
                ],
                if (conversation.detectedIntent != null) ...[
                  const SizedBox(height: 20),
                  const Text(
                    'النية المكتشفة',
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textSecondary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppColors.brandLight,
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Text(
                      conversation.detectedIntent!,
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: AppColors.brand,
                      ),
                    ),
                  ),
                ],
                const SizedBox(height: 28),
                _ActionButtons(conversation: conversation),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _CustomerHeader extends StatelessWidget {
  const _CustomerHeader({required this.customer});

  final Customer customer;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        AppAvatar(name: customer.name, size: 52),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                customer.name,
                style: const TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.bold,
                  color: AppColors.textPrimary,
                ),
              ),
              const SizedBox(height: 3),
              Row(
                children: [
                  const Icon(Icons.phone, size: 12, color: AppColors.textSecondary),
                  const SizedBox(width: 5),
                  Text(
                    customer.phoneNumber,
                    style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _MiniStat extends StatelessWidget {
  const _MiniStat({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textMuted)),
          const SizedBox(height: 3),
          Text(
            value,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}

class _TagChip extends StatelessWidget {
  const _TagChip({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    final isWarranty = label.contains('ضمان');
    final background = isWarranty ? AppColors.resolvedBg : const Color(0xFFFDECD2);
    final foreground = isWarranty ? AppColors.resolvedText : const Color(0xFFB45309);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: background, borderRadius: BorderRadius.circular(999)),
      child: Text(
        label,
        style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: foreground),
      ),
    );
  }
}

class _LastPurchaseCard extends StatelessWidget {
  const _LastPurchaseCard({required this.customer});

  final Customer customer;

  @override
  Widget build(BuildContext context) {
    final daysAgo = customer.lastPurchaseDate == null
        ? null
        : DateTime.now().difference(customer.lastPurchaseDate!).inDays;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        border: Border.all(color: AppColors.border),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            customer.lastPurchaseProductName!,
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.bold,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            [
              if (customer.lastPurchaseBranch != null) customer.lastPurchaseBranch!,
              if (daysAgo != null) 'قبل $daysAgo أيام',
            ].join(' · '),
            style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
          ),
        ],
      ),
    );
  }
}

class _ActionButtons extends StatelessWidget {
  const _ActionButtons({required this.conversation});

  final Conversation conversation;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () => _showTransferDialog(context),
            icon: const Icon(Icons.sync_alt, size: 14),
            label: const Text('تحويل إلى موظف آخر'),
            style: OutlinedButton.styleFrom(
              foregroundColor: AppColors.textPrimary,
              side: const BorderSide(color: AppColors.borderStrong),
            ),
          ),
        ),
        const SizedBox(height: 8),
        SizedBox(
          width: double.infinity,
          child: FilledButton.icon(
            onPressed: () => context.read<ConversationThreadCubit>().resolve(),
            icon: const Icon(Icons.check, size: 14),
            label: const Text('تحديد المحادثة كمُحلولة'),
            style: FilledButton.styleFrom(backgroundColor: AppColors.success),
          ),
        ),
      ],
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

String _formatMonthYear(DateTime date) {
  const months = [
    'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
    'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر',
  ];
  return '${months[date.month - 1]} ${date.year}';
}
