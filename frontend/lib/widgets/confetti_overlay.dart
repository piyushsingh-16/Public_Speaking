import 'dart:math';
import 'package:flutter/material.dart';

/// Confetti animation overlay for celebrations.
/// Used across all age groups to celebrate achievements.
class ConfettiOverlay extends StatefulWidget {
  final bool isPlaying;
  final Duration duration;
  final int particleCount;

  const ConfettiOverlay({
    super.key,
    required this.isPlaying,
    this.duration = const Duration(seconds: 3),
    this.particleCount = 50,
  });

  @override
  State<ConfettiOverlay> createState() => _ConfettiOverlayState();
}

class _ConfettiOverlayState extends State<ConfettiOverlay>
    with TickerProviderStateMixin {
  late List<ConfettiParticle> _particles;
  late AnimationController _controller;
  final Random _random = Random();

  @override
  void initState() {
    super.initState();
    _particles = List.generate(
      widget.particleCount,
      (_) => ConfettiParticle(_random),
    );
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    );
    if (widget.isPlaying) {
      _controller.forward();
    }
  }

  @override
  void didUpdateWidget(ConfettiOverlay oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.isPlaying && !oldWidget.isPlaying) {
      _particles = List.generate(
        widget.particleCount,
        (_) => ConfettiParticle(_random),
      );
      _controller.reset();
      _controller.forward();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isPlaying && !_controller.isAnimating) {
      return const SizedBox.shrink();
    }

    return IgnorePointer(
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return CustomPaint(
            painter: ConfettiPainter(_particles, _controller.value),
            size: Size.infinite,
          );
        },
      ),
    );
  }
}

/// Single confetti particle
class ConfettiParticle {
  final double x;
  final double y;
  final double size;
  final Color color;
  final double speed;
  final double rotation;
  final double rotationSpeed;
  final ConfettiShape shape;

  ConfettiParticle(Random random)
      : x = random.nextDouble(),
        y = -random.nextDouble() * 0.3,
        size = random.nextDouble() * 10 + 5,
        color = _confettiColors[random.nextInt(_confettiColors.length)],
        speed = random.nextDouble() * 0.5 + 0.5,
        rotation = random.nextDouble() * 360,
        rotationSpeed = random.nextDouble() * 10 - 5,
        shape = ConfettiShape.values[random.nextInt(ConfettiShape.values.length)];

  static const List<Color> _confettiColors = [
    Color(0xFFE53935), // Red
    Color(0xFF1E88E5), // Blue
    Color(0xFF43A047), // Green
    Color(0xFFFDD835), // Yellow
    Color(0xFF8E24AA), // Purple
    Color(0xFFFF9800), // Orange
    Color(0xFF00BCD4), // Cyan
    Color(0xFFE91E63), // Pink
  ];
}

enum ConfettiShape { rectangle, circle, star }

/// Custom painter for confetti particles
class ConfettiPainter extends CustomPainter {
  final List<ConfettiParticle> particles;
  final double progress;

  ConfettiPainter(this.particles, this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    for (final particle in particles) {
      final paint = Paint()..color = particle.color;

      // Calculate position with gravity effect
      final y = (particle.y + progress * particle.speed * 1.5) * size.height;
      if (y > size.height * 1.1) continue;

      // Add slight horizontal wobble
      final wobble = sin(progress * 10 + particle.x * 10) * 20;
      final x = particle.x * size.width + wobble;

      canvas.save();
      canvas.translate(x, y);
      canvas.rotate(
        (particle.rotation + progress * particle.rotationSpeed * 360) *
            pi /
            180,
      );

      switch (particle.shape) {
        case ConfettiShape.rectangle:
          canvas.drawRect(
            Rect.fromCenter(
              center: Offset.zero,
              width: particle.size,
              height: particle.size * 0.6,
            ),
            paint,
          );
          break;
        case ConfettiShape.circle:
          canvas.drawCircle(Offset.zero, particle.size / 2, paint);
          break;
        case ConfettiShape.star:
          _drawStar(canvas, particle.size / 2, paint);
          break;
      }

      canvas.restore();
    }
  }

  void _drawStar(Canvas canvas, double radius, Paint paint) {
    final path = Path();
    final innerRadius = radius * 0.4;
    const points = 5;

    for (int i = 0; i < points * 2; i++) {
      final r = i.isEven ? radius : innerRadius;
      final angle = (i * pi / points) - (pi / 2);
      final point = Offset(r * cos(angle), r * sin(angle));
      if (i == 0) {
        path.moveTo(point.dx, point.dy);
      } else {
        path.lineTo(point.dx, point.dy);
      }
    }
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(ConfettiPainter oldDelegate) =>
      progress != oldDelegate.progress;
}

/// Floating stars animation for background celebration
class FloatingStars extends StatefulWidget {
  final int count;
  final Duration duration;

  const FloatingStars({
    super.key,
    this.count = 20,
    this.duration = const Duration(seconds: 5),
  });

  @override
  State<FloatingStars> createState() => _FloatingStarsState();
}

class _FloatingStarsState extends State<FloatingStars>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late List<FloatingStar> _stars;
  final Random _random = Random();

  @override
  void initState() {
    super.initState();
    _stars = List.generate(widget.count, (_) => FloatingStar(_random));
    _controller = AnimationController(
      vsync: this,
      duration: widget.duration,
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: AnimatedBuilder(
        animation: _controller,
        builder: (context, child) {
          return CustomPaint(
            painter: FloatingStarsPainter(_stars, _controller.value),
            size: Size.infinite,
          );
        },
      ),
    );
  }
}

class FloatingStar {
  final double x;
  final double y;
  final double size;
  final double speed;
  final double twinkleOffset;

  FloatingStar(Random random)
      : x = random.nextDouble(),
        y = random.nextDouble(),
        size = random.nextDouble() * 15 + 5,
        speed = random.nextDouble() * 0.5 + 0.5,
        twinkleOffset = random.nextDouble() * 2 * pi;
}

class FloatingStarsPainter extends CustomPainter {
  final List<FloatingStar> stars;
  final double progress;

  FloatingStarsPainter(this.stars, this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    for (final star in stars) {
      // Twinkle effect
      final twinkle =
          (sin(progress * 2 * pi * star.speed + star.twinkleOffset) + 1) / 2;
      final alpha = 0.3 + (twinkle * 0.5);

      final paint = Paint()
        ..color = Colors.amber.withValues(alpha: alpha)
        ..style = PaintingStyle.fill;

      final x = star.x * size.width;
      final y = star.y * size.height;

      // Draw simple star
      _drawStar(
        canvas,
        Offset(x, y),
        star.size * (0.8 + twinkle * 0.4),
        paint,
      );
    }
  }

  void _drawStar(Canvas canvas, Offset center, double radius, Paint paint) {
    final path = Path();
    final innerRadius = radius * 0.4;
    const points = 5;

    for (int i = 0; i < points * 2; i++) {
      final r = i.isEven ? radius : innerRadius;
      final angle = (i * pi / points) - (pi / 2);
      final point = Offset(
        center.dx + r * cos(angle),
        center.dy + r * sin(angle),
      );
      if (i == 0) {
        path.moveTo(point.dx, point.dy);
      } else {
        path.lineTo(point.dx, point.dy);
      }
    }
    path.close();
    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(FloatingStarsPainter oldDelegate) =>
      progress != oldDelegate.progress;
}
