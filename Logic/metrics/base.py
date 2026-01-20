"""
Base metric class for all evaluation metrics.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseMetric(ABC):
    """
    Abstract base class for all evaluation metrics.

    Each metric evaluator must implement:
    - evaluate(): Calculate score and details
    - get_feedback(): Generate feedback based on score
    """

    def __init__(self, student_age: int = 10):
        """
        Initialize metric evaluator.

        Args:
            student_age: Student's age for age-adjusted scoring
        """
        self.student_age = student_age
        self.age_group = self._determine_age_group(student_age)

    def _determine_age_group(self, age: int) -> str:
        """Determine age group from student age."""
        if age <= 5:
            return "pre_primary"
        elif age <= 8:
            return "lower_primary"
        elif age <= 10:
            return "upper_primary"
        elif age <= 13:
            return "middle"
        else:
            return "secondary"

    @abstractmethod
    def evaluate(self, **kwargs) -> Dict[str, Any]:
        """
        Evaluate the metric.

        Returns:
            Dict containing:
                - score: 0-100
                - feedback: List of feedback strings
                - details: Additional metric-specific data
        """
        pass

    @abstractmethod
    def get_feedback(self, score: int, **kwargs) -> List[str]:
        """
        Generate feedback based on score.

        Args:
            score: Metric score (0-100)

        Returns:
            List of feedback strings
        """
        pass

    def clamp_score(self, score: float) -> int:
        """Clamp score to 0-100 range."""
        return max(0, min(100, int(score)))
