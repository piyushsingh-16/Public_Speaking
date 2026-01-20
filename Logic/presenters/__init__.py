"""
Age-appropriate output presenters.

Transforms raw evaluation results into child-friendly presentations
for different age groups.
"""

from .base import BasePresenter
from .pre_primary import PrePrimaryPresenter
from .lower_primary import LowerPrimaryPresenter
from .upper_primary import UpperPrimaryPresenter
from .detailed import DetailedPresenter
from .factory import get_presenter, transform_for_age

__all__ = [
    "BasePresenter",
    "PrePrimaryPresenter",
    "LowerPrimaryPresenter",
    "UpperPrimaryPresenter",
    "DetailedPresenter",
    "get_presenter",
    "transform_for_age",
]
