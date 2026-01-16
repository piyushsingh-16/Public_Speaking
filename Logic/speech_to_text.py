"""
Speech-to-Text Module using faster-whisper
Local processing - no API costs
"""

from faster_whisper import WhisperModel
from typing import Dict, List, Optional
import numpy as np


class SpeechToText:
    """
    Speech recognition using local Whisper model.
    Optimized with faster-whisper for scale.
    """

    # Model sizes: tiny, base, small, medium, large-v2, large-v3
    # tiny: fastest, least accurate
    # base: good balance for most cases
    # small: better accuracy, slower
    # medium/large: best accuracy, much slower
    DEFAULT_MODEL = "base"

    def __init__(self, model_size: str = None, device: str = "cpu", compute_type: str = "int8"):
        """
        Initialize Speech-to-Text engine

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large-v3)
            device: "cpu" or "cuda"
            compute_type: "int8" (faster, less memory) or "float16" (more accurate)
        """
        self.model_size = model_size or self.DEFAULT_MODEL
        self.device = device
        self.compute_type = compute_type

        print(f"Loading Whisper model: {self.model_size} on {device}...")
        self.model = WhisperModel(
            self.model_size,
            device=device,
            compute_type=compute_type
        )
        print("Model loaded successfully!")

    def transcribe(self, audio_path: str, language: str = "en") -> Dict:
        """
        Transcribe audio file with word-level timestamps.

        Args:
            audio_path: Path to audio file
            language: Language code (default: "en" for English)

        Returns:
            Dict containing:
                - full_text: Complete transcript
                - segments: List of segments with timing
                - words: List of words with timestamps and confidence
                - language: Detected language
        """
        # Transcribe with word-level timestamps
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            word_timestamps=True,
            vad_filter=True,  # Voice Activity Detection - helps with noise
            vad_parameters=dict(
                threshold=0.5,
                min_speech_duration_ms=250,
                min_silence_duration_ms=100
            )
        )

        # Collect all data
        full_text = []
        all_segments = []
        all_words = []

        for segment in segments:
            segment_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "confidence": segment.avg_logprob  # Average log probability
            }
            all_segments.append(segment_data)
            full_text.append(segment.text.strip())

            # Extract word-level data
            if hasattr(segment, 'words') and segment.words:
                for word in segment.words:
                    word_data = {
                        "word": word.word.strip(),
                        "start": word.start,
                        "end": word.end,
                        "confidence": word.probability
                    }
                    all_words.append(word_data)

        return {
            "full_text": " ".join(full_text),
            "segments": all_segments,
            "words": all_words,
            "language": info.language,
            "language_probability": info.language_probability
        }

    def get_transcript_confidence(self, words: List[Dict]) -> float:
        """
        Calculate average confidence across all words.

        Args:
            words: List of word dictionaries with confidence scores

        Returns:
            Average confidence score (0-1)
        """
        if not words:
            return 0.0

        confidences = [w.get("confidence", 0) for w in words]
        return float(np.mean(confidences))

    def detect_pauses(self, words: List[Dict], threshold: float = 0.5) -> List[Dict]:
        """
        Detect pauses between words.

        Args:
            words: List of word dictionaries with timestamps
            threshold: Minimum pause duration in seconds

        Returns:
            List of pause dictionaries with start, end, and duration
        """
        pauses = []

        for i in range(len(words) - 1):
            current_end = words[i]["end"]
            next_start = words[i + 1]["start"]
            pause_duration = next_start - current_end

            if pause_duration >= threshold:
                pauses.append({
                    "start": current_end,
                    "end": next_start,
                    "duration": pause_duration,
                    "after_word": words[i]["word"],
                    "before_word": words[i + 1]["word"]
                })

        return pauses


if __name__ == "__main__":
    # Example usage
    print("Speech-to-Text module ready!")
    print("Available models: tiny, base, small, medium, large-v3")
    print("Recommended for scale: base (good balance of speed and accuracy)")
