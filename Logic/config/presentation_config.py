"""
Presentation configuration for age-appropriate child output.

Includes:
- Badge definitions per age group
- Character messages for young children
- Icon mappings for visual feedback
- Color schemes for UI
"""

import random
from typing import Optional


# Badge definitions per age group
BADGES = {
    "pre_primary": [
        {
            "id": "strong_voice",
            "name": "Strong Voice Badge",
            "emoji": "🦁",
            "condition": "loudness_score >= 70",
            "animation": "roar",
        },
        {
            "id": "brave_speaker",
            "name": "Brave Speaker Badge",
            "emoji": "⭐",
            "condition": "voice_present and duration >= 10",
            "animation": "sparkle",
        },
        {
            "id": "happy_talker",
            "name": "Happy Talker Badge",
            "emoji": "🌟",
            "condition": "pitch_variation_score >= 60",
            "animation": "bounce",
        },
    ],
    "lower_primary": [
        {
            "id": "confident_speaker",
            "name": "Confident Speaker Badge",
            "emoji": "🏅",
            "condition": "loudness_score >= 70 and pace_score >= 60",
            "animation": "bounce",
        },
        {
            "id": "clear_voice",
            "name": "Clear Voice Badge",
            "emoji": "🔊",
            "condition": "clarity_score >= 70",
            "animation": "pulse",
        },
        {
            "id": "perfect_pace",
            "name": "Perfect Pace Badge",
            "emoji": "⏱️",
            "condition": "pace_score >= 80",
            "animation": "spin",
        },
        {
            "id": "expressive_star",
            "name": "Expressive Star",
            "emoji": "🌈",
            "condition": "pitch_variation_score >= 75",
            "animation": "rainbow",
        },
    ],
    "upper_primary": [
        {
            "id": "all_rounder",
            "name": "All-Rounder Badge",
            "emoji": "🎯",
            "condition": "all_scores >= 70",
            "animation": "confetti",
        },
        {
            "id": "expression_star",
            "name": "Expression Star",
            "emoji": "🌟",
            "condition": "pitch_variation_score >= 80",
            "animation": "sparkle",
        },
        {
            "id": "confidence_champion",
            "name": "Confidence Champion",
            "emoji": "💪",
            "condition": "loudness_score >= 85",
            "animation": "flex",
        },
        {
            "id": "endurance_master",
            "name": "Endurance Master",
            "emoji": "🏃",
            "condition": "stamina_score >= 80",
            "animation": "run",
        },
        {
            "id": "smooth_speaker",
            "name": "Smooth Speaker",
            "emoji": "🎤",
            "condition": "filler_score >= 90",
            "animation": "mic_drop",
        },
    ],
    "middle": [
        {
            "id": "professional_speaker",
            "name": "Professional Speaker",
            "emoji": "🎓",
            "condition": "overall_score >= 80",
            "animation": "graduate",
        },
        {
            "id": "structure_master",
            "name": "Structure Master",
            "emoji": "📊",
            "condition": "structure_score >= 85",
            "animation": "chart",
        },
    ],
    "secondary": [
        {
            "id": "orator",
            "name": "Master Orator",
            "emoji": "🏆",
            "condition": "overall_score >= 85",
            "animation": "trophy",
        },
    ],
}


# Character messages for pre-primary (ages 3-5)
CHARACTER_MESSAGES = {
    "too_soft": [
        "Try Lion Voice! 🦁 ROAR so everyone can hear you!",
        "Can you be louder like a big dinosaur? 🦖",
        "Let's wake up the sleepy owl with your voice! 🦉",
        "Use your superhero voice! 🦸",
        "Speak up like a singing bird! 🐦",
    ],
    "just_right": [
        "Perfect voice! You sound amazing! ⭐",
        "Goldilocks would say your voice is JUST RIGHT! 🐻",
        "Your voice is as bright as sunshine! ☀️",
        "Wow! You spoke like a star! 🌟",
        "What a wonderful speaker you are! 🎉",
    ],
    "too_loud": [
        "Wow, you're loud! Let's try indoor voice! 🏠",
        "Shh, we don't want to scare the bunny! 🐰",
        "Great energy! Now let's be a little gentler 🌸",
        "You're powerful! Let's use our gentle giant voice 🐘",
    ],
    "celebration": [
        "You did it! Amazing job speaking! 🎉",
        "Superstar! You spoke so well! 🌟",
        "Hooray! What a great speaker you are! 🎊",
        "Give yourself a big hug! You were wonderful! 🤗",
        "You're a speaking champion! 🏆",
    ],
    "encouragement": [
        "You're doing great! Keep trying! 💪",
        "Every speaker practices! You're learning! 📚",
        "I believe in you! Try again! 🌈",
        "You're getting better every time! 🚀",
    ],
}


