"""Database operations using aiosqlite."""
import aiosqlite
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from .models import Song, Cluster, UserProfile


DATABASE_PATH = Path(__file__).parent.parent.parent / "data" / "music_match.db"


async def get_db_connection() -> aiosqlite.Connection:
    """Get database connection."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(DATABASE_PATH)
    conn.row_factory = aiosqlite.Row
    return conn


async def init_db():
    """Initialize database tables."""
    async with await get_db_connection() as db:
        # Create songs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                file_path TEXT,
                bpm REAL DEFAULT 0,
                key TEXT DEFAULT '',
                scale TEXT DEFAULT '',
                energy REAL DEFAULT 0,
                danceability REAL DEFAULT 0,
                acousticness REAL DEFAULT 0,
                valence REAL DEFAULT 0,
                instrumentalness REAL DEFAULT 0,
                loudness REAL DEFAULT 0,
                cluster_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cluster_id) REFERENCES clusters (id)
            )
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

        await db.commit()


async def get_all_songs() -> list[Song]:
    """Get all songs from database."""
    async with await get_db_connection() as db:
        cursor = await db.execute("SELECT * FROM songs ORDER BY title")
        rows = await cursor.fetchall()
        return [_row_to_song(row) for row in rows]


async def get_songs_by_cluster(cluster_id: int, limit: Optional[int] = None) -> list[Song]:
    """Get songs belonging to a cluster."""
    async with await get_db_connection() as db:
        query = "SELECT * FROM songs WHERE cluster_id = ? ORDER BY title"
        if limit:
            query += f" LIMIT {limit}"
        cursor = await db.execute(query, (cluster_id,))
        rows = await cursor.fetchall()
        return [_row_to_song(row) for row in rows]


async def get_song_by_id(song_id: int) -> Optional[Song]:
    """Get a single song by ID."""
    async with await get_db_connection() as db:
        cursor = await db.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        row = await cursor.fetchone()
        return _row_to_song(row) if row else None


async def save_song_features(song: Song) -> int:
    """Save or update song with features."""
    async with await get_db_connection() as db:
        if song.id:
            await db.execute("""
                UPDATE songs SET
                    title = ?, artist = ?, file_path = ?, bpm = ?, key = ?, scale = ?,
                    energy = ?, danceability = ?, acousticness = ?, valence = ?,
                    instrumentalness = ?, loudness = ?, cluster_id = ?
                WHERE id = ?
            """, (
                song.title, song.artist, song.file_path, song.bpm, song.key, song.scale,
                song.energy, song.danceability, song.acousticness, song.valence,
                song.instrumentalness, song.loudness, song.cluster_id, song.id
            ))
            await db.commit()
            return song.id
        else:
            cursor = await db.execute("""
                INSERT INTO songs (
                    title, artist, file_path, bpm, key, scale, energy, danceability,
                    acousticness, valence, instrumentalness, loudness, cluster_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                song.title, song.artist, song.file_path, song.bpm, song.key, song.scale,
                song.energy, song.danceability, song.acousticness, song.valence,
                song.instrumentalness, song.loudness, song.cluster_id
            ))
            await db.commit()
            return cursor.lastrowid


async def get_all_clusters() -> list[Cluster]:
    """Get all clusters."""
    async with await get_db_connection() as db:
        cursor = await db.execute("SELECT * FROM clusters ORDER BY id")
        rows = await cursor.fetchall()
        return [_row_to_cluster(row) for row in rows]


async def get_cluster_by_id(cluster_id: int) -> Optional[Cluster]:
    """Get a single cluster by ID."""
    async with await get_db_connection() as db:
        cursor = await db.execute("SELECT * FROM clusters WHERE id = ?", (cluster_id,))
        row = await cursor.fetchone()
        return _row_to_cluster(row) if row else None


async def save_cluster(cluster: Cluster) -> int:
    """Save or update cluster."""
    async with await get_db_connection() as db:
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
    async with await get_db_connection() as db:
        await db.execute("DELETE FROM clusters")
        await db.execute("UPDATE songs SET cluster_id = NULL")
        await db.commit()


async def update_song_cluster(song_id: int, cluster_id: int):
    """Update song's cluster assignment."""
    async with await get_db_connection() as db:
        await db.execute(
            "UPDATE songs SET cluster_id = ? WHERE id = ?",
            (cluster_id, song_id)
        )
        await db.commit()


async def save_user_profile(profile: UserProfile) -> int:
    """Save user profile."""
    async with await get_db_connection() as db:
        cursor = await db.execute("""
            INSERT INTO user_profiles (feature_vector_json, matched_cluster_id)
            VALUES (?, ?)
        """, (profile.feature_vector_json, profile.matched_cluster_id))
        await db.commit()
        return cursor.lastrowid


async def get_user_profile(profile_id: int) -> Optional[UserProfile]:
    """Get user profile by ID."""
    async with await get_db_connection() as db:
        cursor = await db.execute(
            "SELECT * FROM user_profiles WHERE id = ?",
            (profile_id,)
        )
        row = await cursor.fetchone()
        return _row_to_user_profile(row) if row else None


def _row_to_song(row: aiosqlite.Row) -> Song:
    """Convert database row to Song model."""
    return Song(
        id=row["id"],
        title=row["title"],
        artist=row["artist"],
        file_path=row["file_path"] or "",
        bpm=row["bpm"] or 0.0,
        key=row["key"] or "",
        scale=row["scale"] or "",
        energy=row["energy"] or 0.0,
        danceability=row["danceability"] or 0.0,
        acousticness=row["acousticness"] or 0.0,
        valence=row["valence"] or 0.0,
        instrumentalness=row["instrumentalness"] or 0.0,
        loudness=row["loudness"] or 0.0,
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
