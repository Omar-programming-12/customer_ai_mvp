import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/di/injection_container.dart';
import '../cubit/conversation_list_cubit.dart';
import '../cubit/conversation_list_state.dart';
import '../cubit/conversation_thread_cubit.dart';
import '../widgets/chat_thread_panel.dart';
import '../widgets/conversation_list_panel.dart';
import '../widgets/customer_details_panel.dart';
import '../widgets/dashboard_top_bar.dart';
import '../widgets/filter_chips_row.dart';
import '../widgets/stats_row.dart';

/// The conversations dashboard: the screen described in the brief where an
/// agent reviews conversations, sees which need human attention, opens one,
/// and replies from inside the app.
///
/// Owns both feature Cubits for the lifetime of this screen and bridges
/// them with one [BlocListener]: selecting a conversation in the list opens
/// it in the thread panel. The Cubits don't reference each other directly -
/// that coordination lives here, at the presentation layer, which is what
/// keeps each Cubit independently testable.
class ConversationsPage extends StatelessWidget {
  const ConversationsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => sl<ConversationListCubit>()),
        BlocProvider(create: (_) => sl<ConversationThreadCubit>()),
      ],
      child: BlocListener<ConversationListCubit, ConversationListState>(
        listenWhen: (previous, current) =>
            previous.selectedConversationId != current.selectedConversationId,
        listener: (context, state) {
          final selected = state.conversations
              .where((c) => c.id == state.selectedConversationId)
              .firstOrNull;
          if (selected != null) {
            context.read<ConversationThreadCubit>().openConversation(selected);
          }
        },
        child: Column(
          children: [
            DashboardTopBar(
              onSearchChanged: (query) =>
                  context.read<ConversationListCubit>().search(query),
            ),
            BlocBuilder<ConversationListCubit, ConversationListState>(
              buildWhen: (previous, current) => previous.filter != current.filter,
              builder: (context, state) => FilterChipsRow(
                selected: state.filter,
                onSelected: (filter) =>
                    context.read<ConversationListCubit>().changeFilter(filter),
              ),
            ),
            const StatsRow(),
            const Expanded(
              child: Row(
                children: [
                  ConversationListPanel(),
                  ChatThreadPanel(),
                  CustomerDetailsPanel(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

extension<T> on Iterable<T> {
  T? get firstOrNull => isEmpty ? null : first;
}
