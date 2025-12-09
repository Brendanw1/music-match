"""Audio feature extraction module."""
from .extract import extract_features, normalize_bpm, ESSENTIA_AVAILABLE
from .batch_extract import batch_extract_features, get_audio_files, parse_filename
from .normalize import FeatureScaler, normalize_feature, normalize_loudness
from .spotify_features import (
    normalize_spotify_features,
    spotify_features_to_song_dict,
    get_feature_vector,
    KEY_NAMES,
)

__all__ = [
    # Essentia extraction
    "extract_features",
    "normalize_bpm",
    "ESSENTIA_AVAILABLE",
    "batch_extract_features",
    "get_audio_files",
    "parse_filename",
    # Normalization
    "FeatureScaler",
    "normalize_feature",
    "normalize_loudness",
    # Spotify features
    "normalize_spotify_features",
    "spotify_features_to_song_dict",
    "get_feature_vector",
    "KEY_NAMES",
]
