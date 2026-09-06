import 'package:flutter/material.dart';

import '../../../../core/theme/app_colors.dart';

/// Stands in for a nav destination that isn't built yet. Keeps the shell
/// demonstrably ready to grow (five nav items, one real feature) without
/// spending effort on screens nobody asked for yet.
class PlaceholderPage extends StatelessWidget {
  const PlaceholderPage({super.key, required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.background,
      alignment: Alignment.center,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.construction_rounded,
              size: 40, color: AppColors.textMuted),
          const SizedBox(height: 12),
          Text(
            '$title - قريبًا',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}
