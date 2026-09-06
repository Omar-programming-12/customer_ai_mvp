import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';
import '../cubit/conversation_list_state.dart';
import 'conversation_status_style.dart';

class FilterChipsRow extends StatelessWidget {
  const FilterChipsRow({
    super.key,
    required this.selected,
    required this.onSelected,
  });

  final ConversationFilter selected;
  final ValueChanged<ConversationFilter> onSelected;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      padding: const EdgeInsets.symmetric(horizontal: 32),
      decoration: const BoxDecoration(
        color: AppColors.surface,
        border: Border(bottom: BorderSide(color: AppColors.border)),
      ),
      child: Row(
        children: [
          // Scrollable rather than a plain Row: five chips plus their
          // labels can exceed the available width once the page shrinks
          // below its ideal desktop size, and a bare Row would rather
          // overflow than scroll.
          Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  for (final filter in ConversationFilter.values) ...[
                    _FilterChip(
                      filter: filter,
                      selected: filter == selected,
                      onTap: () => onSelected(filter),
                    ),
                    const SizedBox(width: 8),
                  ],
                ],
              ),
            ),
          ),
          const SizedBox(width: 12),
          FilledButton.icon(
            onPressed: null,
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.brand,
              disabledBackgroundColor: AppColors.brand,
              disabledForegroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 16),
            ),
            icon: const Icon(Icons.add, size: 16),
            label: const Text('محادثة جديدة'),
          ),
        ],
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  const _FilterChip({
    required this.filter,
    required this.selected,
    required this.onTap,
  });

  final ConversationFilter filter;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final matchingStatus = filter.matchingStatus;
    final dotColor = matchingStatus == null
        ? null
        : ConversationStatusStyle.of(matchingStatus).dotColor;
    final label = matchingStatus == null
        ? 'الكل'
        : ConversationStatusStyle.of(matchingStatus).label;

    return Material(
      color: selected ? AppColors.textPrimary : AppColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(999),
        side: BorderSide(
          color: selected ? AppColors.textPrimary : AppColors.border,
        ),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(999),
        onTap: onTap,
        child: Container(
          height: 32,
          padding: const EdgeInsets.symmetric(horizontal: 14),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (dotColor != null) ...[
                Container(
                  width: 6,
                  height: 6,
                  decoration: BoxDecoration(color: dotColor, shape: BoxShape.circle),
                ),
                const SizedBox(width: 6),
              ],
              Text(
                label,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: selected ? Colors.white : AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
