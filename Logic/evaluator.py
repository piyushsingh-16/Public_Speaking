"""
Main Public Speaking Evaluator
Orchestrates the entire evaluation pipeline
"""

import json
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

from audio_processor import AudioProcessor
from speech_to_text import SpeechToText
from evaluation_metrics import EvaluationMetrics


class PublicSpeakingEvaluator:
    """
    Main evaluator class that orchestrates the entire evaluation pipeline.

    Pipeline:
    1. Audio preprocessing (normalization, format conversion)
    2. Speech-to-text with word timestamps
    3. Evaluation metrics analysis
    4. JSON report generation
    """

    def __init__(
        self,
        whisper_model: str = "base",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        Initialize the evaluator

        Args:
            whisper_model: Whisper model size (tiny, base, small, medium, large-v3)
            device: "cpu" or "cuda"
            compute_type: "int8" (faster) or "float16" (more accurate)
        """
        print("Initializing Public Speaking Evaluator...")

        self.audio_processor = AudioProcessor()
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
    ) -> Dict:
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
            Dict containing complete evaluation results
        """
        print(f"\n{'='*60}")
        print(f"Starting evaluation for: {Path(audio_path).name}")
        print(f"{'='*60}\n")

        # Step 1: Preprocess audio
        print("Step 1: Preprocessing audio...")
        processed_audio = None
        try:
            processed_audio = self.audio_processor.preprocess_audio(audio_path)
            audio_duration = self.audio_processor.get_audio_duration(processed_audio)
            print(f"✓ Audio preprocessed successfully (Duration: {audio_duration:.2f}s)")
        except Exception as e:
            return self._error_response(f"Audio preprocessing failed: {str(e)}")

        # Step 2: Transcribe speech
        print("\nStep 2: Transcribing speech...")
        try:
            transcript_data = self.speech_to_text.transcribe(processed_audio)
            print(f"✓ Transcription complete")
            print(f"  - Words detected: {len(transcript_data['words'])}")
            print(f"  - Language: {transcript_data['language']}")
            print(f"  - Text preview: {transcript_data['full_text'][:100]}...")
        except Exception as e:
            return self._error_response(f"Transcription failed: {str(e)}")
        finally:
            # Cleanup temporary file
            if processed_audio:
                self.audio_processor.cleanup(processed_audio)

        # Step 3: Evaluate metrics
        print("\nStep 3: Analyzing speech metrics...")
        evaluator = EvaluationMetrics(student_age=student_age)

        clarity_result = evaluator.evaluate_clarity(transcript_data['words'])
        print(f"✓ Clarity: {clarity_result['score']}/100")

        pace_result = evaluator.evaluate_pace(transcript_data['words'], audio_duration)
        print(f"✓ Pace: {pace_result['score']}/100 ({pace_result['wpm']} wpm)")

        pause_result = evaluator.evaluate_pauses(transcript_data['words'])
        print(f"✓ Pauses: {pause_result['score']}/100")

        filler_result = evaluator.evaluate_fillers(transcript_data['words'])
        print(f"✓ Fillers: {filler_result['score']}/100")

        repetition_result = evaluator.evaluate_repetition(transcript_data['words'])
        print(f"✓ Repetition: {repetition_result['score']}/100")

        structure_result = evaluator.evaluate_structure(
            transcript_data['full_text'],
            transcript_data['segments']
        )
        print(f"✓ Structure: {structure_result['score']}/100")

        # Calculate weighted overall score (age-adjusted weights)
        weights = self._get_age_adjusted_weights(evaluator.age_group)
        overall_score = (
            clarity_result['score'] * weights['clarity'] +
            pace_result['score'] * weights['pace'] +
            pause_result['score'] * weights['pause'] +
            filler_result['score'] * weights['filler'] +
            repetition_result['score'] * weights['repetition'] +
            structure_result['score'] * weights['structure']
        )
        overall_score = round(overall_score, 1)

        print(f"\n{'='*60}")
        print(f"Overall Score: {overall_score}/100")
        print(f"{'='*60}\n")

        # Step 4: Compile final report
        report = {
            "metadata": {
                "student_name": student_name,
                "student_age": student_age,
                "age_group": evaluator.age_group,
                "topic": topic,
                "audio_file": Path(audio_path).name,
                "duration_seconds": round(audio_duration, 2),
                "evaluation_date": datetime.now().isoformat(),
                "model_used": self.speech_to_text.model_size
            },
            "transcript": {
                "full_text": transcript_data['full_text'],
                "word_count": len(transcript_data['words']),
                "language": transcript_data['language']
            },
            "scores": {
                "overall": overall_score,
                "clarity": clarity_result['score'],
                "pace": pace_result['score'],
                "pause_management": pause_result['score'],
                "filler_reduction": filler_result['score'],
                "repetition_control": repetition_result['score'],
                "structure": structure_result['score']
            },
            "detailed_analysis": {
                "clarity": {
                    "score": clarity_result['score'],
                    "average_confidence": clarity_result['average_confidence'],
                    "low_confidence_words": clarity_result['low_confidence_words'],
                    "feedback": clarity_result['feedback']
                },
                "pace": {
                    "score": pace_result['score'],
                    "words_per_minute": pace_result['wpm'],
                    "ideal_range": pace_result['ideal_range'],
                    "feedback": pace_result['feedback']
                },
                "pauses": {
                    "score": pause_result['score'],
                    "total_pauses": pause_result['total_pauses'],
                    "long_pauses": pause_result['long_pauses'],
                    "excessive_pauses": pause_result['excessive_pauses'],
                    "feedback": pause_result['feedback']
                },
                "fillers": {
                    "score": filler_result['score'],
                    "filler_count": filler_result['filler_count'],
                    "filler_ratio": filler_result['filler_ratio'],
                    "common_fillers": filler_result['fillers_found'],
                    "feedback": filler_result['feedback']
                },
                "repetition": {
                    "score": repetition_result['score'],
                    "consecutive_repeats": repetition_result['consecutive_repeats'],
                    "repeated_phrases": repetition_result['repeated_phrases'],
                    "feedback": repetition_result['feedback']
                },
                "structure": {
                    "score": structure_result['score'],
                    "has_introduction": structure_result['has_intro'],
                    "has_body": structure_result['has_body'],
                    "has_conclusion": structure_result['has_conclusion'],
                    "feedback": structure_result['feedback']
                }
            },
            "improvement_suggestions": self._generate_improvement_suggestions(
                clarity_result, pace_result, pause_result,
                filler_result, repetition_result, structure_result
            )
        }

        # Save JSON if requested
        if save_json:
            if output_path is None:
                output_dir = Path("evaluation_results")
                output_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = output_dir / f"evaluation_{timestamp}.json"

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            print(f"✓ Evaluation saved to: {output_path}")

        return report

    def _get_age_adjusted_weights(self, age_group: str) -> Dict[str, float]:
        """
        Get age-adjusted weights for different metrics.
        Younger students: More focus on basic skills (clarity, pace)
        Older students: More focus on advanced skills (structure, content)
        """
        weights = {
            'pre_primary': {
                'clarity': 0.30,
                'pace': 0.25,
                'pause': 0.20,
                'filler': 0.15,
                'repetition': 0.05,
                'structure': 0.05
            },
            'primary': {
                'clarity': 0.25,
                'pace': 0.20,
                'pause': 0.20,
                'filler': 0.15,
                'repetition': 0.10,
                'structure': 0.10
            },
            'middle': {
                'clarity': 0.20,
                'pace': 0.15,
                'pause': 0.15,
                'filler': 0.15,
                'repetition': 0.15,
                'structure': 0.20
            },
            'secondary': {
                'clarity': 0.15,
                'pace': 0.15,
                'pause': 0.10,
                'filler': 0.15,
                'repetition': 0.15,
                'structure': 0.30
            }
        }
        return weights.get(age_group, weights['secondary'])

    def _generate_improvement_suggestions(
        self,
        clarity, pace, pause, filler, repetition, structure
    ) -> List[str]:
        """Generate prioritized improvement suggestions"""
        suggestions = []

        # Collect all feedback with scores
        all_feedback = [
            (clarity['score'], clarity['feedback']),
            (pace['score'], pace['feedback']),
            (pause['score'], pause['feedback']),
            (filler['score'], filler['feedback']),
            (repetition['score'], repetition['feedback']),
            (structure['score'], structure['feedback'])
        ]

        # Sort by score (lowest first = needs most improvement)
        all_feedback.sort(key=lambda x: x[0])

        # Collect feedback, prioritizing areas needing improvement
        for score, feedback_list in all_feedback:
            for feedback in feedback_list:
                if feedback not in suggestions:
                    suggestions.append(feedback)

        return suggestions[:5]  # Top 5 suggestions

    def _error_response(self, error_message: str) -> Dict:
        """Generate error response"""
        return {
            "error": True,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    print("Public Speaking Evaluator - Ready to use!")
    print("\nExample usage:")
    print("  evaluator = PublicSpeakingEvaluator()")
    print("  result = evaluator.evaluate('audio.mp3', student_age=12)")
