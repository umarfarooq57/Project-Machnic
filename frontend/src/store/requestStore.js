/**
 * Service request state management with Zustand.
 */
import { create } from 'zustand';
import api from '../api/client';

export const useRequestStore = create((set, get) => ({
    requests: [],
    activeRequest: null,
    availableRequests: [],
    isLoading: false,
    error: null,

    // Fetch user's requests
    fetchUserRequests: async () => {
        set({ isLoading: true });
        try {
            const response = await api.get('/requests/my/');
            set({ requests: response.data.results || response.data, isLoading: false });
        } catch (error) {
            set({ error: error.message, isLoading: false });
        }
    },

    // Fetch helper's requests
    fetchHelperRequests: async () => {
        set({ isLoading: true });
        try {
            const response = await api.get('/requests/helper/');
            set({ requests: response.data.results || response.data, isLoading: false });
        } catch (error) {
            set({ error: error.message, isLoading: false });
        }
    },

    // Fetch available requests for helpers
    fetchAvailableRequests: async () => {
        set({ isLoading: true });
        try {
            const response = await api.get('/requests/available/');
            set({ availableRequests: response.data.results || response.data, isLoading: false });
        } catch (error) {
            set({ error: error.message, isLoading: false });
        }
    },

    // Fetch single request
    fetchRequest: async (requestId) => {
        set({ isLoading: true });
        try {
            const response = await api.get(`/requests/${requestId}/`);
            set({ activeRequest: response.data, isLoading: false });
            return response.data;
        } catch (error) {
            set({ error: error.message, isLoading: false });
            return null;
        }
    },

    // Create new request
    createRequest: async (data) => {
        set({ isLoading: true });
        try {
            const response = await api.post('/requests/', data);
            set((state) => ({
                requests: [response.data.request, ...state.requests],
                activeRequest: response.data.request,
                isLoading: false,
            }));
            return { success: true, request: response.data.request };
        } catch (error) {
            set({ error: error.response?.data, isLoading: false });
            return { success: false, error: error.response?.data };
        }
    },

    // Accept request (helper)
    acceptRequest: async (requestId) => {
        set({ isLoading: true });
        try {
            const response = await api.post(`/requests/${requestId}/accept/`);
            set({ activeRequest: response.data.request, isLoading: false });
            return { success: true };
        } catch (error) {
            set({ error: error.response?.data, isLoading: false });
            return { success: false, error: error.response?.data?.error };
        }
    },

    // Update request status
    updateStatus: async (requestId, status, data = {}) => {
        try {
            const response = await api.post(`/requests/${requestId}/status/`, { status, ...data });
            set({ activeRequest: response.data.request });
            return { success: true };
        } catch (error) {
            return { success: false, error: error.response?.data };
        }
    },

    // Cancel request
    cancelRequest: async (requestId, reason = '') => {
        try {
            const response = await api.post(`/requests/${requestId}/cancel/`, { reason });
            set({ activeRequest: response.data.request });
            return { success: true };
        } catch (error) {
            return { success: false, error: error.response?.data };
        }
    },

    // Update helper location
    updateHelperLocation: async (requestId, latitude, longitude) => {
        try {
            const response = await api.post(`/requests/${requestId}/location/`, {
                latitude,
                longitude,
            });
            set((state) => ({
                activeRequest: state.activeRequest
                    ? {
                        ...state.activeRequest,
                        helper_latitude: latitude,
                        helper_longitude: longitude,
                        eta_minutes: response.data.eta_minutes,
                    }
                    : null,
            }));
        } catch (error) {
            console.error('Failed to update location:', error);
        }
    },

    // Update active request from WebSocket
    updateActiveRequest: (data) => {
        set((state) => ({
            activeRequest: state.activeRequest
                ? { ...state.activeRequest, ...data }
                : null,
        }));
    },

    // Clear active request
    clearActiveRequest: () => set({ activeRequest: null }),

    // Clear error
    clearError: () => set({ error: null }),
}));
