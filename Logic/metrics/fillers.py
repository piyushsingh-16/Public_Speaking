"""
Filler word metric evaluator.

Detects and evaluates filler word usage with age-adjusted tolerance.
"""

from collections import Counter
from typing import Any, Dict, List

from .base import BaseMetric
from ..config.metrics_config import METRICS_CONFIG
from ..config.age_groups import AGE_GROUPS, get_detailed_age_group


class FillerMetric(BaseMetric):
    """
    Evaluates filler word usage.

    Detects common fillers like "um", "uh", "like", etc.
    Age-adjusted tolerance (more lenient for younger speakers).
    """

    def __init__(self, student_age: int = 10):
        super().__init__(student_age)
        self.filler_words = METRICS_CONFIG["filler_words"]

    def evaluate(self, words: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Evaluate filler word usage.

        Args:
            words: List of word dictionaries

        Returns:
            Dict with filler score and details
        """
        if not words:
            return {
                "score": 100,
                "filler_count": 0,
                "filler_ratio": 0,
                "fillers_found": [],
                "feedback": [],
            }

        total_words = len(words)
        word_texts = [w["word"].lower().strip(".,!?") for w in words]

        # Count fillers
        filler_instances = []
        for i, word in enumerate(word_texts):
            if word in self.filler_words:
                filler_instances.append({
                    "word": word,
                    "timestamp": round(words[i]["start"], 2),
                })

        filler_count = len(filler_instances)
        filler_ratio = filler_count / total_words if total_words > 0 else 0

        # Get age-adjusted tolerance
        detailed_group = get_detailed_age_group(self.student_age)
        tolerance = AGE_GROUPS[detailed_group]["filler_tolerance"]

        # Calculate score
        if filler_ratio <= tolerance:
            filler_score = 100
        else:
            filler_score = max(0, int(100 - (filler_ratio - tolerance) * 300))

        filler_score = self.clamp_score(filler_score)

        # Count most common fillers
        filler_counts = Counter([f["word"] for f in filler_instances])

        # Generate feedback
        feedback = self.get_feedback(
            filler_score,
            filler_count=filler_count,
            filler_ratio=filler_ratio,
            tolerance=tolerance
        )

        return {
            "score": filler_score,
            "filler_count": filler_count,
            "filler_ratio": round(filler_ratio, 3),
            "fillers_found": filler_counts.most_common(5),
            "feedback": feedback,
        }

    def get_feedback(
        self,
        score: int,
        filler_count: int = 0,
        filler_ratio: float = 0,
        tolerance: float = 0.10,
        **kwargs
    ) -> List[str]:
        """Generate feedback based on filler usage."""
        feedback = []

        if filler_ratio > tolerance * 2:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(
                    f"You said 'um' and 'uh' a lot ({filler_count} times). "
                    f"Try taking a breath instead!"
                )
            else:
                feedback.append(
                    f"You used many filler words like 'um', 'uh', 'like' "
                    f"({filler_count} times). Try pausing silently instead"
                )
        elif filler_ratio > tolerance:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(
                    f"You used some filler words ({filler_count} times). "
                    f"Keep practicing!"
                )
            else:
                feedback.append(
                    f"You used some filler words ({filler_count} times). "
                    f"Practice reducing them"
                )
        else:
            feedback.append("Great! Very few filler words used")

        return feedback
