import 'package:flutter_tts/flutter_tts.dart';

/// Text-to-Speech service for reading feedback aloud.
/// Primarily used for pre-primary age group (ages 3-5).
class TtsService {
  static final TtsService _instance = TtsService._internal();
  factory TtsService() => _instance;
  TtsService._internal();

  final FlutterTts _tts = FlutterTts();
  bool _initialized = false;
  bool _ttsEnabled = true;
  bool _isSpeaking = false;

  /// Initialize TTS with child-friendly settings
  Future<void> init() async {
    if (_initialized) return;

    try {
      // Set language
      await _tts.setLanguage('en-US');

      // Slow speech rate for young children (0.0 to 1.0)
      await _tts.setSpeechRate(0.4);

      // Full volume
      await _tts.setVolume(1.0);

      // Slightly higher pitch for friendlier tone
      await _tts.setPitch(1.1);

      // Set up completion handler
      _tts.setCompletionHandler(() {
        _isSpeaking = false;
      });

      // Set up error handler
      _tts.setErrorHandler((message) {
        _isSpeaking = false;
        // Silently fail - TTS is optional
      });

      _initialized = true;
    } catch (e) {
      // TTS not available on this platform
      _initialized = false;
    }
  }

  /// Speak the given text
  Future<void> speak(String text) async {
    if (!_ttsEnabled || text.isEmpty) return;

    await init();
    if (!_initialized) return;

    try {
      _isSpeaking = true;
      await _tts.speak(text);
    } catch (e) {
      _isSpeaking = false;
    }
  }

  /// Speak with a character voice (adjusts pitch/rate)
  Future<void> speakAsCharacter(String text, String character) async {
    if (!_ttsEnabled || text.isEmpty) return;

    await init();
    if (!_initialized) return;

    try {
      // Adjust voice based on character
      switch (character.toLowerCase()) {
        case 'lion':
          await _tts.setPitch(0.9); // Lower, stronger voice
          await _tts.setSpeechRate(0.35);
          break;
        case 'mouse':
          await _tts.setPitch(1.4); // Higher, softer voice
          await _tts.setSpeechRate(0.45);
          break;
        default:
          await _tts.setPitch(1.1);
          await _tts.setSpeechRate(0.4);
      }

      _isSpeaking = true;
      await _tts.speak(text);

      // Reset to default after speaking
      await Future.delayed(const Duration(milliseconds: 100));
      await _tts.setPitch(1.1);
      await _tts.setSpeechRate(0.4);
    } catch (e) {
      _isSpeaking = false;
    }
  }

  /// Stop speaking
  Future<void> stop() async {
    try {
      await _tts.stop();
      _isSpeaking = false;
    } catch (e) {
      // Ignore errors
    }
  }

  /// Check if currently speaking
  bool get isSpeaking => _isSpeaking;

  /// Toggle TTS on/off
  void toggleTts() {
    _ttsEnabled = !_ttsEnabled;
    if (!_ttsEnabled) {
      stop();
    }
  }

  /// Check if TTS is enabled
  bool get isTtsEnabled => _ttsEnabled;

  /// Enable TTS
  void enableTts() {
    _ttsEnabled = true;
  }

  /// Disable TTS
  void disableTts() {
    _ttsEnabled = false;
    stop();
  }

  /// Set speech rate (0.0 to 1.0)
  Future<void> setSpeechRate(double rate) async {
    await init();
    await _tts.setSpeechRate(rate.clamp(0.0, 1.0));
  }

  /// Set pitch (0.5 to 2.0)
  Future<void> setPitch(double pitch) async {
    await init();
    await _tts.setPitch(pitch.clamp(0.5, 2.0));
  }

  /// Get available languages
  Future<List<dynamic>> getLanguages() async {
    await init();
    return await _tts.getLanguages;
  }

  /// Check if TTS is available on this platform
  Future<bool> isAvailable() async {
    await init();
    return _initialized;
  }
}
