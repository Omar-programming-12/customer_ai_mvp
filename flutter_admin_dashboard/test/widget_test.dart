// Smoke test for the conversations dashboard: boots the real app (DI wired
// to the mock data source, exactly as `main()` does) and checks the key
// regions of the screen actually render - sidebar nav, the conversation
// list (with seeded Arabic sample data), and the chat thread for whichever
// conversation is selected by default.

import 'dart:ui';

import 'package:flutter_test/flutter_test.dart';
import 'package:get_it/get_it.dart';

import 'package:customer_ai_admin/app.dart';
import 'package:customer_ai_admin/core/di/injection_container.dart';

void main() {
  setUp(() {
    GetIt.instance.reset();
    initDependencies();
  });

  testWidgets('dashboard renders sidebar, conversation list and chat thread',
      (WidgetTester tester) async {
    // This dashboard is desktop/web-first by design (see the brief) and
    // isn't built to reflow down to the default 800x600 test surface -
    // match it to a realistic desktop viewport instead of shrinking the UI.
    tester.view.physicalSize = const Size(1440, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(const CustomerAiAdminApp());

    // The page title renders synchronously, before any stream emits. It
    // also happens to match the sidebar's "المحادثات" nav label, hence
    // findsWidgets rather than findsOneWidget.
    expect(find.text('المحادثات'), findsWidgets);
    expect(find.text('Customer AI'), findsOneWidget);

    // Let the mock data source's streams deliver their first snapshot.
    await tester.pumpAndSettle();

    // Seeded conversations show up in the list.
    expect(find.text('أحمد محمود السيد'), findsWidgets);
    expect(find.text('مريم حسن الجندي'), findsWidgets);

    // The conversation needing human attention is surfaced, not hidden.
    expect(find.text('تحتاج تدخل بشري'), findsWidgets);

    // A conversation is auto-selected, opening the chat thread panel
    // instead of the "اختر محادثة" empty state.
    expect(find.text('اختر محادثة من القائمة لعرضها'), findsNothing);
  });
}
