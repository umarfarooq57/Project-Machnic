/**
 * Admin Zustand store — API calls for admin dashboard.
 */
import { create } from 'zustand';
import api from '../api/client';

export const useAdminStore = create((set, get) => ({
    // State
    stats: null,
    users: [],
    helpers: [],
    promoCodes: [],
    disputes: [],
    revenueReport: [],
    loading: false,
    error: null,

    // Dashboard
    fetchDashboardStats: async () => {
        set({ loading: true, error: null });
        try {
            const res = await api.get('/admin/dashboard/');
            set({ stats: res.data, loading: false });
        } catch (err) {
            set({ error: err.response?.data?.error || 'Failed to fetch stats', loading: false });
        }
    },

    fetchRevenueReport: async (days = 30) => {
        try {
            const res = await api.get(`/admin/revenue-report/?days=${days}`);
            set({ revenueReport: res.data });
        } catch (err) {
            console.error('Revenue report error:', err);
        }
    },

    // Users
    fetchUsers: async (params = {}) => {
        set({ loading: true });
        try {
            const res = await api.get('/admin/users/', { params });
            set({ users: res.data.results || res.data, loading: false });
        } catch (err) {
            set({ error: err.response?.data?.error || 'Failed to fetch users', loading: false });
        }
    },

    updateUser: async (userId, data) => {
        try {
            await api.patch(`/admin/users/${userId}/`, data);
            get().fetchUsers();
        } catch (err) {
            set({ error: err.response?.data?.error || 'Failed to update user' });
        }
    },

    // Helpers
    fetchHelpers: async (params = {}) => {
        set({ loading: true });
        try {
            const res = await api.get('/admin/helpers/', { params });
            set({ helpers: res.data.results || res.data, loading: false });
        } catch (err) {
            set({ error: err.response?.data?.error || 'Failed to fetch helpers', loading: false });
        }
    },

    verifyHelper: async (helperId, action, reason = '') => {
        try {
            await api.post(`/admin/helpers/${helperId}/verify/`, { action, reason });
            get().fetchHelpers();
        } catch (err) {
            set({ error: err.response?.data?.error || 'Verification failed' });
        }
    },

    // Promo Codes
    fetchPromoCodes: async () => {
        set({ loading: true });
        try {
            const res = await api.get('/admin/promo-codes/');
            set({ promoCodes: res.data.results || res.data, loading: false });
        } catch (err) {
            set({ error: err.response?.data?.error || 'Failed to fetch promo codes', loading: false });
        }
    },

    createPromoCode: async (data) => {
        try {
            await api.post('/admin/promo-codes/', data);
            get().fetchPromoCodes();
        } catch (err) {
            set({ error: err.response?.data?.error || 'Failed to create promo code' });
        }
    },

    deletePromoCode: async (id) => {
        try {
            await api.delete(`/admin/promo-codes/${id}/`);
            get().fetchPromoCodes();
        } catch (err) {
            set({ error: err.response?.data?.error || 'Failed to delete promo code' });
        }
    },

    // Disputes
    fetchDisputes: async () => {
        set({ loading: true });
        try {
            const res = await api.get('/admin/disputes/');
            set({ disputes: res.data.results || res.data, loading: false });
        } catch (err) {
            set({ error: err.response?.data?.error || 'Failed to fetch disputes', loading: false });
        }
    },

    resolveDispute: async (disputeId, notes) => {
        try {
            await api.post(`/admin/disputes/${disputeId}/resolve/`, { resolution_notes: notes });
            get().fetchDisputes();
        } catch (err) {
            set({ error: err.response?.data?.error || 'Failed to resolve dispute' });
        }
    },
}));
