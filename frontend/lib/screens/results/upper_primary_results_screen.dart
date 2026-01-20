import 'package:flutter/material.dart' hide Badge;
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../../models/child_presentation.dart';
import '../../services/evaluation_provider.dart';
import '../../services/sound_service.dart';
import '../../widgets/animated_badge.dart';
import '../../widgets/animated_progress_bar.dart';
import '../../widgets/confetti_overlay.dart';
import '../recording_screen.dart';

/// Upper-primary results screen for ages 9-10.
/// Uses progress bars (no numerical scores visible), single improvement tip,
/// badges earned, and optional streak tracking.
class UpperPrimaryResultsScreen extends StatefulWidget {
  final UpperPrimaryPresentation presentation;

  const UpperPrimaryResultsScreen({super.key, required this.presentation});

  @override
  State<UpperPrimaryResultsScreen> createState() =>
      _UpperPrimaryResultsScreenState();
}

class _UpperPrimaryResultsScreenState extends State<UpperPrimaryResultsScreen>
    with TickerProviderStateMixin {
  bool _showConfetti = false;
  bool _hasPlayedSound = false;

  @override
  void initState() {
    super.initState();

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
    SoundService().playCelebration();
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
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Color(0xFF1A237E),
                  Color(0xFF3949AB),
                  Color(0xFF7986CB),
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

                // Scrollable content
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        // Trophy/celebration icon
                        _buildTrophySection(),
                        const SizedBox(height: 24),

                        // Streak info if available
                        if (presentation.streak != null &&
                            presentation.streak!.current > 0)
                          _buildStreakSection(presentation.streak!),
                        const SizedBox(height: 24),

                        // Progress bars
                        _buildProgressSection(presentation.progressBars),
                        const SizedBox(height: 24),

                        // Improvement tip
                        _buildImprovementTip(presentation.improvementTip),
                        const SizedBox(height: 24),

                        // Badges earned
                        if (presentation.badgesEarned.isNotEmpty)
                          _buildBadgesSection(presentation.badgesEarned),
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
            particleCount: 40,
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
            'Your Progress',
            style: TextStyle(
              fontSize: 22,
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

  Widget _buildTrophySection() {
    return Container(
      width: 100,
      height: 100,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFFFD700),
            Color(0xFFFFA000),
          ],
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.amber.withValues(alpha: 0.5),
            blurRadius: 20,
            spreadRadius: 5,
          ),
        ],
      ),
      child: const Center(
        child: Text(
          '🏆',
          style: TextStyle(fontSize: 50),
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

  Widget _buildStreakSection(Streak streak) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.orange.withValues(alpha: 0.9),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text(
            '🔥',
            style: TextStyle(fontSize: 24),
          ),
          const SizedBox(width: 8),
          Text(
            streak.message ?? '${streak.current} day streak!',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ],
      ),
    ).animate().fadeIn(delay: 300.ms, duration: 500.ms).slideY(
          begin: -0.3,
          end: 0,
        );
  }

  Widget _buildProgressSection(List<ProgressBarMetric> progressBars) {
    if (progressBars.isEmpty) return const SizedBox.shrink();

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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.trending_up, color: Color(0xFF3949AB)),
              SizedBox(width: 8),
              Text(
                'Your Skills',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1A237E),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          ...progressBars.asMap().entries.map((entry) {
            final index = entry.key;
            final bar = entry.value;
            return _buildProgressBarRow(bar, index);
          }),
        ],
      ),
    ).animate().fadeIn(delay: 500.ms, duration: 600.ms).slideY(
          begin: 0.3,
          end: 0,
        );
  }

  Widget _buildProgressBarRow(ProgressBarMetric bar, int index) {
    // Parse color
    Color barColor = const Color(0xFF4CAF50);
    try {
      barColor = Color(int.parse(bar.color.replaceFirst('#', '0xFF')));
    } catch (_) {}

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: AnimatedProgressBar(
        label: bar.label,
        value: bar.value,
        color: barColor,
        height: 16,
        animationDelay: Duration(milliseconds: 600 + (index * 200)),
        showValue: false, // Don't show numbers for this age group
        playSound: false,
      ),
    );
  }

  Widget _buildImprovementTip(ImprovementTip tip) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Colors.amber.shade100,
            Colors.amber.shade50,
          ],
        ),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: Colors.amber.shade300,
          width: 2,
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: Colors.amber.shade200,
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Text(
              '💡',
              style: TextStyle(fontSize: 24),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Tip for next time',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: Colors.amber,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  tip.text,
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                    color: Colors.amber.shade900,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    ).animate().fadeIn(delay: 1200.ms, duration: 600.ms).slideX(
          begin: 0.2,
          end: 0,
        );
  }

  Widget _buildBadgesSection(List<Badge> badges) {
    return Column(
      children: [
        const Text(
          'Badges Earned',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ).animate().fadeIn(delay: 1400.ms, duration: 500.ms),
        const SizedBox(height: 16),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          alignment: WrapAlignment.center,
          children: badges.asMap().entries.map((entry) {
            final index = entry.key;
            final badge = entry.value;
            return AnimatedBadge(
              badge: badge,
              size: 80,
              animationDelay: Duration(milliseconds: 1500 + (index * 200)),
            );
          }).toList(),
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
          foregroundColor: const Color(0xFF3949AB),
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          elevation: 8,
          shadowColor: Colors.black.withValues(alpha: 0.3),
        ),
        child: const Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.mic, size: 24),
            SizedBox(width: 10),
            Text(
              'Practice Again',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    )
        .animate()
        .fadeIn(delay: 1800.ms, duration: 600.ms)
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
