#!/usr/bin/env python3
"""Seed database with synthetic sample data for development."""
import asyncio
import random
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import (
    init_db,
    Song,
    Cluster,
    save_song_features,
    save_cluster,
    clear_clusters,
    update_song_cluster,
    get_all_songs,
)
from app.clustering import (
    train_clusters,
    get_cluster_centroids,
    generate_cluster_description,
    FEATURE_COLUMNS,
)
import pandas as pd
import numpy as np


# Sample artist and title data for realistic song names
ARTISTS = [
    "The Midnight Echo", "Luna Vega", "Neon Dreams", "Arctic Pulse",
    "Solar Flare", "Velvet Thunder", "Crystal Waters", "Iron Butterfly",
    "Silver Moon", "Electric Storm", "Golden Hour", "Midnight Sun",
    "Ocean Drive", "Desert Rose", "Mountain High", "River Flow",
    "City Lights", "Forest Rain", "Summer Haze", "Winter Chill",
    "Dawn Patrol", "Dusk Riders", "Aurora", "Zenith",
    "Horizon", "Eclipse", "Nova", "Stellar",
    "Cosmos", "Galaxy", "Nebula", "Pulsar"
]

TITLE_PARTS = [
    ["Dancing", "Running", "Flying", "Falling", "Rising", "Fading", "Glowing", "Burning"],
    ["Through", "Into", "Beyond", "Under", "Over", "Within", "Among", "Between"],
    ["Stars", "Dreams", "Waves", "Lights", "Shadows", "Flames", "Clouds", "Rain"],
]

TITLE_SINGLE = [
    "Euphoria", "Melancholy", "Serenity", "Chaos", "Bliss", "Tempest",
    "Whispers", "Thunder", "Silence", "Echo", "Reflection", "Mirage",
    "Solitude", "Paradise", "Illusion", "Reverie", "Momentum", "Gravity",
    "Infinity", "Eternity", "Daybreak", "Twilight", "Midnight", "Dawn"
]


def generate_song_title() -> str:
    """Generate a random song title."""
    if random.random() < 0.4:
        return random.choice(TITLE_SINGLE)
    else:
        return " ".join(random.choice(part) for part in TITLE_PARTS)


def generate_synthetic_features() -> dict:
    """Generate realistic random audio features."""
    # Generate base profile (to create natural correlations)
    profile = random.choice(["energetic", "chill", "acoustic", "electronic", "balanced"])

    if profile == "energetic":
        energy = random.uniform(0.6, 1.0)
        danceability = random.uniform(0.5, 1.0)
        valence = random.uniform(0.4, 1.0)
        acousticness = random.uniform(0.0, 0.3)
        instrumentalness = random.uniform(0.0, 0.5)
        loudness = random.uniform(0.5, 0.9)
        bpm = random.uniform(110, 180)
    elif profile == "chill":
        energy = random.uniform(0.1, 0.4)
        danceability = random.uniform(0.2, 0.6)
        valence = random.uniform(0.3, 0.7)
        acousticness = random.uniform(0.3, 0.8)
        instrumentalness = random.uniform(0.2, 0.7)
        loudness = random.uniform(0.2, 0.5)
        bpm = random.uniform(60, 100)
    elif profile == "acoustic":
        energy = random.uniform(0.2, 0.6)
        danceability = random.uniform(0.2, 0.5)
        valence = random.uniform(0.2, 0.8)
        acousticness = random.uniform(0.7, 1.0)
        instrumentalness = random.uniform(0.1, 0.6)
        loudness = random.uniform(0.2, 0.5)
        bpm = random.uniform(70, 130)
    elif profile == "electronic":
        energy = random.uniform(0.5, 0.9)
        danceability = random.uniform(0.6, 1.0)
        valence = random.uniform(0.3, 0.8)
        acousticness = random.uniform(0.0, 0.2)
        instrumentalness = random.uniform(0.4, 0.9)
        loudness = random.uniform(0.5, 0.8)
        bpm = random.uniform(100, 150)
    else:  # balanced
        energy = random.uniform(0.3, 0.7)
        danceability = random.uniform(0.3, 0.7)
        valence = random.uniform(0.3, 0.7)
        acousticness = random.uniform(0.2, 0.6)
        instrumentalness = random.uniform(0.2, 0.6)
        loudness = random.uniform(0.3, 0.6)
        bpm = random.uniform(80, 140)

    # Add some noise for variety
    def add_noise(val, noise=0.1):
        return max(0.0, min(1.0, val + random.uniform(-noise, noise)))

    return {
        "bpm": round(bpm, 1),
        "key": random.choice(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]),
        "scale": random.choice(["major", "minor"]),
        "energy": round(add_noise(energy), 3),
        "danceability": round(add_noise(danceability), 3),
        "acousticness": round(add_noise(acousticness), 3),
        "valence": round(add_noise(valence), 3),
        "instrumentalness": round(add_noise(instrumentalness), 3),
        "loudness": round(add_noise(loudness), 3),
    }


