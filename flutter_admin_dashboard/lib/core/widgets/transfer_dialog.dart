import 'package:flutter/material.dart';

/// Prompts for an agent name to transfer a conversation to. Returns the
/// trimmed name, or `null` if the dialog was cancelled/left empty.
///
/// A plain text field rather than a staff picker: there is no agents
/// directory/data source yet, and building one just for this dialog would
/// be scope creep beyond what this phase asked for.
Future<String?> showTransferDialog(BuildContext context) async {
  final controller = TextEditingController();

  final result = await showDialog<String>(
    context: context,
    builder: (dialogContext) => AlertDialog(
      title: const Text('تحويل المحادثة'),
      content: TextField(
        controller: controller,
        autofocus: true,
        decoration: const InputDecoration(hintText: 'اسم الموظف'),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(dialogContext).pop(),
          child: const Text('إلغاء'),
        ),
        FilledButton(
          onPressed: () => Navigator.of(dialogContext).pop(controller.text),
          child: const Text('تحويل'),
        ),
      ],
    ),
  );

  final trimmed = result?.trim();
  return (trimmed == null || trimmed.isEmpty) ? null : trimmed;
}
