"""
Configuration module for Public Speaking Evaluation System.

Provides centralized configuration for:
- General settings (Whisper, audio processing)
- Age group definitions and weights
- Metric thresholds and settings
- Presentation config (badges, messages, icons)
"""

from .settings import (
    WHISPER_CONFIG,
    AUDIO_CONFIG,
    STT_CONFIG,
    OUTPUT_CONFIG,
    PERFORMANCE_CONFIG,
    FEATURE_FLAGS,
)
from .age_groups import (
    AGE_GROUPS,
    METRIC_WEIGHTS,
    AUDIO_METRIC_WEIGHTS,
    get_age_group,
    get_detailed_age_group,
)
from .metrics_config import (
    METRICS_CONFIG,
    AUDIO_METRICS_CONFIG,
)
from .presentation_config import (
    BADGES,
    CHARACTER_MESSAGES,
    ICONS,
    COLORS,
)

__all__ = [
    # Settings
    "WHISPER_CONFIG",
    "AUDIO_CONFIG",
    "STT_CONFIG",
    "OUTPUT_CONFIG",
    "PERFORMANCE_CONFIG",
    "FEATURE_FLAGS",
    # Age groups
    "AGE_GROUPS",
    "METRIC_WEIGHTS",
    "AUDIO_METRIC_WEIGHTS",
    "get_age_group",
    "get_detailed_age_group",
    # Metrics
    "METRICS_CONFIG",
    "AUDIO_METRICS_CONFIG",
    # Presentation
    "BADGES",
    "CHARACTER_MESSAGES",
    "ICONS",
    "COLORS",
]
