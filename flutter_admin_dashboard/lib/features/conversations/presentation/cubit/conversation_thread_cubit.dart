import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/constants/current_agent.dart';
import '../../domain/entities/conversation.dart';
import '../../domain/entities/conversation_status.dart';
import '../../domain/entities/message.dart';
import '../../domain/usecases/hand_back_to_ai.dart';
import '../../domain/usecases/resolve_conversation.dart';
import '../../domain/usecases/send_message.dart';
import '../../domain/usecases/take_over_conversation.dart';
import '../../domain/usecases/transfer_conversation.dart';
import '../../domain/usecases/watch_messages.dart';
import 'conversation_thread_state.dart';

/// Drives the open conversation panel: the message thread itself, plus the
/// human-handoff actions (take over / resolve / transfer / hand back to AI).
///
/// It's a separate Cubit from [ConversationListCubit] on purpose - opening a
/// conversation and filtering the list are independent concerns with
/// independent async lifecycles (switching the open conversation cancels and
/// restarts a message subscription; filtering the list does not touch the
/// thread at all). The two stay in sync automatically because the mock data
/// source they read from re-emits its full list on every mutation - the
/// same behavior a real Firestore `snapshots()` listener would exhibit -
/// so no direct Cubit-to-Cubit call is needed after an action succeeds.
class ConversationThreadCubit extends Cubit<ConversationThreadState> {
  ConversationThreadCubit({
    required WatchMessages watchMessages,
    required SendMessage sendMessage,
    required TakeOverConversation takeOverConversation,
    required ResolveConversation resolveConversation,
    required TransferConversation transferConversation,
    required HandBackToAi handBackToAi,
  })  : _watchMessages = watchMessages,
        _sendMessage = sendMessage,
        _takeOverConversation = takeOverConversation,
        _resolveConversation = resolveConversation,
        _transferConversation = transferConversation,
        _handBackToAi = handBackToAi,
        super(const ConversationThreadState());

  final WatchMessages _watchMessages;
  final SendMessage _sendMessage;
  final TakeOverConversation _takeOverConversation;
  final ResolveConversation _resolveConversation;
  final TransferConversation _transferConversation;
  final HandBackToAi _handBackToAi;

  StreamSubscription<List<Message>>? _messagesSubscription;

  void openConversation(Conversation conversation) {
    if (state.conversation?.id == conversation.id) {
      // Already open - just refresh the header (status may have changed in
      // the list, e.g. selecting the same still-open conversation again).
      emit(state.copyWith(conversation: conversation));
      return;
    }

    _messagesSubscription?.cancel();
    emit(ConversationThreadState(
      status: ConversationThreadStatus.loading,
      conversation: conversation,
    ));

    _messagesSubscription = _watchMessages(conversation.id).listen(
      (messages) => emit(state.copyWith(
        status: ConversationThreadStatus.loaded,
        messages: messages,
      )),
      onError: (Object error) => emit(state.copyWith(
        status: ConversationThreadStatus.error,
        errorMessage: error.toString(),
      )),
    );
  }

  Future<void> sendMessage(String text) async {
    final conversation = state.conversation;
    if (conversation == null || text.trim().isEmpty) return;

    emit(state.copyWith(isSendingMessage: true));
    try {
      await _sendMessage(
        conversationId: conversation.id,
        text: text.trim(),
        senderDisplayName: CurrentAgent.name,
      );
    } finally {
      emit(state.copyWith(isSendingMessage: false));
    }
  }

  Future<void> takeOver() async {
    final conversation = state.conversation;
    if (conversation == null) return;

    await _takeOverConversation(
      conversationId: conversation.id,
      agentName: CurrentAgent.name,
    );
    emit(state.copyWith(
      conversation: conversation.copyWith(
        status: ConversationStatus.humanTookOver,
        assignedAgentName: CurrentAgent.name,
      ),
    ));
  }

  Future<void> resolve() async {
    final conversation = state.conversation;
    if (conversation == null) return;

    await _resolveConversation(conversation.id);
    emit(state.copyWith(
      conversation: conversation.copyWith(
        status: ConversationStatus.resolved,
      ),
    ));
  }

  Future<void> transfer(String toAgentName) async {
    final conversation = state.conversation;
    if (conversation == null || toAgentName.trim().isEmpty) return;

    await _transferConversation(
      conversationId: conversation.id,
      toAgentName: toAgentName.trim(),
    );
    emit(state.copyWith(
      conversation: conversation.copyWith(
        status: ConversationStatus.humanTookOver,
        assignedAgentName: toAgentName.trim(),
      ),
    ));
  }

  Future<void> handBackToAi() async {
    final conversation = state.conversation;
    if (conversation == null) return;

    await _handBackToAi(conversation.id);
    emit(state.copyWith(
      conversation: conversation.copyWith(
        status: ConversationStatus.aiHandling,
        clearAssignedAgentName: true,
      ),
    ));
  }

  @override
  Future<void> close() {
    _messagesSubscription?.cancel();
    return super.close();
  }
}
