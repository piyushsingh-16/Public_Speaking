"""
Pre-primary (ages 3-5) presenter.

Focus: Voice presence and confidence only.
Style: Character-based, animated, single feedback.
"""

from typing import Any, Dict

from .base import BasePresenter
from ..config.presentation_config import (
    get_random_message,
    get_badges_for_scores,
    CHARACTERS,
)


class PrePrimaryPresenter(BasePresenter):
    """
    Presenter for ages 3-5.

    Only shows:
    - Voice detected (yes/no)
    - Voice strength (lion/mouse/just_right)
    - One badge
    - Character message

    No numbers, no text explanations, no detailed feedback.
    """

    @property
    def age_group(self) -> str:
        return "pre_primary"

    def transform(self, raw_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Transform evaluation for pre-primary display."""
        # Get basic metrics
        loudness_score = self._get_score(raw_evaluation, "loudness")
        duration = self._get_duration(raw_evaluation)

        # Determine voice strength (lion/mouse/just_right)
        voice_strength = self._get_voice_strength(loudness_score)

        # Voice detected if we have any speech
        voice_detected = loudness_score > 20

        # Determine character and state
        character, character_state = self._get_character_info(voice_strength)

        # Get message
        if voice_strength == "lion":
            message = get_random_message("just_right")
        elif voice_strength == "mouse":
            message = get_random_message("too_soft")
        else:
            message = get_random_message("just_right")

        # Check for badges
        scores = {
            "loudness": loudness_score,
            "pitch_variation": self._get_score(raw_evaluation, "pitch_variation"),
        }
        badges = get_badges_for_scores(scores, "pre_primary", duration)
        badge = badges[0] if badges else None

        # Sound effect
        sound_effect = self._get_sound_effect(voice_strength, badge is not None)

        return {
            "age_group": self.age_group,
            "format_version": self.FORMAT_VERSION,
            "visuals": {
                "main_character": character,
                "character_state": character_state,
                "background_theme": "stars" if badge else "clouds",
            },
            "voice_detected": voice_detected,
            "voice_strength": voice_strength,
            "duration_seconds": round(duration, 1),
            "badge": badge,
            "message": {
                "text": message,
                "character": character,
                "tts_enabled": True,
            },
            "audio_feedback": {
                "sound_effect": sound_effect,
                "tts_message": message if voice_detected else "Try speaking louder!",
            },
            "show_to_child": True,
        }

    def _get_voice_strength(self, loudness_score: int) -> str:
        """Map loudness score to child-friendly label."""
        if loudness_score >= 70:
            return "lion"
        elif loudness_score < 40:
            return "mouse"
        else:
            return "just_right"

    def _get_character_info(self, voice_strength: str) -> tuple:
        """Get character and state based on voice strength."""
        if voice_strength == "lion":
            return "lion", "roaring"
        elif voice_strength == "mouse":
            return "lion", "encouraging"
        else:
            return "lion", "celebrating"

    def _get_sound_effect(self, voice_strength: str, earned_badge: bool) -> str:
        """Get appropriate sound effect."""
        if earned_badge:
            return "celebration_fanfare"
        if voice_strength == "lion":
            return "lion_roar"
        elif voice_strength == "mouse":
            return "encouragement_chime"
        else:
            return "celebration_chime"
