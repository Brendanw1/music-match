// Individual song card with feature bars and Spotify support
import type { Song } from '../../types';
import { Card, Badge } from '../ui';
import { AudioPlayer } from '../Spotify';

interface SongCardProps {
  song: Song;
  compact?: boolean;
  showSimilarity?: boolean;
  showPlayer?: boolean;
}

function FeatureBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-slate-500 w-20">{label}</span>
      <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full"
          style={{ width: `${value * 100}%` }}
        />
      </div>
    </div>
  );
}

export default function SongCard({
  song,
  compact = false,
  showSimilarity = false,
  showPlayer = true,
}: SongCardProps) {
  if (compact) {
    return (
      <div className="flex items-center gap-3 p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors">
        {song.thumbnail_url && (
          <img
            src={song.thumbnail_url}
            alt={`${song.album || song.title} cover`}
            className="w-10 h-10 rounded object-cover"
          />
        )}
        <div className="flex-1 min-w-0">
          <p className="text-white font-medium truncate">{song.title}</p>
          <p className="text-slate-400 text-sm truncate">{song.artist}</p>
        </div>
        <div className="flex items-center gap-2 ml-2">
          <Badge variant="default">{Math.round(song.bpm)} BPM</Badge>
          {showSimilarity && song.similarity_score !== undefined && (
            <Badge variant="success">
              {Math.round(song.similarity_score * 100)}% match
            </Badge>
          )}
        </div>
        {showPlayer && song.preview_url && (
          <AudioPlayer previewUrl={song.preview_url} compact />
        )}
      </div>
    );
  }

  return (
    <Card className="p-4 hover:border-purple-500/30 transition-colors">
      <div className="flex gap-4">
        {song.image_url && (
          <img
            src={song.image_url}
            alt={`${song.album || song.title} cover`}
            className="w-20 h-20 rounded-lg object-cover shadow-lg"
          />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-1">
            <div className="flex-1 min-w-0">
              <h3 className="text-white font-semibold truncate">{song.title}</h3>
              <p className="text-slate-400 text-sm truncate">{song.artist}</p>
              {song.album && (
                <p className="text-slate-500 text-xs truncate">{song.album}</p>
              )}
            </div>
            {showSimilarity && song.similarity_score !== undefined && (
              <Badge variant="success">
                {Math.round(song.similarity_score * 100)}%
              </Badge>
            )}
          </div>

          <div className="flex items-center gap-2 mt-2 text-sm">
            <Badge variant="default">{Math.round(song.bpm)} BPM</Badge>
            {song.key && song.scale && (
              <Badge variant="info">{song.key} {song.scale}</Badge>
            )}
            {song.popularity !== undefined && song.popularity > 0 && (
              <Badge variant="warning">{song.popularity}% popular</Badge>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-2 mt-4">
        <FeatureBar label="Energy" value={song.energy} />
        <FeatureBar label="Dance" value={song.danceability} />
        <FeatureBar label="Positivity" value={song.valence} />
        <FeatureBar label="Acoustic" value={song.acousticness} />
      </div>

      {showPlayer && song.preview_url && (
        <div className="mt-4">
          <AudioPlayer previewUrl={song.preview_url} trackName={song.title} compact />
        </div>
      )}

      {song.external_url && (
        <a
          href={song.external_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1"
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
