"""
Pitch variation metric evaluator.

Evaluates expression/prosody based on pitch variation in speech.
"""

from typing import Any, Dict, List

from .base import BaseMetric
from ..models.audio_features import AudioFeatures
from ..config.metrics_config import AUDIO_METRICS_CONFIG


class PitchVariationMetric(BaseMetric):
    """
    Evaluates pitch variation/expression.

    Based on pitch analysis (pyin algorithm) from audio.
    Detects monotone, expressive, or erratic speech patterns.
    """

    def __init__(self, student_age: int = 10):
        super().__init__(student_age)
        self.config = AUDIO_METRICS_CONFIG["pitch"]

    def evaluate(self, audio_features: AudioFeatures, **kwargs) -> Dict[str, Any]:
        """
        Evaluate pitch variation/expression.

        Args:
            audio_features: AudioFeatures dataclass from AudioFeatureExtractor

        Returns:
            Dict with pitch variation score and details
        """
        pitch = audio_features.pitch

        # Handle insufficient data
        if pitch.classification == "insufficient_data" or pitch.voiced_ratio < 0.1:
            # For very young children, don't penalize
            if self.age_group == "pre_primary":
                return {
                    "score": 70,  # Give benefit of doubt
                    "classification": "not_analyzed",
                    "pitch_mean": 0,
                    "pitch_std": 0,
                    "voiced_ratio": pitch.voiced_ratio,
                    "feedback": ["Keep practicing your speaking!"],
                }
            return {
                "score": 50,
                "classification": "insufficient_data",
                "pitch_mean": 0,
                "pitch_std": 0,
                "voiced_ratio": pitch.voiced_ratio,
                "feedback": ["Not enough voiced speech to analyze expression"],
            }

        classification = pitch.classification
        pitch_std = pitch.pitch_std

        # Calculate score based on classification
        monotone_threshold = self.config["monotone_std_threshold"]
        erratic_threshold = self.config["erratic_std_threshold"]

        if classification == "monotone":
            # Monotone: score based on how close to threshold
            # pitch_std of 0 = 40, threshold = 70
            ratio = pitch_std / monotone_threshold
            pitch_score = int(40 + 30 * ratio)
        elif classification == "erratic":
            # Erratic: some penalty but not severe (still has expression!)
            # Start at 80, decrease as it gets more erratic
            excess = pitch_std - erratic_threshold
            pitch_score = int(80 - min(30, excess * 0.3))
        else:
            # Expressive: good!
            # Score from 70-100 based on variation
            middle = (monotone_threshold + erratic_threshold) / 2
            if pitch_std <= middle:
                # Lower half: 70-90
                ratio = (pitch_std - monotone_threshold) / (middle - monotone_threshold)
                pitch_score = int(70 + 20 * ratio)
            else:
                # Upper half: 90-100
                ratio = (pitch_std - middle) / (erratic_threshold - middle)
                pitch_score = int(90 + 10 * (1 - ratio))

        pitch_score = self.clamp_score(pitch_score)

        # Age adjustment for pre-primary
        if self.age_group == "pre_primary" and pitch_score < 60:
            pitch_score = min(70, pitch_score + 20)

        # Generate feedback
        feedback = self.get_feedback(
            pitch_score,
            classification=classification
        )

        return {
            "score": pitch_score,
            "classification": classification,
            "pitch_mean": round(pitch.pitch_mean, 2),
            "pitch_std": round(pitch_std, 2),
            "pitch_range": (
                round(pitch.pitch_range[0], 2),
                round(pitch.pitch_range[1], 2)
            ),
            "voiced_ratio": round(pitch.voiced_ratio, 3),
            "feedback": feedback,
        }

    def get_feedback(
        self,
        score: int,
        classification: str = "expressive",
        **kwargs
    ) -> List[str]:
        """Generate age-appropriate feedback based on pitch variation."""
        feedback = []

        if classification == "monotone":
            if self.age_group == "pre_primary":
                feedback.append(
                    "Try making your voice go up and down like a roller coaster! 🎢"
                )
            elif self.age_group == "lower_primary":
                feedback.append(
                    "Try adding more expression - make your voice go high and low!"
                )
            else:
                feedback.append(
                    "Try adding more expression to your voice - "
                    "go up and down like a roller coaster!"
                )
        elif classification == "erratic":
            if self.age_group == "pre_primary":
                feedback.append(
                    "Great energy! Your voice is very bouncy! 🎉"
                )
            elif self.age_group == "lower_primary":
                feedback.append(
                    "Good energy! Try to control your voice a bit more."
                )
            else:
                feedback.append(
                    "Good energy! Try to control your pitch a bit more."
                )
        else:
            if self.age_group == "pre_primary":
                feedback.append(
                    "Your voice sounds so interesting! ⭐"
                )
            elif self.age_group == "lower_primary":
                feedback.append(
                    "Great expression! Your voice has nice variety!"
                )
            else:
                feedback.append(
                    "Great expression! Your voice has nice variety."
                )

        return feedback

    def get_expression_level(self, score: int) -> int:
        """Map score to 0-5 level for visual display."""
        if score >= 90:
            return 5
        elif score >= 75:
            return 4
        elif score >= 60:
            return 3
        elif score >= 45:
            return 2
        elif score >= 30:
            return 1
        else:
            return 0

    def is_expressive(self, score: int) -> bool:
        """Binary check for lower_primary display."""
        return score >= 60
