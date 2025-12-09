"""Feature extraction and normalization for Spotify audio features."""
from typing import Optional


# Key mapping: Spotify uses 0-11 for C, C#, D, etc.
KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def normalize_spotify_features(spotify_features: dict) -> dict:
    """
    Normalize Spotify audio features to match our clustering format.

    Spotify features are mostly already 0-1, but we need to:
    - Normalize tempo (BPM) to 0-1 range
    - Normalize loudness from dB scale to 0-1
    - Convert key number to key name
    - Map mode to scale name

    Args:
        spotify_features: Raw Spotify audio features dict

    Returns:
        Normalized features dict compatible with clustering
    """
    # Extract tempo and normalize (typical range 40-200 BPM)
    tempo = spotify_features.get("tempo", 120)
    bpm_normalized = min(1.0, max(0.0, (tempo - 40) / 160))

    # Normalize loudness (typical range -60 to 0 dB)
    loudness_db = spotify_features.get("loudness", -10)
    loudness_normalized = min(1.0, max(0.0, (loudness_db + 60) / 60))

    # Convert key number to name
    key_num = spotify_features.get("key", 0)
    key_name = KEY_NAMES[key_num] if 0 <= key_num < 12 else "C"

    # Convert mode to scale
    mode = spotify_features.get("mode", 1)
    scale = "major" if mode == 1 else "minor"

    return {
        # Core features for clustering (all 0-1)
        "bpm_normalized": bpm_normalized,
        "energy": spotify_features.get("energy", 0.5),
        "danceability": spotify_features.get("danceability", 0.5),
        "acousticness": spotify_features.get("acousticness", 0.5),
        "valence": spotify_features.get("valence", 0.5),
        "instrumentalness": spotify_features.get("instrumentalness", 0.5),
        "loudness": loudness_normalized,

        # Additional features (kept for reference)
        "speechiness": spotify_features.get("speechiness", 0),
        "liveness": spotify_features.get("liveness", 0),

        # Raw values
        "bpm": tempo,
        "key": key_name,
        "scale": scale,
        "loudness_db": loudness_db,
    }


def spotify_features_to_song_dict(
    track: dict,
    audio_features: Optional[dict] = None,
    cluster_id: Optional[int] = None
) -> dict:
    """
    Convert Spotify track and audio features to our Song model format.

    Args:
        track: Spotify track data
        audio_features: Spotify audio features (optional)
        cluster_id: Assigned cluster ID (optional)

    Returns:
        Dictionary compatible with Song model
    """
    # Start with track info
    song_dict = {
        "spotify_id": track.get("spotify_id"),
        "title": track.get("title", ""),
        "artist": track.get("artist", ""),
        "album": track.get("album", ""),
        "image_url": track.get("image_url"),
        "thumbnail_url": track.get("thumbnail_url"),
        "preview_url": track.get("preview_url"),
        "external_url": track.get("external_url"),
        "duration_ms": track.get("duration_ms", 0),
        "popularity": track.get("popularity", 0),
        "cluster_id": cluster_id,
    }

    # Add normalized audio features if available
    if audio_features:
        normalized = normalize_spotify_features(audio_features)
        song_dict.update({
            "bpm": normalized["bpm"],
            "key": normalized["key"],
            "scale": normalized["scale"],
            "energy": normalized["energy"],
            "danceability": normalized["danceability"],
            "acousticness": normalized["acousticness"],
            "valence": normalized["valence"],
            "instrumentalness": normalized["instrumentalness"],
            "loudness": normalized["loudness"],
            "speechiness": normalized["speechiness"],
            "liveness": normalized["liveness"],
        })
    else:
        # Default values if no features
        song_dict.update({
            "bpm": 0,
            "key": "",
            "scale": "",
            "energy": 0,
            "danceability": 0,
            "acousticness": 0,
            "valence": 0,
            "instrumentalness": 0,
            "loudness": 0,
            "speechiness": 0,
            "liveness": 0,
        })

    return song_dict


def get_feature_vector(normalized_features: dict) -> list[float]:
    """
    Get feature vector for clustering from normalized features.

    Args:
        normalized_features: Dict from normalize_spotify_features()

    Returns:
        List of feature values in standard order for clustering
    """
    return [
        normalized_features.get("bpm_normalized", 0.5),
        normalized_features.get("energy", 0.5),
        normalized_features.get("danceability", 0.5),
        normalized_features.get("acousticness", 0.5),
        normalized_features.get("valence", 0.5),
        normalized_features.get("instrumentalness", 0.5),
        normalized_features.get("loudness", 0.5),
    ]
