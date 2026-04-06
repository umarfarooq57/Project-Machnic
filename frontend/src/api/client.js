/**
 * Axios API client configuration.
 * Handles authentication tokens and interceptors.
 */
import axios from 'axios';

// API base URL
const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

// Create axios instance
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000,
});

// Token management
let authToken = null;

export const setAuthToken = (token) => {
    authToken = token;
    if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        localStorage.setItem('access_token', token);
    }
};

export const removeAuthToken = () => {
    authToken = null;
    delete api.defaults.headers.common['Authorization'];
    localStorage.removeItem('access_token');
    localStorage.removeItem('roadaid-auth');
};

// Initialize token from localStorage
const storedToken = localStorage.getItem('access_token');
if (storedToken) {
    setAuthToken(storedToken);
}

// Request interceptor
api.interceptors.request.use(
    (config) => {
        // Add token if available
        if (authToken) {
            config.headers.Authorization = `Bearer ${authToken}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Handle 401 errors (token expired)
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                // Try to refresh token
                const refreshToken = JSON.parse(
                    localStorage.getItem('roadaid-auth') || '{}'
                )?.state?.tokens?.refresh;

                if (refreshToken) {
                    const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
                        refresh: refreshToken,
                    });

                    const { access } = response.data;
                    setAuthToken(access);

                    // Update stored tokens
                    const storedData = JSON.parse(
                        localStorage.getItem('roadaid-auth') || '{}'
                    );
                    if (storedData.state?.tokens) {
                        storedData.state.tokens.access = access;
                        localStorage.setItem('roadaid-auth', JSON.stringify(storedData));
                    }

                    originalRequest.headers.Authorization = `Bearer ${access}`;
                    return api(originalRequest);
                }
            } catch (refreshError) {
                // Refresh failed, logout user
                removeAuthToken();
                window.location.href = '/login';
            }
        }

        return Promise.reject(error);
    }
);

export default api;
