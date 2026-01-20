"""
Stamina metric evaluator.

Evaluates energy consistency throughout the speech.
"""

from typing import Any, Dict, List

from .base import BaseMetric
from ..models.audio_features import AudioFeatures
from ..config.metrics_config import AUDIO_METRICS_CONFIG


class StaminaMetric(BaseMetric):
    """
    Evaluates stamina/energy consistency.

    Checks if the speaker maintains energy throughout the speech
    or fades towards the end.
    """

    def __init__(self, student_age: int = 10):
        super().__init__(student_age)
        self.config = AUDIO_METRICS_CONFIG["stamina"]

    def evaluate(self, audio_features: AudioFeatures, **kwargs) -> Dict[str, Any]:
        """
        Evaluate stamina/energy consistency.

        Args:
            audio_features: AudioFeatures dataclass from AudioFeatureExtractor

        Returns:
            Dict with stamina score and details
        """
        stamina = audio_features.stamina
        duration = audio_features.duration_seconds

        # Check minimum duration
        min_duration = self.config["min_duration_for_analysis"]
        if duration < min_duration:
            # Too short to meaningfully analyze stamina
            return {
                "score": 100,  # Give full score for short speeches
                "classification": "short_speech",
                "energy_dropoff": 1.0,
                "energy_consistency": 1.0,
                "energy_segments": [],
                "feedback": ["Speech too short to analyze stamina"],
            }

        # Handle empty features
        if not stamina.energy_segments:
            return {
                "score": 70,
                "classification": "not_analyzed",
                "energy_dropoff": 1.0,
                "energy_consistency": 1.0,
                "energy_segments": [],
                "feedback": ["Energy analysis not available"],
            }

        classification = stamina.classification
        dropoff = stamina.energy_dropoff
        consistency = stamina.energy_consistency

        # Calculate score
        good_dropoff = self.config["good_dropoff_ratio"]
        warning_dropoff = self.config["warning_dropoff_ratio"]
        consistency_threshold = self.config["consistency_threshold"]

        # Dropoff score (0-60 points)
        if dropoff >= good_dropoff:
            dropoff_score = 60
        elif dropoff >= warning_dropoff:
            # Scale from 30-60 based on dropoff
            range_size = good_dropoff - warning_dropoff
            position = dropoff - warning_dropoff
            dropoff_score = int(30 + 30 * position / range_size)
        else:
            # Below warning threshold
            dropoff_score = int(30 * dropoff / warning_dropoff)

        # Consistency score (0-40 points)
        if consistency >= consistency_threshold:
            consistency_score = 40
        else:
            consistency_score = int(40 * consistency / consistency_threshold)

        stamina_score = self.clamp_score(dropoff_score + consistency_score)

        # Age adjustment: younger kids get less penalty
        if self.age_group in ["pre_primary", "lower_primary"]:
            if stamina_score < 70:
                stamina_score = min(80, stamina_score + 20)

        # Generate feedback
        feedback = self.get_feedback(
            stamina_score,
            classification=classification,
            dropoff=dropoff
        )

        return {
            "score": stamina_score,
            "classification": classification,
            "energy_dropoff": round(dropoff, 3),
            "energy_consistency": round(consistency, 3),
            "energy_segments": [round(e, 4) for e in stamina.energy_segments],
            "feedback": feedback,
        }

    def get_feedback(
        self,
        score: int,
        classification: str = "consistent",
        dropoff: float = 1.0,
        **kwargs
    ) -> List[str]:
        """Generate age-appropriate feedback based on stamina."""
        feedback = []

        if classification == "fading":
            if self.age_group == "pre_primary":
                feedback.append(
                    "You started strong! Try to stay loud until the end! 💪"
                )
            elif self.age_group == "lower_primary":
                feedback.append(
                    "Great start! Try to keep your energy up until the very end!"
                )
            else:
                feedback.append(
                    "Your energy dropped towards the end. "
                    "Try to finish as strong as you started!"
                )
        elif classification == "inconsistent":
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(
                    "Try to keep your voice the same volume from start to finish!"
                )
            else:
                feedback.append(
                    "Try to maintain steady energy from start to finish."
                )
        else:
            if self.age_group == "pre_primary":
                feedback.append(
                    "You kept going strong the whole time! Amazing! 🌟"
                )
            elif self.age_group == "lower_primary":
                feedback.append(
                    "Great job keeping your energy up throughout!"
                )
            else:
                feedback.append(
                    "Great job keeping your energy up throughout!"
                )

        return feedback
