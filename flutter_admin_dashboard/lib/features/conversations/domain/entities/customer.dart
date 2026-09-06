import 'package:equatable/equatable.dart';

/// A snapshot of what the support team needs to know about a customer while
/// handling their conversation - identity, history, and purchase context.
class Customer extends Equatable {
  const Customer({
    required this.id,
    required this.name,
    required this.phoneNumber,
    required this.customerSince,
    required this.previousConversationsCount,
    this.tags = const [],
    this.lastPurchaseProductName,
    this.lastPurchaseBranch,
    this.lastPurchaseDate,
  });

  final String id;
  final String name;
  final String phoneNumber;
  final DateTime customerSince;
  final int previousConversationsCount;
  final List<String> tags;

  /// The following three are null when the customer has no purchase on
  /// record - the "آخر عملية شراء" card is simply omitted in that case.
  final String? lastPurchaseProductName;
  final String? lastPurchaseBranch;
  final DateTime? lastPurchaseDate;

  @override
  List<Object?> get props => [
        id,
        name,
        phoneNumber,
        customerSince,
        previousConversationsCount,
        tags,
        lastPurchaseProductName,
        lastPurchaseBranch,
        lastPurchaseDate,
      ];
}
