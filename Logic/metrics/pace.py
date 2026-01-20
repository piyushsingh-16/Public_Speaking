"""
Pace metric evaluator.

Evaluates speaking pace (words per minute) with age-adjusted ideal ranges.
"""

from typing import Any, Dict, List

from .base import BaseMetric
from ..config.age_groups import AGE_GROUPS, get_detailed_age_group


class PaceMetric(BaseMetric):
    """
    Evaluates speaking pace (words per minute).

    Different age groups have different ideal WPM ranges.
    """

    def evaluate(
        self,
        words: List[Dict],
        total_duration: float,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate speaking pace.

        Args:
            words: List of word dictionaries
            total_duration: Total speech duration in seconds

        Returns:
            Dict with pace score and details
        """
        if not words or total_duration == 0:
            return {
                "score": 0,
                "wpm": 0,
                "ideal_range": "N/A",
                "feedback": ["No speech detected"],
            }

        # Calculate WPM
        word_count = len(words)
        speaking_duration = total_duration / 60  # Convert to minutes
        wpm = word_count / speaking_duration if speaking_duration > 0 else 0

        # Get ideal range for age group
        detailed_group = get_detailed_age_group(self.student_age)
        ideal_min, ideal_max = AGE_GROUPS[detailed_group]["wpm_range"]

        # Calculate pace score
        if ideal_min <= wpm <= ideal_max:
            pace_score = 100
        elif wpm < ideal_min:
            # Too slow - proportional penalty
            ratio = wpm / ideal_min if ideal_min > 0 else 0
            pace_score = int(ratio * 100)
        else:
            # Too fast - proportional penalty
            ratio = ideal_max / wpm if wpm > 0 else 0
            pace_score = int(ratio * 100)

        pace_score = self.clamp_score(pace_score)

        # Generate feedback
        feedback = self.get_feedback(pace_score, wpm=wpm, ideal_range=(ideal_min, ideal_max))

        return {
            "score": pace_score,
            "wpm": round(wpm, 1),
            "ideal_range": f"{ideal_min}-{ideal_max} wpm",
            "word_count": word_count,
            "duration_minutes": round(speaking_duration, 2),
            "feedback": feedback,
        }

    def get_feedback(
        self,
        score: int,
        wpm: float = 0,
        ideal_range: tuple = (100, 150),
        **kwargs
    ) -> List[str]:
        """Generate feedback based on pace."""
        feedback = []
        ideal_min, ideal_max = ideal_range

        if wpm < ideal_min:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(
                    f"Try speaking a little faster! ({int(wpm)} words per minute)"
                )
            else:
                feedback.append(
                    f"Your pace is a bit slow ({int(wpm)} words/min). "
                    f"Try speaking a little faster"
                )
        elif wpm > ideal_max:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(
                    f"Great energy! Try slowing down just a little ({int(wpm)} words per minute)"
                )
            else:
                feedback.append(
                    f"Your pace is quite fast ({int(wpm)} words/min). "
                    f"Take your time and slow down"
                )
        else:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(f"Perfect speed! ({int(wpm)} words per minute)")
            else:
                feedback.append(f"Excellent pace! ({int(wpm)} words/min)")

        return feedback
