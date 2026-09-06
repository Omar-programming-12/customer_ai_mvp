import '../repositories/conversation_repository.dart';

/// A human agent claims a conversation the AI escalated.
class TakeOverConversation {
  const TakeOverConversation(this._repository);

  final ConversationRepository _repository;

  Future<void> call({
    required String conversationId,
    required String agentName,
  }) {
    return _repository.takeOverConversation(
      conversationId: conversationId,
      agentName: agentName,
    );
  }
}
