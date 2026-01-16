"""
Configuration settings for Public Speaking Evaluation System
Modify these settings to customize behavior without changing core code
"""

# Whisper Model Configuration
WHISPER_CONFIG = {
    "model_size": "base",  # Options: tiny, base, small, medium, large-v3
    "device": "cpu",       # Options: cpu, cuda
    "compute_type": "int8"  # Options: int8 (faster), float16 (more accurate)
}

# Audio Processing Configuration
AUDIO_CONFIG = {
    "target_sample_rate": 16000,  # Hz (Whisper's native rate)
    "normalize_audio": True,       # Volume normalization
    "supported_formats": ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm']
}

# Speech-to-Text Configuration
STT_CONFIG = {
    "language": "en",              # Primary language
    "vad_filter": True,            # Voice Activity Detection (helps with noise)
    "vad_threshold": 0.5,          # VAD sensitivity (0-1)
    "min_speech_duration_ms": 250, # Minimum speech segment duration
    "min_silence_duration_ms": 100 # Minimum silence duration
}

# Evaluation Metrics Configuration
METRICS_CONFIG = {
    # Pause detection thresholds
    "pause_threshold": 0.5,         # Minimum pause duration (seconds)
    "long_pause_threshold": 2.0,    # Long pause threshold (seconds)
    "excessive_pause_threshold": 4.0, # Excessive pause threshold (seconds)

    # Filler words (can be extended for other languages)
    "filler_words": {
        'um', 'uh', 'umm', 'uhh', 'like', 'you know',
        'sort of', 'kind of', 'basically', 'actually',
        'so', 'well', 'right', 'okay', 'yeah'
    },

    # Clarity scoring
    "low_confidence_threshold": 0.6,  # Words below this are considered unclear

    # Structure detection keywords
    "intro_markers": [
        'hello', 'hi', 'good morning', 'good afternoon',
        'today', 'i will', 'i am going to', 'my topic'
    ],
    "conclusion_markers": [
        'conclusion', 'finally', 'in summary', 'to conclude',
        'thank you', 'that is all', 'in closing'
    ]
}

# Age Group Definitions
AGE_GROUPS = {
    'pre_primary': {
        'min_age': 3,
        'max_age': 5,
        'wpm_range': (40, 90),
        'filler_tolerance': 0.15,  # 15% fillers acceptable
        'pause_tolerance': 0.30     # 30% long pauses acceptable
    },
    'primary': {
        'min_age': 6,
        'max_age': 10,
        'wpm_range': (60, 120),
        'filler_tolerance': 0.10,
        'pause_tolerance': 0.20
    },
    'middle': {
        'min_age': 11,
        'max_age': 13,
        'wpm_range': (100, 150),
        'filler_tolerance': 0.08,
        'pause_tolerance': 0.15
    },
    'secondary': {
        'min_age': 14,
        'max_age': 18,
        'wpm_range': (120, 160),
        'filler_tolerance': 0.05,
        'pause_tolerance': 0.10
    }
}

# Age-Adjusted Metric Weights
# Determines importance of each metric for different age groups
METRIC_WEIGHTS = {
    'pre_primary': {
        'clarity': 0.30,
        'pace': 0.25,
        'pause': 0.20,
        'filler': 0.15,
        'repetition': 0.05,
        'structure': 0.05
    },
    'primary': {
        'clarity': 0.25,
        'pace': 0.20,
        'pause': 0.20,
        'filler': 0.15,
        'repetition': 0.10,
        'structure': 0.10
    },
    'middle': {
        'clarity': 0.20,
        'pace': 0.15,
        'pause': 0.15,
        'filler': 0.15,
        'repetition': 0.15,
        'structure': 0.20
    },
    'secondary': {
        'clarity': 0.15,
        'pace': 0.15,
        'pause': 0.10,
        'filler': 0.15,
        'repetition': 0.15,
        'structure': 0.30
    }
}

# Output Configuration
OUTPUT_CONFIG = {
    "save_json_by_default": True,
    "output_directory": "evaluation_results",
    "json_indent": 2,
    "include_full_transcript": True,
    "max_feedback_suggestions": 5,
    "max_low_confidence_words": 5
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "cleanup_temp_files": True,
    "max_audio_duration": 600,  # Maximum audio length in seconds (10 min)
    "enable_batch_processing": True,
    "batch_size": 10
}

# Feature Flags (for future enhancements)
FEATURE_FLAGS = {
    "enable_video_analysis": False,  # Planned future feature
    "enable_emotion_detection": False,  # Planned future feature
    "enable_multilingual": False,  # Planned future feature
    "enable_real_time_feedback": False  # Planned future feature
}


def get_config(config_type: str = "all"):
    """
    Get configuration by type

    Args:
        config_type: Type of config to retrieve
            Options: whisper, audio, stt, metrics, output, performance, all

    Returns:
        Requested configuration dictionary
    """
    configs = {
        "whisper": WHISPER_CONFIG,
        "audio": AUDIO_CONFIG,
        "stt": STT_CONFIG,
        "metrics": METRICS_CONFIG,
        "output": OUTPUT_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "all": {
            "whisper": WHISPER_CONFIG,
            "audio": AUDIO_CONFIG,
            "stt": STT_CONFIG,
            "metrics": METRICS_CONFIG,
            "output": OUTPUT_CONFIG,
            "performance": PERFORMANCE_CONFIG,
            "age_groups": AGE_GROUPS,
            "metric_weights": METRIC_WEIGHTS,
            "feature_flags": FEATURE_FLAGS
        }
    }

    return configs.get(config_type, configs["all"])


if __name__ == "__main__":
    import json
    print("Current Configuration:")
    print(json.dumps(get_config("all"), indent=2, default=str))
