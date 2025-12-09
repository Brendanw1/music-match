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
  title: string;
  artist: string;
  bpm: number;
  key?: string;
  scale?: string;
  energy: number;
  danceability: number;
  acousticness: number;
  valence: number;
  instrumentalness: number;
  loudness: number;
  cluster_id: number;
  similarity_score?: number;
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
