// Type definitions for Music Match

export interface QuizQuestion {
  id: string;
  question: string;
  options: QuizOption[];
}

export interface QuizOption {
  id: string;
  text: string;
}

export interface QuizAnswer {
  question_id: string;
  option_id: string;
}

export interface UserProfile {
  id?: number;
  feature_vector: Record<string, number>;
  radar_chart_data: RadarDataPoint[];
}

export interface RadarDataPoint {
  feature: string;
  value: number;
  fullMark: number;
}

export interface Cluster {
  id: number;
  description: string;
  song_count: number;
  centroid: Record<string, number>;
  sample_songs?: Song[];
  distance?: number;
}

export interface Song {
  id: number;
  spotify_id?: string;
  title: string;
  artist: string;
  album?: string;
  image_url?: string;
  thumbnail_url?: string;
  preview_url?: string;
  external_url?: string;
  duration_ms?: number;
  popularity?: number;
  bpm: number;
  key?: string;
  scale?: string;
  energy: number;
  danceability: number;
  acousticness: number;
  valence: number;
  instrumentalness: number;
  loudness: number;
  speechiness?: number;
  liveness?: number;
  cluster_id: number;
  similarity_score?: number;
}

// Spotify-specific types
export interface SpotifyTrack {
  id: string;
  name: string;
  artists: string[];
  album: string;
  image_url?: string;
  thumbnail_url?: string;
  preview_url?: string;
  external_url?: string;
  duration_ms: number;
  popularity: number;
}

export interface SpotifyAudioFeatures {
  danceability: number;
  energy: number;
  key: number;
  loudness: number;
  mode: number;
  speechiness: number;
  acousticness: number;
  instrumentalness: number;
  liveness: number;
  valence: number;
  tempo: number;
  duration_ms: number;
  time_signature: number;
}

export interface NormalizedFeatures {
  bpm_normalized: number;
  energy: number;
  danceability: number;
  acousticness: number;
  valence: number;
  instrumentalness: number;
  loudness: number;
  speechiness: number;
  liveness: number;
  key: string;
  scale: string;
}

export interface SpotifySearchResult {
  tracks: SpotifyTrack[];
  query: string;
  limit: number;
  offset: number;
}

export interface SpotifyTrackFeatures {
  track_id: string;
  features: SpotifyAudioFeatures;
  normalized: NormalizedFeatures;
  cached: boolean;
}

export interface SpotifyRecommendationsResult {
  recommendations: SpotifyTrack[];
  seed_tracks: string[];
  limit: number;
}

export interface QuizResult {
  user_profile: UserProfile;
  matched_cluster: Cluster;
  adjacent_clusters: Cluster[];
  songs: Song[];
}

export interface ClusterVisualization {
  songs: VisualizationPoint[];
  centroids: CentroidPoint[];
}

export interface VisualizationPoint {
  id: number;
  x: number;
  y: number;
  cluster_id: number;
  title: string;
  artist?: string;
}

export interface CentroidPoint {
  cluster_id: number;
  x: number;
  y: number;
}

export interface ApiResponse<T> {
  data: T;
  error?: string;
}
