import 'package:flutter/material.dart';
import '../services/sound_service.dart';

/// Animated progress bar widget for displaying scores.
/// Used primarily for upper-primary age group (ages 9-10).
class AnimatedProgressBar extends StatefulWidget {
  final String label;
  final int value; // 0-100
  final Color color;
  final Duration animationDelay;
  final Duration animationDuration;
  final bool showValue;
  final bool playSound;
  final double height;
  final double borderRadius;

  const AnimatedProgressBar({
    super.key,
    required this.label,
    required this.value,
    required this.color,
    this.animationDelay = Duration.zero,
    this.animationDuration = const Duration(milliseconds: 1500),
    this.showValue = true,
    this.playSound = true,
    this.height = 20,
    this.borderRadius = 10,
  });

  @override
  State<AnimatedProgressBar> createState() => _AnimatedProgressBarState();
}

class _AnimatedProgressBarState extends State<AnimatedProgressBar>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: widget.animationDuration,
    );
    _animation = Tween<double>(
      begin: 0,
      end: widget.value / 100,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));

    Future.delayed(widget.animationDelay, () {
      if (mounted) {
        _controller.forward();
        if (widget.playSound) {
          SoundService().play('progress_fill');
        }
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  widget.label,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 16,
                  ),
                ),
                if (widget.showValue)
                  Text(
                    '${(_animation.value * 100).round()}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                      color: widget.color,
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            Container(
              height: widget.height,
              decoration: BoxDecoration(
                color: widget.color.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(widget.borderRadius),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(widget.borderRadius),
                child: Stack(
                  children: [
                    // Progress fill
                    FractionallySizedBox(
                      widthFactor: _animation.value,
                      child: Container(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [
                              widget.color,
                              widget.color.withValues(alpha: 0.7),
                            ],
                          ),
                          borderRadius:
                              BorderRadius.circular(widget.borderRadius),
                        ),
                      ),
                    ),
                    // Shine effect
                    if (_animation.value > 0.05)
                      AnimatedPositioned(
                        duration: widget.animationDuration,
                        left: (_animation.value *
                                MediaQuery.of(context).size.width *
                                0.7) -
                            30,
                        top: 0,
                        bottom: 0,
                        child: Container(
                          width: 30,
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                Colors.transparent,
                                Colors.white.withValues(alpha: 0.3),
                                Colors.transparent,
                              ],
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

/// Compact progress bar for displaying multiple metrics
class CompactProgressBar extends StatelessWidget {
  final String label;
  final int value;
  final Color color;
  final double height;

  const CompactProgressBar({
    super.key,
    required this.label,
    required this.value,
    required this.color,
    this.height = 8,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade600,
              ),
            ),
            Text(
              '$value',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        Container(
          height: height,
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.15),
            borderRadius: BorderRadius.circular(height / 2),
          ),
          child: FractionallySizedBox(
            alignment: Alignment.centerLeft,
            widthFactor: value / 100,
            child: Container(
              decoration: BoxDecoration(
                color: color,
                borderRadius: BorderRadius.circular(height / 2),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
