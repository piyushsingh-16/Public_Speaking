import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

class AnimatedMicButton extends StatefulWidget {
  final bool isRecording;
  final VoidCallback onTap;

  const AnimatedMicButton({
    super.key,
    required this.isRecording,
    required this.onTap,
  });

  @override
  State<AnimatedMicButton> createState() => _AnimatedMicButtonState();
}

class _AnimatedMicButtonState extends State<AnimatedMicButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    );
  }

  @override
  void didUpdateWidget(AnimatedMicButton oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isRecording) {
      _controller.repeat();
    } else {
      _controller.stop();
      _controller.reset();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Outer pulse animation when recording
          if (widget.isRecording)
            AnimatedBuilder(
              animation: _controller,
              builder: (context, child) {
                return Container(
                  width: 120 + (_controller.value * 40),
                  height: 120 + (_controller.value * 40),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.red.withValues(alpha: 0.2 * (1 - _controller.value)),
                  ),
                );
              },
            ),

          // Second pulse layer
          if (widget.isRecording)
            AnimatedBuilder(
              animation: _controller,
              builder: (context, child) {
                final delayedValue = (_controller.value + 0.3) % 1.0;
                return Container(
                  width: 120 + (delayedValue * 30),
                  height: 120 + (delayedValue * 30),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.red.withValues(alpha: 0.15 * (1 - delayedValue)),
                  ),
                );
              },
            ),

          // Main button
          AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: widget.isRecording
                    ? [
                        const Color(0xFFF44336),
                        const Color(0xFFE53935),
                      ]
                    : [
                        const Color(0xFF6C63FF),
                        const Color(0xFF5A52E0),
                      ],
              ),
              boxShadow: [
                BoxShadow(
                  color: (widget.isRecording
                          ? Colors.red
                          : const Color(0xFF6C63FF))
                      .withValues(alpha: 0.4),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Icon(
              widget.isRecording ? Icons.stop_rounded : Icons.mic,
              color: Colors.white,
              size: 48,
            ),
          )
              .animate(target: widget.isRecording ? 1 : 0)
              .scale(
                begin: const Offset(1, 1),
                end: const Offset(1.1, 1.1),
                duration: 200.ms,
              ),
        ],
      ),
    );
  }
}
