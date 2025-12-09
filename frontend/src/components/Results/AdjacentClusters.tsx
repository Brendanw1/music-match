// Adjacent/nearby clusters to explore
import type { Cluster } from '../../types';
import { useNavigate } from 'react-router-dom';
import { Card, Badge, Button } from '../ui';

interface AdjacentClustersProps {
  clusters: Cluster[];
  title?: string;
}

export default function AdjacentClusters({
  clusters,
  title = 'You might also like',
}: AdjacentClustersProps) {
  const navigate = useNavigate();

  if (clusters.length === 0) {
    return null;
  }

  return (
    <div>
      <h3 className="text-lg font-semibold text-white mb-4">{title}</h3>
      <div className="grid gap-4 md:grid-cols-2">
        {clusters.map((cluster) => (
          <Card key={cluster.id} variant="interactive" className="p-4">
            <div className="flex items-start justify-between mb-2">
              <h4 className="text-white font-medium">{cluster.description}</h4>
              <Badge variant="default">{cluster.song_count}</Badge>
            </div>

            {cluster.sample_songs && cluster.sample_songs.length > 0 && (
              <p className="text-slate-400 text-sm mb-3">
                Including: {cluster.sample_songs.slice(0, 2).map(s => s.title).join(', ')}
              </p>
            )}

            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(`/recommendations/${cluster.id}`)}
            >
              Explore
            </Button>
          </Card>
        ))}
      </div>
    </div>
  );
}
