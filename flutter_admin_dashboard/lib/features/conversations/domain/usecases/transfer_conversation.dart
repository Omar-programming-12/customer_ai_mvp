import '../repositories/conversation_repository.dart';

/// Reassigns a conversation to a different agent.
class TransferConversation {
  const TransferConversation(this._repository);

  final ConversationRepository _repository;

  Future<void> call({
    required String conversationId,
    required String toAgentName,
  }) {
    return _repository.transferConversation(
      conversationId: conversationId,
      toAgentName: toAgentName,
    );
  }
}
