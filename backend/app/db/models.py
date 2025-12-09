"""Database models for Music Match."""
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Song:
    """Song model with audio features."""
    id: Optional[int] = None
    title: str = ""
    artist: str = ""
    file_path: str = ""
    bpm: float = 0.0
    key: str = ""
    scale: str = ""
    energy: float = 0.0
    danceability: float = 0.0
    acousticness: float = 0.0
    valence: float = 0.0
    instrumentalness: float = 0.0
    loudness: float = 0.0
    cluster_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert song to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "file_path": self.file_path,
            "bpm": self.bpm,
            "key": self.key,
            "scale": self.scale,
            "energy": self.energy,
            "danceability": self.danceability,
            "acousticness": self.acousticness,
            "valence": self.valence,
            "instrumentalness": self.instrumentalness,
            "loudness": self.loudness,
            "cluster_id": self.cluster_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def get_feature_vector(self) -> list[float]:
        """Get normalized feature vector for clustering."""
        return [
            self.bpm / 200.0,  # Normalize BPM (assuming max 200)
            self.energy,
            self.danceability,
            self.acousticness,
            self.valence,
            self.instrumentalness,
            self.loudness,
        ]


@dataclass
class Cluster:
    """Cluster model with centroid information."""
    id: Optional[int] = None
    centroid_json: str = "{}"
    description: str = ""
    song_count: int = 0

    @property
    def centroid(self) -> dict:
        """Parse centroid JSON."""
        return json.loads(self.centroid_json)

    @centroid.setter
    def centroid(self, value: dict):
        """Set centroid from dict."""
        self.centroid_json = json.dumps(value)

    def to_dict(self) -> dict:
        """Convert cluster to dictionary."""
        return {
            "id": self.id,
            "centroid": self.centroid,
            "description": self.description,
            "song_count": self.song_count,
        }


@dataclass
class UserProfile:
    """User profile with feature vector from quiz."""
    id: Optional[int] = None
    feature_vector_json: str = "{}"
    matched_cluster_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def feature_vector(self) -> dict:
        """Parse feature vector JSON."""
        return json.loads(self.feature_vector_json)

    @feature_vector.setter
    def feature_vector(self, value: dict):
        """Set feature vector from dict."""
        self.feature_vector_json = json.dumps(value)

    def to_dict(self) -> dict:
        """Convert user profile to dictionary."""
        return {
            "id": self.id,
            "feature_vector": self.feature_vector,
            "matched_cluster_id": self.matched_cluster_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
