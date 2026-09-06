import 'package:flutter/material.dart';

import '../../../conversations/presentation/pages/conversations_page.dart';
import '../widgets/app_sidebar.dart';
import 'placeholder_page.dart';

/// The top-level frame: sidebar + whichever page is active. Which index is
/// selected is transient UI state local to this single widget, so it's a
/// plain `StatefulWidget` rather than a Cubit - promoting it to shared state
/// would only make sense once something outside this widget needs to know
/// or change the active page.
class AppShellPage extends StatefulWidget {
  const AppShellPage({super.key});

  @override
  State<AppShellPage> createState() => _AppShellPageState();
}

class _AppShellPageState extends State<AppShellPage> {
  // "المحادثات" (index 1) is the flagship screen for this phase, so it
  // opens selected by default rather than the empty "لوحة التحكم" overview.
  int _selectedIndex = 1;

  static const _pages = [
    PlaceholderPage(title: 'لوحة التحكم'),
    ConversationsPage(),
    PlaceholderPage(title: 'العملاء'),
    PlaceholderPage(title: 'التقارير'),
    PlaceholderPage(title: 'الإعدادات'),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          AppSidebar(
            selectedIndex: _selectedIndex,
            onSelect: (index) => setState(() => _selectedIndex = index),
          ),
          Expanded(
            child: IndexedStack(
              index: _selectedIndex,
              children: _pages,
            ),
          ),
        ],
      ),
    );
  }
}
