"""
Audio Preprocessing Module
Uses ffmpeg for efficient audio handling at scale
"""

import os
import ffmpeg
import tempfile
from pathlib import Path


class AudioProcessor:
    """
    Handles audio preprocessing for speech evaluation.
    Optimized for scale with ffmpeg.
    """

    SUPPORTED_FORMATS = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm']
    TARGET_SAMPLE_RATE = 16000  # Whisper's native sample rate

    def __init__(self, temp_dir=None):
        """
        Initialize AudioProcessor

        Args:
            temp_dir: Directory for temporary files (optional)
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()

    def is_supported_format(self, file_path):
        """Check if file format is supported"""
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_FORMATS

    def preprocess_audio(self, input_path, output_path=None, normalize=True):
        """
        Preprocess audio file using ffmpeg.

        Args:
            input_path: Path to input audio file
            output_path: Path for output audio file (optional, creates temp if None)
            normalize: Whether to normalize audio volume

        Returns:
            Path to processed audio file
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        if not self.is_supported_format(input_path):
            raise ValueError(f"Unsupported format: {Path(input_path).suffix}")

        # Create output path if not provided
        if output_path is None:
            output_path = os.path.join(
                self.temp_dir,
                f"processed_{Path(input_path).stem}.wav"
            )

        try:
            # Build ffmpeg pipeline
            stream = ffmpeg.input(input_path)
            audio = stream.audio

            if normalize:
                # Normalize audio to -20dB (good for speech)
                audio = audio.filter('loudnorm', I=-20, TP=-1.5, LRA=11)

            # Output configuration: mono, 16kHz WAV
            output = ffmpeg.output(
                audio,
                output_path,
                acodec='pcm_s16le',
                ac=1,
                ar=self.TARGET_SAMPLE_RATE
            )

            # Run with overwrite and quiet mode
            ffmpeg.run(output, overwrite_output=True, quiet=True)

            return output_path

        except ffmpeg.Error as e:
            raise RuntimeError(f"FFmpeg processing failed: {e.stderr.decode() if e.stderr else str(e)}")

    def get_audio_duration(self, file_path):
        """
        Get duration of audio file in seconds.

        Args:
            file_path: Path to audio file

        Returns:
            Duration in seconds (float)
        """
        try:
            probe = ffmpeg.probe(file_path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            raise RuntimeError(f"Failed to get audio duration: {str(e)}")

    def cleanup(self, file_path):
        """Remove temporary file"""
        try:
            if os.path.exists(file_path) and self.temp_dir in file_path:
                os.remove(file_path)
        except Exception as e:
            print(f"Warning: Failed to cleanup {file_path}: {e}")
