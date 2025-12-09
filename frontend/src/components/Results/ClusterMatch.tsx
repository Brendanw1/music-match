// Matched cluster display card
import type { Cluster } from '../../types';
import { Card, Badge } from '../ui';
import SongCard from '../Recommendations/SongCard';

interface ClusterMatchProps {
  cluster: Cluster;
  title?: string;
  showSamples?: boolean;
}

export default function ClusterMatch({
  cluster,
  title = 'Your Music Match',
  showSamples = true,
}: ClusterMatchProps) {
  return (
    <Card variant="highlighted" className="p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-purple-400 text-sm font-medium mb-1">{title}</p>
          <h2 className="text-2xl font-bold text-white">{cluster.description}</h2>
        </div>
        <Badge variant="purple">{cluster.song_count} songs</Badge>
      </div>

      {cluster.distance !== undefined && (
        <p className="text-slate-400 text-sm mb-4">
          Match confidence: {Math.round((1 - cluster.distance) * 100)}%
        </p>
      )}

      {showSamples && cluster.sample_songs && cluster.sample_songs.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-slate-400 mb-3">Sample tracks:</h3>
          <div className="space-y-2">
            {cluster.sample_songs.slice(0, 3).map((song) => (
              <SongCard key={song.id} song={song} compact />
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}
