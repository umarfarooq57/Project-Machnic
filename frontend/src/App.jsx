import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';

// Layouts
import MainLayout from './components/layout/MainLayout';
import AuthLayout from './components/layout/AuthLayout';

// Pages
import Login from './pages/auth/Login';
import Signup from './pages/auth/Signup';
import UserDashboard from './pages/dashboard/UserDashboard';
import HelperDashboard from './pages/dashboard/HelperDashboard';
import CreateRequest from './pages/request/CreateRequest';
import ActiveRequest from './pages/request/ActiveRequest';
import RequestHistory from './pages/request/RequestHistory';
import ChatPage from './pages/chat/ChatPage';
import ProfilePage from './pages/profile/ProfilePage';
import HelperRegistration from './pages/helper/HelperRegistration';
import PaymentPage from './pages/payments/PaymentPage';
import NotificationsPage from './pages/notifications/NotificationsPage';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/AdminUsers';
import AdminHelpers from './pages/admin/AdminHelpers';
import AdminPromoCodes from './pages/admin/AdminPromoCodes';

// Landing Page
import LandingPage from './pages/landing/LandingPage';

// Protected Route Component
function ProtectedRoute({ children, requireHelper = false }) {
    const { isAuthenticated, user } = useAuthStore();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (requireHelper && !user?.is_helper) {
        return <Navigate to="/dashboard" replace />;
    }

    return children;
}

// Public Route Component (redirects if authenticated)
function PublicRoute({ children }) {
    const { isAuthenticated } = useAuthStore();

    if (isAuthenticated) {
        return <Navigate to="/dashboard" replace />;
    }

    return children;
}

// Admin Route Component
function AdminRoute({ children }) {
    const { isAuthenticated, user } = useAuthStore();

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (user?.role !== 'admin') {
        return <Navigate to="/dashboard" replace />;
    }

    return children;
}

function App() {
    return (
        <Routes>
            {/* Public Routes */}
            <Route element={<AuthLayout />}>
                <Route
                    path="/login"
                    element={
                        <PublicRoute>
                            <Login />
                        </PublicRoute>
                    }
                />
                <Route
                    path="/signup"
                    element={
                        <PublicRoute>
                            <Signup />
                        </PublicRoute>
                    }
                />
            </Route>

            {/* Protected Routes */}
            <Route element={<MainLayout />}>
                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <UserDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/helper/dashboard"
                    element={
                        <ProtectedRoute requireHelper>
                            <HelperDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/helper/register"
                    element={
                        <ProtectedRoute>
                            <HelperRegistration />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/request/new"
                    element={
                        <ProtectedRoute>
                            <CreateRequest />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/request/:requestId"
                    element={
                        <ProtectedRoute>
                            <ActiveRequest />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/requests"
                    element={
                        <ProtectedRoute>
                            <RequestHistory />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/chat/:roomId"
                    element={
                        <ProtectedRoute>
                            <ChatPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/profile"
                    element={
                        <ProtectedRoute>
                            <ProfilePage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/payment/:requestId"
                    element={
                        <ProtectedRoute>
                            <PaymentPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/notifications"
                    element={
                        <ProtectedRoute>
                            <NotificationsPage />
                        </ProtectedRoute>
                    }
                />
            </Route>

            {/* Admin Routes */}
            <Route element={<MainLayout />}>
                <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
                <Route path="/admin/users" element={<AdminRoute><AdminUsers /></AdminRoute>} />
                <Route path="/admin/helpers" element={<AdminRoute><AdminHelpers /></AdminRoute>} />
                <Route path="/admin/promo-codes" element={<AdminRoute><AdminPromoCodes /></AdminRoute>} />
            </Route>

            {/* Landing Page (public) */}
            <Route path="/" element={<LandingPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}

export default App;
