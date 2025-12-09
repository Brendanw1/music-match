"""Database operations using aiosqlite."""
import aiosqlite
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from .models import Song, Cluster, UserProfile, SpotifyCache


DATABASE_PATH = Path(__file__).parent.parent.parent / "data" / "music_match.db"


def _get_db_path() -> Path:
    """Get database path and ensure directory exists."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return DATABASE_PATH


async def init_db():
    """Initialize database tables."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row

        # Create songs table with Spotify fields
        await db.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spotify_id TEXT UNIQUE,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                album TEXT DEFAULT '',
                file_path TEXT,
                image_url TEXT,
                thumbnail_url TEXT,
                preview_url TEXT,
                external_url TEXT,
                duration_ms INTEGER DEFAULT 0,
                popularity INTEGER DEFAULT 0,
                bpm REAL DEFAULT 0,
                key TEXT DEFAULT '',
                scale TEXT DEFAULT '',
                energy REAL DEFAULT 0,
                danceability REAL DEFAULT 0,
                acousticness REAL DEFAULT 0,
                valence REAL DEFAULT 0,
                instrumentalness REAL DEFAULT 0,
                loudness REAL DEFAULT 0,
                speechiness REAL DEFAULT 0,
                liveness REAL DEFAULT 0,
                cluster_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cluster_id) REFERENCES clusters (id)
            )
        """)

        # Create index on spotify_id for faster lookups
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_songs_spotify_id ON songs(spotify_id)
        """)

        # Create clusters table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                centroid_json TEXT NOT NULL,
                description TEXT DEFAULT '',
                song_count INTEGER DEFAULT 0
            )
        """)

        # Create user_profiles table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_vector_json TEXT NOT NULL,
                matched_cluster_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (matched_cluster_id) REFERENCES clusters (id)
            )
        """)

        # Create spotify_cache table for caching audio features
        await db.execute("""
            CREATE TABLE IF NOT EXISTS spotify_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spotify_id TEXT UNIQUE NOT NULL,
                features_json TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_spotify_cache_id ON spotify_cache(spotify_id)
        """)

        await db.commit()


async def get_all_songs() -> list[Song]:
    """Get all songs from database."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM songs ORDER BY title")
        rows = await cursor.fetchall()
        return [_row_to_song(row) for row in rows]


async def get_songs_by_cluster(cluster_id: int, limit: Optional[int] = None) -> list[Song]:
    """Get songs belonging to a cluster."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM songs WHERE cluster_id = ? ORDER BY popularity DESC, title"
        if limit:
            query += f" LIMIT {limit}"
        cursor = await db.execute(query, (cluster_id,))
        rows = await cursor.fetchall()
        return [_row_to_song(row) for row in rows]


async def get_song_by_id(song_id: int) -> Optional[Song]:
    """Get a single song by ID."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        row = await cursor.fetchone()
        return _row_to_song(row) if row else None


async def get_song_by_spotify_id(spotify_id: str) -> Optional[Song]:
    """Get a song by Spotify ID."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM songs WHERE spotify_id = ?", (spotify_id,))
        row = await cursor.fetchone()
        return _row_to_song(row) if row else None


async def save_song(song: Song) -> int:
    """Save or update song with all fields including Spotify data."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row

        # Check if song with this spotify_id already exists
        if song.spotify_id:
            cursor = await db.execute(
                "SELECT id FROM songs WHERE spotify_id = ?",
                (song.spotify_id,)
            )
            existing = await cursor.fetchone()
            if existing:
                song.id = existing["id"]

        if song.id:
            await db.execute("""
                UPDATE songs SET
                    spotify_id = ?, title = ?, artist = ?, album = ?, file_path = ?,
                    image_url = ?, thumbnail_url = ?, preview_url = ?, external_url = ?,
                    duration_ms = ?, popularity = ?, bpm = ?, key = ?, scale = ?,
                    energy = ?, danceability = ?, acousticness = ?, valence = ?,
                    instrumentalness = ?, loudness = ?, speechiness = ?, liveness = ?,
                    cluster_id = ?
                WHERE id = ?
            """, (
                song.spotify_id, song.title, song.artist, song.album, song.file_path,
                song.image_url, song.thumbnail_url, song.preview_url, song.external_url,
                song.duration_ms, song.popularity, song.bpm, song.key, song.scale,
                song.energy, song.danceability, song.acousticness, song.valence,
                song.instrumentalness, song.loudness, song.speechiness, song.liveness,
                song.cluster_id, song.id
            ))
            await db.commit()
            return song.id
        else:
            cursor = await db.execute("""
                INSERT INTO songs (
                    spotify_id, title, artist, album, file_path,
                    image_url, thumbnail_url, preview_url, external_url,
                    duration_ms, popularity, bpm, key, scale,
                    energy, danceability, acousticness, valence,
                    instrumentalness, loudness, speechiness, liveness, cluster_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                song.spotify_id, song.title, song.artist, song.album, song.file_path,
                song.image_url, song.thumbnail_url, song.preview_url, song.external_url,
                song.duration_ms, song.popularity, song.bpm, song.key, song.scale,
                song.energy, song.danceability, song.acousticness, song.valence,
                song.instrumentalness, song.loudness, song.speechiness, song.liveness,
                song.cluster_id
            ))
            await db.commit()
            return cursor.lastrowid


# Keep legacy function name for backwards compatibility
save_song_features = save_song


async def get_all_clusters() -> list[Cluster]:
    """Get all clusters."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM clusters ORDER BY id")
        rows = await cursor.fetchall()
        return [_row_to_cluster(row) for row in rows]


async def get_cluster_by_id(cluster_id: int) -> Optional[Cluster]:
    """Get a single cluster by ID."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM clusters WHERE id = ?", (cluster_id,))
        row = await cursor.fetchone()
        return _row_to_cluster(row) if row else None


