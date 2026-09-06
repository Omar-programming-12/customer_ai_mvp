import 'package:equatable/equatable.dart';

import '../../domain/entities/conversation.dart';
import '../../domain/entities/message.dart';

enum ConversationThreadStatus { empty, loading, loaded, error }

/// State for whichever conversation is currently open in the chat thread
/// panel. `conversation` is kept alongside `messages` so the panel's header
/// (name, status badge, assigned agent) can update immediately after an
/// action like "resolve" without waiting on a separate read.
class ConversationThreadState extends Equatable {
  const ConversationThreadState({
    this.status = ConversationThreadStatus.empty,
    this.conversation,
    this.messages = const [],
    this.isSendingMessage = false,
    this.errorMessage,
  });

  final ConversationThreadStatus status;
  final Conversation? conversation;
  final List<Message> messages;
  final bool isSendingMessage;
  final String? errorMessage;

  ConversationThreadState copyWith({
    ConversationThreadStatus? status,
    Conversation? conversation,
    List<Message>? messages,
    bool? isSendingMessage,
    String? errorMessage,
  }) {
    return ConversationThreadState(
      status: status ?? this.status,
      conversation: conversation ?? this.conversation,
      messages: messages ?? this.messages,
      isSendingMessage: isSendingMessage ?? this.isSendingMessage,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props =>
      [status, conversation, messages, isSendingMessage, errorMessage];
}
