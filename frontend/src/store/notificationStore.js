/**
 * Notification state management with Zustand.
 */
import { create } from 'zustand';
import api from '../api/client';

export const useNotificationStore = create((set, get) => ({
    notifications: [],
    unreadCount: 0,
    isLoading: false,

    // Fetch notifications
    fetchNotifications: async () => {
        set({ isLoading: true });
        try {
            const response = await api.get('/notifications/');
            const notifications = response.data.results || response.data;
            set({
                notifications,
                unreadCount: notifications.filter((n) => !n.is_read).length,
                isLoading: false,
            });
        } catch (error) {
            set({ isLoading: false });
        }
    },

    // Mark notification as read
    markAsRead: async (notificationId) => {
        try {
            await api.post(`/notifications/${notificationId}/read/`);
            set((state) => ({
                notifications: state.notifications.map((n) =>
                    n.id === notificationId ? { ...n, is_read: true } : n
                ),
                unreadCount: Math.max(0, state.unreadCount - 1),
            }));
        } catch (error) {
            console.error('Failed to mark notification as read:', error);
        }
    },

    // Mark all as read
    markAllAsRead: async () => {
        try {
            await api.post('/notifications/read-all/');
            set((state) => ({
                notifications: state.notifications.map((n) => ({ ...n, is_read: true })),
                unreadCount: 0,
            }));
        } catch (error) {
            console.error('Failed to mark all notifications as read:', error);
        }
    },

    // Add new notification (from WebSocket)
    addNotification: (notification) => {
        set((state) => ({
            notifications: [notification, ...state.notifications],
            unreadCount: state.unreadCount + 1,
        }));
    },
}));
