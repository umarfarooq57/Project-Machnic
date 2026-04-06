/**
 * Authentication state management with Zustand.
 * Handles login, logout, and token management.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api, { setAuthToken, removeAuthToken } from '../api/client';

export const useAuthStore = create(
    persist(
        (set, get) => ({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,

            // Login action
            login: async (email, password) => {
                set({ isLoading: true, error: null });
                try {
                    const response = await api.post('/auth/login/', { email, password });
                    const { user, access, refresh } = response.data;

                    setAuthToken(access);

                    set({
                        user,
                        tokens: { access, refresh },
                        isAuthenticated: true,
                        isLoading: false,
                    });

                    return { success: true };
                } catch (error) {
                    const message = error.response?.data?.detail || 'Login failed';
                    set({ error: message, isLoading: false });
                    return { success: false, error: message };
                }
            },

            // Register action
            register: async (userData) => {
                set({ isLoading: true, error: null });
                try {
                    const response = await api.post('/auth/register/', userData);
                    const { user, tokens } = response.data;

                    setAuthToken(tokens.access);

                    set({
                        user,
                        tokens,
                        isAuthenticated: true,
                        isLoading: false,
                    });

                    return { success: true };
                } catch (error) {
                    const errors = error.response?.data || { detail: 'Registration failed' };
                    set({ error: errors, isLoading: false });
                    return { success: false, error: errors };
                }
            },

            // Logout action
            logout: async () => {
                try {
                    const { tokens } = get();
                    if (tokens?.refresh) {
                        await api.post('/auth/logout/', { refresh: tokens.refresh });
                    }
                } catch (error) {
                    console.error('Logout error:', error);
                } finally {
                    removeAuthToken();
                    set({
                        user: null,
                        tokens: null,
                        isAuthenticated: false,
                        error: null,
                    });
                }
            },

            // Refresh token action
            refreshToken: async () => {
                const { tokens } = get();
                if (!tokens?.refresh) return false;

                try {
                    const response = await api.post('/auth/token/refresh/', {
                        refresh: tokens.refresh,
                    });
                    const { access } = response.data;

                    setAuthToken(access);
                    set((state) => ({
                        tokens: { ...state.tokens, access },
                    }));

                    return true;
                } catch (error) {
                    get().logout();
                    return false;
                }
            },

            // Update user profile
            updateProfile: async (data) => {
                set({ isLoading: true });
                try {
                    const response = await api.patch('/auth/profile/', data);
                    set({ user: response.data, isLoading: false });
                    return { success: true };
                } catch (error) {
                    set({ isLoading: false });
                    return { success: false, error: error.response?.data };
                }
            },

            // Update user location
            updateLocation: async (latitude, longitude) => {
                try {
                    await api.post('/auth/profile/location/', { latitude, longitude });
                    set((state) => ({
                        user: { ...state.user, latitude, longitude },
                    }));
                } catch (error) {
                    console.error('Failed to update location:', error);
                }
            },

            // Clear error
            clearError: () => set({ error: null }),
        }),
        {
            name: 'roadaid-auth',
            partialize: (state) => ({
                user: state.user,
                tokens: state.tokens,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
);
