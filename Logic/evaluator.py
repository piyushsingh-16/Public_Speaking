"""
Main Public Speaking Evaluator

Orchestrates the entire evaluation pipeline:
1. Audio preprocessing (normalization, format conversion)
2. Audio feature extraction (loudness, pitch, stamina)
3. Speech-to-text with word timestamps
4. Evaluation metrics analysis (9 metrics)
5. Age-appropriate presentation generation
6. JSON report generation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .processors.audio_processor import AudioProcessor
from .processors.speech_to_text import SpeechToText
from .processors.audio_features import AudioFeatureExtractor
from .metrics.evaluator import MetricsEvaluator
from .presenters.factory import transform_for_age
from .config.age_groups import get_detailed_age_group
from .config.settings import WHISPER_CONFIG, OUTPUT_CONFIG


class PublicSpeakingEvaluator:
    """
    Main evaluator class that orchestrates the entire evaluation pipeline.

    Pipeline:
    1. Audio preprocessing (normalization, format conversion)
    2. Audio feature extraction (RMS, pitch, energy)
    3. Speech-to-text with word timestamps
    4. Evaluation metrics analysis (9 metrics)
    5. Age-appropriate presentation generation
    6. JSON report generation

    Returns dual structure:
    - raw_evaluation: Detailed data for teachers/parents
    - child_presentation: Age-appropriate visual feedback
    """

    def __init__(
        self,
        whisper_model: str = None,
        device: str = None,
        compute_type: str = None
    ):
        """
        Initialize the evaluator.

        Args:
            whisper_model: Whisper model size (tiny, base, small, medium, large-v3)
            device: "cpu" or "cuda"
            compute_type: "int8" (faster) or "float16" (more accurate)
        """
        print("Initializing Public Speaking Evaluator...")

        # Use config defaults if not specified
        whisper_model = whisper_model or WHISPER_CONFIG["model_size"]
        device = device or WHISPER_CONFIG["device"]
        compute_type = compute_type or WHISPER_CONFIG["compute_type"]

        # Initialize processors
        self.audio_processor = AudioProcessor()
        self.audio_feature_extractor = AudioFeatureExtractor()
        self.speech_to_text = SpeechToText(
            model_size=whisper_model,
            device=device,
            compute_type=compute_type
        )

        print("Evaluator ready!")

    def evaluate(
        self,
        audio_path: str,
        student_age: int,
        student_name: Optional[str] = None,
        topic: Optional[str] = None,
        save_json: bool = True,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a public speaking audio file.

        Args:
            audio_path: Path to audio file
            student_age: Student's age (for age-adjusted scoring)
            student_name: Student's name (optional)
            topic: Speech topic/prompt (optional)
            save_json: Whether to save result as JSON file
            output_path: Custom output path for JSON (optional)

        Returns:
            Dict containing:
                - raw_evaluation: Complete evaluation results
                - child_presentation: Age-appropriate presentation
        """
        print(f"\n{'='*60}")
        print(f"Starting evaluation for: {Path(audio_path).name}")
        print(f"Student age: {student_age} ({get_detailed_age_group(student_age)})")
        print(f"{'='*60}\n")

        processed_audio = None
        audio_features = None

        try:
            # Step 1: Preprocess audio
            print("Step 1: Preprocessing audio...")
            processed_audio = self.audio_processor.preprocess_audio(audio_path)
            audio_duration = self.audio_processor.get_audio_duration(processed_audio)
            print(f"  Audio preprocessed (Duration: {audio_duration:.2f}s)")

            # Step 2: Extract audio features (before cleanup!)
            print("\nStep 2: Extracting audio features...")
            audio_features = self.audio_feature_extractor.extract_features(processed_audio)
            if audio_features.is_valid():
                print(f"  Loudness: {audio_features.loudness.classification}")
                print(f"  Pitch: {audio_features.pitch.classification}")
                print(f"  Stamina: {audio_features.stamina.classification}")
            else:
                print("  Warning: Audio feature extraction incomplete")

            # Step 3: Transcribe speech
            print("\nStep 3: Transcribing speech...")
            transcript_data = self.speech_to_text.transcribe(processed_audio)
            print(f"  Words detected: {len(transcript_data['words'])}")
            print(f"  Language: {transcript_data['language']}")
            if transcript_data['full_text']:
                preview = transcript_data['full_text'][:80]
                print(f"  Preview: {preview}...")

        except Exception as e:
            return self._error_response(f"Processing failed: {str(e)}")
        finally:
            # Cleanup temporary file
            if processed_audio:
                self.audio_processor.cleanup(processed_audio)

        # Step 4: Evaluate all metrics
        print("\nStep 4: Analyzing speech metrics...")
        metrics_evaluator = MetricsEvaluator(student_age=student_age)
        evaluation_results = metrics_evaluator.evaluate_all(
            words=transcript_data['words'],
            full_text=transcript_data['full_text'],
            segments=transcript_data['segments'],
            total_duration=audio_duration,
            audio_features=audio_features,
        )

        # Print scores
        scores = metrics_evaluator.get_scores_dict(evaluation_results)
        print(f"  Overall: {scores['overall']}/100")
        print(f"  Clarity: {scores['clarity']}/100")
        print(f"  Pace: {scores['pace']}/100")
        print(f"  Loudness: {scores['loudness']}/100")
        print(f"  Pitch Variation: {scores['pitch_variation']}/100")
        print(f"  Stamina: {scores['stamina']}/100")

        # Generate improvement suggestions
        suggestions = metrics_evaluator.generate_improvement_suggestions(
            evaluation_results,
            max_suggestions=OUTPUT_CONFIG["max_feedback_suggestions"]
        )

        # Step 5: Build raw evaluation report
        age_group = get_detailed_age_group(student_age)
        raw_report = {
            "metadata": {
                "student_name": student_name,
                "student_age": student_age,
                "age_group": age_group,
                "topic": topic,
                "audio_file": Path(audio_path).name,
                "duration_seconds": round(audio_duration, 2),
                "word_count": len(transcript_data['words']),
                "evaluation_date": datetime.now().isoformat(),
                "model_used": self.speech_to_text.model_size
            },
            "transcript": {
                "full_text": transcript_data['full_text'],
                "word_count": len(transcript_data['words']),
                "language": transcript_data['language'],
                "language_probability": transcript_data.get('language_probability', 0)
            },
            "scores": scores,
            "detailed_analysis": {
                "clarity": evaluation_results['clarity'],
                "pace": evaluation_results['pace'],
                "pauses": evaluation_results['pause_management'],
                "fillers": evaluation_results['filler_reduction'],
                "repetition": evaluation_results['repetition_control'],
                "structure": evaluation_results['structure'],
                "loudness": evaluation_results['loudness'],
                "pitch_variation": evaluation_results['pitch_variation'],
                "stamina": evaluation_results['stamina'],
            },
            "improvement_suggestions": suggestions,
            "audio_features": audio_features.to_dict() if audio_features else None,
        }

        # Step 6: Generate age-appropriate presentation
        print("\nStep 5: Generating age-appropriate presentation...")
        child_presentation = transform_for_age(raw_report, student_age)
        print(f"  Format: {child_presentation['age_group']}")

        # Combine into final result
        result = {
            "raw_evaluation": raw_report,
            "child_presentation": child_presentation,
        }

        print(f"\n{'='*60}")
        print(f"Overall Score: {scores['overall']}/100")
        print(f"{'='*60}\n")

        # Save JSON if requested
        if save_json:
            output_path = self._save_json(result, output_path)
            print(f"Evaluation saved to: {output_path}")

        return result

    def _save_json(
        self,
        result: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """Save evaluation result to JSON file."""
        if output_path is None:
            output_dir = Path(OUTPUT_CONFIG["output_directory"])
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"evaluation_{timestamp}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=OUTPUT_CONFIG["json_indent"], ensure_ascii=False)

        return str(output_path)

    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate error response."""
        return {
            "error": True,
            "message": error_message,
            "timestamp": datetime.now().isoformat(),
            "raw_evaluation": None,
            "child_presentation": None,
        }


if __name__ == "__main__":
    print("Public Speaking Evaluator - Ready to use!")
    print("\nExample usage:")
    print("  evaluator = PublicSpeakingEvaluator()")
    print("  result = evaluator.evaluate('audio.mp3', student_age=8)")
    print("  raw_data = result['raw_evaluation']")
    print("  child_ui = result['child_presentation']")
