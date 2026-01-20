"""
Lower primary (ages 6-8) presenter.

Focus: 3 icon-based metrics + badge.
Style: Visual icons, no numbers, no text explanations.
"""

from typing import Any, Dict, List

from .base import BasePresenter
from ..config.presentation_config import (
    get_badges_for_scores,
    get_icon_for_level,
    get_pace_icon,
    COLORS,
)
from ..config.age_groups import AGE_GROUPS


class LowerPrimaryPresenter(BasePresenter):
    """
    Presenter for ages 6-8.

    Shows:
    - 3 visual metric icons with levels
    - One badge
    - Celebration message

    No numbers, no detailed explanations.
    """

    @property
    def age_group(self) -> str:
        return "lower_primary"

    def transform(self, raw_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Transform evaluation for lower primary display."""
        # Get metric scores
        loudness_score = self._get_score(raw_evaluation, "loudness")
        pace_score = self._get_score(raw_evaluation, "pace")
        pitch_score = self._get_score(raw_evaluation, "pitch_variation")
        duration = self._get_duration(raw_evaluation)

        # Get WPM for pace icon
        pace_data = raw_evaluation.get("detailed_analysis", {}).get("pace", {})
        wpm = pace_data.get("words_per_minute", pace_data.get("wpm", 100))

        # Build metrics array (max 3)
        metrics = self._build_metrics(
            loudness_score, pace_score, pitch_score, wpm
        )

        # Check for badges
        scores = {
            "loudness": loudness_score,
            "pace": pace_score,
            "pitch_variation": pitch_score,
            "clarity": self._get_score(raw_evaluation, "clarity"),
        }
        badges = get_badges_for_scores(scores, "lower_primary", duration)
        badge = badges[0] if badges else None

        # Build message
        message = self._build_message(scores, badge)

        return {
            "age_group": self.age_group,
            "format_version": self.FORMAT_VERSION,
            "metrics": metrics,
            "badge": badge,
            "message": {
                "text": message,
                "character": None,
                "tts_enabled": False,
            },
            "show_to_child": True,
        }

    def _build_metrics(
        self,
        loudness_score: int,
        pace_score: int,
        pitch_score: int,
        wpm: float
    ) -> List[Dict]:
        """Build the 3 metric visuals."""
        metrics = []

        # Voice strength (level-based)
        voice_level = self._score_to_level(loudness_score)
        voice_icon = get_icon_for_level("voice_strength", voice_level)
        metrics.append({
            "id": "voice_strength",
            "icon": voice_icon["icon"],
            "level": voice_level,
            "max_level": 5,
            "label": voice_icon["label"],
            "color": COLORS["metrics"]["confidence"],
        })

        # Pace (icon-based, not level)
        ideal_range = AGE_GROUPS["lower_primary"]["wpm_range"]
        pace_icon_data = get_pace_icon(pace_score, wpm, ideal_range)
        metrics.append({
            "id": "pace",
            "icon": pace_icon_data["icon"],
            "label": pace_icon_data["label"],
            "color": COLORS["metrics"]["pace"],
        })

        # Expression (level-based)
        expression_level = self._score_to_level(pitch_score)
        expression_icon = get_icon_for_level("expression", expression_level)
        metrics.append({
            "id": "expression",
            "icon": expression_icon["icon"],
            "level": expression_level,
            "max_level": 5,
            "label": expression_icon["label"],
            "color": COLORS["metrics"]["expression"],
        })

        return metrics

    def _score_to_level(self, score: int) -> int:
        """Convert 0-100 score to 0-5 level."""
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

    def _build_message(self, scores: Dict, badge: Dict) -> str:
        """Build celebration/encouragement message."""
        avg_score = sum(scores.values()) / len(scores)

        if badge:
            return f"Great job! You unlocked the {badge['name']}! {badge['emoji']}"
        elif avg_score >= 70:
            return "Wonderful speaking! Keep it up!"
        elif avg_score >= 50:
            return "Good effort! You're getting better!"
        else:
            return "Nice try! Keep practicing!"
