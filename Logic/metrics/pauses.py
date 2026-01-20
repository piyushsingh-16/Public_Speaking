"""
Pause management metric evaluator.

Evaluates pause patterns using word timestamps (noise-tolerant).
"""

from typing import Any, Dict, List

from .base import BaseMetric
from ..config.metrics_config import METRICS_CONFIG
from ..config.age_groups import AGE_GROUPS, get_detailed_age_group


class PauseMetric(BaseMetric):
    """
    Evaluates pause patterns.

    Uses word timestamps for noise-tolerant pause detection.
    Age-adjusted tolerance for young speakers.
    """

    def __init__(self, student_age: int = 10):
        super().__init__(student_age)
        self.long_pause_threshold = METRICS_CONFIG["long_pause_threshold"]
        self.excessive_pause_threshold = METRICS_CONFIG["excessive_pause_threshold"]

    def evaluate(self, words: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Evaluate pause patterns.

        Args:
            words: List of word dictionaries with timestamps

        Returns:
            Dict with pause score and details
        """
        if len(words) < 2:
            return {
                "score": 100,
                "total_pauses": 0,
                "long_pauses": 0,
                "excessive_pauses": 0,
                "feedback": ["Not enough speech to evaluate pauses"],
            }

        # Detect pauses between words
        pauses = []
        for i in range(len(words) - 1):
            pause_duration = words[i + 1]["start"] - words[i]["end"]
            if pause_duration > 0:
                pauses.append({
                    "duration": pause_duration,
                    "position": i,
                    "after_word": words[i]["word"],
                })

        # Classify pauses
        long_pauses = [p for p in pauses if p["duration"] > self.long_pause_threshold]
        excessive_pauses = [p for p in pauses if p["duration"] > self.excessive_pause_threshold]

        # Calculate score
        total_words = len(words)
        long_pause_ratio = len(long_pauses) / total_words if total_words > 0 else 0

        # Get age-adjusted tolerance
        detailed_group = get_detailed_age_group(self.student_age)
        tolerance = AGE_GROUPS[detailed_group]["pause_tolerance"]

        # Calculate score
        if long_pause_ratio <= tolerance:
            pause_score = 100
        else:
            pause_score = max(0, int(100 - (long_pause_ratio - tolerance) * 200))

        # Heavy penalty for excessive pauses (>4 sec)
        pause_score -= len(excessive_pauses) * 10
        pause_score = self.clamp_score(pause_score)

        # Generate feedback
        feedback = self.get_feedback(
            pause_score,
            long_pauses=len(long_pauses),
            excessive_pauses=len(excessive_pauses)
        )

        return {
            "score": pause_score,
            "total_pauses": len(pauses),
            "long_pauses": len(long_pauses),
            "excessive_pauses": len(excessive_pauses),
            "long_pause_ratio": round(long_pause_ratio, 3),
            "feedback": feedback,
        }

    def get_feedback(
        self,
        score: int,
        long_pauses: int = 0,
        excessive_pauses: int = 0,
        **kwargs
    ) -> List[str]:
        """Generate feedback based on pause patterns."""
        feedback = []

        if excessive_pauses > 0:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(
                    f"You had {excessive_pauses} really long pauses. "
                    f"Try to keep talking!"
                )
            else:
                feedback.append(
                    f"You had {excessive_pauses} very long pauses (>4 seconds). "
                    f"Try to keep moving forward"
                )
        elif long_pauses > 3:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(
                    "You have some long pauses. It's okay to pause briefly!"
                )
            else:
                feedback.append(
                    "You have several long pauses. "
                    "It's okay to pause, but try to keep them brief"
                )
        elif long_pauses > 0:
            feedback.append("Good control of pauses! Just a few long ones")
        else:
            feedback.append("Excellent! No excessive pauses detected")

        return feedback
