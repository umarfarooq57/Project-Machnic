/**
 * Chat state management with Zustand.
 */
import { create } from 'zustand';
import api from '../api/client';

export const useChatStore = create((set, get) => ({
    currentRoom: null,
    messages: [],
    isTyping: false,
    typingUser: null,
    isLoading: false,

    // Fetch chat room for a request
    fetchChatRoom: async (requestId) => {
        set({ isLoading: true });
        try {
            const response = await api.get(`/chat/request/${requestId}/`);
            set({ currentRoom: response.data, isLoading: false });
            return response.data;
        } catch (error) {
            set({ isLoading: false });
            return null;
        }
    },

    // Fetch messages for a room
    fetchMessages: async (roomId) => {
        set({ isLoading: true });
        try {
            const response = await api.get(`/chat/${roomId}/messages/`);
            set({ messages: response.data.results || response.data, isLoading: false });
        } catch (error) {
            set({ isLoading: false });
        }
    },

    // Send a message
    sendMessage: async (roomId, content, messageType = 'text') => {
        try {
            const response = await api.post(`/chat/${roomId}/send/`, {
                content,
                message_type: messageType,
            });
            set((state) => ({
                messages: [...state.messages, response.data],
            }));
            return { success: true };
        } catch (error) {
            return { success: false, error: error.message };
        }
    },

    // Add message from WebSocket
    addMessage: (message) => {
        set((state) => ({
            messages: [...state.messages, message],
        }));
    },

    // Set typing indicator
    setTypingIndicator: (isTyping, userName = null) => {
        set({ isTyping, typingUser: userName });
    },

    // Mark messages as read
    markAsRead: async (roomId) => {
        try {
            await api.post(`/chat/${roomId}/read/`);
        } catch (error) {
            console.error('Failed to mark messages as read:', error);
        }
    },

    // Clear chat state
    clearChat: () => set({ currentRoom: null, messages: [], isTyping: false }),
}));
