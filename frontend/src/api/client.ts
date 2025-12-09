// API client for Music Match backend
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const healthCheck = () => api.get('/health');

// Quiz endpoints
export const getQuiz = () => api.get('/api/quiz');
export const submitQuizAnswer = (answerId: string, answer: any) => 
  api.post(`/api/quiz/${answerId}`, answer);

// Recommendations endpoints
export const getRecommendations = (userId: string) => 
  api.get(`/api/recommendations/${userId}`);

// Features endpoints
export const extractFeatures = (audioFile: File) => {
  const formData = new FormData();
  formData.append('audio', audioFile);
  return api.post('/api/features/extract', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};