async def save_cluster(cluster: Cluster) -> int:
    """Save or update cluster."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        if cluster.id:
            await db.execute("""
                UPDATE clusters SET centroid_json = ?, description = ?, song_count = ?
                WHERE id = ?
            """, (cluster.centroid_json, cluster.description, cluster.song_count, cluster.id))
            await db.commit()
            return cluster.id
        else:
            cursor = await db.execute("""
                INSERT INTO clusters (centroid_json, description, song_count)
                VALUES (?, ?, ?)
            """, (cluster.centroid_json, cluster.description, cluster.song_count))
            await db.commit()
            return cursor.lastrowid


async def clear_clusters():
    """Clear all clusters and reset song cluster assignments."""
    async with aiosqlite.connect(_get_db_path()) as db:
        await db.execute("DELETE FROM clusters")
        await db.execute("UPDATE songs SET cluster_id = NULL")
        await db.commit()


async def update_song_cluster(song_id: int, cluster_id: int):
    """Update song's cluster assignment."""
    async with aiosqlite.connect(_get_db_path()) as db:
        await db.execute(
            "UPDATE songs SET cluster_id = ? WHERE id = ?",
            (cluster_id, song_id)
        )
        await db.commit()


async def save_user_profile(profile: UserProfile) -> int:
    """Save user profile."""
    async with aiosqlite.connect(_get_db_path()) as db:
        cursor = await db.execute("""
            INSERT INTO user_profiles (feature_vector_json, matched_cluster_id)
            VALUES (?, ?)
        """, (profile.feature_vector_json, profile.matched_cluster_id))
        await db.commit()
        return cursor.lastrowid


async def get_user_profile(profile_id: int) -> Optional[UserProfile]:
    """Get user profile by ID."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM user_profiles WHERE id = ?",
            (profile_id,)
        )
        row = await cursor.fetchone()
        return _row_to_user_profile(row) if row else None


# Spotify cache functions
async def get_cached_features(spotify_id: str) -> Optional[dict]:
    """Get cached audio features for a Spotify track."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT features_json FROM spotify_cache WHERE spotify_id = ?",
            (spotify_id,)
        )
        row = await cursor.fetchone()
        if row:
            return json.loads(row["features_json"])
        return None


async def get_cached_features_batch(spotify_ids: list[str]) -> dict[str, dict]:
    """Get cached audio features for multiple Spotify tracks."""
    if not spotify_ids:
        return {}

    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        placeholders = ",".join("?" * len(spotify_ids))
        cursor = await db.execute(
            f"SELECT spotify_id, features_json FROM spotify_cache WHERE spotify_id IN ({placeholders})",
            spotify_ids
        )
        rows = await cursor.fetchall()
        return {
            row["spotify_id"]: json.loads(row["features_json"])
            for row in rows
        }


async def cache_features(spotify_id: str, features: dict):
    """Cache audio features for a Spotify track."""
    async with aiosqlite.connect(_get_db_path()) as db:
        await db.execute("""
            INSERT OR REPLACE INTO spotify_cache (spotify_id, features_json, cached_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (spotify_id, json.dumps(features)))
        await db.commit()


async def cache_features_batch(features_list: list[dict]):
    """Cache audio features for multiple Spotify tracks."""
    if not features_list:
        return

    async with aiosqlite.connect(_get_db_path()) as db:
        for features in features_list:
            spotify_id = features.get("spotify_id")
            if spotify_id:
                await db.execute("""
                    INSERT OR REPLACE INTO spotify_cache (spotify_id, features_json, cached_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """, (spotify_id, json.dumps(features)))
        await db.commit()


def _row_to_song(row: aiosqlite.Row) -> Song:
    """Convert database row to Song model."""
    return Song(
        id=row["id"],
        spotify_id=row["spotify_id"] if "spotify_id" in row.keys() else None,
        title=row["title"],
        artist=row["artist"],
        album=row["album"] if "album" in row.keys() else "",
        file_path=row["file_path"] or "",
        image_url=row["image_url"] if "image_url" in row.keys() else None,
        thumbnail_url=row["thumbnail_url"] if "thumbnail_url" in row.keys() else None,
        preview_url=row["preview_url"] if "preview_url" in row.keys() else None,
        external_url=row["external_url"] if "external_url" in row.keys() else None,
        duration_ms=row["duration_ms"] if "duration_ms" in row.keys() else 0,
        popularity=row["popularity"] if "popularity" in row.keys() else 0,
        bpm=row["bpm"] or 0.0,
        key=row["key"] or "",
        scale=row["scale"] or "",
        energy=row["energy"] or 0.0,
        danceability=row["danceability"] or 0.0,
        acousticness=row["acousticness"] or 0.0,
        valence=row["valence"] or 0.0,
        instrumentalness=row["instrumentalness"] or 0.0,
        loudness=row["loudness"] or 0.0,
        speechiness=row["speechiness"] if "speechiness" in row.keys() else 0.0,
        liveness=row["liveness"] if "liveness" in row.keys() else 0.0,
        cluster_id=row["cluster_id"],
        created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
    )


def _row_to_cluster(row: aiosqlite.Row) -> Cluster:
    """Convert database row to Cluster model."""
    return Cluster(
        id=row["id"],
        centroid_json=row["centroid_json"],
        description=row["description"] or "",
        song_count=row["song_count"] or 0,
    )


def _row_to_user_profile(row: aiosqlite.Row) -> UserProfile:
    """Convert database row to UserProfile model."""
    return UserProfile(
        id=row["id"],
        feature_vector_json=row["feature_vector_json"],
        matched_cluster_id=row["matched_cluster_id"],
        created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
    )
