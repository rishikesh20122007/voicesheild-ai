import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach the JWT token to every request automatically, if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('vs_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// If the server ever returns 401 (expired/invalid token), clear the
// stored token so the user is prompted to log in again.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('vs_token');
    }
    return Promise.reject(error);
  }
);

// --- Auth ---
export const registerUser = (data) => api.post('/api/auth/register', data);
export const loginUser = (data) => api.post('/api/auth/login', data);
export const getCurrentUser = () => api.get('/api/auth/me');

// --- Analysis ---
export const analyzeAudio = (formData) =>
  api.post('/api/analyze/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

// --- History ---
export const getHistory = () => api.get('/api/history');
export const getScanDetail = (scanId) => api.get(`/api/history/${scanId}`);
export const deleteScan = (scanId) => api.delete(`/api/history/${scanId}`);

// --- Dashboard ---
export const getDashboardStats = () => api.get('/api/dashboard/stats');

export default api;