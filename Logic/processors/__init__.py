"""
Audio and speech processing modules.

Provides:
- AudioProcessor: Audio preprocessing with ffmpeg
- SpeechToText: Whisper-based transcription
- AudioFeatureExtractor: Waveform analysis (RMS, pitch, energy)
"""

from .audio_processor import AudioProcessor
from .speech_to_text import SpeechToText
from .audio_features import AudioFeatureExtractor

__all__ = [
    "AudioProcessor",
    "SpeechToText",
    "AudioFeatureExtractor",
]
