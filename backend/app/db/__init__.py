"""Database module."""
from .models import Song, Cluster, UserProfile
from .database import (
    init_db,
    get_db_connection,
    get_all_songs,
    get_songs_by_cluster,
    get_song_by_id,
    save_song_features,
    get_all_clusters,
    get_cluster_by_id,
    save_cluster,
    clear_clusters,
    update_song_cluster,
    save_user_profile,
    get_user_profile,
)

__all__ = [
    "Song",
    "Cluster",
    "UserProfile",
    "init_db",
    "get_db_connection",
    "get_all_songs",
    "get_songs_by_cluster",
    "get_song_by_id",
    "save_song_features",
    "get_all_clusters",
    "get_cluster_by_id",
    "save_cluster",
    "clear_clusters",
    "update_song_cluster",
    "save_user_profile",
    "get_user_profile",
]
