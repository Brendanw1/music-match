#!/usr/bin/env python3
"""CLI commands for Music Match backend."""
import asyncio
import argparse
import sys
from pathlib import Path


def init_db_command(args):
    """Initialize the database."""
    from app.db import init_db

    async def run():
        print("Initializing database...")
        await init_db()
        print("Database initialized successfully!")

    asyncio.run(run())


def extract_command(args):
    """Extract features from audio files."""
    from app.feature_extraction import batch_extract_features

    async def run():
        audio_dir = Path(args.audio_dir)
        if not audio_dir.exists():
            print(f"Error: Directory not found: {audio_dir}")
            sys.exit(1)

        print(f"Extracting features from: {audio_dir}")
        await batch_extract_features(audio_dir)
        print("Feature extraction complete!")

    asyncio.run(run())


def cluster_command(args):
    """Run clustering on songs in database."""
    from app.db import init_db, get_all_songs, save_cluster, clear_clusters, update_song_cluster, get_cluster_by_id
    from app.clustering import train_clusters, get_cluster_centroids, generate_cluster_description, find_optimal_k
    import pandas as pd
    import json

    async def run():
        await init_db()

        songs = await get_all_songs()
        if not songs:
            print("No songs in database. Run feature extraction first.")
            sys.exit(1)

        print(f"Found {len(songs)} songs")

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

        n_clusters = args.n_clusters
        if args.auto:
            print("Finding optimal number of clusters...")
            n_clusters = find_optimal_k(df)
            print(f"Optimal k: {n_clusters}")

        print(f"Training {n_clusters} clusters...")

        # Clear existing clusters
        await clear_clusters()

        # Train model
        model, silhouette = train_clusters(df, n_clusters)
        print(f"Silhouette score: {silhouette:.3f}")

        # Save clusters
        centroids = get_cluster_centroids(model)
        cluster_id_map = {}

        for centroid in centroids:
            cluster_idx = centroid.pop("cluster_id")
            description = generate_cluster_description(centroid)

            from app.db import Cluster
            cluster = Cluster(
                centroid_json=json.dumps(centroid),
                description=description,
                song_count=0
            )

            db_cluster_id = await save_cluster(cluster)
            cluster_id_map[cluster_idx] = db_cluster_id
            print(f"  Cluster {db_cluster_id}: {description}")

        # Assign songs
        labels = model.labels_
        cluster_counts = {}

        for i, song in enumerate(songs):
            cluster_idx = labels[i]
            db_cluster_id = cluster_id_map[cluster_idx]
            await update_song_cluster(song.id, db_cluster_id)
            cluster_counts[db_cluster_id] = cluster_counts.get(db_cluster_id, 0) + 1

        # Update counts
        for db_cluster_id, count in cluster_counts.items():
            existing = await get_cluster_by_id(db_cluster_id)
            if existing:
                existing.song_count = count
                await save_cluster(existing)

        print("\nClustering complete!")

    asyncio.run(run())


def seed_command(args):
    """Seed database with sample data."""
    import subprocess
    script_path = Path(__file__).parent / "scripts" / "seed_sample_data.py"

    cmd = [sys.executable, str(script_path)]
    if args.songs:
        cmd.extend(["--songs", str(args.songs)])
    if args.clusters:
        cmd.extend(["--clusters", str(args.clusters)])

    subprocess.run(cmd)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Music Match CLI",
        prog="python -m cli"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init-db command
    init_parser = subparsers.add_parser("init-db", help="Initialize database")
    init_parser.set_defaults(func=init_db_command)

    # extract command
    extract_parser = subparsers.add_parser("extract", help="Extract features from audio files")
    extract_parser.add_argument("audio_dir", help="Directory containing audio files")
    extract_parser.set_defaults(func=extract_command)

    # cluster command
    cluster_parser = subparsers.add_parser("cluster", help="Run clustering on songs")
    cluster_parser.add_argument("-n", "--n-clusters", type=int, default=8, help="Number of clusters")
    cluster_parser.add_argument("--auto", action="store_true", help="Auto-detect optimal clusters")
    cluster_parser.set_defaults(func=cluster_command)

    # seed command
    seed_parser = subparsers.add_parser("seed", help="Seed database with sample data")
    seed_parser.add_argument("--songs", type=int, default=50, help="Number of songs")
    seed_parser.add_argument("--clusters", type=int, default=8, help="Number of clusters")
    seed_parser.set_defaults(func=seed_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
