import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';

import '../../domain/entities/conversation.dart';
import '../../domain/usecases/watch_conversations.dart';
import 'conversation_list_state.dart';

/// Drives the conversation list panel: subscribes to the live conversation
/// stream once and keeps re-deriving `visibleConversations` as the active
/// filter, search text, or the underlying data changes.
///
/// This is genuine Cubit territory - it owns an async subscription and
/// several pieces of state (filter, search, selection) that all interact -
/// as opposed to, say, the sidebar's active-nav-item highlight, which is
/// trivial local widget state and stays a plain `StatefulWidget`.
class ConversationListCubit extends Cubit<ConversationListState> {
  ConversationListCubit({required WatchConversations watchConversations})
      : _watchConversations = watchConversations,
        super(const ConversationListState()) {
    _subscribe();
  }

  final WatchConversations _watchConversations;
  StreamSubscription<List<Conversation>>? _subscription;

  void _subscribe() {
    _subscription = _watchConversations().listen(
      (conversations) {
        var next = state.copyWith(
          status: ConversationListStatus.loaded,
          conversations: conversations,
        );

        // Keep a selection alive across list refreshes; default to the
        // top-priority conversation the first time data arrives.
        if (next.selectedConversationId == null && conversations.isNotEmpty) {
          next = next.copyWith(
            selectedConversationId: next.visibleConversations.first.id,
          );
        }

        emit(next);
      },
      onError: (Object error) {
        emit(state.copyWith(
          status: ConversationListStatus.error,
          errorMessage: error.toString(),
        ));
      },
    );
  }

  void changeFilter(ConversationFilter filter) {
    emit(state.copyWith(filter: filter));
  }

  void search(String query) {
    emit(state.copyWith(searchQuery: query));
  }

  void selectConversation(String conversationId) {
    emit(state.copyWith(selectedConversationId: conversationId));
  }

  @override
  Future<void> close() {
    _subscription?.cancel();
    return super.close();
  }
}
