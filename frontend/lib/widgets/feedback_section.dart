import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

class FeedbackSection extends StatelessWidget {
  final String title;
  final IconData icon;
  final Color color;
  final int score;
  final List<String> feedback;
  final String? extraInfo;
  final int delay;

  const FeedbackSection({
    super.key,
    required this.title,
    required this.icon,
    required this.color,
    required this.score,
    required this.feedback,
    this.extraInfo,
    this.delay = 0,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
          leading: Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          title: Row(
            children: [
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ),
              _buildScoreBadge(),
            ],
          ),
          children: [
            if (extraInfo != null)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 12),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: color.withValues(alpha: 0.2)),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: color, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        extraInfo!,
                        style: TextStyle(
                          color: color,
                          fontSize: 13,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ...feedback.map((text) => _buildFeedbackItem(text)),
          ],
        ),
      ),
    )
        .animate()
        .fadeIn(delay: Duration(milliseconds: delay), duration: 400.ms)
        .slideX(begin: 0.1, end: 0);
  }

  Widget _buildFeedbackItem(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            margin: const EdgeInsets.only(top: 6),
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                color: Colors.grey[700],
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildScoreBadge() {
    Color bgColor;
    Color textColor;
    IconData badgeIcon;

    if (score >= 80) {
      bgColor = const Color(0xFF4CAF50).withValues(alpha: 0.1);
      textColor = const Color(0xFF4CAF50);
      badgeIcon = Icons.star;
    } else if (score >= 60) {
      bgColor = const Color(0xFFFF9800).withValues(alpha: 0.1);
      textColor = const Color(0xFFFF9800);
      badgeIcon = Icons.thumb_up;
    } else {
      bgColor = const Color(0xFFF44336).withValues(alpha: 0.1);
      textColor = const Color(0xFFF44336);
      badgeIcon = Icons.trending_up;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(badgeIcon, color: textColor, size: 16),
          const SizedBox(width: 4),
          Text(
            '$score',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: textColor,
            ),
          ),
        ],
      ),
    );
  }
}
