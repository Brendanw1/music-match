// Spotify search component with debounced search and results display
import { useState, useCallback, useEffect, useRef } from 'react';
import type { SpotifyTrack } from '../../types';
import { spotifyApi } from '../../api/client';
import { Card, Loading } from '../ui';
import SpotifyTrackCard from './SpotifyTrackCard';

interface SpotifySearchProps {
  onTrackSelect?: (track: SpotifyTrack) => void;
  selectedTracks?: SpotifyTrack[];
  maxSelections?: number;
  placeholder?: string;
  showPlayer?: boolean;
}

export default function SpotifySearch({
  onTrackSelect,
  selectedTracks = [],
  maxSelections = 5,
  placeholder = 'Search for songs...',
  showPlayer = true,
}: SpotifySearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SpotifyTrack[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const debounceRef = useRef<number | null>(null);

  const search = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([]);
      setHasSearched(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await spotifyApi.search(searchQuery, 20);
      setResults(response.tracks);
      setHasSearched(true);
    } catch (err) {
      setError('Failed to search tracks. Please try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) {
      window.clearTimeout(debounceRef.current);
    }

    if (query.trim()) {
      debounceRef.current = window.setTimeout(() => {
        search(query);
      }, 300);
    } else {
      setResults([]);
      setHasSearched(false);
    }

    return () => {
      if (debounceRef.current) {
        window.clearTimeout(debounceRef.current);
      }
    };
  }, [query, search]);

  const handleTrackSelect = useCallback(
    (track: SpotifyTrack) => {
      if (!onTrackSelect) return;

      const isSelected = selectedTracks.some((t) => t.id === track.id);

      if (isSelected) {
        // Deselect
        onTrackSelect(track);
      } else if (selectedTracks.length < maxSelections) {
        // Select
        onTrackSelect(track);
      }
    },
    [onTrackSelect, selectedTracks, maxSelections]
  );

  const isTrackSelected = (trackId: string) =>
    selectedTracks.some((t) => t.id === trackId);

  return (
    <Card className="p-4">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
        />
        <div className="absolute right-3 top-1/2 -translate-y-1/2">
          {loading ? (
            <Loading size="sm" />
          ) : (
            <svg
              className="w-5 h-5 text-slate-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          )}
        </div>
      </div>

      {selectedTracks.length > 0 && (
        <div className="mt-4">
          <p className="text-sm text-slate-400 mb-2">
            Selected ({selectedTracks.length}/{maxSelections}):
          </p>
          <div className="flex flex-wrap gap-2">
            {selectedTracks.map((track) => (
              <button
                key={track.id}
                onClick={() => handleTrackSelect(track)}
                className="flex items-center gap-2 px-3 py-1.5 bg-purple-600/20 border border-purple-500/50 rounded-full text-sm text-white hover:bg-purple-600/30 transition-colors"
              >
                {track.thumbnail_url && (
                  <img
                    src={track.thumbnail_url}
                    alt=""
                    className="w-5 h-5 rounded-full"
                  />
                )}
                <span className="truncate max-w-[150px]">{track.name}</span>
                <svg
                  className="w-4 h-4 text-slate-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {hasSearched && !loading && results.length === 0 && (
        <div className="mt-6 text-center text-slate-500">
          No tracks found for "{query}"
        </div>
      )}

      {results.length > 0 && (
        <div className="mt-4 space-y-3 max-h-96 overflow-y-auto">
          {results.map((track) => (
            <SpotifyTrackCard
              key={track.id}
              track={track}
              onSelect={handleTrackSelect}
              selected={isTrackSelected(track.id)}
              showPlayer={showPlayer}
              compact
            />
          ))}
        </div>
      )}
    </Card>
  );
}
