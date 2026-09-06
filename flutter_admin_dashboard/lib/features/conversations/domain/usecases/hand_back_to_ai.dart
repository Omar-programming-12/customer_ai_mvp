import '../repositories/conversation_repository.dart';

/// Gives control of a conversation back to the AI after a human agent was
/// handling it.
class HandBackToAi {
  const HandBackToAi(this._repository);

  final ConversationRepository _repository;

  Future<void> call(String conversationId) {
    return _repository.handBackToAi(conversationId);
  }
}
