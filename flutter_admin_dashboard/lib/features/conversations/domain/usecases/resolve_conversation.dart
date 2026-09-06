import '../repositories/conversation_repository.dart';

/// Marks a conversation as closed.
class ResolveConversation {
  const ResolveConversation(this._repository);

  final ConversationRepository _repository;

  Future<void> call(String conversationId) {
    return _repository.resolveConversation(conversationId);
  }
}
