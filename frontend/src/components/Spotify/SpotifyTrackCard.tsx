// Spotify track card with album art and preview player
import type { SpotifyTrack } from '../../types';
import { Card, Badge } from '../ui';
import AudioPlayer from './AudioPlayer';

interface SpotifyTrackCardProps {
  track: SpotifyTrack;
  onSelect?: (track: SpotifyTrack) => void;
  selected?: boolean;
  showPlayer?: boolean;
  compact?: boolean;
}

function formatDuration(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

export default function SpotifyTrackCard({
  track,
  onSelect,
  selected = false,
  showPlayer = true,
  compact = false,
}: SpotifyTrackCardProps) {
  const handleClick = () => {
    if (onSelect) {
      onSelect(track);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  if (compact) {
    return (
      <div
        className={`flex items-center gap-3 p-2 rounded-lg transition-colors cursor-pointer ${
          selected
            ? 'bg-purple-600/20 border border-purple-500/50'
            : 'bg-slate-800/50 hover:bg-slate-800 border border-transparent'
        }`}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={0}
      >
        {track.thumbnail_url && (
          <img
            src={track.thumbnail_url}
            alt={`${track.album} cover`}
            className="w-10 h-10 rounded object-cover"
          />
        )}
        <div className="flex-1 min-w-0">
          <p className="text-white text-sm font-medium truncate">{track.name}</p>
          <p className="text-slate-400 text-xs truncate">
            {track.artists.join(', ')}
          </p>
        </div>
        {showPlayer && track.preview_url && (
          <AudioPlayer previewUrl={track.preview_url} compact />
        )}
      </div>
    );
  }

  return (
    <Card
      className={`p-4 transition-all cursor-pointer ${
        selected
          ? 'border-purple-500 bg-purple-600/10'
          : 'hover:border-purple-500/30'
      }`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
    >
      <div className="flex gap-4">
        {track.image_url && (
          <img
            src={track.image_url}
            alt={`${track.album} cover`}
            className="w-24 h-24 rounded-lg object-cover shadow-lg"
          />
        )}
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-semibold truncate">{track.name}</h3>
          <p className="text-slate-400 text-sm truncate">
            {track.artists.join(', ')}
          </p>
          <p className="text-slate-500 text-xs truncate mt-1">{track.album}</p>

          <div className="flex items-center gap-2 mt-3">
            <Badge variant="default">{formatDuration(track.duration_ms)}</Badge>
            {track.popularity > 0 && (
              <Badge variant="info">{track.popularity}% popular</Badge>
            )}
            {selected && <Badge variant="success">Selected</Badge>}
          </div>
        </div>
      </div>

      {showPlayer && (
        <div className="mt-4">
          <AudioPlayer
            previewUrl={track.preview_url}
            trackName={track.name}
            compact
          />
        </div>
      )}

      {track.external_url && (
        <a
          href={track.external_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1"
          onClick={(e) => e.stopPropagation()}
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z" />
          </svg>
          Open in Spotify
        </a>
      )}
    </Card>
  );
}
