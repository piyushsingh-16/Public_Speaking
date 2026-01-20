import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/sound_service.dart';

/// Star rating widget for displaying scores visually.
/// Used primarily for lower-primary age group (ages 6-8).
class StarRating extends StatelessWidget {
  final int level; // 0-maxLevel
  final int maxLevel;
  final double starSize;
  final Color activeColor;
  final Color inactiveColor;
  final Duration staggerDelay;
  final bool playSound;
  final bool animated;

  const StarRating({
    super.key,
    required this.level,
    this.maxLevel = 5,
    this.starSize = 40,
    this.activeColor = Colors.amber,
    this.inactiveColor = Colors.grey,
    this.staggerDelay = const Duration(milliseconds: 150),
    this.playSound = true,
    this.animated = true,
  });

  @override
  Widget build(BuildContext context) {
    // Play star collection sound
    if (playSound && level > 0) {
      Future.delayed(staggerDelay * level, () {
        SoundService().play('star_collect');
      });
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(maxLevel, (index) {
        final isActive = index < level;
        final star = Icon(
          isActive ? Icons.star_rounded : Icons.star_outline_rounded,
          size: starSize,
          color: isActive ? activeColor : inactiveColor.withValues(alpha: 0.3),
        );

        if (!animated) return star;

        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 2),
          child: star
              .animate(
                delay: Duration(
                  milliseconds: staggerDelay.inMilliseconds * index,
                ),
              )
              .scale(
                begin: const Offset(0, 0),
                end: const Offset(1, 1),
                duration: 300.ms,
                curve: Curves.elasticOut,
              )
              .then()
              .shimmer(
                duration: 600.ms,
                color: isActive
                    ? Colors.white.withValues(alpha: 0.4)
                    : Colors.transparent,
              ),
        );
      }),
    );
  }
}

/// Large animated star for celebration effects
class CelebrationStar extends StatelessWidget {
  final double size;
  final Color color;
  final Duration delay;

  const CelebrationStar({
    super.key,
    this.size = 60,
    this.color = Colors.amber,
    this.delay = Duration.zero,
  });

  @override
  Widget build(BuildContext context) {
    return Icon(
      Icons.star_rounded,
      size: size,
      color: color,
    )
        .animate(delay: delay)
        .scale(
          begin: const Offset(0, 0),
          end: const Offset(1, 1),
          duration: 500.ms,
          curve: Curves.elasticOut,
        )
        .then()
        .animate(onPlay: (controller) => controller.repeat(reverse: true))
        .scale(
          begin: const Offset(1, 1),
          end: const Offset(1.1, 1.1),
          duration: 800.ms,
        )
        .shimmer(duration: 1200.ms);
  }
}

/// Row of celebration stars that animate in sequence
class CelebrationStars extends StatelessWidget {
  final int count;
  final double starSize;
  final Color color;

  const CelebrationStars({
    super.key,
    this.count = 5,
    this.starSize = 40,
    this.color = Colors.amber,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(count, (index) {
        return CelebrationStar(
          size: starSize,
          color: color,
          delay: Duration(milliseconds: 100 * index),
        );
      }),
    );
  }
}
