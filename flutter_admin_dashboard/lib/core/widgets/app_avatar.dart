import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// An initials-based avatar. The tint is derived deterministically from
/// [name] (via its hash) so the same customer always gets the same color
/// without the caller having to track a palette index.
class AppAvatar extends StatelessWidget {
  const AppAvatar({
    super.key,
    required this.name,
    this.size = 40,
  });

  final String name;
  final double size;

  @override
  Widget build(BuildContext context) {
    final palette = AppColors.avatarPalette;
    final tint = palette[name.hashCode.abs() % palette.length];
    final trimmed = name.trim();
    final initial = trimmed.isEmpty ? '؟' : trimmed.substring(0, 1);

    return CircleAvatar(
      radius: size / 2,
      backgroundColor: tint.bg,
      child: Text(
        initial,
        style: TextStyle(
          color: tint.fg,
          fontWeight: FontWeight.bold,
          fontSize: size * 0.4,
        ),
      ),
    );
  }
}
