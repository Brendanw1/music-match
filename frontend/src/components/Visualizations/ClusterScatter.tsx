// 2D scatter plot visualization of clusters
import { useState, useEffect } from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import type { ClusterVisualization, VisualizationPoint } from '../../types';
import { clustersApi } from '../../api/client';
import { Loading, Card } from '../ui';

// Color palette for clusters
const CLUSTER_COLORS = [
  '#a855f7', // purple
  '#3b82f6', // blue
  '#22c55e', // green
  '#f59e0b', // amber
  '#ef4444', // red
  '#06b6d4', // cyan
  '#ec4899', // pink
  '#8b5cf6', // violet
  '#f97316', // orange
  '#14b8a6', // teal
];

interface ClusterScatterProps {
  onSongClick?: (songId: number) => void;
}

export default function ClusterScatter({ onSongClick }: ClusterScatterProps) {
  const [data, setData] = useState<ClusterVisualization | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadVisualization();
  }, []);

  const loadVisualization = async () => {
    try {
      setLoading(true);
      const vizData = await clustersApi.getVisualization();
      setData(vizData);
    } catch (err) {
      console.error('Failed to load visualization:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="h-96 flex items-center justify-center">
        <Loading text="Loading visualization..." />
      </div>
    );
  }

  if (!data || data.songs.length === 0) {
    return (
      <Card className="p-8 text-center">
        <p className="text-slate-400">No visualization data available.</p>
      </Card>
    );
  }

  // Group songs by cluster
  const clusterIds = [...new Set(data.songs.map((s) => s.cluster_id))].sort();

  const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ payload: VisualizationPoint }> }) => {
    if (active && payload && payload.length) {
      const song = payload[0].payload;
      return (
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-xl">
          <p className="text-white font-medium">{song.title}</p>
          {song.artist && <p className="text-slate-400 text-sm">{song.artist}</p>}
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Cluster Visualization</h3>
      <p className="text-slate-400 text-sm mb-4">
        Songs plotted by similarity (PCA reduction). Each color represents a different cluster.
      </p>

      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <XAxis
              type="number"
              dataKey="x"
              domain={['auto', 'auto']}
              tick={{ fill: '#64748b', fontSize: 10 }}
              axisLine={{ stroke: '#475569' }}
              tickLine={{ stroke: '#475569' }}
            />
            <YAxis
              type="number"
              dataKey="y"
              domain={['auto', 'auto']}
              tick={{ fill: '#64748b', fontSize: 10 }}
              axisLine={{ stroke: '#475569' }}
              tickLine={{ stroke: '#475569' }}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* Songs */}
            {clusterIds.map((clusterId, index) => {
              const clusterSongs = data.songs.filter((s) => s.cluster_id === clusterId);
              return (
                <Scatter
                  key={clusterId}
                  data={clusterSongs}
                  fill={CLUSTER_COLORS[index % CLUSTER_COLORS.length]}
                >
                  {clusterSongs.map((song, i) => (
                    <Cell
                      key={i}
                      cursor={onSongClick ? 'pointer' : 'default'}
                      onClick={() => onSongClick?.(song.id)}
                      opacity={0.7}
                    />
                  ))}
                </Scatter>
              );
            })}

            {/* Centroids */}
            <Scatter
              data={data.centroids.map((c) => ({ ...c, x: c.x, y: c.y }))}
              shape="star"
              fill="#ffffff"
            >
              {data.centroids.map((_, i) => (
                <Cell key={i} strokeWidth={2} stroke={CLUSTER_COLORS[i % CLUSTER_COLORS.length]} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mt-4 justify-center">
        {clusterIds.map((clusterId, index) => (
          <div key={clusterId} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: CLUSTER_COLORS[index % CLUSTER_COLORS.length] }}
            />
            <span className="text-slate-400 text-sm">Cluster {clusterId}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
