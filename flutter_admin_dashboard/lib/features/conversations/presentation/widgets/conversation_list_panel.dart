import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/theme/app_colors.dart';
import '../cubit/conversation_list_cubit.dart';
import '../cubit/conversation_list_state.dart';
import 'conversation_list_item.dart';

class ConversationListPanel extends StatelessWidget {
  const ConversationListPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 340,
      decoration: const BoxDecoration(
        color: AppColors.surface,
        border: Border(left: BorderSide(color: AppColors.border)),
      ),
      child: Column(
        children: [
          BlocBuilder<ConversationListCubit, ConversationListState>(
            buildWhen: (previous, current) =>
                previous.conversations.length != current.conversations.length ||
                previous.visibleConversations.length !=
                    current.visibleConversations.length,
            builder: (context, state) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
                decoration: const BoxDecoration(
                  border: Border(bottom: BorderSide(color: AppColors.divider)),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'كل المحادثات',
                            style: TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          Text(
                            'عرض ${state.visibleConversations.length} من ${state.conversations.length}',
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppColors.textMuted,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.more_vert,
                        size: 18, color: AppColors.textSecondary),
                  ],
                ),
              );
            },
          ),
          Expanded(
            child: BlocBuilder<ConversationListCubit, ConversationListState>(
              builder: (context, state) {
                if (state.status == ConversationListStatus.loading) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (state.status == ConversationListStatus.error) {
                  return Center(
                    child: Text(
                      state.errorMessage ?? 'حدث خطأ أثناء تحميل المحادثات',
                      style: const TextStyle(color: AppColors.danger),
                    ),
                  );
                }

                final conversations = state.visibleConversations;

                if (conversations.isEmpty) {
                  return const Center(
                    child: Text(
                      'لا توجد محادثات مطابقة',
                      style: TextStyle(color: AppColors.textMuted),
                    ),
                  );
                }

                return ListView.builder(
                  itemCount: conversations.length,
                  itemBuilder: (context, index) {
                    final conversation = conversations[index];
                    return ConversationListItem(
                      conversation: conversation,
                      selected: conversation.id == state.selectedConversationId,
                      onTap: () => context
                          .read<ConversationListCubit>()
                          .selectConversation(conversation.id),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