# Icon mappings for visual feedback (lower_primary)
ICONS = {
    "pace": {
        "too_slow": {"icon": "🐢", "label": "Turtle Pace"},
        "just_right": {"icon": "👍", "label": "Perfect!"},
        "too_fast": {"icon": "🐇", "label": "Bunny Fast"},
    },
    "voice_strength": {
        "levels": [
            {"icon": "🔇", "label": "Very Quiet"},
            {"icon": "🔈", "label": "Quiet"},
            {"icon": "🔉", "label": "Good"},
            {"icon": "🔊", "label": "Great"},
            {"icon": "📢", "label": "Strong"},
            {"icon": "🔊✨", "label": "Perfect!"},
        ],
    },
    "expression": {
        "levels": [
            {"icon": "😐", "label": "Flat"},
            {"icon": "🙂", "label": "Okay"},
            {"icon": "😊", "label": "Good"},
            {"icon": "😃", "label": "Great"},
            {"icon": "🤩", "label": "Amazing"},
            {"icon": "⭐", "label": "Superstar!"},
        ],
    },
}


# Color schemes for UI
COLORS = {
    "metrics": {
        "confidence": "#4CAF50",   # Green
        "clarity": "#2196F3",      # Blue
        "expression": "#FF9800",   # Orange
        "pace": "#9C27B0",         # Purple
        "stamina": "#E91E63",      # Pink
        "structure": "#00BCD4",    # Cyan
    },
    "levels": {
        "poor": "#F44336",         # Red
        "needs_work": "#FF9800",   # Orange
        "good": "#FFEB3B",         # Yellow
        "great": "#8BC34A",        # Light Green
        "excellent": "#4CAF50",    # Green
    },
    "age_themes": {
        "pre_primary": {
            "primary": "#FFD54F",   # Sunny yellow
            "secondary": "#FF8A65", # Soft orange
            "background": "#FFF8E1", # Cream
        },
        "lower_primary": {
            "primary": "#64B5F6",   # Sky blue
            "secondary": "#81C784", # Green
            "background": "#E3F2FD", # Light blue
        },
        "upper_primary": {
            "primary": "#9575CD",   # Purple
            "secondary": "#4DD0E1", # Teal
            "background": "#EDE7F6", # Light purple
        },
        "middle": {
            "primary": "#4DB6AC",   # Teal
            "secondary": "#7986CB", # Indigo
            "background": "#E0F2F1", # Light teal
        },
        "secondary": {
            "primary": "#5C6BC0",   # Deep indigo
            "secondary": "#26A69A", # Teal
            "background": "#E8EAF6", # Light indigo
        },
    },
}


# Character definitions for visual feedback
CHARACTERS = {
    "lion": {
        "name": "Leo the Lion",
        "states": {
            "roaring": "Leo is roaring with pride!",
            "celebrating": "Leo is so happy with you!",
            "encouraging": "Leo says try again!",
            "sleeping": "Leo is sleeping... speak louder to wake him!",
        },
    },
    "robot": {
        "name": "Robo the Robot",
        "states": {
            "powered_up": "Robo is fully charged!",
            "celebrating": "Robo is doing a happy dance!",
            "encouraging": "Robo believes in you!",
            "low_power": "Robo needs your voice energy!",
        },
    },
    "owl": {
        "name": "Oliver the Owl",
        "states": {
            "wise": "Oliver thinks you're very smart!",
            "celebrating": "Oliver hoots with joy!",
            "encouraging": "Oliver says practice makes perfect!",
            "sleeping": "Oliver is napping... wake him up!",
        },
    },
}


