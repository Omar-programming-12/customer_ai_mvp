import '../entities/message.dart';
import '../repositories/conversation_repository.dart';

/// Streams the live message history for one open conversation thread.
class WatchMessages {
  const WatchMessages(this._repository);

  final ConversationRepository _repository;

  Stream<List<Message>> call(String conversationId) =>
      _repository.watchMessages(conversationId);
}