async def seed_songs(n_songs: int = 50):
    """Generate and save synthetic songs."""
    print(f"Generating {n_songs} synthetic songs...")

    for i in range(n_songs):
        features = generate_synthetic_features()

        song = Song(
            title=generate_song_title(),
            artist=random.choice(ARTISTS),
            file_path=f"synthetic/song_{i+1}.mp3",
            **features
        )

        await save_song_features(song)

        if (i + 1) % 10 == 0:
            print(f"  Created {i + 1} songs...")

    print(f"Created {n_songs} songs successfully!")


async def run_clustering(n_clusters: int = 8):
    """Run clustering on all songs and save cluster data."""
    print(f"\nRunning k-means clustering with {n_clusters} clusters...")

    # Clear existing clusters
    await clear_clusters()

    # Get all songs
    songs = await get_all_songs()

    if not songs:
        print("No songs found in database!")
        return

    # Build features DataFrame
    features_data = []
    for song in songs:
        features_data.append({
            "id": song.id,
            "bpm_normalized": song.bpm / 200.0,
            "energy": song.energy,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "valence": song.valence,
            "instrumentalness": song.instrumentalness,
            "loudness": song.loudness,
        })

    df = pd.DataFrame(features_data)

    # Train clustering model
    model, silhouette = train_clusters(df, n_clusters)
    print(f"Clustering complete! Silhouette score: {silhouette:.3f}")

    # Get centroids
    centroids = get_cluster_centroids(model)

    # Save clusters
    cluster_id_map = {}  # Map from model cluster index to database ID

    for centroid in centroids:
        cluster_idx = centroid.pop("cluster_id")
        description = generate_cluster_description(centroid)

        cluster = Cluster(
            centroid_json=json.dumps(centroid),
            description=description,
            song_count=0  # Will update after assigning songs
        )

        db_cluster_id = await save_cluster(cluster)
        cluster_id_map[cluster_idx] = db_cluster_id
        print(f"  Cluster {db_cluster_id}: {description}")

    # Assign songs to clusters
    labels = model.labels_
    cluster_counts = {}

    for i, song in enumerate(songs):
        cluster_idx = labels[i]
        db_cluster_id = cluster_id_map[cluster_idx]

        await update_song_cluster(song.id, db_cluster_id)
        cluster_counts[db_cluster_id] = cluster_counts.get(db_cluster_id, 0) + 1

    # Update cluster song counts
    for db_cluster_id, count in cluster_counts.items():
        cluster = Cluster(id=db_cluster_id, song_count=count)
        # Re-fetch to get centroid data
        from app.db import get_cluster_by_id
        existing = await get_cluster_by_id(db_cluster_id)
        if existing:
            existing.song_count = count
            await save_cluster(existing)

    print(f"\nAssigned songs to clusters:")
    for cluster_id, count in sorted(cluster_counts.items()):
        print(f"  Cluster {cluster_id}: {count} songs")


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Seed database with sample data")
    parser.add_argument("--songs", type=int, default=50, help="Number of songs to generate")
    parser.add_argument("--clusters", type=int, default=8, help="Number of clusters")
    parser.add_argument("--skip-songs", action="store_true", help="Skip song generation (only run clustering)")

    args = parser.parse_args()

    print("Initializing database...")
    await init_db()

    if not args.skip_songs:
        await seed_songs(args.songs)

    await run_clustering(args.clusters)

    print("\nSeeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
