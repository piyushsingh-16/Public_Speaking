"""
Tests for age-appropriate presenters.
"""

import pytest
from Logic.presenters.factory import get_presenter, transform_for_age
from Logic.presenters.pre_primary import PrePrimaryPresenter
from Logic.presenters.lower_primary import LowerPrimaryPresenter
from Logic.presenters.upper_primary import UpperPrimaryPresenter
from Logic.presenters.detailed import DetailedPresenter


# Sample raw evaluation data for testing
SAMPLE_EVALUATION = {
    "metadata": {
        "student_name": "Test Student",
        "student_age": 8,
        "age_group": "lower_primary",
        "duration_seconds": 45.0,
    },
    "scores": {
        "overall": 75,
        "clarity": 80,
        "pace": 70,
        "pause_management": 75,
        "filler_reduction": 85,
        "repetition_control": 78,
        "structure": 65,
        "loudness": 82,
        "pitch_variation": 70,
        "stamina": 75,
    },
    "detailed_analysis": {
        "clarity": {"score": 80, "feedback": ["Good clarity!"]},
        "pace": {"score": 70, "wpm": 95, "feedback": ["Good pace"]},
        "pauses": {"score": 75, "feedback": ["Good pauses"]},
        "fillers": {"score": 85, "feedback": ["Few fillers"]},
        "repetition": {"score": 78, "feedback": ["Good flow"]},
        "structure": {"score": 65, "feedback": ["Needs intro"]},
        "loudness": {"score": 82, "classification": "optimal", "feedback": ["Good volume"]},
        "pitch_variation": {"score": 70, "classification": "expressive", "feedback": ["Nice expression"]},
        "stamina": {"score": 75, "classification": "consistent", "feedback": ["Good energy"]},
    },
    "improvement_suggestions": [
        "Add a clear introduction",
        "Keep up the good pace",
    ],
}


class TestPresenterFactory:
    """Test presenter factory functions."""

    def test_get_presenter_pre_primary(self):
        """Test getting presenter for ages 3-5."""
        presenter = get_presenter(4)
        assert isinstance(presenter, PrePrimaryPresenter)
        assert presenter.age_group == "pre_primary"

    def test_get_presenter_lower_primary(self):
        """Test getting presenter for ages 6-8."""
        presenter = get_presenter(7)
        assert isinstance(presenter, LowerPrimaryPresenter)
        assert presenter.age_group == "lower_primary"

    def test_get_presenter_upper_primary(self):
        """Test getting presenter for ages 9-10."""
        presenter = get_presenter(10)
        assert isinstance(presenter, UpperPrimaryPresenter)
        assert presenter.age_group == "upper_primary"

    def test_get_presenter_detailed(self):
        """Test getting presenter for ages 11+."""
        presenter = get_presenter(12)
        assert isinstance(presenter, DetailedPresenter)
        assert presenter.age_group in ["middle", "secondary"]


class TestPrePrimaryPresenter:
    """Test pre-primary (ages 3-5) presenter."""

    def test_transform_returns_correct_structure(self):
        """Test that transform returns correct keys."""
        presenter = PrePrimaryPresenter(4)
        result = presenter.transform(SAMPLE_EVALUATION)

        assert "age_group" in result
        assert result["age_group"] == "pre_primary"
        assert "voice_detected" in result
        assert "voice_strength" in result
        assert "message" in result
        assert "show_to_child" in result

    def test_voice_strength_lion(self):
        """Test voice strength classification for loud voice."""
        presenter = PrePrimaryPresenter(4)
        eval_data = SAMPLE_EVALUATION.copy()
        eval_data["scores"]["loudness"] = 85

        result = presenter.transform(eval_data)
        assert result["voice_strength"] == "lion"

    def test_voice_strength_mouse(self):
        """Test voice strength classification for soft voice."""
        presenter = PrePrimaryPresenter(4)
        eval_data = SAMPLE_EVALUATION.copy()
        eval_data["scores"]["loudness"] = 30

        result = presenter.transform(eval_data)
        assert result["voice_strength"] == "mouse"


class TestLowerPrimaryPresenter:
    """Test lower primary (ages 6-8) presenter."""

    def test_transform_returns_correct_structure(self):
        """Test that transform returns correct keys."""
        presenter = LowerPrimaryPresenter(7)
        result = presenter.transform(SAMPLE_EVALUATION)

        assert "age_group" in result
        assert result["age_group"] == "lower_primary"
        assert "metrics" in result
        assert len(result["metrics"]) == 3  # Voice, pace, expression
        assert "message" in result

    def test_metrics_have_correct_format(self):
        """Test that metrics have icons and levels."""
        presenter = LowerPrimaryPresenter(7)
        result = presenter.transform(SAMPLE_EVALUATION)

        for metric in result["metrics"]:
            assert "id" in metric
            assert "icon" in metric


class TestUpperPrimaryPresenter:
    """Test upper primary (ages 9-10) presenter."""

    def test_transform_returns_correct_structure(self):
        """Test that transform returns correct keys."""
        presenter = UpperPrimaryPresenter(10)
        result = presenter.transform(SAMPLE_EVALUATION)

        assert "age_group" in result
        assert result["age_group"] == "upper_primary"
        assert "progress_bars" in result
        assert "improvement_tip" in result
        assert "badges_earned" in result

    def test_progress_bars_count(self):
        """Test that there are 4 progress bars."""
        presenter = UpperPrimaryPresenter(10)
        result = presenter.transform(SAMPLE_EVALUATION)

        assert len(result["progress_bars"]) == 4

    def test_single_improvement_tip(self):
        """Test that only one improvement tip is provided."""
        presenter = UpperPrimaryPresenter(10)
        result = presenter.transform(SAMPLE_EVALUATION)

        assert "text" in result["improvement_tip"]
        assert "target_metric" in result["improvement_tip"]


class TestDetailedPresenter:
    """Test detailed (ages 11+) presenter."""

    def test_transform_returns_correct_structure(self):
        """Test that transform returns full analysis."""
        presenter = DetailedPresenter(12)
        result = presenter.transform(SAMPLE_EVALUATION)

        assert "age_group" in result
        assert result["age_group"] in ["middle", "secondary"]
        assert "scores" in result
        assert "detailed_analysis" in result
        assert "improvement_suggestions" in result


class TestTransformForAge:
    """Test the main transform_for_age function."""

    def test_deterministic_output(self):
        """Test that same input produces same output."""
        result1 = transform_for_age(SAMPLE_EVALUATION, 8)
        result2 = transform_for_age(SAMPLE_EVALUATION, 8)

        # Compare key fields (message may have randomness)
        assert result1["age_group"] == result2["age_group"]
        assert result1["metrics"] == result2["metrics"]

    def test_different_ages_different_output(self):
        """Test that different ages produce different formats."""
        result_5 = transform_for_age(SAMPLE_EVALUATION, 5)
        result_8 = transform_for_age(SAMPLE_EVALUATION, 8)
        result_12 = transform_for_age(SAMPLE_EVALUATION, 12)

        assert result_5["age_group"] == "pre_primary"
        assert result_8["age_group"] == "lower_primary"
        assert result_12["age_group"] in ["middle", "secondary"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
