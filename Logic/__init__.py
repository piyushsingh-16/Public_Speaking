"""
Public Speaking Evaluation System - Logic Module

A comprehensive evaluation system for school students' public speaking skills.
Optimized for scale, local processing, and age-appropriate feedback.
"""

from .evaluator import PublicSpeakingEvaluator
from .audio_processor import AudioProcessor
from .speech_to_text import SpeechToText
from .evaluation_metrics import EvaluationMetrics

__version__ = "1.0.0"
__author__ = "K12 Public Speaking Platform"

__all__ = [
    "PublicSpeakingEvaluator",
    "AudioProcessor",
    "SpeechToText",
    "EvaluationMetrics"
]
