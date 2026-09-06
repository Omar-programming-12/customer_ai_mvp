import '../entities/conversation.dart';
import '../entities/message.dart';

/// The single boundary the presentation layer talks through to read and act
/// on conversations. Everything below this interface (data models, whether
/// the source is an in-memory mock or Firestore, JSON mapping) is an
/// implementation detail the rest of the app never sees.
///
/// Reads are streams rather than one-shot futures on purpose: the target
/// backend is Firestore, whose `snapshots()` API is stream-based, and the
/// dashboard's whole premise is agents seeing new/escalated conversations
/// live. The mock implementation honors the same contract with in-memory
/// broadcast streams, so swapping it for a Firestore-backed implementation
/// later is a one-file change in the DI container - no use case or Cubit
/// changes.
abstract class ConversationRepository {
  /// Emits the full conversation list every time any conversation changes
  /// (new message, status change, hand-off, ...).
  Stream<List<Conversation>> watchConversations();

  /// Emits the full message history for [conversationId] every time a new
  /// message is added to it.
  Stream<List<Message>> watchMessages(String conversationId);

  /// Appends a message sent by [sender] (an agent replying manually, in
  /// today's UI) to the conversation.
  Future<void> sendMessage({
    required String conversationId,
    required String text,
    required String senderDisplayName,
  });

  /// A human agent claims a conversation the AI flagged for help.
  Future<void> takeOverConversation({
    required String conversationId,
    required String agentName,
  });

  /// Marks a conversation as closed.
  Future<void> resolveConversation(String conversationId);

  /// Reassigns a conversation to a different agent.
  Future<void> transferConversation({
    required String conversationId,
    required String toAgentName,
  });

  /// Gives control of the conversation back to the AI.
  Future<void> handBackToAi(String conversationId);
}
