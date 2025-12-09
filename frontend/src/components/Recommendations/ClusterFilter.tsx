// Cluster filter tabs for browsing recommendations
import type { Cluster } from '../../types';

interface ClusterFilterProps {
  clusters: Cluster[];
  activeClusterId: number | null;
  onSelectCluster: (clusterId: number) => void;
}

export default function ClusterFilter({
  clusters,
  activeClusterId,
  onSelectCluster,
}: ClusterFilterProps) {
  return (
    <div className="flex flex-wrap gap-2 mb-6">
      {clusters.map((cluster) => (
        <button
          key={cluster.id}
          onClick={() => onSelectCluster(cluster.id)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
            activeClusterId === cluster.id
              ? 'bg-purple-600 text-white'
              : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700 hover:text-white'
          }`}
        >
          {cluster.description}
          <span className="ml-2 text-xs opacity-70">({cluster.song_count})</span>
        </button>
      ))}
    </div>
  );
}
