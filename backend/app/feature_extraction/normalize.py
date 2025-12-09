"""Feature normalization utilities."""
import numpy as np
from typing import Optional
import json
from pathlib import Path


class FeatureScaler:
    """MinMax scaler for audio features."""

    def __init__(self):
        self.min_values: dict[str, float] = {}
        self.max_values: dict[str, float] = {}
        self.fitted = False

    def fit(self, features_list: list[dict]) -> "FeatureScaler":
        """
        Fit scaler to feature data.

        Args:
            features_list: List of feature dictionaries

        Returns:
            Self for chaining
        """
        if not features_list:
            return self

        # Get all feature keys
        keys = set()
        for features in features_list:
            keys.update(features.keys())

        # Calculate min/max for each feature
        for key in keys:
            values = [f.get(key, 0) for f in features_list if isinstance(f.get(key), (int, float))]
            if values:
                self.min_values[key] = min(values)
                self.max_values[key] = max(values)

        self.fitted = True
        return self

    def transform(self, features: dict) -> dict:
        """
        Transform features using fitted min/max values.

        Args:
            features: Feature dictionary

        Returns:
            Normalized feature dictionary
        """
        if not self.fitted:
            return features

        normalized = {}
        for key, value in features.items():
            if isinstance(value, (int, float)) and key in self.min_values:
                min_val = self.min_values[key]
                max_val = self.max_values[key]

                if max_val - min_val > 0:
                    normalized[key] = (value - min_val) / (max_val - min_val)
                else:
                    normalized[key] = 0.5
            else:
                normalized[key] = value

        return normalized

    def fit_transform(self, features_list: list[dict]) -> list[dict]:
        """
        Fit and transform in one step.

        Args:
            features_list: List of feature dictionaries

        Returns:
            List of normalized feature dictionaries
        """
        self.fit(features_list)
        return [self.transform(f) for f in features_list]

    def save(self, filepath: Path):
        """Save scaler parameters to file."""
        data = {
            "min_values": self.min_values,
            "max_values": self.max_values,
            "fitted": self.fitted
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, filepath: Path) -> "FeatureScaler":
        """Load scaler parameters from file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        self.min_values = data.get("min_values", {})
        self.max_values = data.get("max_values", {})
        self.fitted = data.get("fitted", False)
        return self


def normalize_feature(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize a single feature value to 0-1 range.

    Args:
        value: Feature value
        min_val: Minimum expected value
        max_val: Maximum expected value

    Returns:
        Normalized value between 0 and 1
    """
    if max_val - min_val <= 0:
        return 0.5

    normalized = (value - min_val) / (max_val - min_val)
    return max(0.0, min(1.0, normalized))


def normalize_bpm(bpm: float, min_bpm: float = 40, max_bpm: float = 200) -> float:
    """
    Normalize BPM to 0-1 range.

    Args:
        bpm: Beats per minute
        min_bpm: Minimum expected BPM
        max_bpm: Maximum expected BPM

    Returns:
        Normalized BPM value
    """
    return normalize_feature(bpm, min_bpm, max_bpm)


def normalize_loudness(loudness_db: float, min_db: float = -60, max_db: float = 0) -> float:
    """
    Normalize loudness (in dB) to 0-1 range.

    Args:
        loudness_db: Loudness in decibels
        min_db: Minimum expected loudness
        max_db: Maximum expected loudness

    Returns:
        Normalized loudness value
    """
    return normalize_feature(loudness_db, min_db, max_db)
