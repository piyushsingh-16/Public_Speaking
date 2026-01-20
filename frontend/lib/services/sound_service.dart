import 'package:audioplayers/audioplayers.dart';

/// Service for playing sound effects throughout the app.
/// Uses singleton pattern for consistent audio management.
class SoundService {
  static final SoundService _instance = SoundService._internal();
  factory SoundService() => _instance;
  SoundService._internal();

  final AudioPlayer _player = AudioPlayer();
  bool _soundEnabled = true;
  bool _initialized = false;

  /// Sound effect file mapping
  static const Map<String, String> _soundFiles = {
    // Celebration sounds
    'celebration_fanfare': 'sounds/celebration_fanfare.mp3',
    'celebration_chime': 'sounds/celebration_chime.mp3',
    'encouragement_chime': 'sounds/encouragement_chime.mp3',

    // Character sounds (for pre-primary)
    'lion_roar': 'sounds/lion_roar.mp3',
    'mouse_squeak': 'sounds/mouse_squeak.mp3',

    // Achievement sounds
    'badge_unlock': 'sounds/badge_unlock.mp3',
    'star_collect': 'sounds/star_collect.mp3',

    // Progress sounds (for upper-primary)
    'progress_fill': 'sounds/progress_fill.mp3',
    'level_up': 'sounds/level_up.mp3',

    // General feedback
    'success': 'sounds/success.mp3',
    'tap': 'sounds/tap.mp3',
  };

  /// Initialize the sound service
  Future<void> init() async {
    if (_initialized) return;

    // Set default volume
    await _player.setVolume(0.7);
    _initialized = true;
  }

  /// Play a sound effect by name
  Future<void> play(String? soundEffect) async {
    if (!_soundEnabled || soundEffect == null || soundEffect.isEmpty) return;

    await init();

    final file = _soundFiles[soundEffect];
    if (file != null) {
      try {
        await _player.stop(); // Stop any currently playing sound
        await _player.play(AssetSource(file));
      } catch (e) {
        // Silently fail if sound file not found
        // This allows the app to work without sound assets
        debugPrint('SoundService: Could not play $soundEffect: $e');
      }
    }
  }

  /// Play celebration sound based on performance level
  Future<void> playCelebration({bool isHighScore = false}) async {
    if (isHighScore) {
      await play('celebration_fanfare');
    } else {
      await play('celebration_chime');
    }
  }

  /// Play character sound for pre-primary
  Future<void> playCharacterSound(String voiceStrength) async {
    switch (voiceStrength) {
      case 'lion':
        await play('lion_roar');
        break;
      case 'mouse':
        await play('mouse_squeak');
        break;
      default:
        await play('celebration_chime');
    }
  }

  /// Toggle sound on/off
  void toggleSound() {
    _soundEnabled = !_soundEnabled;
  }

  /// Check if sound is enabled
  bool get isSoundEnabled => _soundEnabled;

  /// Enable sound
  void enableSound() {
    _soundEnabled = true;
  }

  /// Disable sound
  void disableSound() {
    _soundEnabled = false;
  }

  /// Set volume (0.0 to 1.0)
  Future<void> setVolume(double volume) async {
    await _player.setVolume(volume.clamp(0.0, 1.0));
  }

  /// Stop currently playing sound
  Future<void> stop() async {
    await _player.stop();
  }

  /// Dispose resources
  Future<void> dispose() async {
    await _player.dispose();
  }
}

/// Debug print helper (only in debug mode)
void debugPrint(String message) {
  assert(() {
    // ignore: avoid_print
    print(message);
    return true;
  }());
}
