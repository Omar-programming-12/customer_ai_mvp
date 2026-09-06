import 'package:equatable/equatable.dart';

import 'message_sender.dart';

/// A single message inside a conversation thread.
class Message extends Equatable {
  const Message({
    required this.id,
    required this.conversationId,
    required this.sender,
    required this.text,
    required this.sentAt,
    this.senderDisplayName,
  });

  final String id;
  final String conversationId;
  final MessageSender sender;
  final String text;
  final DateTime sentAt;

  /// Only meaningful for [MessageSender.agent] (the agent's name, e.g.
  /// "ياسمين علي"). Customer/AI/system messages don't need one - the UI
  /// already labels them by sender type.
  final String? senderDisplayName;

  @override
  List<Object?> get props =>
      [id, conversationId, sender, text, sentAt, senderDisplayName];
}
