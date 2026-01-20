"""
Metric thresholds and configuration for speech evaluation.

Includes:
- Transcript-based metrics (clarity, pace, pauses, fillers, repetition, structure)
- Audio-based metrics (loudness, pitch variation, stamina)
"""

# Transcript-based Evaluation Metrics Configuration
METRICS_CONFIG = {
    # Pause detection thresholds (in seconds)
    "pause_threshold": 0.5,           # Minimum pause duration
    "long_pause_threshold": 2.0,      # Long pause threshold
    "excessive_pause_threshold": 4.0,  # Excessive pause threshold

    # Filler words (can be extended for other languages)
    "filler_words": {
        "um", "uh", "umm", "uhh", "like", "you know",
        "sort of", "kind of", "basically", "actually",
        "so", "well", "right", "okay", "yeah",
    },

    # Clarity scoring
    "low_confidence_threshold": 0.6,  # Words below this are considered unclear

    # Structure detection keywords
    "intro_markers": [
        "hello", "hi", "good morning", "good afternoon",
        "today", "i will", "i am going to", "my topic",
        "let me tell you", "my name is",
    ],
    "conclusion_markers": [
        "conclusion", "finally", "in summary", "to conclude",
        "thank you", "that is all", "in closing", "to sum up",
        "the end", "that's all",
    ],

    # Repetition detection
    "min_word_length_for_repeat": 3,  # Ignore short word repeats
    "phrase_repeat_threshold": 3,      # Phrase appears 3+ times = repetition
}


# Audio-based Evaluation Metrics Configuration
AUDIO_METRICS_CONFIG = {
    # Loudness thresholds (in dB, relative to normalized audio)
    "loudness": {
        # Optimal dB range for speaking volume
        "optimal_db_range": (-25, -12),
        # Below this = too soft (needs encouragement)
        "too_soft_threshold": -30,
        # Above this = too loud (needs calming)
        "too_loud_threshold": -8,
        # dB variance threshold for inconsistent volume
        "variance_threshold": 8.0,
        # RMS thresholds (linear scale 0-1)
        "rms_optimal_range": (0.02, 0.15),
        "rms_soft_threshold": 0.01,
        "rms_loud_threshold": 0.25,
    },

    # Pitch variation thresholds (in Hz)
    "pitch": {
        # Expected pitch range for children (higher than adults)
        "child_pitch_range": (150, 400),
        # Expected pitch range for adolescents/adults
        "adult_pitch_range": (85, 300),
        # Below this std = monotone
        "monotone_std_threshold": 15.0,
        # Above this std = erratic pitch
        "erratic_std_threshold": 100.0,
        # Minimum voiced frames required for pitch analysis
        "min_voiced_ratio": 0.3,
        # Pitch analysis parameters
        "frame_length": 2048,
        "hop_length": 512,
        "fmin": 65,   # Minimum frequency for pitch detection
        "fmax": 500,  # Maximum frequency for pitch detection
    },

    # Stamina/Energy consistency thresholds
    "stamina": {
        # Number of segments to divide audio into
        "n_segments": 4,
        # Energy should stay above this ratio of initial energy
        "good_dropoff_ratio": 0.75,
        # Warning threshold for significant energy fade
        "warning_dropoff_ratio": 0.50,
        # Coefficient of variation threshold for consistency
        "consistency_threshold": 0.25,
        # Minimum duration (seconds) for stamina analysis
        "min_duration_for_analysis": 15.0,
    },
}


# Mapping of metric IDs to human-readable names
METRIC_NAMES = {
    "clarity": "Clarity",
    "pace": "Speaking Pace",
    "pause": "Pause Management",
    "filler": "Filler Words",
    "repetition": "Repetition",
    "structure": "Speech Structure",
    "loudness": "Voice Strength",
    "pitch_variation": "Expression",
    "stamina": "Energy Consistency",
}


# Feedback templates for each metric
FEEDBACK_TEMPLATES = {
    "clarity": {
        "excellent": "Great clarity! Your words were easy to understand.",
        "good": "Good effort! Some words were unclear, practice speaking with confidence.",
        "needs_work": "Try speaking a bit louder and clearer.",
    },
    "pace": {
        "too_slow": "Your pace is a bit slow ({wpm} words/min). Try speaking a little faster.",
        "excellent": "Excellent pace! ({wpm} words/min)",
        "too_fast": "Your pace is quite fast ({wpm} words/min). Take your time and slow down.",
    },
    "loudness": {
        "too_soft": "Your voice is a bit quiet. Try speaking louder so everyone can hear!",
        "excellent": "Great voice strength! You're easy to hear.",
        "too_loud": "You have a powerful voice! Try speaking just a bit softer.",
        "inconsistent": "Try to keep your voice at the same volume throughout.",
    },
    "pitch_variation": {
        "monotone": "Try adding more expression to your voice - go up and down like a roller coaster!",
        "excellent": "Great expression! Your voice has nice variety.",
        "erratic": "Good energy! Try to control your pitch a bit more.",
    },
    "stamina": {
        "fading": "Your energy dropped towards the end. Try to finish as strong as you started!",
        "excellent": "Great job keeping your energy up throughout!",
        "inconsistent": "Try to maintain steady energy from start to finish.",
    },
}
