"""
Age group definitions and metric weights for different student ages.

Age Groups:
- pre_primary (3-5): Focus on voice presence and confidence
- lower_primary (6-8): Introduce basic metrics with visual feedback
- upper_primary (9-10): Progress bars and single improvement tips
- middle (11-13): Detailed analysis
- secondary (14-18): Full professional feedback
"""

from typing import Literal

# Type definitions
AgeGroupType = Literal["pre_primary", "lower_primary", "upper_primary", "middle", "secondary"]
DetailedAgeGroupType = Literal["pre_primary", "lower_primary", "upper_primary", "middle", "secondary"]


# Age Group Definitions
AGE_GROUPS = {
    "pre_primary": {
        "min_age": 3,
        "max_age": 5,
        "wpm_range": (40, 90),
        "filler_tolerance": 0.15,   # 15% fillers acceptable
        "pause_tolerance": 0.30,    # 30% long pauses acceptable
        "description": "Monkey See, Monkey Do - Focus on voice presence",
    },
    "lower_primary": {
        "min_age": 6,
        "max_age": 8,
        "wpm_range": (60, 110),
        "filler_tolerance": 0.12,
        "pause_tolerance": 0.25,
        "description": "Play the Role - Visual icon-based feedback",
    },
    "upper_primary": {
        "min_age": 9,
        "max_age": 10,
        "wpm_range": (80, 130),
        "filler_tolerance": 0.10,
        "pause_tolerance": 0.20,
        "description": "Gamified Improvement - Progress bars + tips",
    },
    "middle": {
        "min_age": 11,
        "max_age": 13,
        "wpm_range": (100, 150),
        "filler_tolerance": 0.08,
        "pause_tolerance": 0.15,
        "description": "Detailed Analysis - Full metrics with explanations",
    },
    "secondary": {
        "min_age": 14,
        "max_age": 18,
        "wpm_range": (120, 160),
        "filler_tolerance": 0.05,
        "pause_tolerance": 0.10,
        "description": "Professional Feedback - Complete detailed analysis",
    },
}


# Transcript-based Metric Weights (age-adjusted)
# Determines importance of each metric for different age groups
METRIC_WEIGHTS = {
    "pre_primary": {
        "clarity": 0.25,
        "pace": 0.20,
        "pause": 0.15,
        "filler": 0.10,
        "repetition": 0.05,
        "structure": 0.05,
        # Audio metrics get 20% total
        "loudness": 0.15,
        "pitch_variation": 0.05,
        "stamina": 0.00,
    },
    "lower_primary": {
        "clarity": 0.20,
        "pace": 0.15,
        "pause": 0.15,
        "filler": 0.10,
        "repetition": 0.05,
        "structure": 0.05,
        # Audio metrics
        "loudness": 0.15,
        "pitch_variation": 0.10,
        "stamina": 0.05,
    },
    "upper_primary": {
        "clarity": 0.18,
        "pace": 0.15,
        "pause": 0.12,
        "filler": 0.10,
        "repetition": 0.08,
        "structure": 0.07,
        # Audio metrics
        "loudness": 0.12,
        "pitch_variation": 0.10,
        "stamina": 0.08,
    },
    "middle": {
        "clarity": 0.15,
        "pace": 0.12,
        "pause": 0.10,
        "filler": 0.12,
        "repetition": 0.12,
        "structure": 0.15,
        # Audio metrics
        "loudness": 0.08,
        "pitch_variation": 0.08,
        "stamina": 0.08,
    },
    "secondary": {
        "clarity": 0.12,
        "pace": 0.10,
        "pause": 0.08,
        "filler": 0.12,
        "repetition": 0.12,
        "structure": 0.20,
        # Audio metrics
        "loudness": 0.08,
        "pitch_variation": 0.10,
        "stamina": 0.08,
    },
}


# Audio-specific metric weights (subset for clarity)
AUDIO_METRIC_WEIGHTS = {
    "pre_primary": {
        "loudness": 0.70,        # Primary focus for young kids
        "pitch_variation": 0.30,  # Binary only (expressive vs flat)
        "stamina": 0.00,         # Ignored for this age
    },
    "lower_primary": {
        "loudness": 0.50,
        "pitch_variation": 0.35,
        "stamina": 0.15,
    },
    "upper_primary": {
        "loudness": 0.40,
        "pitch_variation": 0.35,
        "stamina": 0.25,
    },
    "middle": {
        "loudness": 0.33,
        "pitch_variation": 0.34,
        "stamina": 0.33,
    },
    "secondary": {
        "loudness": 0.30,
        "pitch_variation": 0.40,
        "stamina": 0.30,
    },
}


def get_age_group(age: int) -> AgeGroupType:
    """
    Determine age group from student age.
    Uses the original 4-group system for backward compatibility.

    Args:
        age: Student's age in years

    Returns:
        Age group identifier
    """
    if age <= 5:
        return "pre_primary"
    elif age <= 10:
        # Map to "primary" style for backward compatibility
        return "lower_primary" if age <= 8 else "upper_primary"
    elif age <= 13:
        return "middle"
    else:
        return "secondary"


def get_detailed_age_group(age: int) -> DetailedAgeGroupType:
    """
    Determine detailed age group for presentation purposes.
    Uses 5-group system with split primary for child-appropriate output.

    Args:
        age: Student's age in years

    Returns:
        Detailed age group identifier
    """
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


def get_wpm_range(age: int) -> tuple[int, int]:
    """Get ideal WPM range for a given age."""
    age_group = get_detailed_age_group(age)
    return AGE_GROUPS[age_group]["wpm_range"]


def get_tolerance(age: int, tolerance_type: str) -> float:
    """
    Get tolerance value for a given age and tolerance type.

    Args:
        age: Student's age
        tolerance_type: 'filler' or 'pause'

    Returns:
        Tolerance value (0-1)
    """
    age_group = get_detailed_age_group(age)
    key = f"{tolerance_type}_tolerance"
    return AGE_GROUPS[age_group].get(key, 0.10)
