"""
Repetition metric evaluator.

Detects word and phrase repetition that may indicate nervousness
or lack of preparation.
"""

from collections import Counter
from typing import Any, Dict, List

from .base import BaseMetric
from ..config.metrics_config import METRICS_CONFIG


class RepetitionMetric(BaseMetric):
    """
    Evaluates word and phrase repetition.

    Excessive repetition may indicate:
    - Nervousness
    - Lack of preparation
    - Need for more practice
    """

    def __init__(self, student_age: int = 10):
        super().__init__(student_age)
        self.min_word_length = METRICS_CONFIG.get("min_word_length_for_repeat", 3)
        self.phrase_threshold = METRICS_CONFIG.get("phrase_repeat_threshold", 3)

    def evaluate(self, words: List[Dict], **kwargs) -> Dict[str, Any]:
        """
        Evaluate repetition patterns.

        Args:
            words: List of word dictionaries

        Returns:
            Dict with repetition score and details
        """
        if len(words) < 5:
            return {
                "score": 100,
                "consecutive_repeats": 0,
                "repeated_phrases": [],
                "feedback": [],
            }

        word_texts = [w["word"].lower().strip(".,!?") for w in words]

        # Find consecutive repeated words
        consecutive_repeats = []
        for i in range(len(word_texts) - 1):
            word = word_texts[i]
            if (word == word_texts[i + 1] and
                len(word) >= self.min_word_length):
                consecutive_repeats.append(word)

        # Find repeated 2-3 word phrases
        phrases = []
        for i in range(len(word_texts) - 2):
            phrase = " ".join(word_texts[i:i+3])
            phrases.append(phrase)

        phrase_counts = Counter(phrases)
        repeated_phrases = [
            (phrase, count)
            for phrase, count in phrase_counts.items()
            if count >= self.phrase_threshold
        ]

        # Calculate score
        repeat_penalty = (len(consecutive_repeats) * 5) + (len(repeated_phrases) * 10)

        # Age adjustment: younger kids get less penalty
        if self.age_group in ["pre_primary", "lower_primary"]:
            repeat_penalty = repeat_penalty * 0.5

        repetition_score = self.clamp_score(100 - repeat_penalty)

        # Generate feedback
        feedback = self.get_feedback(
            repetition_score,
            consecutive_repeats=len(consecutive_repeats),
            repeated_phrases=len(repeated_phrases)
        )

        return {
            "score": repetition_score,
            "consecutive_repeats": len(consecutive_repeats),
            "repeated_phrases": repeated_phrases[:3],  # Top 3
            "feedback": feedback,
        }

    def get_feedback(
        self,
        score: int,
        consecutive_repeats: int = 0,
        repeated_phrases: int = 0,
        **kwargs
    ) -> List[str]:
        """Generate feedback based on repetition patterns."""
        feedback = []

        if repeated_phrases > 2:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(
                    "You repeated some phrases. Try to keep going with new ideas!"
                )
            else:
                feedback.append(
                    "You repeated some phrases multiple times. "
                    "Try to move forward with new ideas"
                )
        elif consecutive_repeats > 3:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(
                    "You repeated some words. Take a breath and continue!"
                )
            else:
                feedback.append(
                    "You repeated some words back-to-back. "
                    "Take a breath and continue"
                )
        elif consecutive_repeats > 0:
            feedback.append("Just a bit of repetition noticed - doing well overall")
        else:
            feedback.append("Excellent! No noticeable repetition")

        return feedback
