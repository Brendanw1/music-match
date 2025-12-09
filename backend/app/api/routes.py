"""API routes for Music Match."""
import json
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from ..db import (
    Song,
    UserProfile,
    get_all_clusters,
    get_cluster_by_id,
    get_songs_by_cluster,
    get_song_by_id,
    get_all_songs,
    save_user_profile,
    get_song_by_spotify_id,
    save_song,
    get_cached_features,
    cache_features,
)
from ..quiz import get_questions, calculate_user_vector, get_radar_chart_data
from ..recommendations import get_recommendations, get_cluster_recommendations
from ..clustering import reduce_for_visualization, reduce_centroids_for_visualization, FEATURE_COLUMNS
from ..services import SpotifyService
from ..feature_extraction import normalize_spotify_features, spotify_features_to_song_dict
import pandas as pd


# Initialize Spotify service (lazy loading)
_spotify_service: Optional[SpotifyService] = None


def get_spotify_service() -> SpotifyService:
    """Get or create SpotifyService instance."""
    global _spotify_service
    if _spotify_service is None:
        _spotify_service = SpotifyService()
    return _spotify_service


router = APIRouter()


# Pydantic models for request/response
class QuizAnswer(BaseModel):
    question_id: str
    option_id: str


class QuizSubmission(BaseModel):
    answers: list[QuizAnswer]


class QuizResultResponse(BaseModel):
    user_profile: dict
    matched_cluster: dict
    adjacent_clusters: list[dict]
    songs: list[dict]


# Quiz routes
@router.get("/quiz/questions")
async def get_quiz_questions():
    """Get all quiz questions."""
    return {"questions": get_questions()}


@router.post("/quiz/submit")
async def submit_quiz(submission: QuizSubmission):
    """
    Submit quiz answers and get recommendations.

    Returns user profile, matched cluster, and song recommendations.
    """
    # Convert to list of dicts
    answers = [
        {"question_id": a.question_id, "option_id": a.option_id}
        for a in submission.answers
    ]

    # Calculate user feature vector
    user_vector = calculate_user_vector(answers)

    # Get radar chart data
    radar_data = get_radar_chart_data(user_vector)

    # Save user profile
    profile = UserProfile()
    profile.feature_vector = user_vector

    # Get recommendations
    recommendations = await get_recommendations(user_vector)

    # Update profile with matched cluster
    if recommendations.get("matched_cluster"):
        profile.matched_cluster_id = recommendations["matched_cluster"].get("id")

    # Save to database
    profile_id = await save_user_profile(profile)

    return {
        "user_profile": {
            "id": profile_id,
            "feature_vector": user_vector,
            "radar_chart_data": radar_data
        },
        "matched_cluster": recommendations.get("matched_cluster"),
        "adjacent_clusters": recommendations.get("adjacent_clusters", []),
        "songs": recommendations.get("songs", [])
    }


# Cluster routes
@router.get("/clusters")
async def get_clusters():
    """Get all clusters with sample songs."""
    clusters = await get_all_clusters()

    result = []
    for cluster in clusters:
        sample_songs = await get_songs_by_cluster(cluster.id, limit=5)
        result.append({
            **cluster.to_dict(),
            "sample_songs": [s.to_dict() for s in sample_songs]
        })

    return {"clusters": result}


@router.get("/clusters/visualization")
async def get_clusters_visualization():
    """
    Get 2D coordinates for cluster visualization scatter plot.

    Returns all songs with x, y coordinates and cluster assignments,
    plus centroid positions.
    """
    songs = await get_all_songs()
    clusters = await get_all_clusters()

    if not songs:
        return {"songs": [], "centroids": []}

    # Build features DataFrame
    features_data = []
    for song in songs:
        features_data.append({
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "cluster_id": song.cluster_id,
            "bpm_normalized": song.bpm / 200.0,
            "energy": song.energy,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "valence": song.valence,
            "instrumentalness": song.instrumentalness,
            "loudness": song.loudness,
        })

    df = pd.DataFrame(features_data)

    # Reduce to 2D
    coords = reduce_for_visualization(df)
    df["x"] = coords["x"]
    df["y"] = coords["y"]

    # Build centroids list
    centroids = []
    for cluster in clusters:
        centroid = cluster.centroid
        centroid["cluster_id"] = cluster.id
        centroids.append(centroid)

    # Get centroid coordinates in same PCA space
    if centroids:
        centroid_coords = reduce_centroids_for_visualization(centroids, df)
    else:
        centroid_coords = []

    return {
        "songs": [
            {
                "id": row["id"],
                "title": row["title"],
                "artist": row["artist"],
                "x": float(row["x"]),
                "y": float(row["y"]),
                "cluster_id": row["cluster_id"]
            }
            for _, row in df.iterrows()
        ],
        "centroids": centroid_coords
    }


