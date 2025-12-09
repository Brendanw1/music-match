// API client for Music Match backend
import axios from 'axios';
import type {
  QuizQuestion,
  QuizAnswer,
  QuizResult,
  Cluster,
  Song,
  ClusterVisualization,
  SpotifyTrack,
  SpotifySearchResult,
  SpotifyTrackFeatures,
  SpotifyRecommendationsResult,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const healthCheck = () => api.get('/health');

// Quiz API
export const quizApi = {
  getQuestions: async (): Promise<QuizQuestion[]> => {
    const response = await api.get<{ questions: QuizQuestion[] }>('/quiz/questions');
    return response.data.questions;
  },

  submitQuiz: async (answers: QuizAnswer[]): Promise<QuizResult> => {
    const response = await api.post<QuizResult>('/quiz/submit', { answers });
    return response.data;
  },
};

// Recommendations API
export const recommendationsApi = {
  getByCluster: async (
    clusterId: number,
    limit?: number,
    userVector?: Record<string, number>
  ): Promise<Song[]> => {
    const params: Record<string, string | number> = {};
    if (limit) params.limit = limit;
    if (userVector) params.user_vector = JSON.stringify(userVector);

    const response = await api.get<{ songs: Song[] }>(
      `/recommendations/${clusterId}`,
      { params }
    );
    return response.data.songs;
  },
};

// Clusters API
export const clustersApi = {
  getAll: async (): Promise<Cluster[]> => {
    const response = await api.get<{ clusters: Cluster[] }>('/clusters');
    return response.data.clusters;
  },

  getById: async (clusterId: number): Promise<Cluster & { songs: Song[] }> => {
    const response = await api.get<Cluster & { songs: Song[] }>(
      `/clusters/${clusterId}`
    );
    return response.data;
  },

  getVisualization: async (): Promise<ClusterVisualization> => {
    const response = await api.get<ClusterVisualization>('/clusters/visualization');
    return response.data;
  },
};

// Songs API
export const songsApi = {
  getById: async (songId: number): Promise<Song> => {
    const response = await api.get<Song>(`/songs/${songId}`);
    return response.data;
  },
};

// Spotify API
export const spotifyApi = {
  search: async (
    query: string,
    limit = 20,
    offset = 0
  ): Promise<SpotifySearchResult> => {
    const response = await api.get<SpotifySearchResult>('/spotify/search', {
      params: { q: query, limit, offset },
    });
    return response.data;
  },

  getTrack: async (trackId: string): Promise<SpotifyTrack> => {
    const response = await api.get<SpotifyTrack>(`/spotify/track/${trackId}`);
    return response.data;
  },

  getTrackFeatures: async (trackId: string): Promise<SpotifyTrackFeatures> => {
    const response = await api.get<SpotifyTrackFeatures>(
      `/spotify/track/${trackId}/features`
    );
    return response.data;
  },

  getTrackFull: async (
    trackId: string
  ): Promise<{ track: Song; source: string }> => {
    const response = await api.get<{ track: Song; source: string }>(
      `/spotify/track/${trackId}/full`
    );
    return response.data;
  },

  getRecommendations: async (
    seedTracks: string[],
    limit = 20,
    targetFeatures?: {
      energy?: number;
      danceability?: number;
      valence?: number;
      acousticness?: number;
      instrumentalness?: number;
    }
  ): Promise<SpotifyRecommendationsResult> => {
    const params: Record<string, string | number> = {
      seed_tracks: seedTracks.join(','),
      limit,
    };

    if (targetFeatures) {
      if (targetFeatures.energy !== undefined) {
        params.target_energy = targetFeatures.energy;
      }
      if (targetFeatures.danceability !== undefined) {
        params.target_danceability = targetFeatures.danceability;
      }
      if (targetFeatures.valence !== undefined) {
        params.target_valence = targetFeatures.valence;
      }
      if (targetFeatures.acousticness !== undefined) {
        params.target_acousticness = targetFeatures.acousticness;
      }
      if (targetFeatures.instrumentalness !== undefined) {
        params.target_instrumentalness = targetFeatures.instrumentalness;
      }
    }

    const response = await api.get<SpotifyRecommendationsResult>(
      '/spotify/recommendations',
      { params }
    );
    return response.data;
  },

  importTrack: async (
    trackId: string,
    clusterId?: number
  ): Promise<{ song: Song; imported: boolean; message: string }> => {
    const params = clusterId !== undefined ? { cluster_id: clusterId } : {};
    const response = await api.post<{
      song: Song;
      imported: boolean;
      message: string;
    }>(`/spotify/import/${trackId}`, null, { params });
    return response.data;
  },
};
