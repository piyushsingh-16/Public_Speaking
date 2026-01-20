import 'package:flutter/material.dart' hide Badge;
import 'package:flutter_animate/flutter_animate.dart';
import 'package:provider/provider.dart';
import '../../models/child_presentation.dart';
import '../../services/evaluation_provider.dart';
import '../../services/sound_service.dart';
import '../../services/tts_service.dart';
import '../../widgets/animated_badge.dart';
import '../../widgets/character_display.dart';
import '../../widgets/confetti_overlay.dart';
import '../recording_screen.dart';

/// Pre-primary results screen for ages 3-5.
/// Uses character-based feedback (lion/mouse), single badge, and TTS.
/// No numbers or scores shown - purely visual and auditory feedback.
class PrePrimaryResultsScreen extends StatefulWidget {
  final PrePrimaryPresentation presentation;

  const PrePrimaryResultsScreen({super.key, required this.presentation});

  @override
  State<PrePrimaryResultsScreen> createState() =>
      _PrePrimaryResultsScreenState();
}

class _PrePrimaryResultsScreenState extends State<PrePrimaryResultsScreen>
    with TickerProviderStateMixin {
  late AnimationController _bounceController;
  late AnimationController _pulseController;
  bool _showConfetti = false;
  bool _hasPlayedSound = false;

  @override
  void initState() {
    super.initState();
    _bounceController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    )..repeat(reverse: true);

    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    )..repeat(reverse: true);

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

    // Play character sound
    final character = widget.presentation.visuals.mainCharacter;
    SoundService().playCharacterSound(character);

    // Speak the message using TTS
    if (widget.presentation.message.ttsEnabled) {
      final message = widget.presentation.message.text;
      TtsService().speakAsCharacter(message, character);
    }
  }

  @override
  void dispose() {
    _bounceController.dispose();
    _pulseController.dispose();
    TtsService().stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final presentation = widget.presentation;
    final character = presentation.visuals.mainCharacter;
    final characterState = presentation.visuals.characterState;

    return Scaffold(
      body: Stack(
        children: [
          // Background gradient based on character
          Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: _getBackgroundColors(character),
              ),
            ),
          ),

          // Main content
          SafeArea(
            child: Column(
              children: [
                // Back button
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      IconButton(
                        onPressed: _goBack,
                        icon: const Icon(Icons.arrow_back_ios),
                        color: Colors.white,
                      ),
                    ],
                  ),
                ),

                // Main character display
                Expanded(
                  flex: 3,
                  child: _buildCharacterSection(character, characterState),
                ),

                // Message bubble
                Expanded(
                  flex: 2,
                  child: _buildMessageSection(),
                ),

                // Badge section
                if (presentation.badge != null)
                  Expanded(
                    flex: 2,
                    child: _buildBadgeSection(presentation.badge!),
                  ),

                // Try again button
                Padding(
                  padding: const EdgeInsets.all(24),
                  child: _buildTryAgainButton(),
                ),
              ],
            ),
          ),

          // Confetti overlay
          ConfettiOverlay(
            isPlaying: _showConfetti,
            particleCount: 60,
          ),
        ],
      ),
    );
  }

  Widget _buildCharacterSection(String character, String state) {
    return Center(
      child: AnimatedBuilder(
        animation: _bounceController,
        builder: (context, child) {
          return Transform.translate(
            offset: Offset(0, -20 * _bounceController.value),
            child: child,
          );
        },
        child: CharacterDisplay(
          character: character,
          state: state,
          size: 200,
        ).animate().fadeIn(duration: 800.ms).scale(
              begin: const Offset(0.5, 0.5),
              end: const Offset(1, 1),
              curve: Curves.elasticOut,
              duration: 1200.ms,
            ),
      ),
    );
  }

  Widget _buildMessageSection() {
    final message = widget.presentation.message;
    final character = widget.presentation.visuals.mainCharacter;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: CharacterMessageBubble(
        message: message.text.isNotEmpty ? message.text : _getDefaultMessage(character),
        character: character,
        onTap: () {
          // Replay the message
          TtsService().speakAsCharacter(
            message.text.isNotEmpty ? message.text : _getDefaultMessage(character),
            character,
          );
        },
      ).animate().fadeIn(delay: 600.ms, duration: 600.ms).slideY(
            begin: 0.3,
            end: 0,
            curve: Curves.easeOutBack,
          ),
    );
  }

  Widget _buildBadgeSection(Badge badge) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            'You earned a badge!',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: Colors.white.withValues(alpha: 0.9),
            ),
          ).animate().fadeIn(delay: 1000.ms, duration: 500.ms),
          const SizedBox(height: 16),
          AnimatedBadge(
            badge: badge,
            size: 100,
          ).animate().fadeIn(delay: 1200.ms, duration: 600.ms).scale(
                begin: const Offset(0, 0),
                end: const Offset(1, 1),
                curve: Curves.elasticOut,
                duration: 1000.ms,
              ),
        ],
      ),
    );
  }

  Widget _buildTryAgainButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _goBack,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.white,
          foregroundColor: _getPrimaryColor(widget.presentation.visuals.mainCharacter),
          padding: const EdgeInsets.symmetric(vertical: 20),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(30),
          ),
          elevation: 8,
          shadowColor: Colors.black.withValues(alpha: 0.3),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.mic, size: 28),
            const SizedBox(width: 12),
            const Text(
              'Speak Again!',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    )
        .animate()
        .fadeIn(delay: 1500.ms, duration: 600.ms)
        .slideY(begin: 0.5, end: 0);
  }

  List<Color> _getBackgroundColors(String character) {
    switch (character) {
      case 'lion':
        return [
          const Color(0xFFFF9800),
          const Color(0xFFFFB74D),
          const Color(0xFFFFF3E0),
        ];
      case 'mouse':
        return [
          const Color(0xFF9E9E9E),
          const Color(0xFFBDBDBD),
          const Color(0xFFF5F5F5),
        ];
      case 'elephant':
        return [
          const Color(0xFF7986CB),
          const Color(0xFF9FA8DA),
          const Color(0xFFE8EAF6),
        ];
      default:
        return [
          const Color(0xFF4CAF50),
          const Color(0xFF81C784),
          const Color(0xFFE8F5E9),
        ];
    }
  }

  Color _getPrimaryColor(String? character) {
    switch (character) {
      case 'lion':
        return const Color(0xFFFF9800);
      case 'mouse':
        return const Color(0xFF757575);
      case 'elephant':
        return const Color(0xFF5C6BC0);
      default:
        return const Color(0xFF4CAF50);
    }
  }

  String _getDefaultMessage(String character) {
    switch (character) {
      case 'lion':
        return 'ROAR! You spoke like a brave lion!';
      case 'mouse':
        return 'Squeak! Try speaking a bit louder next time!';
      default:
        return 'Great job speaking today!';
    }
  }

  void _goBack() {
    TtsService().stop();
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