@router.get("/clusters/{cluster_id}")
async def get_cluster(cluster_id: int):
    """Get a specific cluster with all its songs."""
    cluster = await get_cluster_by_id(cluster_id)

    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    songs = await get_songs_by_cluster(cluster_id)

    return {
        **cluster.to_dict(),
        "songs": [s.to_dict() for s in songs]
    }


# Recommendation routes
@router.get("/recommendations/{cluster_id}")
async def get_recommendations_by_cluster(
    cluster_id: int,
    limit: int = 20,
    user_vector: Optional[str] = None
):
    """
    Get song recommendations from a specific cluster.

    Optionally pass user_vector as JSON string for personalized ranking.
    """
    # Parse user vector if provided
    parsed_vector = None
    if user_vector:
        try:
            parsed_vector = json.loads(user_vector)
        except json.JSONDecodeError:
            pass

    songs = await get_cluster_recommendations(cluster_id, parsed_vector, limit)

    return {"songs": songs}


# Song routes
@router.get("/songs/{song_id}")
async def get_song(song_id: int):
    """Get a specific song by ID."""
    song = await get_song_by_id(song_id)

    if not song:
        raise HTTPException(status_code=404, detail="Song not found")

    return song.to_dict()


# Spotify routes
@router.get("/spotify/search")
async def search_spotify_tracks(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=50, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Search for tracks on Spotify.

    Returns track metadata including album art and preview URLs.
    """
    try:
        spotify = get_spotify_service()
        tracks = spotify.search_tracks(q, limit=limit, offset=offset)
        return {"tracks": tracks, "query": q, "limit": limit, "offset": offset}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spotify search failed: {str(e)}")


@router.get("/spotify/track/{track_id}")
async def get_spotify_track(track_id: str):
    """
    Get a Spotify track by ID.

    Returns track metadata without audio features.
    """
    try:
        spotify = get_spotify_service()
        track = spotify.get_track(track_id)

        if not track:
            raise HTTPException(status_code=404, detail="Track not found")

        return track
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get track: {str(e)}")


@router.get("/spotify/track/{track_id}/features")
async def get_spotify_track_features(track_id: str):
    """
    Get audio features for a Spotify track.

    Returns normalized features suitable for clustering,
    with caching to reduce API calls.
    """
    try:
        # Check cache first
        cached = await get_cached_features(track_id)
        if cached:
            return {
                "track_id": track_id,
                "features": cached,
                "normalized": normalize_spotify_features(cached),
                "cached": True
            }

        # Fetch from Spotify
        spotify = get_spotify_service()
        features = spotify.get_audio_features(track_id)

        if not features:
            raise HTTPException(status_code=404, detail="Audio features not found")

        # Cache the features
        await cache_features(track_id, features)

        return {
            "track_id": track_id,
            "features": features,
            "normalized": normalize_spotify_features(features),
            "cached": False
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get features: {str(e)}")


@router.get("/spotify/track/{track_id}/full")
async def get_spotify_track_with_features(track_id: str):
    """
    Get a Spotify track with its audio features.

    Returns complete track data ready for display and clustering.
    """
    try:
        # Check if we already have this song in our database
        existing_song = await get_song_by_spotify_id(track_id)
        if existing_song:
            return {
                "track": existing_song.to_dict(),
                "source": "database"
            }

        # Fetch from Spotify
        spotify = get_spotify_service()
        track_data = spotify.get_track_with_features(track_id)

        if not track_data:
            raise HTTPException(status_code=404, detail="Track not found")

        # Cache features if available
        if track_data.get("audio_features"):
            await cache_features(track_id, track_data["audio_features"])

        # Convert to song dict format
        song_data = spotify_features_to_song_dict(
            track_data,
            track_data.get("audio_features"),
            cluster_id=None
        )

        return {
            "track": song_data,
            "source": "spotify"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get track: {str(e)}")


@router.get("/spotify/recommendations")
async def get_spotify_recommendations(
    seed_tracks: str = Query(..., description="Comma-separated track IDs (max 5)"),
    limit: int = Query(20, ge=1, le=100, description="Number of recommendations"),
    target_energy: Optional[float] = Query(None, ge=0, le=1),
    target_danceability: Optional[float] = Query(None, ge=0, le=1),
    target_valence: Optional[float] = Query(None, ge=0, le=1),
    target_acousticness: Optional[float] = Query(None, ge=0, le=1),
    target_instrumentalness: Optional[float] = Query(None, ge=0, le=1),
):
    """
    Get Spotify recommendations based on seed tracks.

    Optionally filter by target audio features for more
    personalized recommendations.
    """
    try:
        # Parse seed tracks
        track_ids = [t.strip() for t in seed_tracks.split(",") if t.strip()]

        if not track_ids:
            raise HTTPException(status_code=400, detail="At least one seed track is required")

        if len(track_ids) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 seed tracks allowed")

        spotify = get_spotify_service()
        tracks = spotify.get_recommendations(
            seed_tracks=track_ids,
            limit=limit,
            target_energy=target_energy,
            target_danceability=target_danceability,
            target_valence=target_valence,
            target_acousticness=target_acousticness,
            target_instrumentalness=target_instrumentalness,
        )

        return {
            "recommendations": tracks,
            "seed_tracks": track_ids,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/spotify/import/{track_id}")
async def import_spotify_track(track_id: str, cluster_id: Optional[int] = None):
    """
    Import a Spotify track into the local database.

    Fetches track metadata and audio features, then saves
    to the songs table for use in clustering and recommendations.
    """
    try:
        # Check if already imported
        existing = await get_song_by_spotify_id(track_id)
        if existing:
            return {
                "song": existing.to_dict(),
                "imported": False,
                "message": "Track already exists in database"
            }

        # Fetch from Spotify
        spotify = get_spotify_service()
        track_data = spotify.get_track_with_features(track_id)

        if not track_data:
            raise HTTPException(status_code=404, detail="Track not found on Spotify")

        # Convert to song dict
        song_dict = spotify_features_to_song_dict(
            track_data,
            track_data.get("audio_features"),
            cluster_id=cluster_id
        )

        # Create Song object
        song = Song(
            spotify_id=song_dict.get("spotify_id"),
            title=song_dict.get("title", "Unknown"),
            artist=song_dict.get("artist", "Unknown"),
            album=song_dict.get("album", ""),
            image_url=song_dict.get("image_url"),
            thumbnail_url=song_dict.get("thumbnail_url"),
            preview_url=song_dict.get("preview_url"),
            external_url=song_dict.get("external_url"),
            duration_ms=song_dict.get("duration_ms", 0),
            popularity=song_dict.get("popularity", 0),
            bpm=song_dict.get("bpm", 120.0),
            energy=song_dict.get("energy", 0.5),
            danceability=song_dict.get("danceability", 0.5),
            acousticness=song_dict.get("acousticness", 0.5),
            valence=song_dict.get("valence", 0.5),
            instrumentalness=song_dict.get("instrumentalness", 0.5),
            loudness=song_dict.get("loudness", 0.5),
            speechiness=song_dict.get("speechiness", 0.0),
            liveness=song_dict.get("liveness", 0.0),
            key=song_dict.get("key", "C"),
            scale=song_dict.get("scale", "major"),
            cluster_id=cluster_id,
        )

        # Save to database
        song_id = await save_song(song)
        song.id = song_id

        # Cache the audio features
        if track_data.get("audio_features"):
            await cache_features(track_id, track_data["audio_features"])

        return {
            "song": song.to_dict(),
            "imported": True,
            "message": "Track successfully imported"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import track: {str(e)}")
