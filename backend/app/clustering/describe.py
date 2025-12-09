"""Generate human-readable descriptions for clusters."""


def generate_cluster_description(centroid: dict) -> str:
    """
    Generate a human-readable description for a cluster based on its centroid.

    Uses thresholds:
    - High: > 0.7
    - Medium: 0.3 - 0.7
    - Low: < 0.3

    Args:
        centroid: Dictionary of feature values

    Returns:
        Human-readable description of the cluster
    """
    energy = centroid.get("energy", 0.5)
    danceability = centroid.get("danceability", 0.5)
    acousticness = centroid.get("acousticness", 0.5)
    valence = centroid.get("valence", 0.5)
    instrumentalness = centroid.get("instrumentalness", 0.5)
    loudness = centroid.get("loudness", 0.5)
    bpm = centroid.get("bpm_normalized", 0.5)

    # Define characteristic patterns
    patterns = []

    # High energy + high danceability + high valence = Party
    if energy > 0.7 and danceability > 0.7 and valence > 0.6:
        return "Upbeat party anthems - energetic, danceable, and feel-good tracks"

    # High energy + high danceability + low valence = Intense dance
    if energy > 0.7 and danceability > 0.6 and valence < 0.4:
        return "Intense electronic - driving beats with darker undertones"

    # Low energy + high acousticness + low valence = Melancholic acoustic
    if energy < 0.4 and acousticness > 0.6 and valence < 0.4:
        return "Melancholic acoustic - introspective, stripped-back emotional pieces"

    # Low energy + high acousticness + high valence = Warm acoustic
    if energy < 0.5 and acousticness > 0.6 and valence > 0.5:
        return "Warm acoustic - cozy, feel-good unplugged vibes"

    # High instrumentalness + low energy = Ambient
    if instrumentalness > 0.7 and energy < 0.4:
        return "Ambient soundscapes - atmospheric instrumental journeys"

    # High instrumentalness + high energy = Electronic/instrumental
    if instrumentalness > 0.6 and energy > 0.6:
        return "Instrumental energy - dynamic tracks without vocals"

    # High energy + low danceability + high loudness = Rock/Metal
    if energy > 0.7 and danceability < 0.5 and loudness > 0.6:
        return "High-octane rock - powerful, intense guitar-driven sound"

    # Medium everything with high danceability = Groovy
    if 0.4 < energy < 0.7 and danceability > 0.6:
        return "Groovy mid-tempo - smooth rhythms perfect for casual listening"

    # High valence + medium energy = Feel-good
    if valence > 0.7 and 0.4 < energy < 0.7:
        return "Feel-good favorites - positive vibes without being overwhelming"

    # Low valence + medium energy = Moody
    if valence < 0.3 and 0.4 < energy < 0.7:
        return "Moody and atmospheric - contemplative tracks with depth"

    # Fast tempo + high energy
    if bpm > 0.7 and energy > 0.6:
        return "Fast and furious - high-tempo adrenaline rushers"

    # Slow tempo + low energy
    if bpm < 0.4 and energy < 0.4:
        return "Slow and steady - relaxed tracks for winding down"

    # Build description from individual features
    descriptors = []

    if energy > 0.7:
        descriptors.append("high-energy")
    elif energy < 0.3:
        descriptors.append("chill")

    if danceability > 0.7:
        descriptors.append("danceable")

    if acousticness > 0.7:
        descriptors.append("acoustic")
    elif acousticness < 0.3:
        descriptors.append("electronic")

    if valence > 0.7:
        descriptors.append("uplifting")
    elif valence < 0.3:
        descriptors.append("melancholic")

    if instrumentalness > 0.7:
        descriptors.append("instrumental")

    if descriptors:
        return f"{' '.join(descriptors).capitalize()} tracks"

    return "Balanced mix - versatile tracks spanning multiple styles"


def get_cluster_mood_emoji(centroid: dict) -> str:
    """
    Get an emoji representing the cluster mood.

    Args:
        centroid: Dictionary of feature values

    Returns:
        Emoji string
    """
    energy = centroid.get("energy", 0.5)
    valence = centroid.get("valence", 0.5)
    acousticness = centroid.get("acousticness", 0.5)
    instrumentalness = centroid.get("instrumentalness", 0.5)

    if energy > 0.7 and valence > 0.6:
        return "🔥"
    if energy > 0.7 and valence < 0.4:
        return "⚡"
    if acousticness > 0.7:
        return "🎸"
    if instrumentalness > 0.7 and energy < 0.4:
        return "🌙"
    if valence > 0.7:
        return "☀️"
    if valence < 0.3:
        return "🌧️"
    if energy < 0.3:
        return "😌"

    return "🎵"
