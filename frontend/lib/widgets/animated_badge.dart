import 'package:flutter/material.dart' hide Badge;
import 'package:flutter_animate/flutter_animate.dart';
import '../models/child_presentation.dart';
import '../services/sound_service.dart';

/// Animated badge widget that displays earned badges with celebration effects.
/// Used across all age groups to show achievements.
class AnimatedBadge extends StatefulWidget {
  final Badge badge;
  final double size;
  final Duration animationDelay;
  final VoidCallback? onAnimationComplete;
  final bool playSound;

  const AnimatedBadge({
    super.key,
    required this.badge,
    this.size = 120,
    this.animationDelay = Duration.zero,
    this.onAnimationComplete,
    this.playSound = true,
  });

  @override
  State<AnimatedBadge> createState() => _AnimatedBadgeState();
}

class _AnimatedBadgeState extends State<AnimatedBadge> {
  @override
  void initState() {
    super.initState();
    // Play badge unlock sound after animation starts
    if (widget.playSound) {
      Future.delayed(
        widget.animationDelay + const Duration(milliseconds: 300),
        () {
          SoundService().play('badge_unlock');
        },
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: widget.size,
      height: widget.size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: RadialGradient(
          colors: [
            Colors.amber.shade100,
            Colors.amber.shade300,
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.amber.withValues(alpha: 0.4),
            blurRadius: 20,
            spreadRadius: 5,
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            widget.badge.emoji,
            style: TextStyle(fontSize: widget.size * 0.35),
          ),
          const SizedBox(height: 4),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Text(
              widget.badge.name,
              style: TextStyle(
                fontSize: widget.size * 0.1,
                fontWeight: FontWeight.bold,
                color: Colors.amber.shade900,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    )
        .animate(delay: widget.animationDelay)
        .scale(
          begin: const Offset(0, 0),
          end: const Offset(1, 1),
          duration: 500.ms,
          curve: Curves.elasticOut,
        )
        .then()
        .shimmer(
          duration: 1000.ms,
          color: Colors.white.withValues(alpha: 0.3),
        )
        .callback(
          callback: (_) => widget.onAnimationComplete?.call(),
        );
  }
}

/// A smaller badge variant for displaying in lists or grids
class BadgeChip extends StatelessWidget {
  final Badge badge;
  final bool isLocked;
  final VoidCallback? onTap;

  const BadgeChip({
    super.key,
    required this.badge,
    this.isLocked = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: isLocked
              ? Colors.grey.shade200
              : Colors.amber.shade100,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isLocked
                ? Colors.grey.shade300
                : Colors.amber.shade400,
            width: 2,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              isLocked ? '🔒' : badge.emoji,
              style: TextStyle(
                fontSize: 20,
                color: isLocked ? Colors.grey : null,
              ),
            ),
            const SizedBox(width: 8),
            Text(
              badge.name,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: isLocked
                    ? Colors.grey.shade500
                    : Colors.amber.shade900,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
