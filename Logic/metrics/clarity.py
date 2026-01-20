"""
Clarity metric evaluator.

Evaluates speech clarity based on ASR confidence scores.
NOT based on pronunciation correctness (accent-agnostic, child-safe).
"""

from typing import Any, Dict, List

import numpy as np

from .base import BaseMetric
from ..config.metrics_config import METRICS_CONFIG


class ClarityMetric(BaseMetric):
    """
    Evaluates speech clarity based on confidence scores.

    Higher ASR confidence = clearer speech.
    Does not penalize accents or pronunciation variations.
    """

    def __init__(self, student_age: int = 10):
        super().__init__(student_age)
        self.low_conf_threshold = METRICS_CONFIG["low_confidence_threshold"]

    def evaluate(self, words: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Evaluate speech clarity.

        Args:
            words: List of word dictionaries with confidence scores

        Returns:
            Dict with clarity score and details
        """
        if not words:
            return {
                "score": 0,
                "average_confidence": 0,
                "low_confidence_count": 0,
                "low_confidence_words": [],
                "feedback": ["No speech detected"],
            }

        confidences = [w["confidence"] for w in words]
        avg_confidence = float(np.mean(confidences))

        # Find low confidence words (potential unclear speech)
        low_confidence_words = [
            {
                "word": w["word"],
                "confidence": round(w["confidence"], 3),
                "timestamp": round(w["start"], 2),
            }
            for w in words if w["confidence"] < self.low_conf_threshold
        ]

        # Calculate clarity score (0-100)
        clarity_score = self.clamp_score(avg_confidence * 100)

        # Generate feedback
        feedback = self.get_feedback(clarity_score)

        return {
            "score": clarity_score,
            "average_confidence": round(avg_confidence, 3),
            "low_confidence_count": len(low_confidence_words),
            "low_confidence_words": low_confidence_words[:5],  # Top 5 only
            "feedback": feedback,
        }

    def get_feedback(self, score: int, **kwargs) -> List[str]:
        """Generate age-appropriate feedback based on clarity score."""
        feedback = []

        if score < 50:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append("Try speaking a bit louder and clearer!")
            else:
                feedback.append("Try speaking a bit louder and clearer")
        elif score < 70:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append("Good effort! Keep practicing speaking clearly!")
            else:
                feedback.append(
                    "Good effort! Some words were unclear, "
                    "practice speaking with confidence"
                )
        else:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append("Great job! Your words were easy to understand!")
            else:
                feedback.append("Great clarity! Your words were easy to understand")

        return feedback
