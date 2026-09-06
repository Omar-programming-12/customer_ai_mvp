import 'package:get_it/get_it.dart';

import '../../features/conversations/data/datasources/conversation_data_source.dart';
import '../../features/conversations/data/datasources/conversation_mock_data_source.dart';
import '../../features/conversations/data/repositories/conversation_repository_impl.dart';
import '../../features/conversations/domain/repositories/conversation_repository.dart';
import '../../features/conversations/domain/usecases/hand_back_to_ai.dart';
import '../../features/conversations/domain/usecases/resolve_conversation.dart';
import '../../features/conversations/domain/usecases/send_message.dart';
import '../../features/conversations/domain/usecases/take_over_conversation.dart';
import '../../features/conversations/domain/usecases/transfer_conversation.dart';
import '../../features/conversations/domain/usecases/watch_conversations.dart';
import '../../features/conversations/domain/usecases/watch_messages.dart';
import '../../features/conversations/presentation/cubit/conversation_list_cubit.dart';
import '../../features/conversations/presentation/cubit/conversation_thread_cubit.dart';

/// The app's single service locator. `initDependencies()` runs once from
/// `main()` before `runApp`; every layer looks its dependencies up through
/// `sl<T>()` (or, for widgets, through a `BlocProvider` that calls
/// `sl<SomeCubit>()`) instead of constructing them inline.
///
/// This is also the one place a future Firebase/FastAPI integration
/// touches: swapping the mock data source for a real one means registering
/// a Firestore-backed `ConversationDataSource` implementation here instead
/// - with every repository, use case, Cubit and widget above it untouched.
final sl = GetIt.instance;

void initDependencies() {
  // Data sources
  sl.registerLazySingleton<ConversationDataSource>(
    () => ConversationMockDataSource(),
  );

  // Repositories
  sl.registerLazySingleton<ConversationRepository>(
    () => ConversationRepositoryImpl(sl()),
  );

  // Use cases
  sl.registerLazySingleton(() => WatchConversations(sl()));
  sl.registerLazySingleton(() => WatchMessages(sl()));
  sl.registerLazySingleton(() => SendMessage(sl()));
  sl.registerLazySingleton(() => TakeOverConversation(sl()));
  sl.registerLazySingleton(() => ResolveConversation(sl()));
  sl.registerLazySingleton(() => TransferConversation(sl()));
  sl.registerLazySingleton(() => HandBackToAi(sl()));

  // Presentation - a fresh Cubit per screen visit, not a singleton: list and
  // thread state should reset if the dashboard is ever torn down and
  // rebuilt (e.g. on logout, once auth exists), which a singleton would
  // silently keep stale.
  sl.registerFactory(() => ConversationListCubit(watchConversations: sl()));
  sl.registerFactory(
    () => ConversationThreadCubit(
      watchMessages: sl(),
      sendMessage: sl(),
      takeOverConversation: sl(),
      resolveConversation: sl(),
      transferConversation: sl(),
      handBackToAi: sl(),
    ),
  );
}
