"""
Upper primary (ages 9-10) presenter.

Focus: 4 progress bars + single improvement tip.
Style: Gamified with progress tracking and badges.
"""

from typing import Any, Dict, List

from .base import BasePresenter
from ..config.presentation_config import get_badges_for_scores, COLORS


class UpperPrimaryPresenter(BasePresenter):
    """
    Presenter for ages 9-10.

    Shows:
    - 4 progress bars (confidence, clarity, expression, pace)
    - Single improvement tip
    - Badges earned

    Gamified but with visible progress numbers.
    """

    @property
    def age_group(self) -> str:
        return "upper_primary"

    def transform(self, raw_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Transform evaluation for upper primary display."""
        # Get metric scores
        loudness_score = self._get_score(raw_evaluation, "loudness")
        clarity_score = self._get_score(raw_evaluation, "clarity")
        pitch_score = self._get_score(raw_evaluation, "pitch_variation")
        pace_score = self._get_score(raw_evaluation, "pace")
        stamina_score = self._get_score(raw_evaluation, "stamina")
        filler_score = self._get_score(raw_evaluation, "filler_reduction")
        structure_score = self._get_score(raw_evaluation, "structure")
        duration = self._get_duration(raw_evaluation)

        # Build progress bars (4 main ones)
        progress_bars = self._build_progress_bars(
            loudness_score, clarity_score, pitch_score, pace_score
        )

        # Get all scores for badge calculation
        scores = {
            "loudness": loudness_score,
            "clarity": clarity_score,
            "pitch_variation": pitch_score,
            "pace": pace_score,
            "stamina": stamina_score,
            "filler": filler_score,
            "structure": structure_score,
            "overall": raw_evaluation.get("scores", {}).get("overall", 0),
        }

        # Check for badges
        badges = get_badges_for_scores(scores, "upper_primary", duration)

        # Find the single improvement tip
        improvement_tip = self._get_improvement_tip(raw_evaluation, scores)

        return {
            "age_group": self.age_group,
            "format_version": self.FORMAT_VERSION,
            "progress_bars": progress_bars,
            "improvement_tip": improvement_tip,
            "badges_earned": badges,
            "streak": None,  # Can be populated from user history
            "show_to_child": True,
        }

    def _build_progress_bars(
        self,
        loudness: int,
        clarity: int,
        expression: int,
        pace: int
    ) -> List[Dict]:
        """Build 4 progress bar representations."""
        return [
            {
                "id": "confidence",
                "label": "Confidence",
                "value": loudness,
                "color": COLORS["metrics"]["confidence"],
            },
            {
                "id": "clarity",
                "label": "Clarity",
                "value": clarity,
                "color": COLORS["metrics"]["clarity"],
            },
            {
                "id": "expression",
                "label": "Expression",
                "value": expression,
                "color": COLORS["metrics"]["expression"],
            },
            {
                "id": "pace",
                "label": "Pace",
                "value": pace,
                "color": COLORS["metrics"]["pace"],
            },
        ]

    def _get_improvement_tip(
        self,
        raw_evaluation: Dict,
        scores: Dict
    ) -> Dict:
        """
        Find the single most impactful improvement tip.

        Picks the lowest scoring metric and generates one tip.
        """
        # Map metrics to tip text
        tip_map = {
            "loudness": {
                "text": "Try speaking a bit louder next time!",
                "target_metric": "confidence",
            },
            "clarity": {
                "text": "Focus on pronouncing each word clearly.",
                "target_metric": "clarity",
            },
            "pitch_variation": {
                "text": "Add more expression - make your voice go up and down!",
                "target_metric": "expression",
            },
            "pace": {
                "text": "Watch your speaking speed - not too fast, not too slow.",
                "target_metric": "pace",
            },
            "filler": {
                "text": "Try using fewer filler words like 'um' - pause silently instead!",
                "target_metric": "confidence",
            },
            "stamina": {
                "text": "Keep your energy up until the very end!",
                "target_metric": "confidence",
            },
            "structure": {
                "text": "Start with a greeting and end with 'thank you'!",
                "target_metric": "clarity",
            },
        }

        # Find lowest scoring metric (excluding overall)
        metric_scores = {k: v for k, v in scores.items() if k != "overall"}
        if not metric_scores:
            return {
                "text": "Great job! Keep practicing!",
                "target_metric": "confidence",
            }

        lowest_metric = min(metric_scores, key=metric_scores.get)
        lowest_score = metric_scores[lowest_metric]

        # If all scores are good, give encouragement
        if lowest_score >= 80:
            return {
                "text": "Amazing work! You're doing great - keep it up!",
                "target_metric": "confidence",
            }

        # Get the tip for the lowest metric
        tip_info = tip_map.get(lowest_metric, {
            "text": f"Let's work on improving your {lowest_metric.replace('_', ' ')}!",
            "target_metric": lowest_metric,
        })

        return tip_info
