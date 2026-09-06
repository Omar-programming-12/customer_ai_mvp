import 'package:equatable/equatable.dart';

import 'channel.dart';
import 'conversation_status.dart';
import 'customer.dart';

/// A customer conversation as it appears in the agent's conversation list -
/// the customer it's with, its current handling status, and enough of the
/// last message to render a list row without loading the full thread.
class Conversation extends Equatable {
  const Conversation({
    required this.id,
    required this.customer,
    required this.status,
    required this.channel,
    required this.lastMessagePreview,
    required this.lastMessageAt,
    this.assignedAgentName,
    this.detectedIntent,
  });

  final String id;
  final Customer customer;
  final ConversationStatus status;
  final Channel channel;
  final String lastMessagePreview;
  final DateTime lastMessageAt;

  /// The agent currently handling it, once [status] is
  /// [ConversationStatus.humanTookOver]. Null otherwise.
  final String? assignedAgentName;

  /// A short, human-readable label for what the AI/router determined the
  /// customer wants (e.g. "دعم فني - شكوى ضمان"). Null when nothing has been
  /// determined yet.
  final String? detectedIntent;

  Conversation copyWith({
    ConversationStatus? status,
    String? lastMessagePreview,
    DateTime? lastMessageAt,
    String? assignedAgentName,
    bool clearAssignedAgentName = false,
  }) {
    return Conversation(
      id: id,
      customer: customer,
      status: status ?? this.status,
      channel: channel,
      lastMessagePreview: lastMessagePreview ?? this.lastMessagePreview,
      lastMessageAt: lastMessageAt ?? this.lastMessageAt,
      assignedAgentName: clearAssignedAgentName
          ? null
          : (assignedAgentName ?? this.assignedAgentName),
      detectedIntent: detectedIntent,
    );
  }

  @override
  List<Object?> get props => [
        id,
        customer,
        status,
        channel,
        lastMessagePreview,
        lastMessageAt,
        assignedAgentName,
        detectedIntent,
      ];
}