def get_random_message(category: str) -> str:
    """Get a random message from a category."""
    messages = CHARACTER_MESSAGES.get(category, CHARACTER_MESSAGES["encouragement"])
    return random.choice(messages)


def get_icon_for_level(metric: str, level: int, max_level: int = 5) -> dict:
    """
    Get icon and label for a metric level.

    Args:
        metric: Metric type ('voice_strength', 'expression')
        level: Current level (0 to max_level)
        max_level: Maximum level

    Returns:
        Dict with 'icon' and 'label'
    """
    icons = ICONS.get(metric, {}).get("levels", [])
    if not icons:
        return {"icon": "❓", "label": "Unknown"}

    # Map level to icon index
    index = min(level, len(icons) - 1)
    return icons[index]


def get_pace_icon(pace_score: int, wpm: float, ideal_range: tuple) -> dict:
    """Get pace icon based on score and WPM."""
    min_wpm, max_wpm = ideal_range

    if wpm < min_wpm * 0.8:
        return ICONS["pace"]["too_slow"]
    elif wpm > max_wpm * 1.2:
        return ICONS["pace"]["too_fast"]
    else:
        return ICONS["pace"]["just_right"]


def get_badges_for_scores(
    scores: dict,
    age_group: str,
    duration: Optional[float] = None
) -> list:
    """
    Calculate which badges were earned based on scores.

    Args:
        scores: Dict of metric scores
        age_group: Age group identifier
        duration: Speech duration in seconds

    Returns:
        List of earned badge dicts
    """
    earned_badges = []
    available_badges = BADGES.get(age_group, [])

    for badge in available_badges:
        condition = badge["condition"]
        earned = False

        # Compound conditions first (check before simple ones)
        if "loudness_score >= " in condition and " and pace_score >= " in condition:
            parts = condition.split(" and ")
            loudness_threshold = int(parts[0].split(">= ")[1])
            pace_threshold = int(parts[1].split(">= ")[1])
            earned = (
                scores.get("loudness", 0) >= loudness_threshold
                and scores.get("pace", 0) >= pace_threshold
            )
        elif "voice_present and duration >= " in condition:
            min_duration = int(condition.split(">= ")[1])
            voice_present = scores.get("loudness", 0) > 30
            earned = voice_present and (duration or 0) >= min_duration
        # Simple condition evaluation
        elif "all_scores >= " in condition:
            threshold = int(condition.split(">= ")[1])
            earned = all(v >= threshold for v in scores.values() if isinstance(v, (int, float)))
        elif "loudness_score >= " in condition:
            threshold = int(condition.split(">= ")[1])
            earned = scores.get("loudness", 0) >= threshold
        elif "clarity_score >= " in condition:
            threshold = int(condition.split(">= ")[1])
            earned = scores.get("clarity", 0) >= threshold
        elif "pace_score >= " in condition:
            threshold = int(condition.split(">= ")[1])
            earned = scores.get("pace", 0) >= threshold
        elif "pitch_variation_score >= " in condition:
            threshold = int(condition.split(">= ")[1])
            earned = scores.get("pitch_variation", 0) >= threshold
        elif "stamina_score >= " in condition:
            threshold = int(condition.split(">= ")[1])
            earned = scores.get("stamina", 0) >= threshold
        elif "filler_score >= " in condition:
            threshold = int(condition.split(">= ")[1])
            earned = scores.get("filler", 0) >= threshold
        elif "structure_score >= " in condition:
            threshold = int(condition.split(">= ")[1])
            earned = scores.get("structure", 0) >= threshold
        elif "overall_score >= " in condition:
            threshold = int(condition.split(">= ")[1])
            earned = scores.get("overall", 0) >= threshold

        if earned:
            earned_badges.append({
                "id": badge["id"],
                "name": badge["name"],
                "emoji": badge["emoji"],
                "animation": badge.get("animation", "bounce"),
            })

    return earned_badges
