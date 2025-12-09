"""Audio feature extraction using Essentia."""
from pathlib import Path
from typing import Optional
import numpy as np

try:
    import essentia
    import essentia.standard as es
    ESSENTIA_AVAILABLE = True
except ImportError:
    ESSENTIA_AVAILABLE = False
    print("Warning: Essentia not available. Feature extraction will use mock data.")


def extract_features(audio_path: str | Path) -> dict:
    """
    Extract audio features from a file using Essentia.

    Args:
        audio_path: Path to audio file

    Returns:
        Dictionary with normalized features (0-1 except bpm which stays raw)
    """
    if not ESSENTIA_AVAILABLE:
        return _mock_features()

    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Load audio
    loader = es.MonoLoader(filename=str(audio_path))
    audio = loader()

    features = {}

    # BPM extraction
    rhythm_extractor = es.RhythmExtractor2013()
    bpm, beats, beats_confidence, _, _ = rhythm_extractor(audio)
    features["bpm"] = float(bpm)

    # Key extraction
    key_extractor = es.KeyExtractor()
    key, scale, key_strength = key_extractor(audio)
    features["key"] = key
    features["scale"] = scale

    # Energy
    energy_algo = es.Energy()
    energy = energy_algo(audio)
    # Normalize energy (log scale, typical range 0-10000)
    features["energy"] = min(1.0, max(0.0, np.log1p(energy) / 10))

    # Danceability
    danceability_algo = es.Danceability()
    danceability, _ = danceability_algo(audio)
    features["danceability"] = float(danceability)

    # Loudness (integrated)
    loudness_algo = es.LoudnessEBUR128()
    _, _, integrated_loudness, _ = loudness_algo(audio)
    # Normalize loudness (typical range -60 to 0 dB)
    features["loudness"] = min(1.0, max(0.0, (integrated_loudness + 60) / 60))

    # Spectral features for acousticness approximation
    spectrum_algo = es.Spectrum()
    spectral_centroid_algo = es.Centroid()
    spectral_flatness_algo = es.Flatness()

    frame_size = 2048
    hop_size = 1024

    centroid_values = []
    flatness_values = []

    for frame in es.FrameGenerator(audio, frameSize=frame_size, hopSize=hop_size):
        spectrum = spectrum_algo(frame)
        if len(spectrum) > 0 and np.sum(spectrum) > 0:
            centroid_values.append(spectral_centroid_algo(spectrum))
            flatness_values.append(spectral_flatness_algo(spectrum))

    avg_centroid = np.mean(centroid_values) if centroid_values else 0.5
    avg_flatness = np.mean(flatness_values) if flatness_values else 0.5

    # Acousticness: high flatness + low centroid suggests acoustic
    # Electronic music tends to have specific frequency peaks (low flatness)
    features["acousticness"] = min(1.0, max(0.0, avg_flatness * 2))

    # Instrumentalness approximation using voice activity detection
    try:
        # Use speech/music discriminator as proxy
        speech_algo = es.SpeechDetector()
        frame_results = []
        for frame in es.FrameGenerator(audio, frameSize=frame_size, hopSize=hop_size):
            if len(frame) >= frame_size:
                speech_prob = speech_algo(frame)
                frame_results.append(speech_prob)

        if frame_results:
            avg_speech = np.mean(frame_results)
            # Invert: high speech = low instrumentalness
            features["instrumentalness"] = 1.0 - min(1.0, avg_speech)
        else:
            features["instrumentalness"] = 0.5
    except Exception:
        # Fallback if speech detector fails
        features["instrumentalness"] = 0.5

    # Valence approximation using mode and spectral features
    # Major key + high energy + fast tempo suggests positive valence
    mode_factor = 1.0 if scale == "major" else 0.6
    tempo_factor = min(1.0, features["bpm"] / 140)
    energy_factor = features["energy"]

    features["valence"] = min(1.0, (mode_factor * 0.4 + tempo_factor * 0.3 + energy_factor * 0.3))

    return features


def _mock_features() -> dict:
    """Generate mock features when Essentia is not available."""
    import random
    return {
        "bpm": random.uniform(60, 180),
        "key": random.choice(["C", "D", "E", "F", "G", "A", "B"]),
        "scale": random.choice(["major", "minor"]),
        "energy": random.uniform(0, 1),
        "danceability": random.uniform(0, 1),
        "acousticness": random.uniform(0, 1),
        "valence": random.uniform(0, 1),
        "instrumentalness": random.uniform(0, 1),
        "loudness": random.uniform(0, 1),
    }


def normalize_bpm(bpm: float, min_bpm: float = 40, max_bpm: float = 200) -> float:
    """Normalize BPM to 0-1 range."""
    return min(1.0, max(0.0, (bpm - min_bpm) / (max_bpm - min_bpm)))
