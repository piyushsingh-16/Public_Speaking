"""
Combined metrics evaluator.

Orchestrates all individual metric evaluators and calculates
weighted overall score.
"""

from typing import Any, Dict, List, Optional

from .clarity import ClarityMetric
from .pace import PaceMetric
from .pauses import PauseMetric
from .fillers import FillerMetric
from .repetition import RepetitionMetric
from .structure import StructureMetric
from .loudness import LoudnessMetric
from .pitch_variation import PitchVariationMetric
from .stamina import StaminaMetric
from ..models.audio_features import AudioFeatures
from ..config.age_groups import METRIC_WEIGHTS, get_detailed_age_group


class MetricsEvaluator:
    """
    Combined metrics evaluator.

    Evaluates all metrics and calculates weighted overall score.
    """

    def __init__(self, student_age: int = 10):
        """
        Initialize all metric evaluators.

        Args:
            student_age: Student's age for age-adjusted scoring
        """
        self.student_age = student_age
        self.age_group = get_detailed_age_group(student_age)

        # Transcript-based metrics
        self.clarity = ClarityMetric(student_age)
        self.pace = PaceMetric(student_age)
        self.pauses = PauseMetric(student_age)
        self.fillers = FillerMetric(student_age)
        self.repetition = RepetitionMetric(student_age)
        self.structure = StructureMetric(student_age)

        # Audio-based metrics
        self.loudness = LoudnessMetric(student_age)
        self.pitch_variation = PitchVariationMetric(student_age)
        self.stamina = StaminaMetric(student_age)

    def evaluate_all(
        self,
        words: List[Dict],
        full_text: str,
        segments: List[Dict],
        total_duration: float,
        audio_features: Optional[AudioFeatures] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate all metrics.

        Args:
            words: List of word dictionaries with timestamps and confidence
            full_text: Complete transcript text
            segments: List of speech segments
            total_duration: Total duration in seconds
            audio_features: AudioFeatures from waveform analysis (optional)

        Returns:
            Dict containing all metric scores and details
        """
        # Transcript-based evaluations
        clarity_result = self.clarity.evaluate(words=words)
        pace_result = self.pace.evaluate(words=words, total_duration=total_duration)
        pause_result = self.pauses.evaluate(words=words)
        filler_result = self.fillers.evaluate(words=words)
        repetition_result = self.repetition.evaluate(words=words)
        structure_result = self.structure.evaluate(
            full_text=full_text, segments=segments
        )

        # Audio-based evaluations (if features available)
        if audio_features and audio_features.is_valid():
            loudness_result = self.loudness.evaluate(audio_features=audio_features)
            pitch_result = self.pitch_variation.evaluate(audio_features=audio_features)
            stamina_result = self.stamina.evaluate(audio_features=audio_features)
        else:
            # Default scores if audio features not available
            loudness_result = {
                "score": 70,
                "classification": "not_analyzed",
                "feedback": ["Audio features not available"],
            }
            pitch_result = {
                "score": 70,
                "classification": "not_analyzed",
                "feedback": ["Audio features not available"],
            }
            stamina_result = {
                "score": 70,
                "classification": "not_analyzed",
                "feedback": ["Audio features not available"],
            }

        # Calculate weighted overall score
        weights = METRIC_WEIGHTS[self.age_group]
        overall_score = (
            clarity_result["score"] * weights["clarity"] +
            pace_result["score"] * weights["pace"] +
            pause_result["score"] * weights["pause"] +
            filler_result["score"] * weights["filler"] +
            repetition_result["score"] * weights["repetition"] +
            structure_result["score"] * weights["structure"] +
            loudness_result["score"] * weights["loudness"] +
            pitch_result["score"] * weights["pitch_variation"] +
            stamina_result["score"] * weights["stamina"]
        )
        overall_score = round(overall_score, 1)

        return {
            "overall": overall_score,
            "clarity": clarity_result,
            "pace": pace_result,
            "pause_management": pause_result,
            "filler_reduction": filler_result,
            "repetition_control": repetition_result,
            "structure": structure_result,
            "loudness": loudness_result,
            "pitch_variation": pitch_result,
            "stamina": stamina_result,
        }

    def get_scores_dict(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract just the scores from full results.

        Args:
            results: Full evaluation results

        Returns:
            Dict of metric scores only
        """
        return {
            "overall": results["overall"],
            "clarity": results["clarity"]["score"],
            "pace": results["pace"]["score"],
            "pause_management": results["pause_management"]["score"],
            "filler_reduction": results["filler_reduction"]["score"],
            "repetition_control": results["repetition_control"]["score"],
            "structure": results["structure"]["score"],
            "loudness": results["loudness"]["score"],
            "pitch_variation": results["pitch_variation"]["score"],
            "stamina": results["stamina"]["score"],
        }

    def generate_improvement_suggestions(
        self,
        results: Dict[str, Any],
        max_suggestions: int = 5
    ) -> List[str]:
        """
        Generate prioritized improvement suggestions.

        Args:
            results: Full evaluation results
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of improvement suggestions, ordered by priority
        """
        # Collect all feedback with scores
        all_feedback = []
        for metric_name in [
            "clarity", "pace", "pause_management", "filler_reduction",
            "repetition_control", "structure", "loudness", "pitch_variation", "stamina"
        ]:
            metric_result = results.get(metric_name, {})
            score = metric_result.get("score", 100)
            feedback_list = metric_result.get("feedback", [])

            for feedback in feedback_list:
                # Skip generic "not analyzed" feedback
                if "not available" not in feedback.lower():
                    all_feedback.append((score, feedback))

        # Sort by score (lowest first = needs most improvement)
        all_feedback.sort(key=lambda x: x[0])

        # Collect unique suggestions
        suggestions = []
        seen = set()
        for score, feedback in all_feedback:
            if feedback not in seen:
                suggestions.append(feedback)
                seen.add(feedback)
            if len(suggestions) >= max_suggestions:
                break

        return suggestions
