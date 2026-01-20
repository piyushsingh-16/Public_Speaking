"""
Public Speaking Evaluation System - Logic Module

A comprehensive evaluation system for school students' public speaking skills.
Optimized for scale, local processing, and age-appropriate feedback.
"""

from .evaluator import PublicSpeakingEvaluator
from .processors import AudioProcessor, SpeechToText, AudioFeatureExtractor
from .metrics import MetricsEvaluator

__version__ = "1.0.0"
__author__ = "K12 Public Speaking Platform"

__all__ = [
    "PublicSpeakingEvaluator",
    "AudioProcessor",
    "SpeechToText",
    "AudioFeatureExtractor",
    "MetricsEvaluator",
]
