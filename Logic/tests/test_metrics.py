"""
Tests for evaluation metrics.
"""

import pytest
from Logic.metrics.clarity import ClarityMetric
from Logic.metrics.pace import PaceMetric
from Logic.metrics.pauses import PauseMetric
from Logic.metrics.fillers import FillerMetric
from Logic.metrics.repetition import RepetitionMetric
from Logic.metrics.structure import StructureMetric
from Logic.metrics.loudness import LoudnessMetric
from Logic.metrics.pitch_variation import PitchVariationMetric
from Logic.metrics.stamina import StaminaMetric
from Logic.models.audio_features import AudioFeatures, LoudnessFeatures, PitchFeatures, StaminaFeatures


# Sample word data for testing
SAMPLE_WORDS = [
    {"word": "Hello", "start": 0.0, "end": 0.5, "confidence": 0.95},
    {"word": "my", "start": 0.6, "end": 0.8, "confidence": 0.92},
    {"word": "name", "start": 0.9, "end": 1.2, "confidence": 0.88},
    {"word": "is", "start": 1.3, "end": 1.5, "confidence": 0.90},
    {"word": "John", "start": 1.6, "end": 2.0, "confidence": 0.85},
    {"word": "um", "start": 2.5, "end": 2.7, "confidence": 0.70},
    {"word": "and", "start": 2.8, "end": 3.0, "confidence": 0.88},
    {"word": "I", "start": 3.1, "end": 3.2, "confidence": 0.95},
    {"word": "like", "start": 3.3, "end": 3.6, "confidence": 0.90},
    {"word": "speaking", "start": 3.7, "end": 4.2, "confidence": 0.82},
]


class TestClarityMetric:
    """Test clarity metric evaluator."""

    def test_evaluate_returns_score(self):
        """Test that evaluate returns a score."""
        metric = ClarityMetric(student_age=10)
        result = metric.evaluate(words=SAMPLE_WORDS)

        assert "score" in result
        assert 0 <= result["score"] <= 100

    def test_empty_words_returns_zero(self):
        """Test that empty words returns zero score."""
        metric = ClarityMetric(student_age=10)
        result = metric.evaluate(words=[])

        assert result["score"] == 0

    def test_high_confidence_high_score(self):
        """Test that high confidence words produce high score."""
        metric = ClarityMetric(student_age=10)
        high_conf_words = [
            {"word": "test", "start": 0, "end": 1, "confidence": 0.95}
            for _ in range(10)
        ]
        result = metric.evaluate(words=high_conf_words)

        assert result["score"] >= 90


class TestPaceMetric:
    """Test pace metric evaluator."""

    def test_evaluate_returns_wpm(self):
        """Test that evaluate returns WPM."""
        metric = PaceMetric(student_age=10)
        result = metric.evaluate(words=SAMPLE_WORDS, total_duration=10.0)

        assert "wpm" in result
        assert "score" in result

    def test_ideal_pace_high_score(self):
        """Test that ideal pace gives high score."""
        metric = PaceMetric(student_age=10)
        # 100 words in 1 minute = 100 WPM (ideal for 10 year old)
        words = [{"word": "test", "start": i * 0.6, "end": i * 0.6 + 0.5, "confidence": 0.9}
                 for i in range(100)]
        result = metric.evaluate(words=words, total_duration=60.0)

        assert result["score"] >= 80


class TestPauseMetric:
    """Test pause metric evaluator."""

    def test_evaluate_returns_pause_counts(self):
        """Test that evaluate returns pause information."""
        metric = PauseMetric(student_age=10)
        result = metric.evaluate(words=SAMPLE_WORDS)

        assert "total_pauses" in result
        assert "long_pauses" in result
        assert "score" in result

    def test_no_long_pauses_high_score(self):
        """Test that no long pauses gives high score."""
        metric = PauseMetric(student_age=10)
        # Words with no long pauses
        words = [
            {"word": f"word{i}", "start": i * 0.5, "end": i * 0.5 + 0.4, "confidence": 0.9}
            for i in range(20)
        ]
        result = metric.evaluate(words=words)

        assert result["score"] >= 90


class TestFillerMetric:
    """Test filler metric evaluator."""

    def test_evaluate_returns_filler_count(self):
        """Test that evaluate returns filler information."""
        metric = FillerMetric(student_age=10)
        result = metric.evaluate(words=SAMPLE_WORDS)

        assert "filler_count" in result
        assert "score" in result

    def test_detects_fillers(self):
        """Test that fillers are detected."""
        metric = FillerMetric(student_age=10)
        result = metric.evaluate(words=SAMPLE_WORDS)

        # "um" and "like" are fillers
        assert result["filler_count"] >= 1


