import 'package:flutter/material.dart' hide Badge;
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../../models/child_presentation.dart';
import '../../services/evaluation_provider.dart';
import '../../services/sound_service.dart';
import '../../widgets/animated_badge.dart';
import '../../widgets/star_rating.dart';
import '../../widgets/confetti_overlay.dart';
import '../recording_screen.dart';

/// Lower-primary results screen for ages 6-8.
/// Uses icon-based metrics with star ratings, badges, no numerical scores.
/// Visual and engaging with simple feedback.
class LowerPrimaryResultsScreen extends StatefulWidget {
  final LowerPrimaryPresentation presentation;

  const LowerPrimaryResultsScreen({super.key, required this.presentation});

  @override
  State<LowerPrimaryResultsScreen> createState() =>
      _LowerPrimaryResultsScreenState();
}

class _LowerPrimaryResultsScreenState extends State<LowerPrimaryResultsScreen>
    with TickerProviderStateMixin {
  late AnimationController _celebrationController;
  bool _showConfetti = false;
  bool _hasPlayedSound = false;

  @override
  void initState() {
    super.initState();
    _celebrationController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    // Play celebration after a short delay
    Future.delayed(const Duration(milliseconds: 500), () {
      if (mounted && !_hasPlayedSound) {
        _hasPlayedSound = true;
        _playCelebration();
      }
    });
  }

  void _playCelebration() {
    setState(() => _showConfetti = true);
    _celebrationController.forward();
    SoundService().playCelebration();
  }

  @override
  void dispose() {
    _celebrationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final presentation = widget.presentation;

    return Scaffold(
      body: Stack(
        children: [
          // Background gradient
          Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFF667EEA),
                  Color(0xFF764BA2),
                  Color(0xFFF093FB),
                ],
              ),
            ),
          ),

          // Main content
          SafeArea(
            child: Column(
              children: [
                // Header
                _buildHeader(),

                // Success message
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        // Celebration icon
                        _buildCelebrationIcon(),
                        const SizedBox(height: 24),

                        // Message
                        _buildMessage(presentation.message),
                        const SizedBox(height: 32),

                        // Metrics section
                        _buildMetricsSection(presentation.metrics),
                        const SizedBox(height: 32),

                        // Badge section
                        if (presentation.badge != null)
                          _buildBadgeSection(presentation.badge!),
                        const SizedBox(height: 24),

                        // Try again button
                        _buildTryAgainButton(),
                        const SizedBox(height: 20),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Confetti overlay
          ConfettiOverlay(
            isPlaying: _showConfetti,
            particleCount: 50,
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          IconButton(
            onPressed: _goBack,
            icon: const Icon(Icons.arrow_back_ios),
            color: Colors.white,
          ),
          const Spacer(),
          const Text(
            'Great Job!',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const Spacer(),
          const SizedBox(width: 48),
        ],
      ),
    );
  }

  Widget _buildCelebrationIcon() {
    return Container(
      width: 120,
      height: 120,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: Colors.white.withValues(alpha: 0.2),
      ),
      child: const Center(
        child: Text(
          '🎉',
          style: TextStyle(fontSize: 60),
        ),
      ),
    )
        .animate()
        .fadeIn(duration: 600.ms)
        .scale(
          begin: const Offset(0.5, 0.5),
          end: const Offset(1, 1),
          curve: Curves.elasticOut,
          duration: 1000.ms,
        )
        .then()
        .shimmer(duration: 2000.ms);
  }

  Widget _buildMessage(ChildMessage message) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        message.text.isNotEmpty ? message.text : 'You did amazing!',
        style: const TextStyle(
          fontSize: 22,
          fontWeight: FontWeight.w600,
          color: Colors.white,
        ),
        textAlign: TextAlign.center,
      ),
    ).animate().fadeIn(delay: 300.ms, duration: 500.ms).slideY(
          begin: 0.2,
          end: 0,
        );
  }

  Widget _buildMetricsSection(List<IconMetric> metrics) {
    if (metrics.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          const Text(
            'Your Powers',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Color(0xFF667EEA),
            ),
          ),
          const SizedBox(height: 20),
          ...metrics.asMap().entries.map((entry) {
            final index = entry.key;
            final metric = entry.value;
            return _buildMetricRow(metric, index);
          }),
        ],
      ),
    ).animate().fadeIn(delay: 500.ms, duration: 600.ms).slideY(
          begin: 0.3,
          end: 0,
        );
  }

  Widget _buildMetricRow(IconMetric metric, int index) {
    // Parse color if provided
    Color metricColor = const Color(0xFF667EEA);
    if (metric.color != null) {
      try {
        metricColor = Color(
          int.parse(metric.color!.replaceFirst('#', '0xFF')),
        );
      } catch (_) {}
    }

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        children: [
          // Icon
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: metricColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(15),
            ),
            child: Center(
              child: Text(
                metric.icon,
                style: const TextStyle(fontSize: 28),
              ),
            ),
          ),
          const SizedBox(width: 16),

          // Label or ID
          Expanded(
            child: Text(
              metric.label ?? _formatMetricId(metric.id),
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
            ),
          ),

          // Stars if level is provided
          if (metric.level != null)
            StarRating(
              level: metric.level!,
              maxLevel: metric.maxLevel,
              starSize: 20,
              activeColor: Colors.amber,
              playSound: false,
            ),
        ],
      ),
    )
        .animate()
        .fadeIn(
          delay: Duration(milliseconds: 600 + (index * 150)),
          duration: 400.ms,
        )
        .slideX(begin: 0.2, end: 0);
  }

  String _formatMetricId(String id) {
    // Convert snake_case to Title Case
    return id
        .split('_')
        .map((word) => word.isNotEmpty
            ? '${word[0].toUpperCase()}${word.substring(1)}'
            : '')
        .join(' ');
  }

  Widget _buildBadgeSection(Badge badge) {
    return Column(
      children: [
        const Text(
          'You earned a badge!',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ).animate().fadeIn(delay: 1000.ms, duration: 500.ms),
        const SizedBox(height: 16),
        AnimatedBadge(
          badge: badge,
          size: 100,
          animationDelay: 1200.ms,
        ),
      ],
    );
  }

  Widget _buildTryAgainButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _goBack,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white,
          foregroundColor: const Color(0xFF667EEA),
          padding: const EdgeInsets.symmetric(vertical: 18),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(25),
          ),
          elevation: 8,
          shadowColor: Colors.black.withValues(alpha: 0.3),
        ),
        child: const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.mic, size: 26),
            SizedBox(width: 10),
            Text(
              'Try Again!',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    )
        .animate()
        .fadeIn(delay: 1400.ms, duration: 600.ms)
        .slideY(begin: 0.5, end: 0);
  }

  void _goBack() {
    context.read<EvaluationProvider>().reset();
    Navigator.pushAndRemoveUntil(
      context,
      PageRouteBuilder(
        pageBuilder: (context, animation, secondaryAnimation) =>
            const RecordingScreen(),
        transitionsBuilder: (context, animation, secondaryAnimation, child) {
          return FadeTransition(
            opacity: animation,
            child: child,
          );
        },
        transitionDuration: const Duration(milliseconds: 400),
      ),
      (route) => false,
    );
  }
}
