"""
Loudness metric evaluator.

Evaluates voice strength/energy based on RMS audio features.
"""

from typing import Any, Dict, List

from .base import BaseMetric
from ..models.audio_features import AudioFeatures
from ..config.metrics_config import AUDIO_METRICS_CONFIG


class LoudnessMetric(BaseMetric):
    """
    Evaluates voice strength/loudness.

    Based on RMS energy extracted from audio waveform.
    Maps to child-friendly feedback (lion voice, mouse voice, etc.)
    """

    def __init__(self, student_age: int = 10):
        super().__init__(student_age)
        self.config = AUDIO_METRICS_CONFIG["loudness"]

    def evaluate(self, audio_features: AudioFeatures, **kwargs) -> Dict[str, Any]:
        """
        Evaluate loudness/voice strength.

        Args:
            audio_features: AudioFeatures dataclass from AudioFeatureExtractor

        Returns:
            Dict with loudness score and details
        """
        loudness = audio_features.loudness

        # Handle empty/invalid features
        if loudness.rms_mean == 0:
            return {
                "score": 0,
                "rms_db": -60,
                "classification": "no_audio",
                "variance": 0,
                "feedback": ["No audio detected"],
            }

        # Get thresholds
        optimal_min, optimal_max = self.config["optimal_db_range"]
        too_soft = self.config["too_soft_threshold"]
        too_loud = self.config["too_loud_threshold"]

        rms_db = loudness.rms_db_mean
        classification = loudness.classification

        # Calculate score based on how close to optimal range
        if optimal_min <= rms_db <= optimal_max:
            # In optimal range - full score
            loudness_score = 100
        elif rms_db < too_soft:
            # Very soft - low score
            # Map from -60dB (0) to too_soft threshold (50)
            loudness_score = max(0, int(50 * (rms_db + 60) / (too_soft + 60)))
        elif rms_db < optimal_min:
            # Soft but not too soft - moderate score
            range_size = optimal_min - too_soft
            position = rms_db - too_soft
            loudness_score = int(50 + 50 * position / range_size)
        elif rms_db > too_loud:
            # Too loud - penalty
            loudness_score = max(50, int(100 - (rms_db - too_loud) * 5))
        else:
            # Between optimal_max and too_loud
            range_size = too_loud - optimal_max
            position = rms_db - optimal_max
            loudness_score = int(100 - 20 * position / range_size)

        loudness_score = self.clamp_score(loudness_score)

        # Check variance (consistency)
        variance_threshold = self.config["variance_threshold"]
        is_inconsistent = loudness.rms_db_std > variance_threshold

        # Generate feedback
        feedback = self.get_feedback(
            loudness_score,
            classification=classification,
            is_inconsistent=is_inconsistent
        )

        return {
            "score": loudness_score,
            "rms_db": round(rms_db, 2),
            "rms_mean": round(loudness.rms_mean, 4),
            "classification": classification,
            "variance": round(loudness.rms_db_std, 2),
            "is_consistent": not is_inconsistent,
            "feedback": feedback,
        }

    def get_feedback(
        self,
        score: int,
        classification: str = "optimal",
        is_inconsistent: bool = False,
        **kwargs
    ) -> List[str]:
        """Generate age-appropriate feedback based on loudness."""
        feedback = []

        if classification == "too_soft":
            if self.age_group == "pre_primary":
                feedback.append(
                    "Try using your Lion Voice! 🦁 ROAR so everyone can hear you!"
                )
            elif self.age_group == "lower_primary":
                feedback.append(
                    "Your voice is a bit quiet. Try speaking louder like a superhero!"
                )
            else:
                feedback.append(
                    "Your voice is a bit quiet. "
                    "Try speaking louder so everyone can hear!"
                )
        elif classification == "too_loud":
            if self.age_group == "pre_primary":
                feedback.append(
                    "Wow, you're loud! Let's try your indoor voice! 🏠"
                )
            elif self.age_group == "lower_primary":
                feedback.append(
                    "Great energy! Try speaking just a bit softer."
                )
            else:
                feedback.append(
                    "You have a powerful voice! Try speaking just a bit softer."
                )
        else:
            if self.age_group == "pre_primary":
                feedback.append(
                    "Perfect voice! You sound amazing! ⭐"
                )
            elif self.age_group == "lower_primary":
                feedback.append(
                    "Great voice strength! You're easy to hear!"
                )
            else:
                feedback.append(
                    "Great voice strength! You're easy to hear."
                )

        # Add consistency feedback for older students
        if is_inconsistent and self.age_group not in ["pre_primary", "lower_primary"]:
            feedback.append(
                "Try to keep your voice at the same volume throughout."
            )

        return feedback

    def get_voice_strength_level(self, score: int) -> int:
        """Map score to 0-5 level for visual display."""
        if score >= 90:
            return 5
        elif score >= 75:
            return 4
        elif score >= 60:
            return 3
        elif score >= 40:
            return 2
        elif score >= 20:
            return 1
        else:
            return 0

    def get_voice_strength_label(self, score: int) -> str:
        """Map score to child-friendly label."""
        if score >= 70:
            return "lion"
        elif score < 40:
            return "mouse"
        else:
            return "just_right"
