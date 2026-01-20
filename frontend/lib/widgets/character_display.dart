import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../services/sound_service.dart';
import '../services/tts_service.dart';

/// Character display widget for pre-primary age group (ages 3-5).
/// Shows animated characters (lion, mouse) based on voice strength.
class CharacterDisplay extends StatefulWidget {
  final String character; // "lion", "mouse", etc.
  final String state; // "roaring", "celebrating", "encouraging", "sleeping"
  final double size;
  final VoidCallback? onTap;
  final bool playSound;

  const CharacterDisplay({
    super.key,
    required this.character,
    required this.state,
    this.size = 200,
    this.onTap,
    this.playSound = true,
  });

  @override
  State<CharacterDisplay> createState() => _CharacterDisplayState();
}

class _CharacterDisplayState extends State<CharacterDisplay> {
  @override
  void initState() {
    super.initState();
    // Play sound based on character state
    if (widget.playSound) {
      _playCharacterSound();
    }
  }

  void _playCharacterSound() {
    final soundService = SoundService();
    switch (widget.character.toLowerCase()) {
      case 'lion':
        if (widget.state == 'roaring') {
          soundService.play('lion_roar');
        } else {
          soundService.play('celebration_chime');
        }
        break;
      case 'mouse':
        soundService.play('mouse_squeak');
        break;
      default:
        soundService.play('celebration_chime');
    }
  }

  String _getCharacterEmoji() {
    final character = widget.character.toLowerCase();
    final state = widget.state.toLowerCase();

    if (character == 'lion') {
      switch (state) {
        case 'roaring':
          return '🦁';
        case 'celebrating':
          return '🦁';
        case 'encouraging':
          return '🦁';
        case 'sleeping':
          return '🦁';
        default:
          return '🦁';
      }
    } else if (character == 'mouse') {
      return '🐭';
    }
    return '🌟';
  }

  String _getStateEmoji() {
    switch (widget.state.toLowerCase()) {
      case 'roaring':
        return '💪';
      case 'celebrating':
        return '🎉';
      case 'encouraging':
        return '💖';
      case 'sleeping':
        return '💤';
      default:
        return '✨';
    }
  }

  Color _getBackgroundColor() {
    switch (widget.character.toLowerCase()) {
      case 'lion':
        return Colors.orange.shade100;
      case 'mouse':
        return Colors.grey.shade200;
      default:
        return Colors.amber.shade100;
    }
  }

  Color _getAccentColor() {
    switch (widget.character.toLowerCase()) {
      case 'lion':
        return Colors.orange;
      case 'mouse':
        return Colors.grey;
      default:
        return Colors.amber;
    }
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        // Play sound again on tap
        _playCharacterSound();
        widget.onTap?.call();
      },
      child: Container(
        width: widget.size,
        height: widget.size,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: RadialGradient(
            colors: [
              _getBackgroundColor(),
              _getAccentColor().withValues(alpha: 0.3),
            ],
          ),
          boxShadow: [
            BoxShadow(
              color: _getAccentColor().withValues(alpha: 0.3),
              blurRadius: 30,
              spreadRadius: 10,
            ),
          ],
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Main character emoji
            Text(
              _getCharacterEmoji(),
              style: TextStyle(fontSize: widget.size * 0.45),
            ),
            // State emoji (positioned at bottom-right)
            Positioned(
              right: widget.size * 0.1,
              bottom: widget.size * 0.1,
              child: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.1),
                      blurRadius: 10,
                    ),
                  ],
                ),
                child: Text(
                  _getStateEmoji(),
                  style: TextStyle(fontSize: widget.size * 0.15),
                ),
              )
                  .animate(
                    delay: 500.ms,
                  )
                  .scale(
                    begin: const Offset(0, 0),
                    duration: 400.ms,
                    curve: Curves.elasticOut,
                  ),
            ),
          ],
        ),
      )
          .animate()
          .scale(
            begin: const Offset(0.5, 0.5),
            duration: 600.ms,
            curve: Curves.elasticOut,
          )
          .then()
          .animate(onPlay: (controller) => controller.repeat(reverse: true))
          .scale(
            begin: const Offset(1, 1),
            end: const Offset(1.05, 1.05),
            duration: 1000.ms,
          ),
    );
  }
}

/// Voice strength indicator for pre-primary
class VoiceStrengthIndicator extends StatelessWidget {
  final String voiceStrength; // "lion", "mouse", "just_right"
  final double size;

  const VoiceStrengthIndicator({
    super.key,
    required this.voiceStrength,
    this.size = 100,
  });

  @override
  Widget build(BuildContext context) {
    String emoji;
    String label;
    Color color;

    switch (voiceStrength.toLowerCase()) {
      case 'lion':
        emoji = '🦁';
        label = 'ROAR!';
        color = Colors.orange;
        break;
      case 'mouse':
        emoji = '🐭';
        label = 'Speak up!';
        color = Colors.grey;
        break;
      default:
        emoji = '⭐';
        label = 'Perfect!';
        color = Colors.amber;
    }

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: color.withValues(alpha: 0.2),
            border: Border.all(color: color, width: 3),
          ),
          child: Center(
            child: Text(
              emoji,
              style: TextStyle(fontSize: size * 0.5),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}

/// Message bubble for character speech
class CharacterMessageBubble extends StatelessWidget {
  final String message;
  final String? character;
  final bool ttsEnabled;
  final VoidCallback? onTap;

  const CharacterMessageBubble({
    super.key,
    required this.message,
    this.character,
    this.ttsEnabled = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        if (ttsEnabled) {
          if (character != null) {
            TtsService().speakAsCharacter(message, character!);
          } else {
            TtsService().speak(message);
          }
        }
        onTap?.call();
      },
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 24),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.orange.withValues(alpha: 0.2),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Row(
          children: [
            Expanded(
              child: Text(
                message,
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  height: 1.4,
                ),
                textAlign: TextAlign.center,
              ),
            ),
            if (ttsEnabled) ...[
              const SizedBox(width: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.orange.shade100,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.volume_up_rounded,
                  color: Colors.orange.shade700,
                  size: 24,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
