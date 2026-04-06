/**
 * Notification store — fetch, mark read, count unread.
 */
import { create } from 'zustand';
import api from '../services/api';

export const useNotificationStore = create((set, get) => ({
    notifications: [],
    unreadCount: 0,
    loading: false,

    fetchNotifications: async () => {
        set({ loading: true });
        try {
            const res = await api.get('/notifications/');
            const list = res.data.results || res.data;
            set({
                notifications: list,
                unreadCount: list.filter(n => !n.is_read).length,
                loading: false,
            });
        } catch {
            set({ loading: false });
        }
    },

    markAsRead: async (notificationId) => {
        try {
            await api.post(`/notifications/${notificationId}/read/`);
            const updated = get().notifications.map(n =>
                n.id === notificationId ? { ...n, is_read: true } : n
            );
            set({
                notifications: updated,
                unreadCount: updated.filter(n => !n.is_read).length,
            });
        } catch { /* silent */ }
    },

    markAllRead: async () => {
        try {
            await api.post('/notifications/read-all/');
            const updated = get().notifications.map(n => ({ ...n, is_read: true }));
            set({ notifications: updated, unreadCount: 0 });
        } catch { /* silent */ }
    },
}));
