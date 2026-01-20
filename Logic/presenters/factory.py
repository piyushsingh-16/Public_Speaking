"""
Presenter factory functions.

Provides easy access to the appropriate presenter based on age.
"""

from typing import Any, Dict

from .base import BasePresenter
from .pre_primary import PrePrimaryPresenter
from .lower_primary import LowerPrimaryPresenter
from .upper_primary import UpperPrimaryPresenter
from .detailed import DetailedPresenter


def get_presenter(student_age: int) -> BasePresenter:
    """
    Get the appropriate presenter for a student's age.

    Args:
        student_age: Student's age in years

    Returns:
        Appropriate presenter instance
    """
    if student_age <= 5:
        return PrePrimaryPresenter(student_age)
    elif student_age <= 8:
        return LowerPrimaryPresenter(student_age)
    elif student_age <= 10:
        return UpperPrimaryPresenter(student_age)
    else:
        return DetailedPresenter(student_age)


def transform_for_age(
    raw_evaluation: Dict[str, Any],
    student_age: int
) -> Dict[str, Any]:
    """
    Transform raw evaluation to age-appropriate presentation.

    This is the main entry point for presentation transformation.

    Args:
        raw_evaluation: Full evaluation result from evaluator
        student_age: Student's age in years

    Returns:
        Age-appropriate presentation dict
    """
    presenter = get_presenter(student_age)
    return presenter.transform(raw_evaluation)
