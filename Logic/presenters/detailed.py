"""
Detailed presenter for ages 11+.

Focus: Full detailed analysis with multiple suggestions.
Style: Professional, informative, actionable.
"""

from typing import Any, Dict, List

from .base import BasePresenter


class DetailedPresenter(BasePresenter):
    """
    Presenter for ages 11+.

    Shows full detailed analysis:
    - All metric scores
    - Detailed analysis per metric
    - Multiple improvement suggestions
    """

    @property
    def age_group(self) -> str:
        if self.student_age <= 13:
            return "middle"
        return "secondary"

    def transform(self, raw_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Transform evaluation for detailed display."""
        # For older students, we mostly pass through the raw evaluation
        # with some formatting adjustments

        scores = raw_evaluation.get("scores", {})
        detailed_analysis = raw_evaluation.get("detailed_analysis", {})
        suggestions = raw_evaluation.get("improvement_suggestions", [])

        # Clean up scores dict
        clean_scores = {}
        for key, value in scores.items():
            if isinstance(value, dict):
                clean_scores[key] = value.get("score", 0)
            else:
                clean_scores[key] = value

        # Clean up detailed analysis (extract key info)
        clean_analysis = {}
        for metric, data in detailed_analysis.items():
            if isinstance(data, dict):
                clean_analysis[metric] = {
                    "score": data.get("score", 0),
                    "feedback": data.get("feedback", []),
                    # Include key details based on metric
                    **self._get_metric_details(metric, data),
                }
            else:
                clean_analysis[metric] = {"score": data}

        return {
            "age_group": self.age_group,
            "format_version": self.FORMAT_VERSION,
            "scores": clean_scores,
            "detailed_analysis": clean_analysis,
            "improvement_suggestions": suggestions[:5],  # Max 5 suggestions
            "show_to_child": True,
        }

    def _get_metric_details(self, metric: str, data: Dict) -> Dict:
        """Extract relevant details for each metric type."""
        details = {}

        if metric == "clarity":
            details["average_confidence"] = data.get("average_confidence")
            details["low_confidence_count"] = data.get("low_confidence_count")

        elif metric == "pace":
            details["words_per_minute"] = data.get("words_per_minute", data.get("wpm"))
            details["ideal_range"] = data.get("ideal_range")

        elif metric in ["pause_management", "pauses"]:
            details["long_pauses"] = data.get("long_pauses")
            details["excessive_pauses"] = data.get("excessive_pauses")

        elif metric in ["filler_reduction", "fillers"]:
            details["filler_count"] = data.get("filler_count")
            details["common_fillers"] = data.get("common_fillers", data.get("fillers_found"))

        elif metric in ["repetition_control", "repetition"]:
            details["consecutive_repeats"] = data.get("consecutive_repeats")
            details["repeated_phrases"] = data.get("repeated_phrases")

        elif metric == "structure":
            details["has_intro"] = data.get("has_intro", data.get("has_introduction"))
            details["has_conclusion"] = data.get("has_conclusion")

        elif metric == "loudness":
            details["classification"] = data.get("classification")
            details["rms_db"] = data.get("rms_db")

        elif metric == "pitch_variation":
            details["classification"] = data.get("classification")
            details["pitch_range"] = data.get("pitch_range")

        elif metric == "stamina":
            details["classification"] = data.get("classification")
            details["energy_dropoff"] = data.get("energy_dropoff")

        return details
