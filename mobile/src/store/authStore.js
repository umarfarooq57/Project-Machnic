/**
 * Auth store — login, register, logout, profile, auto-login.
 */
import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';
import api from '../services/api';

export const useAuthStore = create((set) => ({
  user: null,
  tokens: null,
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const res = await api.post('/auth/login/', { email, password });
      const { user, tokens } = res.data;
      set({ user, tokens, loading: false });
      await SecureStore.setItemAsync('access', tokens.access);
      await SecureStore.setItemAsync('refresh', tokens.refresh);
    } catch (e) {
      set({ error: e.response?.data?.detail || 'Login failed', loading: false });
    }
  },

  register: async (email, fullName, password, passwordConfirm) => {
    set({ loading: true, error: null });
    try {
      const res = await api.post('/auth/register/', {
        email, full_name: fullName, password, password_confirm: passwordConfirm,
      });
      const { user, tokens } = res.data;
      set({ user, tokens, loading: false });
      await SecureStore.setItemAsync('access', tokens.access);
      await SecureStore.setItemAsync('refresh', tokens.refresh);
    } catch (e) {
      const msg = e.response?.data?.detail
        || (e.response?.data?.email && e.response.data.email[0])
        || 'Registration failed';
      set({ error: msg, loading: false });
    }
  },

  logout: async () => {
    set({ user: null, tokens: null, error: null });
    await SecureStore.deleteItemAsync('access');
    await SecureStore.deleteItemAsync('refresh');
  },

  autoLogin: async () => {
    const access = await SecureStore.getItemAsync('access');
    if (!access) return;
    try {
      const res = await api.get('/auth/profile/', {
        headers: { Authorization: `Bearer ${access}` },
      });
      set({ user: res.data, tokens: { access } });
    } catch {
      set({ user: null, tokens: null });
    }
  },

  updateProfile: async (data) => {
    set({ loading: true, error: null });
    try {
      const res = await api.patch('/auth/profile/', data);
      set({ user: res.data, loading: false });
    } catch (e) {
      set({ error: 'Failed to update profile', loading: false });
    }
  },
}));
