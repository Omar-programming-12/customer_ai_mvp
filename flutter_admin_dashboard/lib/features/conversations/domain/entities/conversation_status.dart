/// The lifecycle state of a customer conversation.
///
/// This is a pure domain concept - it carries no UI information (colors,
/// icons, labels). Presentation-layer code maps each value to how it should
/// look; see `conversation_status_style.dart`.
enum ConversationStatus {
  /// The AI is answering the customer and no human is involved yet.
  aiHandling,

  /// The AI could not confidently continue and flagged the conversation for
  /// a human agent. Nobody has taken it over yet.
  needsHuman,

  /// A human agent has taken over and is replying directly.
  humanTookOver,

  /// The conversation is closed - no further action is expected.
  resolved,
}
