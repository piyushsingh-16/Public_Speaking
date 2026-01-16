import re
from typing import Dict, List, Tuple
from collections import Counter
import numpy as np


class EvaluationMetrics:
    """
    Evaluates speech based on school-specific requirements:
    - Noise-tolerant
    - Accent-agnostic
    - Child-safe (no harsh pronunciation scoring)
    - Age-adjusted weightings
    """

    # Common filler words (language can be expanded)
    FILLER_WORDS = {
        'um', 'uh', 'umm', 'uhh', 'like', 'you know',
        'sort of', 'kind of', 'basically', 'actually',
        'so', 'well', 'right', 'okay', 'yeah'
    }

    # Age group definitions and ideal ranges
    AGE_GROUPS = {
        'pre_primary': {'min_age': 3, 'max_age': 5, 'wpm_range': (40, 90)},
        'primary': {'min_age': 6, 'max_age': 10, 'wpm_range': (60, 120)},
        'middle': {'min_age': 11, 'max_age': 13, 'wpm_range': (100, 150)},
        'secondary': {'min_age': 14, 'max_age': 18, 'wpm_range': (120, 160)}
    }

    def __init__(self, student_age: int = 10):
        """
        Initialize evaluation engine

        Args:
            student_age: Student's age for age-adjusted scoring
        """
        self.student_age = student_age
        self.age_group = self._determine_age_group(student_age)

    def _determine_age_group(self, age: int) -> str:
        """Determine age group from student age"""
        for group, config in self.AGE_GROUPS.items():
            if config['min_age'] <= age <= config['max_age']:
                return group
        return 'secondary'  # Default to highest group

    def evaluate_clarity(self, words: List[Dict]) -> Dict:
        """
        Evaluate speech clarity based on confidence scores.
        NOT based on pronunciation correctness (accent-agnostic, child-safe).

        Args:
            words: List of word dictionaries with confidence scores

        Returns:
            Dict with clarity score and details
        """
        if not words:
            return {
                'score': 0,
                'average_confidence': 0,
                'low_confidence_words': [],
                'feedback': 'No speech detected'
            }

        confidences = [w['confidence'] for w in words]
        avg_confidence = np.mean(confidences)

        # Find low confidence words (potential unclear speech)
        low_conf_threshold = 0.6
        low_confidence_words = [
            {
                'word': w['word'],
                'confidence': w['confidence'],
                'timestamp': w['start']
            }
            for w in words if w['confidence'] < low_conf_threshold
        ]

        # Calculate clarity score (0-100)
        # Higher confidence = better clarity
        clarity_score = min(100, int(avg_confidence * 100))

        # Age-adjusted feedback
        feedback = []
        if clarity_score < 50:
            feedback.append("Try speaking a bit louder and clearer")
        elif clarity_score < 70:
            feedback.append("Good effort! Some words were unclear, practice speaking with confidence")
        else:
            feedback.append("Great clarity! Your words were easy to understand")

        return {
            'score': clarity_score,
            'average_confidence': round(avg_confidence, 2),
            'low_confidence_count': len(low_confidence_words),
            'low_confidence_words': low_confidence_words[:5],  # Top 5 only
            'feedback': feedback
        }

    def evaluate_pace(self, words: List[Dict], total_duration: float) -> Dict:
        """
        Evaluate speaking pace (words per minute).

        Args:
            words: List of word dictionaries
            total_duration: Total speech duration in seconds

        Returns:
            Dict with pace score and details
        """
        if not words or total_duration == 0:
            return {
                'score': 0,
                'wpm': 0,
                'feedback': 'No speech detected'
            }

        # Calculate actual speaking time (excluding long pauses)
        word_count = len(words)
        speaking_duration = total_duration / 60  # Convert to minutes
        wpm = word_count / speaking_duration if speaking_duration > 0 else 0

        # Get ideal range for age group
        ideal_min, ideal_max = self.AGE_GROUPS[self.age_group]['wpm_range']

        # Calculate pace score
        if ideal_min <= wpm <= ideal_max:
            pace_score = 100
        elif wpm < ideal_min:
            # Too slow
            ratio = wpm / ideal_min
            pace_score = int(ratio * 100)
        else:
            # Too fast
            ratio = ideal_max / wpm
            pace_score = int(ratio * 100)

        pace_score = max(0, min(100, pace_score))

        # Generate feedback
        feedback = []
        if wpm < ideal_min:
            feedback.append(f"Your pace is a bit slow ({int(wpm)} words/min). Try speaking a little faster")
        elif wpm > ideal_max:
            feedback.append(f"Your pace is quite fast ({int(wpm)} words/min). Take your time and slow down")
        else:
            feedback.append(f"Excellent pace! ({int(wpm)} words/min)")

        return {
            'score': pace_score,
            'wpm': round(wpm, 1),
            'ideal_range': f"{ideal_min}-{ideal_max} wpm",
            'feedback': feedback
        }

    def evaluate_pauses(self, words: List[Dict]) -> Dict:
        """
        Evaluate pause patterns.
        Only uses word timestamps (noise-tolerant).

        Args:
            words: List of word dictionaries with timestamps

        Returns:
            Dict with pause score and details
        """
        if len(words) < 2:
            return {
                'score': 100,
                'total_pauses': 0,
                'long_pauses': [],
                'feedback': ['Not enough speech to evaluate pauses']
            }

        pauses = []
        for i in range(len(words) - 1):
            pause_duration = words[i + 1]['start'] - words[i]['end']
            if pause_duration > 0:
                pauses.append({
                    'duration': pause_duration,
                    'position': i,
                    'after_word': words[i]['word']
                })

        # Classify pauses
        long_pauses = [p for p in pauses if p['duration'] > 2.0]  # >2 sec
        excessive_pauses = [p for p in pauses if p['duration'] > 4.0]  # >4 sec

        # Calculate score
        total_words = len(words)
        long_pause_ratio = len(long_pauses) / total_words if total_words > 0 else 0

        # Age-adjusted tolerance
        if self.age_group == 'pre_primary':
            tolerance = 0.3  # 30% long pauses acceptable
        elif self.age_group == 'primary':
            tolerance = 0.2  # 20%
        else:
            tolerance = 0.1  # 10%

        if long_pause_ratio <= tolerance:
            pause_score = 100
        else:
            pause_score = max(0, int(100 - (long_pause_ratio - tolerance) * 200))

        # Heavy penalty for excessive pauses (>4 sec)
        pause_score -= len(excessive_pauses) * 10
        pause_score = max(0, pause_score)

        # Generate feedback
        feedback = []
        if len(excessive_pauses) > 0:
            feedback.append(f"You had {len(excessive_pauses)} very long pauses (>4 seconds). Try to keep moving forward")
        elif len(long_pauses) > 3:
            feedback.append("You have several long pauses. It's okay to pause, but try to keep them brief")
        elif len(long_pauses) > 0:
            feedback.append("Good control of pauses! Just a few long ones")
        else:
            feedback.append("Excellent! No excessive pauses detected")

        return {
            'score': pause_score,
            'total_pauses': len(pauses),
            'long_pauses': len(long_pauses),
            'excessive_pauses': len(excessive_pauses),
            'feedback': feedback
        }

    def evaluate_fillers(self, words: List[Dict]) -> Dict:
        """
        Detect and evaluate filler word usage.
        Age-adjusted penalties.

        Args:
            words: List of word dictionaries

        Returns:
            Dict with filler score and details
        """
        if not words:
            return {
                'score': 100,
                'filler_count': 0,
                'filler_ratio': 0,
                'fillers_found': [],
                'feedback': []
            }

        total_words = len(words)
        word_texts = [w['word'].lower().strip('.,!?') for w in words]

        # Count fillers
        filler_instances = []
        for i, word in enumerate(word_texts):
            if word in self.FILLER_WORDS:
                filler_instances.append({
                    'word': word,
                    'timestamp': words[i]['start']
                })

        filler_count = len(filler_instances)
        filler_ratio = filler_count / total_words if total_words > 0 else 0

        # Age-adjusted tolerance
        if self.age_group == 'pre_primary':
            tolerance = 0.15  # 15% fillers acceptable
        elif self.age_group == 'primary':
            tolerance = 0.10  # 10%
        else:
            tolerance = 0.05  # 5%

        # Calculate score
        if filler_ratio <= tolerance:
            filler_score = 100
        else:
            filler_score = max(0, int(100 - (filler_ratio - tolerance) * 300))

        # Generate feedback
        feedback = []
        if filler_ratio > tolerance * 2:
            feedback.append(f"You used many filler words like 'um', 'uh', 'like' ({filler_count} times). Try pausing silently instead")
        elif filler_ratio > tolerance:
            feedback.append(f"You used some filler words ({filler_count} times). Practice reducing them")
        else:
            feedback.append("Great! Very few filler words used")

        return {
            'score': filler_score,
            'filler_count': filler_count,
            'filler_ratio': round(filler_ratio, 3),
            'fillers_found': Counter([f['word'] for f in filler_instances]).most_common(5),
            'feedback': feedback
        }

    def evaluate_repetition(self, words: List[Dict]) -> Dict:
        """
        Detect word and phrase repetition.
        Excessive repetition indicates lack of preparation or nervousness.

        Args:
            words: List of word dictionaries

        Returns:
            Dict with repetition score and details
        """
        if len(words) < 5:
            return {
                'score': 100,
                'repeated_words': [],
                'repeated_phrases': [],
                'feedback': []
            }

        word_texts = [w['word'].lower().strip('.,!?') for w in words]

        # Find consecutive repeated words
        consecutive_repeats = []
        for i in range(len(word_texts) - 1):
            if word_texts[i] == word_texts[i + 1] and len(word_texts[i]) > 2:
                consecutive_repeats.append(word_texts[i])

        # Find repeated 2-3 word phrases
        phrases = []
        for i in range(len(word_texts) - 2):
            phrase = ' '.join(word_texts[i:i+3])
            phrases.append(phrase)

        phrase_counts = Counter(phrases)
        repeated_phrases = [(phrase, count) for phrase, count in phrase_counts.items() if count > 2]

        # Calculate score
        total_words = len(words)
        repeat_penalty = (len(consecutive_repeats) * 5) + (len(repeated_phrases) * 10)
        repetition_score = max(0, 100 - repeat_penalty)

        # Generate feedback
        feedback = []
        if len(repeated_phrases) > 2:
            feedback.append(f"You repeated some phrases multiple times. Try to move forward with new ideas")
        elif len(consecutive_repeats) > 3:
            feedback.append("You repeated some words back-to-back. Take a breath and continue")
        elif len(consecutive_repeats) > 0:
            feedback.append("Just a bit of repetition noticed - doing well overall")
        else:
            feedback.append("Excellent! No noticeable repetition")

        return {
            'score': repetition_score,
            'consecutive_repeats': len(consecutive_repeats),
            'repeated_phrases': repeated_phrases[:3],  # Top 3
            'feedback': feedback
        }

    def evaluate_structure(self, full_text: str, segments: List[Dict]) -> Dict:
        """
        Evaluate speech structure (intro, body, conclusion).
        More important for older students.

        Args:
            full_text: Complete transcript
            segments: List of speech segments

        Returns:
            Dict with structure score and details
        """
        # Simplified structure detection
        text_lower = full_text.lower()

        # Look for introduction markers
        intro_markers = ['hello', 'hi', 'good morning', 'good afternoon', 'today', 'i will', 'i am going to', 'my topic']
        has_intro = any(marker in text_lower[:200] for marker in intro_markers)

        # Look for conclusion markers
        conclusion_markers = ['conclusion', 'finally', 'in summary', 'to conclude', 'thank you', 'that is all']
        has_conclusion = any(marker in text_lower[-200:] for marker in conclusion_markers)

        # Check for body (middle section with content)
        has_body = len(segments) >= 3

        # Calculate structure score
        structure_score = 0
        if has_intro:
            structure_score += 35
        if has_body:
            structure_score += 30
        if has_conclusion:
            structure_score += 35

        # Age-adjusted importance
        if self.age_group in ['pre_primary', 'primary']:
            # Less important for younger students
            structure_score = min(100, structure_score + 30)

        # Generate feedback
        feedback = []
        missing = []
        if not has_intro:
            missing.append('introduction')
        if not has_conclusion:
            missing.append('conclusion')

        if missing and self.age_group in ['middle', 'secondary']:
            feedback.append(f"Try adding a clear {' and '.join(missing)} to your speech")
        elif missing:
            feedback.append(f"Great effort! Next time, try starting with a greeting or ending with 'thank you'")
        else:
            feedback.append("Excellent structure! Clear beginning, middle, and end")

        return {
            'score': structure_score,
            'has_intro': has_intro,
            'has_body': has_body,
            'has_conclusion': has_conclusion,
            'feedback': feedback
        }


if __name__ == "__main__":
    # Example usage
    print("Evaluation Metrics Engine ready!")
    print(f"Age groups: {list(EvaluationMetrics.AGE_GROUPS.keys())}")
