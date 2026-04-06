/**
 * API client with token refresh, error handling, and env-based URL.
 */
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://192.168.1.100:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  timeout: 20000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Request interceptor ──
api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('access');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response interceptor (auto-refresh) ──
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      try {
        const refresh = await SecureStore.getItemAsync('refresh');
        if (refresh) {
          const res = await axios.post(`${API_URL}/auth/token/refresh/`, { refresh });
          await SecureStore.setItemAsync('access', res.data.access);
          original.headers.Authorization = `Bearer ${res.data.access}`;
          return api(original);
        }
      } catch {
        await SecureStore.deleteItemAsync('access');
        await SecureStore.deleteItemAsync('refresh');
      }
    }
    return Promise.reject(error);
  }
);

export default api;
