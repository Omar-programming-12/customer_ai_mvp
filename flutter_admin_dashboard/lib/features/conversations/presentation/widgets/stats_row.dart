import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../../core/theme/app_colors.dart';
import '../../domain/entities/conversation_status.dart';
import '../cubit/conversation_list_cubit.dart';
import 'stat_card.dart';

/// The "تحتاج تدخل بشري" count is read live from
/// [ConversationListCubit] - it's the one number here the mock data source
/// actually models. The other three stand in for platform-wide metrics
/// (totals across every agent, resolution throughput) that a small in-memory
/// mock has no basis to compute; a real backend would serve them from an
/// aggregation query/endpoint rather than the conversation list itself.
class StatsRow extends StatelessWidget {
  const StatsRow({super.key});

  @override
  Widget build(BuildContext context) {
    final needsHumanCount = context.select<ConversationListCubit, int>(
      (cubit) => cubit.state.conversations
          .where((c) => c.status == ConversationStatus.needsHuman)
          .length,
    );

    return Container(
      color: AppColors.background,
      padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 18),
      child: Row(
        children: [
          const StatCard(
            label: 'محادثات نشطة',
            value: '128',
            icon: Icons.chat_bubble_rounded,
            iconColor: AppColors.brand,
            trend: '+12% عن أمس',
            trendColor: AppColors.success,
          ),
          const SizedBox(width: 16),
          StatCard(
            label: 'تحتاج تدخل بشري',
            value: '$needsHumanCount',
            icon: Icons.warning_amber_rounded,
            iconColor: AppColors.danger,
            trend: 'يتطلب إجراء فوري',
            trendColor: AppColors.danger,
          ),
          const SizedBox(width: 16),
          const StatCard(
            label: 'تم حلها اليوم',
            value: '43',
            icon: Icons.check_circle_rounded,
            iconColor: AppColors.success,
            trend: '+8 عن أمس',
            trendColor: AppColors.success,
          ),
          const SizedBox(width: 16),
          const StatCard(
            label: 'متوسط وقت الرد',
            value: '1.4 د',
            icon: Icons.access_time_rounded,
            iconColor: AppColors.brand,
            trend: 'أفضل من الهدف',
            trendColor: AppColors.success,
          ),
        ],
      ),
    );
  }
}
