"""API routes for Music Match."""
import json
from fastapi import APIRouter, HTTPException
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
)
from ..quiz import get_questions, calculate_user_vector, get_radar_chart_data
from ..recommendations import get_recommendations, get_cluster_recommendations
from ..clustering import reduce_for_visualization, reduce_centroids_for_visualization, FEATURE_COLUMNS
import pandas as pd


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
