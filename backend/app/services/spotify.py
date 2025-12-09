"""Spotify API service for Music Match."""
import os
from typing import Optional
from functools import lru_cache
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class SpotifyService:
    """Service for interacting with Spotify Web API."""

    def __init__(self):
        """Initialize Spotify client with client credentials flow."""
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables must be set"
            )

        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self._client = spotipy.Spotify(auth_manager=auth_manager)

    def search_tracks(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> list[dict]:
        """
        Search for tracks by name/artist.

        Args:
            query: Search query string
            limit: Maximum number of results (1-50)
            offset: Offset for pagination

        Returns:
            List of track dictionaries with relevant info
        """
        results = self._client.search(
            q=query,
            type="track",
            limit=min(limit, 50),
            offset=offset
        )

        tracks = []
        for item in results.get("tracks", {}).get("items", []):
            tracks.append(self._format_track(item))

        return tracks

    def get_track(self, track_id: str) -> Optional[dict]:
        """
        Get a single track by Spotify ID.

        Args:
            track_id: Spotify track ID

        Returns:
            Track dictionary or None if not found
        """
        try:
            track = self._client.track(track_id)
            return self._format_track(track)
        except spotipy.exceptions.SpotifyException:
            return None

    def get_tracks(self, track_ids: list[str]) -> list[dict]:
        """
        Get multiple tracks by Spotify IDs.

        Args:
            track_ids: List of Spotify track IDs (max 50)

        Returns:
            List of track dictionaries
        """
        if not track_ids:
            return []

        # Spotify API allows max 50 tracks per request
        track_ids = track_ids[:50]

        try:
            results = self._client.tracks(track_ids)
            return [
                self._format_track(track)
                for track in results.get("tracks", [])
                if track is not None
            ]
        except spotipy.exceptions.SpotifyException:
            return []

    def get_audio_features(self, track_id: str) -> Optional[dict]:
        """
        Get audio features for a single track.

        Args:
            track_id: Spotify track ID

        Returns:
            Audio features dictionary or None if not found
        """
        try:
            features = self._client.audio_features([track_id])
            if features and features[0]:
                return self._format_audio_features(features[0])
            return None
        except spotipy.exceptions.SpotifyException:
            return None

    def get_audio_features_batch(self, track_ids: list[str]) -> list[dict]:
        """
        Get audio features for multiple tracks.

        Args:
            track_ids: List of Spotify track IDs (max 100)

        Returns:
            List of audio features dictionaries
        """
        if not track_ids:
            return []

        # Spotify API allows max 100 tracks per request
        track_ids = track_ids[:100]

        try:
            features_list = self._client.audio_features(track_ids)
            return [
                self._format_audio_features(features)
                for features in features_list
                if features is not None
            ]
        except spotipy.exceptions.SpotifyException:
            return []

    def get_recommendations(
        self,
        seed_tracks: list[str],
        seed_artists: Optional[list[str]] = None,
        seed_genres: Optional[list[str]] = None,
        limit: int = 20,
        **target_features
    ) -> list[dict]:
        """
        Get track recommendations based on seeds.

        Args:
            seed_tracks: List of track IDs (up to 5 total seeds)
            seed_artists: Optional list of artist IDs
            seed_genres: Optional list of genre names
            limit: Number of recommendations (1-100)
            **target_features: Target audio feature values (e.g., target_energy=0.8)

        Returns:
            List of recommended track dictionaries
        """
        # Spotify requires at least one seed and max 5 total
        total_seeds = len(seed_tracks or []) + len(seed_artists or []) + len(seed_genres or [])
        if total_seeds == 0:
            return []
        if total_seeds > 5:
            seed_tracks = seed_tracks[:5]
            seed_artists = None
            seed_genres = None

        try:
            results = self._client.recommendations(
                seed_tracks=seed_tracks[:5] if seed_tracks else None,
                seed_artists=seed_artists[:5] if seed_artists else None,
                seed_genres=seed_genres[:5] if seed_genres else None,
                limit=min(limit, 100),
                **target_features
            )

            tracks = []
            for track in results.get("tracks", []):
                tracks.append(self._format_track(track))

            return tracks
        except spotipy.exceptions.SpotifyException:
            return []

    def get_track_with_features(self, track_id: str) -> Optional[dict]:
        """
        Get track info with audio features combined.

        Args:
            track_id: Spotify track ID

        Returns:
            Combined track and features dictionary
        """
        track = self.get_track(track_id)
        if not track:
            return None

        features = self.get_audio_features(track_id)
        if features:
            track["audio_features"] = features

        return track

    def _format_track(self, track: dict) -> dict:
        """Format raw Spotify track data into our schema."""
        album = track.get("album", {})
        artists = track.get("artists", [])

        # Get the best quality image available
        images = album.get("images", [])
        image_url = images[0]["url"] if images else None
        thumbnail_url = images[-1]["url"] if images else None

        return {
            "spotify_id": track.get("id"),
            "title": track.get("name", ""),
            "artist": ", ".join(a.get("name", "") for a in artists),
            "artist_ids": [a.get("id") for a in artists],
            "album": album.get("name", ""),
            "album_id": album.get("id"),
            "image_url": image_url,
            "thumbnail_url": thumbnail_url,
            "preview_url": track.get("preview_url"),
            "duration_ms": track.get("duration_ms", 0),
            "popularity": track.get("popularity", 0),
            "explicit": track.get("explicit", False),
            "external_url": track.get("external_urls", {}).get("spotify"),
        }

    def _format_audio_features(self, features: dict) -> dict:
        """Format raw Spotify audio features into our schema."""
        return {
            "spotify_id": features.get("id"),
            "danceability": features.get("danceability", 0),
            "energy": features.get("energy", 0),
            "key": features.get("key", 0),
            "loudness": features.get("loudness", 0),
            "mode": features.get("mode", 0),  # 0 = minor, 1 = major
            "speechiness": features.get("speechiness", 0),
            "acousticness": features.get("acousticness", 0),
            "instrumentalness": features.get("instrumentalness", 0),
            "liveness": features.get("liveness", 0),
            "valence": features.get("valence", 0),
            "tempo": features.get("tempo", 0),
            "duration_ms": features.get("duration_ms", 0),
            "time_signature": features.get("time_signature", 4),
        }


# Singleton instance
_spotify_service: Optional[SpotifyService] = None


def get_spotify_service() -> SpotifyService:
    """Get or create the Spotify service singleton."""
    global _spotify_service
    if _spotify_service is None:
        _spotify_service = SpotifyService()
    return _spotify_service


def reset_spotify_service():
    """Reset the Spotify service (useful for testing)."""
    global _spotify_service
    _spotify_service = None
