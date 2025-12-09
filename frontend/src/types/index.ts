// Type definitions for Music Match

export interface Song {
  id: string;
  title: string;
  artist: string;
  album?: string;
  duration?: number;
  features?: AudioFeatures;
}

export interface AudioFeatures {
  tempo?: number;
  energy?: number;
  danceability?: number;
  valence?: number;
  acousticness?: number;
  instrumentalness?: number;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: QuizOption[];
}

export interface QuizOption {
  id: string;
  text: string;
  value: any;
}

export interface Recommendation {
  song: Song;
  score: number;
  reason?: string;
}

export interface Cluster {
  id: string;
  name: string;
  songs: Song[];
  centroid: AudioFeatures;
}
