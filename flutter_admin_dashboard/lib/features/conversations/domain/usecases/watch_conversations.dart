import '../entities/conversation.dart';
import '../repositories/conversation_repository.dart';

/// Streams the live conversation list for the conversation list panel.
class WatchConversations {
  const WatchConversations(this._repository);

  final ConversationRepository _repository;

  Stream<List<Conversation>> call() => _repository.watchConversations();
}