class TestRepetitionMetric:
    """Test repetition metric evaluator."""

    def test_evaluate_returns_repetition_info(self):
        """Test that evaluate returns repetition information."""
        metric = RepetitionMetric(student_age=10)
        result = metric.evaluate(words=SAMPLE_WORDS)

        assert "consecutive_repeats" in result
        assert "score" in result

    def test_consecutive_repeats_detected(self):
        """Test that consecutive repeats are detected."""
        metric = RepetitionMetric(student_age=10)
        # Need at least 5 words for repetition detection
        words = [
            {"word": "hello", "start": 0, "end": 0.5, "confidence": 0.9},
            {"word": "hello", "start": 0.6, "end": 1.0, "confidence": 0.9},
            {"word": "world", "start": 1.1, "end": 1.5, "confidence": 0.9},
            {"word": "today", "start": 1.6, "end": 2.0, "confidence": 0.9},
            {"word": "great", "start": 2.1, "end": 2.5, "confidence": 0.9},
        ]
        result = metric.evaluate(words=words)

        assert result["consecutive_repeats"] >= 1


class TestStructureMetric:
    """Test structure metric evaluator."""

    def test_evaluate_returns_structure_info(self):
        """Test that evaluate returns structure information."""
        metric = StructureMetric(student_age=10)
        result = metric.evaluate(
            full_text="Hello everyone, today I will talk about cats. Thank you.",
            segments=[{}, {}, {}]
        )

        assert "has_intro" in result
        assert "has_conclusion" in result
        assert "score" in result

    def test_detects_intro(self):
        """Test that intro markers are detected."""
        metric = StructureMetric(student_age=10)
        result = metric.evaluate(
            full_text="Hello everyone, today I will talk about cats.",
            segments=[{}, {}, {}]
        )

        assert result["has_intro"] is True

    def test_detects_conclusion(self):
        """Test that conclusion markers are detected."""
        metric = StructureMetric(student_age=10)
        result = metric.evaluate(
            full_text="That is my speech. Thank you for listening.",
            segments=[{}, {}, {}]
        )

        assert result["has_conclusion"] is True


class TestLoudnessMetric:
    """Test loudness metric evaluator."""

    def test_evaluate_returns_loudness_info(self):
        """Test that evaluate returns loudness information."""
        metric = LoudnessMetric(student_age=10)
        features = AudioFeatures(
            loudness=LoudnessFeatures(
                rms_mean=0.05,
                rms_db_mean=-20,
                classification="optimal"
            ),
            duration_seconds=30.0
        )
        result = metric.evaluate(audio_features=features)

        assert "score" in result
        assert "classification" in result

    def test_optimal_loudness_high_score(self):
        """Test that optimal loudness gives high score."""
        metric = LoudnessMetric(student_age=10)
        features = AudioFeatures(
            loudness=LoudnessFeatures(
                rms_mean=0.05,
                rms_db_mean=-18,
                classification="optimal"
            ),
            duration_seconds=30.0
        )
        result = metric.evaluate(audio_features=features)

        assert result["score"] >= 80


class TestPitchVariationMetric:
    """Test pitch variation metric evaluator."""

    def test_evaluate_returns_pitch_info(self):
        """Test that evaluate returns pitch information."""
        metric = PitchVariationMetric(student_age=10)
        features = AudioFeatures(
            pitch=PitchFeatures(
                pitch_mean=250,
                pitch_std=30,
                voiced_ratio=0.7,
                classification="expressive"
            ),
            duration_seconds=30.0
        )
        result = metric.evaluate(audio_features=features)

        assert "score" in result
        assert "classification" in result

    def test_expressive_pitch_high_score(self):
        """Test that expressive pitch gives high score."""
        metric = PitchVariationMetric(student_age=10)
        features = AudioFeatures(
            pitch=PitchFeatures(
                pitch_mean=250,
                pitch_std=40,
                voiced_ratio=0.8,
                classification="expressive"
            ),
            duration_seconds=30.0
        )
        result = metric.evaluate(audio_features=features)

        assert result["score"] >= 70


class TestStaminaMetric:
    """Test stamina metric evaluator."""

    def test_evaluate_returns_stamina_info(self):
        """Test that evaluate returns stamina information."""
        metric = StaminaMetric(student_age=10)
        features = AudioFeatures(
            stamina=StaminaFeatures(
                energy_segments=[0.05, 0.05, 0.04, 0.04],
                energy_dropoff=0.8,
                energy_consistency=0.85,
                classification="consistent"
            ),
            duration_seconds=30.0
        )
        result = metric.evaluate(audio_features=features)

        assert "score" in result
        assert "classification" in result

    def test_consistent_energy_high_score(self):
        """Test that consistent energy gives high score."""
        metric = StaminaMetric(student_age=10)
        features = AudioFeatures(
            stamina=StaminaFeatures(
                energy_segments=[0.05, 0.05, 0.05, 0.05],
                energy_dropoff=1.0,
                energy_consistency=0.95,
                classification="consistent"
            ),
            duration_seconds=30.0
        )
        result = metric.evaluate(audio_features=features)

        assert result["score"] >= 80


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
