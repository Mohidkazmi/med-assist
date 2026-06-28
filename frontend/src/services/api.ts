import axios from 'axios';

// Read API base URL from Vite environment variables
// Fallback to local Docker-exposed FastAPI backend port 8001
const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1';

export const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Call Failed:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);
