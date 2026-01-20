"""
Structure metric evaluator.

Evaluates speech structure (introduction, body, conclusion).
More important for older students.
"""

from typing import Any, Dict, List

from .base import BaseMetric
from ..config.metrics_config import METRICS_CONFIG


class StructureMetric(BaseMetric):
    """
    Evaluates speech structure.

    Looks for:
    - Introduction markers (greeting, topic introduction)
    - Body content
    - Conclusion markers (summary, thank you)
    """

    def __init__(self, student_age: int = 10):
        super().__init__(student_age)
        self.intro_markers = METRICS_CONFIG["intro_markers"]
        self.conclusion_markers = METRICS_CONFIG["conclusion_markers"]

    def evaluate(
        self,
        full_text: str,
        segments: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate speech structure.

        Args:
            full_text: Complete transcript
            segments: List of speech segments

        Returns:
            Dict with structure score and details
        """
        if not full_text:
            return {
                "score": 0,
                "has_intro": False,
                "has_body": False,
                "has_conclusion": False,
                "feedback": ["No speech detected"],
            }

        text_lower = full_text.lower()

        # Look for introduction markers in first 200 characters
        has_intro = any(
            marker in text_lower[:200]
            for marker in self.intro_markers
        )

        # Look for conclusion markers in last 200 characters
        has_conclusion = any(
            marker in text_lower[-200:]
            for marker in self.conclusion_markers
        )

        # Check for body (middle section with content)
        has_body = len(segments) >= 3 or len(full_text) > 100

        # Calculate structure score
        structure_score = 0
        if has_intro:
            structure_score += 35
        if has_body:
            structure_score += 30
        if has_conclusion:
            structure_score += 35

        # Age-adjusted importance
        # Structure is less critical for younger students
        if self.age_group in ["pre_primary", "lower_primary"]:
            structure_score = min(100, structure_score + 30)
        elif self.age_group == "upper_primary":
            structure_score = min(100, structure_score + 15)

        structure_score = self.clamp_score(structure_score)

        # Generate feedback
        feedback = self.get_feedback(
            structure_score,
            has_intro=has_intro,
            has_conclusion=has_conclusion
        )

        return {
            "score": structure_score,
            "has_intro": has_intro,
            "has_body": has_body,
            "has_conclusion": has_conclusion,
            "feedback": feedback,
        }

    def get_feedback(
        self,
        score: int,
        has_intro: bool = False,
        has_conclusion: bool = False,
        **kwargs
    ) -> List[str]:
        """Generate feedback based on structure."""
        feedback = []
        missing = []

        if not has_intro:
            missing.append("introduction")
        if not has_conclusion:
            missing.append("conclusion")

        if missing and self.age_group in ["middle", "secondary"]:
            feedback.append(
                f"Try adding a clear {' and '.join(missing)} to your speech"
            )
        elif missing:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(
                    "Great job! Next time, try starting with 'Hello' "
                    "or ending with 'Thank you'!"
                )
            else:
                feedback.append(
                    "Great effort! Next time, try starting with a greeting "
                    "or ending with 'thank you'"
                )
        else:
            if self.age_group in ["pre_primary", "lower_primary"]:
                feedback.append(
                    "Excellent! You started and ended your speech perfectly!"
                )
            else:
                feedback.append(
                    "Excellent structure! Clear beginning, middle, and end"
                )

        return feedback
