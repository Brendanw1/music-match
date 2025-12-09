// Cluster explorer page
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Cluster, Song } from '../../types';
import { clustersApi, recommendationsApi } from '../../api/client';
import { Button, Loading, Card } from '../ui';
import ClusterFilter from './ClusterFilter';
import RecommendationGrid from './RecommendationGrid';

export default function ClusterExplorer() {
  const navigate = useNavigate();
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [activeClusterId, setActiveClusterId] = useState<number | null>(null);
  const [songs, setSongs] = useState<Song[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingSongs, setLoadingSongs] = useState(false);

  useEffect(() => {
    loadClusters();
  }, []);

  useEffect(() => {
    if (activeClusterId !== null) {
      loadSongs(activeClusterId);
    }
  }, [activeClusterId]);

  const loadClusters = async () => {
    try {
      setLoading(true);
      const data = await clustersApi.getAll();
      setClusters(data);
      if (data.length > 0) {
        setActiveClusterId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load clusters:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadSongs = async (clusterId: number) => {
    try {
      setLoadingSongs(true);
      const data = await recommendationsApi.getByCluster(clusterId, 20);
      setSongs(data);
    } catch (err) {
      console.error('Failed to load songs:', err);
      setSongs([]);
    } finally {
      setLoadingSongs(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" text="Loading clusters..." />
      </div>
    );
  }

  const activeCluster = clusters.find((c) => c.id === activeClusterId);

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-white">Explore Music</h1>
              <p className="text-slate-400">
                Browse songs by cluster and discover new favorites
              </p>
            </div>
            <Button variant="ghost" onClick={() => navigate('/')}>
              Back to Quiz
            </Button>
          </div>
        </header>

        {/* Cluster filters */}
        <ClusterFilter
          clusters={clusters}
          activeClusterId={activeClusterId}
          onSelectCluster={setActiveClusterId}
        />

        {/* Active cluster info */}
        {activeCluster && (
          <Card className="p-4 mb-6">
            <h2 className="text-xl font-semibold text-white mb-1">
              {activeCluster.description}
            </h2>
            <p className="text-slate-400 text-sm">
              {activeCluster.song_count} songs in this cluster
            </p>
          </Card>
        )}

        {/* Songs grid */}
        {loadingSongs ? (
          <div className="py-12 flex justify-center">
            <Loading text="Loading songs..." />
          </div>
        ) : (
          <RecommendationGrid songs={songs} />
        )}
      </div>
    </div>
  );
}
