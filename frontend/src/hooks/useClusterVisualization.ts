// Cluster visualization data hook
import { useState, useCallback, useEffect } from 'react';
import type { ClusterVisualization } from '../types';
import { clustersApi } from '../api/client';

interface UseClusterVisualizationState {
  data: ClusterVisualization | null;
  loading: boolean;
  error: string | null;
}

export function useClusterVisualization(autoLoad = false) {
  const [state, setState] = useState<UseClusterVisualizationState>({
    data: null,
    loading: false,
    error: null,
  });

  const load = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const data = await clustersApi.getVisualization();
      setState({ data, loading: false, error: null });
      return data;
    } catch (err) {
      setState({
        data: null,
        loading: false,
        error: 'Failed to load visualization data',
      });
      throw err;
    }
  }, []);

  useEffect(() => {
    if (autoLoad) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      load();
    }
  }, [autoLoad, load]);

  return {
    ...state,
    load,
    reload: load,
  };
}
