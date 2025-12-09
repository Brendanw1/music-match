"""Quiz scoring and user vector calculation."""
import numpy as np
from typing import Optional

from .questions import QUIZ_QUESTIONS, get_question_by_id


FEATURE_KEYS = [
    "bpm_normalized",
    "energy",
    "danceability",
    "acousticness",
    "valence",
    "instrumentalness",
    "loudness"
]


def calculate_user_vector(answers: list[dict]) -> dict[str, float]:
    """
    Calculate user feature vector from quiz answers.

    Args:
        answers: List of {"question_id": str, "option_id": str}

    Returns:
        Dictionary mapping feature names to normalized values (0-1)
    """
    # Accumulate weights for each feature
    feature_totals: dict[str, list[float]] = {key: [] for key in FEATURE_KEYS}

    for answer in answers:
        question_id = answer.get("question_id")
        option_id = answer.get("option_id")

        question = get_question_by_id(question_id)
        if not question:
            continue

        # Find the selected option
        selected_option = None
        for opt in question["options"]:
            if opt["id"] == option_id:
                selected_option = opt
                break

        if not selected_option:
            continue

        # Add weights from this answer
        weights = selected_option.get("weights", {})
        for feature, weight in weights.items():
            if feature in feature_totals:
                feature_totals[feature].append(weight)

    # Calculate average for each feature
    result = {}
    for feature in FEATURE_KEYS:
        values = feature_totals[feature]
        if values:
            result[feature] = sum(values) / len(values)
        else:
            # Default to middle value if no answers affected this feature
            result[feature] = 0.5

    return result


def vector_to_array(vector: dict[str, float]) -> np.ndarray:
    """
    Convert feature vector dictionary to numpy array.

    Args:
        vector: Dictionary mapping feature names to values

    Returns:
        Numpy array with features in standard order
    """
    return np.array([vector.get(key, 0.5) for key in FEATURE_KEYS])


def array_to_vector(arr: np.ndarray) -> dict[str, float]:
    """
    Convert numpy array back to feature vector dictionary.

    Args:
        arr: Numpy array with features in standard order

    Returns:
        Dictionary mapping feature names to values
    """
    return {key: float(arr[i]) for i, key in enumerate(FEATURE_KEYS)}


def get_radar_chart_data(vector: dict[str, float]) -> list[dict]:
    """
    Format feature vector for radar chart display.

    Args:
        vector: Feature vector dictionary

    Returns:
        List of {feature, value, fullMark} dicts for radar chart
    """
    display_names = {
        "bpm_normalized": "Tempo",
        "energy": "Energy",
        "danceability": "Danceability",
        "acousticness": "Acoustic",
        "valence": "Positivity",
        "instrumentalness": "Instrumental",
        "loudness": "Loudness"
    }

    return [
        {
            "feature": display_names.get(key, key),
            "value": round(vector.get(key, 0.5) * 100, 1),
            "fullMark": 100
        }
        for key in FEATURE_KEYS
    ]
