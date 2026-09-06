/// Formats a timestamp the way the dashboard's Arabic UI copy does
/// elsewhere ("منذ دقيقتين", "أمس، 6:40 م") rather than deferring to
/// `intl`'s generic Arabic locale output, which uses different conventions
/// (Arabic-indic digits, different day names) than the rest of this UI.
String formatRelativeArabic(DateTime dateTime, {DateTime? now}) {
  final reference = now ?? DateTime.now();
  final diff = reference.difference(dateTime);

  if (diff.inSeconds < 60) return 'الآن';

  if (diff.inMinutes < 60) {
    return 'منذ ${_arabicCount(diff.inMinutes, singular: 'دقيقة', dual: 'دقيقتين', plural: 'دقائق')}';
  }

  if (diff.inHours < 24) {
    return 'منذ ${_arabicCount(diff.inHours, singular: 'ساعة', dual: 'ساعتين', plural: 'ساعات')}';
  }

  if (diff.inHours < 48) {
    return 'أمس، ${formatClockArabic(dateTime)}';
  }

  return '${dateTime.day}/${dateTime.month}/${dateTime.year}';
}

String _arabicCount(
  int count, {
  required String singular,
  required String dual,
  required String plural,
}) {
  if (count == 1) return singular;
  if (count == 2) return dual;
  if (count >= 3 && count <= 10) return '$count $plural';
  return '$count $singular';
}

String formatClockArabic(DateTime dateTime) {
  final hour24 = dateTime.hour;
  final hour12 = hour24 % 12 == 0 ? 12 : hour24 % 12;
  final minute = dateTime.minute.toString().padLeft(2, '0');
  final period = hour24 < 12 ? 'ص' : 'م';
  return '$hour12:$minute $period';
}
