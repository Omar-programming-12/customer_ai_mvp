import 'package:equatable/equatable.dart';

import '../../domain/entities/conversation.dart';
import '../../domain/entities/conversation_status.dart';

enum ConversationListStatus { loading, loaded, error }

/// The set of filter chips shown above the conversation list.
enum ConversationFilter {
  all,
  needsHuman,
  aiHandling,
  humanTookOver,
  resolved;

  /// The status a conversation must have to pass this filter, or `null` for
  /// [ConversationFilter.all] (no restriction).
  ConversationStatus? get matchingStatus => switch (this) {
        ConversationFilter.all => null,
        ConversationFilter.needsHuman => ConversationStatus.needsHuman,
        ConversationFilter.aiHandling => ConversationStatus.aiHandling,
        ConversationFilter.humanTookOver => ConversationStatus.humanTookOver,
        ConversationFilter.resolved => ConversationStatus.resolved,
      };
}

class ConversationListState extends Equatable {
  const ConversationListState({
    this.status = ConversationListStatus.loading,
    this.conversations = const [],
    this.filter = ConversationFilter.all,
    this.searchQuery = '',
    this.selectedConversationId,
    this.errorMessage,
  });

  final ConversationListStatus status;

  /// The full, unfiltered list as last received from the repository.
  final List<Conversation> conversations;
  final ConversationFilter filter;
  final String searchQuery;
  final String? selectedConversationId;
  final String? errorMessage;

  /// Conversations needing human attention are always surfaced first
  /// (regardless of the active filter/sort), then the rest ordered by most
  /// recent activity - the same triage the mockup this screen is built from
  /// was designed around.
  List<Conversation> get visibleConversations {
    final matchingStatus = filter.matchingStatus;
    final query = searchQuery.trim().toLowerCase();

    final filtered = conversations.where((conversation) {
      final matchesFilter =
          matchingStatus == null || conversation.status == matchingStatus;
      final matchesSearch = query.isEmpty ||
          conversation.customer.name.toLowerCase().contains(query) ||
          conversation.customer.phoneNumber.contains(query);
      return matchesFilter && matchesSearch;
    }).toList();

    filtered.sort((a, b) {
      final aNeedsHuman = a.status == ConversationStatus.needsHuman;
      final bNeedsHuman = b.status == ConversationStatus.needsHuman;
      if (aNeedsHuman != bNeedsHuman) {
        return aNeedsHuman ? -1 : 1;
      }
      return b.lastMessageAt.compareTo(a.lastMessageAt);
    });

    return filtered;
  }

  ConversationListState copyWith({
    ConversationListStatus? status,
    List<Conversation>? conversations,
    ConversationFilter? filter,
    String? searchQuery,
    String? selectedConversationId,
    String? errorMessage,
  }) {
    return ConversationListState(
      status: status ?? this.status,
      conversations: conversations ?? this.conversations,
      filter: filter ?? this.filter,
      searchQuery: searchQuery ?? this.searchQuery,
      selectedConversationId:
          selectedConversationId ?? this.selectedConversationId,
      errorMessage: errorMessage,
    );
  }

  @override
  List<Object?> get props => [
        status,
        conversations,
        filter,
        searchQuery,
        selectedConversationId,
        errorMessage,
      ];
}
