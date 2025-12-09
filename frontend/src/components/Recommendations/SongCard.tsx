// Individual song card with feature bars
import type { Song } from '../../types';
import { Card, Badge } from '../ui';

interface SongCardProps {
  song: Song;
  compact?: boolean;
  showSimilarity?: boolean;
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

export default function SongCard({ song, compact = false, showSimilarity = false }: SongCardProps) {
  if (compact) {
    return (
      <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors">
        <div className="flex-1 min-w-0">
          <p className="text-white font-medium truncate">{song.title}</p>
          <p className="text-slate-400 text-sm truncate">{song.artist}</p>
        </div>
        <div className="flex items-center gap-2 ml-4">
          <Badge variant="default">{Math.round(song.bpm)} BPM</Badge>
          {showSimilarity && song.similarity_score !== undefined && (
            <Badge variant="success">
              {Math.round(song.similarity_score * 100)}% match
            </Badge>
          )}
        </div>
      </div>
    );
  }

  return (
    <Card className="p-4 hover:border-purple-500/30 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-white font-semibold truncate">{song.title}</h3>
          <p className="text-slate-400 text-sm truncate">{song.artist}</p>
        </div>
        {showSimilarity && song.similarity_score !== undefined && (
          <Badge variant="success">
            {Math.round(song.similarity_score * 100)}%
          </Badge>
        )}
      </div>

      <div className="flex items-center gap-3 mb-4 text-sm">
        <Badge variant="default">{Math.round(song.bpm)} BPM</Badge>
        {song.key && song.scale && (
          <Badge variant="info">{song.key} {song.scale}</Badge>
        )}
      </div>

      <div className="space-y-2">
        <FeatureBar label="Energy" value={song.energy} />
        <FeatureBar label="Dance" value={song.danceability} />
        <FeatureBar label="Positivity" value={song.valence} />
        <FeatureBar label="Acoustic" value={song.acousticness} />
      </div>
    </Card>
  );
}
