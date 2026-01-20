"""
Base presenter class for age-appropriate output transformation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BasePresenter(ABC):
    """
    Abstract base class for age-appropriate presenters.

    Each presenter transforms raw evaluation results into
    a format suitable for its target age group.
    """

    FORMAT_VERSION = "1.0"

    def __init__(self, student_age: int):
        """
        Initialize presenter.

        Args:
            student_age: Student's age in years
        """
        self.student_age = student_age

    @property
    @abstractmethod
    def age_group(self) -> str:
        """Return the age group identifier."""
        pass

    @abstractmethod
    def transform(self, raw_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw evaluation into age-appropriate presentation.

        Args:
            raw_evaluation: Full evaluation result from evaluator

        Returns:
            Age-appropriate presentation dict
        """
        pass

    def _get_score(self, raw_evaluation: Dict, metric: str) -> int:
        """Safely get a metric score from raw evaluation."""
        if "scores" in raw_evaluation:
            return raw_evaluation["scores"].get(metric, 0)
        return raw_evaluation.get(metric, {}).get("score", 0)

    def _get_duration(self, raw_evaluation: Dict) -> float:
        """Get speech duration from evaluation."""
        if "metadata" in raw_evaluation:
            return raw_evaluation["metadata"].get("duration_seconds", 0)
        return 0
