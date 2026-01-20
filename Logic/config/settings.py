"""
General settings for the Public Speaking Evaluation System.

These settings control:
- Whisper model configuration
- Audio processing settings
- Speech-to-text parameters
- Output formatting
- Performance tuning
"""

# Whisper Model Configuration
WHISPER_CONFIG = {
    "model_size": "base",      # Options: tiny, base, small, medium, large-v3
    "device": "cpu",           # Options: cpu, cuda
    "compute_type": "int8",    # Options: int8 (faster), float16 (more accurate)
}

# Audio Processing Configuration
AUDIO_CONFIG = {
    "target_sample_rate": 16000,  # Hz (Whisper's native rate)
    "normalize_audio": True,       # Volume normalization
    "supported_formats": [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"],
}

# Speech-to-Text Configuration
STT_CONFIG = {
    "language": "en",              # Primary language
    "vad_filter": True,            # Voice Activity Detection (helps with noise)
    "vad_threshold": 0.5,          # VAD sensitivity (0-1)
    "min_speech_duration_ms": 250, # Minimum speech segment duration
    "min_silence_duration_ms": 100,# Minimum silence duration
}

# Output Configuration
OUTPUT_CONFIG = {
    "save_json_by_default": True,
    "output_directory": "evaluation_results",
    "json_indent": 2,
    "include_full_transcript": True,
    "max_feedback_suggestions": 5,
    "max_low_confidence_words": 5,
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "cleanup_temp_files": True,
    "max_audio_duration": 600,    # Maximum audio length in seconds (10 min)
    "enable_batch_processing": True,
    "batch_size": 10,
}

# Feature Flags (for future enhancements)
FEATURE_FLAGS = {
    "enable_video_analysis": False,
    "enable_emotion_detection": False,
    "enable_multilingual": False,
    "enable_real_time_feedback": False,
    "enable_audio_features": True,  # NEW: Enable loudness, pitch, stamina
}


def get_config(config_type: str = "all") -> dict:
    """
    Get configuration by type.

    Args:
        config_type: Type of config to retrieve
            Options: whisper, audio, stt, output, performance, features, all

    Returns:
        Requested configuration dictionary
    """
    configs = {
        "whisper": WHISPER_CONFIG,
        "audio": AUDIO_CONFIG,
        "stt": STT_CONFIG,
        "output": OUTPUT_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "features": FEATURE_FLAGS,
        "all": {
            "whisper": WHISPER_CONFIG,
            "audio": AUDIO_CONFIG,
            "stt": STT_CONFIG,
            "output": OUTPUT_CONFIG,
            "performance": PERFORMANCE_CONFIG,
            "feature_flags": FEATURE_FLAGS,
        },
    }
    return configs.get(config_type, configs["all"])
