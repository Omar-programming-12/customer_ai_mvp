import '../repositories/conversation_repository.dart';

/// Sends the agent's manual reply. This is the Flutter side of
/// "Flutter → FastAPI → Meta Messenger → Customer"; today it only appends to
/// the mock thread, but the call shape already matches what will eventually
/// need to reach FastAPI (conversation, text, who sent it).
class SendMessage {
  const SendMessage(this._repository);

  final ConversationRepository _repository;

  Future<void> call({
    required String conversationId,
    required String text,
    required String senderDisplayName,
  }) {
    return _repository.sendMessage(
      conversationId: conversationId,
      text: text,
      senderDisplayName: senderDisplayName,
    );
  }
}
