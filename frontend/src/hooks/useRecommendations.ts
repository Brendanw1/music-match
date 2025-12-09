// Recommendations fetching and caching hook
import { useState, useCallback } from 'react';
import type { Song, Cluster } from '../types';
import { recommendationsApi, clustersApi } from '../api/client';

interface UseRecommendationsState {
  songs: Song[];
  clusters: Cluster[];
  activeClusterId: number | null;
  loading: boolean;
  error: string | null;
}

export function useRecommendations() {
  const [state, setState] = useState<UseRecommendationsState>({
    songs: [],
    clusters: [],
    activeClusterId: null,
    loading: false,
    error: null,
  });

  // Cache for songs by cluster
  const [songCache, setSongCache] = useState<Map<number, Song[]>>(new Map());

  const loadClusters = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const clusters = await clustersApi.getAll();
      setState((prev) => ({ ...prev, clusters, loading: false }));
      return clusters;
    } catch (err) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: 'Failed to load clusters',
      }));
      throw err;
    }
  }, []);

  const loadSongsByCluster = useCallback(
    async (
      clusterId: number,
      limit?: number,
      userVector?: Record<string, number>
    ) => {
      // Check cache first (only if no userVector for personalized results)
      if (!userVector && songCache.has(clusterId)) {
        const cachedSongs = songCache.get(clusterId)!;
        setState((prev) => ({
          ...prev,
          songs: cachedSongs,
          activeClusterId: clusterId,
        }));
        return cachedSongs;
      }

      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const songs = await recommendationsApi.getByCluster(
          clusterId,
          limit,
          userVector
        );

        // Cache results if not personalized
        if (!userVector) {
          setSongCache((prev) => new Map(prev).set(clusterId, songs));
        }

        setState((prev) => ({
          ...prev,
          songs,
          activeClusterId: clusterId,
          loading: false,
        }));
        return songs;
      } catch (err) {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: 'Failed to load songs',
        }));
        throw err;
      }
    },
    [songCache]
  );

  const clearCache = useCallback(() => {
    setSongCache(new Map());
  }, []);

  return {
    ...state,
    loadClusters,
    loadSongsByCluster,
    clearCache,
  };
}
