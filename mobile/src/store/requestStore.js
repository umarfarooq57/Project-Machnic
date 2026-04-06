/**
 * Service request store — create, track, cancel, rate, history.
 */
import { create } from 'zustand';
import api from '../services/api';

export const useRequestStore = create((set, get) => ({
    activeRequest: null,
    requests: [],
    loading: false,
    error: null,

    createRequest: async (data) => {
        set({ loading: true, error: null });
        try {
            const res = await api.post('/requests/', data);
            set({ activeRequest: res.data.request || res.data, loading: false });
            return res.data;
        } catch (e) {
            set({ error: e.response?.data?.detail || 'Failed to create request', loading: false });
            return null;
        }
    },

    fetchActiveRequest: async (requestId) => {
        set({ loading: true });
        try {
            const res = await api.get(`/requests/${requestId}/`);
            set({ activeRequest: res.data, loading: false });
        } catch {
            set({ loading: false });
        }
    },

    cancelRequest: async (requestId) => {
        try {
            await api.post(`/requests/${requestId}/cancel/`);
            set({ activeRequest: null });
        } catch (e) {
            set({ error: e.response?.data?.detail || 'Failed to cancel' });
        }
    },

    submitRating: async (requestId, rating, review = '') => {
        try {
            await api.post(`/requests/${requestId}/rate/`, { rating, review });
        } catch (e) {
            set({ error: e.response?.data?.detail || 'Failed to submit rating' });
        }
    },

    fetchHistory: async () => {
        set({ loading: true });
        try {
            const res = await api.get('/requests/');
            set({ requests: res.data.results || res.data, loading: false });
        } catch {
            set({ loading: false });
        }
    },

    triggerSOS: async (latitude, longitude, message = '') => {
        try {
            const res = await api.post('/requests/sos/', { latitude, longitude, message });
            return res.data;
        } catch (e) {
            set({ error: e.response?.data?.detail || 'SOS failed' });
            return null;
        }
    },

    applyPromoCode: async (code, orderAmount) => {
        try {
            const res = await api.post('/admin/promo/apply/', { code, order_amount: orderAmount });
            return res.data;
        } catch (e) {
            set({ error: e.response?.data?.detail || 'Invalid promo code' });
            return null;
        }
    },
}));
