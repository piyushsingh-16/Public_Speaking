"""
Audio Feature Extraction Module

Extracts loudness, pitch, and energy metrics from audio waveform
using librosa for analysis.

Features extracted:
- Loudness (RMS energy, dB levels)
- Pitch variation (using pyin algorithm)
- Stamina (energy consistency over time)
"""

import warnings
from typing import Optional, Tuple

import numpy as np

# Suppress librosa warnings about audioread
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="librosa")

import librosa

from ..models.audio_features import (
    AudioFeatures,
    LoudnessFeatures,
    PitchFeatures,
    StaminaFeatures,
)
from ..config.metrics_config import AUDIO_METRICS_CONFIG


class AudioFeatureExtractor:
    """
    Extracts audio features for public speaking evaluation.
    Works directly on audio waveform using librosa.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        frame_length: int = 2048,
        hop_length: int = 512,
        n_segments: int = 4,
    ):
        """
        Initialize the audio feature extractor.

        Args:
            sample_rate: Target sample rate (default: 16kHz to match Whisper)
            frame_length: FFT window size for analysis
            hop_length: Number of samples between frames
            n_segments: Number of segments for stamina analysis
        """
        self.sample_rate = sample_rate
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.n_segments = n_segments

        # Load config
        self.loudness_config = AUDIO_METRICS_CONFIG["loudness"]
        self.pitch_config = AUDIO_METRICS_CONFIG["pitch"]
        self.stamina_config = AUDIO_METRICS_CONFIG["stamina"]

    def extract_features(self, audio_path: str) -> AudioFeatures:
        """
        Extract all audio features from an audio file.

        Args:
            audio_path: Path to audio file (WAV format preferred)

        Returns:
            AudioFeatures dataclass with all extracted features
        """
        try:
            # Load audio file
            y, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)

            if len(y) == 0:
                return AudioFeatures.empty()

            duration = len(y) / sr

            # Extract features
            loudness = self._extract_loudness(y, sr)
            pitch = self._extract_pitch(y, sr)
            stamina = self._extract_stamina(loudness.rms_over_time)

            return AudioFeatures(
                loudness=loudness,
                pitch=pitch,
                stamina=stamina,
                duration_seconds=duration,
                sample_rate=sr,
            )

        except Exception as e:
            print(f"Error extracting audio features: {e}")
            return AudioFeatures.empty()

    def _extract_loudness(self, y: np.ndarray, sr: int) -> LoudnessFeatures:
        """
        Extract loudness/RMS energy metrics.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            LoudnessFeatures with RMS metrics
        """
        # Calculate RMS energy
        rms = librosa.feature.rms(
            y=y,
            frame_length=self.frame_length,
            hop_length=self.hop_length
        )[0]

        # Basic stats
        rms_mean = float(np.mean(rms))
        rms_std = float(np.std(rms))

        # Convert to dB
        rms_db = librosa.amplitude_to_db(rms, ref=1.0)
        rms_db_mean = float(np.mean(rms_db))
        rms_db_std = float(np.std(rms_db))

        # Classify loudness
        optimal_range = self.loudness_config["optimal_db_range"]
        too_soft = self.loudness_config["too_soft_threshold"]
        too_loud = self.loudness_config["too_loud_threshold"]

        if rms_db_mean < too_soft:
            classification = "too_soft"
        elif rms_db_mean > too_loud:
            classification = "too_loud"
        else:
            classification = "optimal"

        return LoudnessFeatures(
            rms_mean=rms_mean,
            rms_std=rms_std,
            rms_db_mean=rms_db_mean,
            rms_db_std=rms_db_std,
            rms_over_time=rms.tolist(),
            classification=classification,
        )

    def _extract_pitch(self, y: np.ndarray, sr: int) -> PitchFeatures:
        """
        Extract pitch/prosody metrics using pyin algorithm.

        Args:
            y: Audio time series
            sr: Sample rate

        Returns:
            PitchFeatures with pitch metrics
        """
        # Use pyin for robust pitch detection
        fmin = self.pitch_config["fmin"]
        fmax = self.pitch_config["fmax"]

        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                fmin=fmin,
                fmax=fmax,
                sr=sr,
                frame_length=self.frame_length,
                hop_length=self.hop_length,
            )
        except Exception as e:
            print(f"Pitch extraction failed: {e}")
            return PitchFeatures()

        # Filter to only voiced frames
        voiced_f0 = f0[~np.isnan(f0)]
        voiced_ratio = len(voiced_f0) / len(f0) if len(f0) > 0 else 0

        # Check if we have enough voiced frames
        min_voiced = self.pitch_config["min_voiced_ratio"]
        if voiced_ratio < min_voiced or len(voiced_f0) < 5:
            return PitchFeatures(
                voiced_ratio=voiced_ratio,
                classification="insufficient_data",
            )

        # Calculate pitch statistics
        pitch_mean = float(np.mean(voiced_f0))
        pitch_std = float(np.std(voiced_f0))
        pitch_min = float(np.min(voiced_f0))
        pitch_max = float(np.max(voiced_f0))

        # Classify pitch variation
        monotone_threshold = self.pitch_config["monotone_std_threshold"]
        erratic_threshold = self.pitch_config["erratic_std_threshold"]

        if pitch_std < monotone_threshold:
            classification = "monotone"
        elif pitch_std > erratic_threshold:
            classification = "erratic"
        else:
            classification = "expressive"

        # Convert f0 to list, replacing nan with None
        pitch_over_time = [
            float(v) if not np.isnan(v) else None
            for v in f0
        ]

        return PitchFeatures(
            pitch_mean=pitch_mean,
            pitch_std=pitch_std,
            pitch_range=(pitch_min, pitch_max),
            pitch_over_time=pitch_over_time,
            voiced_ratio=voiced_ratio,
            classification=classification,
        )

    def _extract_stamina(self, rms_over_time: list) -> StaminaFeatures:
        """
        Extract stamina/energy consistency metrics.

        Args:
            rms_over_time: RMS values over time from loudness extraction

        Returns:
            StaminaFeatures with energy consistency metrics
        """
        if not rms_over_time or len(rms_over_time) < self.n_segments:
            return StaminaFeatures()

        rms_array = np.array(rms_over_time)

        # Divide into segments
        segment_length = len(rms_array) // self.n_segments
        if segment_length == 0:
            return StaminaFeatures()

        energy_segments = []
        for i in range(self.n_segments):
            start = i * segment_length
            end = start + segment_length if i < self.n_segments - 1 else len(rms_array)
            segment_energy = float(np.mean(rms_array[start:end]))
            energy_segments.append(segment_energy)

        # Calculate dropoff (last segment / first segment)
        if energy_segments[0] > 0:
            energy_dropoff = energy_segments[-1] / energy_segments[0]
        else:
            energy_dropoff = 1.0

        # Calculate consistency (inverse of coefficient of variation)
        mean_energy = np.mean(energy_segments)
        if mean_energy > 0:
            cv = np.std(energy_segments) / mean_energy
            energy_consistency = max(0, 1 - cv)
        else:
            energy_consistency = 0.0

        # Classify stamina
        good_dropoff = self.stamina_config["good_dropoff_ratio"]
        warning_dropoff = self.stamina_config["warning_dropoff_ratio"]
        consistency_threshold = self.stamina_config["consistency_threshold"]

        if energy_dropoff >= good_dropoff and energy_consistency >= consistency_threshold:
            classification = "consistent"
        elif energy_dropoff < warning_dropoff:
            classification = "fading"
        else:
            classification = "inconsistent"

        return StaminaFeatures(
            energy_segments=energy_segments,
            energy_dropoff=energy_dropoff,
            energy_consistency=energy_consistency,
            classification=classification,
        )


if __name__ == "__main__":
    print("Audio Feature Extractor ready!")
    print("Features: Loudness (RMS), Pitch (pyin), Stamina (energy consistency)")
