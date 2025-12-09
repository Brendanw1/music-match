"""Recommendation engine for matching users to songs."""
import numpy as np
from typing import Optional

from ..db import (
    Song,
    Cluster,
    get_all_clusters,
    get_songs_by_cluster,
    get_cluster_by_id,
)
from ..quiz.scoring import FEATURE_KEYS, vector_to_array


def find_nearest_cluster(
    user_vector: dict[str, float],
    centroids: list[dict]
) -> tuple[int, float]:
    """
    Find the cluster nearest to user's feature vector.

    Args:
        user_vector: User's feature vector from quiz
        centroids: List of cluster centroid dictionaries

    Returns:
        Tuple of (cluster_id, distance)
    """
    user_arr = vector_to_array(user_vector)

    best_cluster_id = 0
    best_distance = float('inf')

    for centroid in centroids:
        cluster_id = centroid.get("cluster_id", 0)
        centroid_arr = np.array([
            centroid.get(key, 0.5) for key in FEATURE_KEYS
        ])

        distance = np.linalg.norm(user_arr - centroid_arr)

        if distance < best_distance:
            best_distance = distance
            best_cluster_id = cluster_id

    return best_cluster_id, float(best_distance)


def get_adjacent_clusters(
    user_vector: dict[str, float],
    centroids: list[dict],
    n: int = 3
) -> list[int]:
    """
    Get n clusters closest to user's feature vector.

    Args:
        user_vector: User's feature vector from quiz
        centroids: List of cluster centroid dictionaries
        n: Number of clusters to return

    Returns:
        List of cluster IDs sorted by distance
    """
    user_arr = vector_to_array(user_vector)

    distances = []
    for centroid in centroids:
        cluster_id = centroid.get("cluster_id", 0)
        centroid_arr = np.array([
            centroid.get(key, 0.5) for key in FEATURE_KEYS
        ])
        distance = np.linalg.norm(user_arr - centroid_arr)
        distances.append((cluster_id, distance))

    # Sort by distance and return top n cluster IDs
    distances.sort(key=lambda x: x[1])
    return [d[0] for d in distances[:n]]


def rank_songs_in_cluster(
    user_vector: dict[str, float],
    songs: list[Song],
    limit: int = 20
) -> list[dict]:
    """
    Rank songs within a cluster by similarity to user vector.

    Args:
        user_vector: User's feature vector from quiz
        songs: List of songs in the cluster
        limit: Maximum number of songs to return

    Returns:
        List of song dictionaries with similarity scores
    """
    user_arr = vector_to_array(user_vector)

    scored_songs = []
    for song in songs:
        song_arr = np.array([
            song.bpm / 200.0,  # bpm_normalized
            song.energy,
            song.danceability,
            song.acousticness,
            song.valence,
            song.instrumentalness,
            song.loudness,
        ])

        # Calculate cosine similarity
        dot_product = np.dot(user_arr, song_arr)
        norm_product = np.linalg.norm(user_arr) * np.linalg.norm(song_arr)

        if norm_product > 0:
            similarity = dot_product / norm_product
        else:
            similarity = 0

        scored_songs.append({
            **song.to_dict(),
            "similarity_score": round(float(similarity), 3)
        })

    # Sort by similarity (highest first) and limit
    scored_songs.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_songs[:limit]


async def get_recommendations(
    user_vector: dict[str, float],
    limit: int = 20
) -> dict:
    """
    Get song recommendations for a user based on their feature vector.

    Args:
        user_vector: User's feature vector from quiz
        limit: Maximum songs per cluster

    Returns:
        Dictionary with matched cluster, songs, and adjacent clusters
    """
    # Get all clusters
    clusters = await get_all_clusters()

    if not clusters:
        return {
            "matched_cluster": None,
            "songs": [],
            "adjacent_clusters": []
        }

    # Build centroids list
    centroids = []
    for cluster in clusters:
        centroid = cluster.centroid
        centroid["cluster_id"] = cluster.id
        centroids.append(centroid)

    # Find nearest cluster
    matched_cluster_id, distance = find_nearest_cluster(user_vector, centroids)

    # Get matched cluster details
    matched_cluster = await get_cluster_by_id(matched_cluster_id)

    # Get songs from matched cluster
    songs = await get_songs_by_cluster(matched_cluster_id)
    ranked_songs = rank_songs_in_cluster(user_vector, songs, limit)

    # Get adjacent clusters
    adjacent_ids = get_adjacent_clusters(user_vector, centroids, n=3)
    # Remove matched cluster from adjacent list if present
    adjacent_ids = [cid for cid in adjacent_ids if cid != matched_cluster_id][:2]

    adjacent_clusters = []
    for cluster_id in adjacent_ids:
        cluster = await get_cluster_by_id(cluster_id)
        if cluster:
            # Get sample songs for preview
            sample_songs = await get_songs_by_cluster(cluster_id, limit=3)
            adjacent_clusters.append({
                **cluster.to_dict(),
                "sample_songs": [s.to_dict() for s in sample_songs]
            })

    # Get sample songs for matched cluster
    matched_sample = await get_songs_by_cluster(matched_cluster_id, limit=5)

    matched_cluster_data = matched_cluster.to_dict() if matched_cluster else {}
    matched_cluster_data["distance"] = round(distance, 3)
    matched_cluster_data["sample_songs"] = [s.to_dict() for s in matched_sample]

    return {
        "matched_cluster": matched_cluster_data,
        "songs": ranked_songs,
        "adjacent_clusters": adjacent_clusters
    }


async def get_cluster_recommendations(
    cluster_id: int,
    user_vector: Optional[dict[str, float]] = None,
    limit: int = 20
) -> list[dict]:
    """
    Get recommendations from a specific cluster.

    Args:
        cluster_id: Cluster ID to get songs from
        user_vector: Optional user vector for ranking
        limit: Maximum songs to return

    Returns:
        List of song dictionaries
    """
    songs = await get_songs_by_cluster(cluster_id)

    if user_vector:
        return rank_songs_in_cluster(user_vector, songs, limit)

    # Without user vector, return songs sorted by title
    return [song.to_dict() for song in songs[:limit]]
