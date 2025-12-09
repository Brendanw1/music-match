// Grid layout for song recommendations
import type { Song } from '../../types';
import SongCard from './SongCard';

interface RecommendationGridProps {
  songs: Song[];
  userVector?: Record<string, number>;
  columns?: 2 | 3 | 4;
}

export default function RecommendationGrid({
  songs,
  columns = 3,
}: RecommendationGridProps) {
  const gridCols = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
  };

  if (songs.length === 0) {
    return (
      <div className="text-center py-12 text-slate-400">
        No songs found in this cluster.
      </div>
    );
  }

  return (
    <div className={`grid gap-4 ${gridCols[columns]}`}>
      {songs.map((song) => (
        <SongCard
          key={song.id}
          song={song}
          showSimilarity={song.similarity_score !== undefined}
        />
      ))}
    </div>
  );
}
