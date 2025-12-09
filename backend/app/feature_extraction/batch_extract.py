"""Batch feature extraction for directories of audio files."""
import asyncio
from pathlib import Path
from typing import Optional
import os

from .extract import extract_features
from ..db import Song, save_song_features, init_db


SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac"}


def get_audio_files(directory: Path) -> list[Path]:
    """Get all supported audio files in a directory recursively."""
    audio_files = []
    for ext in SUPPORTED_EXTENSIONS:
        audio_files.extend(directory.rglob(f"*{ext}"))
    return sorted(audio_files)


def parse_filename(filepath: Path) -> tuple[str, str]:
    """
    Try to parse artist and title from filename.

    Supports formats:
    - "Artist - Title.mp3"
    - "Title.mp3" (artist will be "Unknown Artist")
    """
    stem = filepath.stem

    if " - " in stem:
        parts = stem.split(" - ", 1)
        return parts[0].strip(), parts[1].strip()

    return "Unknown Artist", stem.strip()


async def process_audio_file(filepath: Path) -> Optional[Song]:
    """
    Extract features from a single audio file and create Song object.

    Args:
        filepath: Path to audio file

    Returns:
        Song object with features, or None if extraction failed
    """
    try:
        # Extract features
        features = extract_features(filepath)

        # Parse metadata from filename
        artist, title = parse_filename(filepath)

        # Create song object
        song = Song(
            title=title,
            artist=artist,
            file_path=str(filepath),
            bpm=features.get("bpm", 0),
            key=features.get("key", ""),
            scale=features.get("scale", ""),
            energy=features.get("energy", 0),
            danceability=features.get("danceability", 0),
            acousticness=features.get("acousticness", 0),
            valence=features.get("valence", 0),
            instrumentalness=features.get("instrumentalness", 0),
            loudness=features.get("loudness", 0),
        )

        return song

    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None


async def batch_extract_features(
    directory: Path,
    save_to_db: bool = True
) -> list[Song]:
    """
    Extract features from all audio files in a directory.

    Args:
        directory: Directory containing audio files
        save_to_db: Whether to save results to database

    Returns:
        List of Song objects with extracted features
    """
    if save_to_db:
        await init_db()

    audio_files = get_audio_files(directory)

    if not audio_files:
        print(f"No audio files found in {directory}")
        return []

    print(f"Found {len(audio_files)} audio files")

    songs = []
    for i, filepath in enumerate(audio_files):
        print(f"Processing [{i+1}/{len(audio_files)}]: {filepath.name}")

        song = await process_audio_file(filepath)

        if song:
            if save_to_db:
                song_id = await save_song_features(song)
                song.id = song_id
            songs.append(song)

    print(f"\nSuccessfully processed {len(songs)}/{len(audio_files)} files")
    return songs
