/**
 * Main Layout component with navigation and sidebar.
 */
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useNotificationStore } from '../../store/notificationStore';
import { useEffect } from 'react';
import './MainLayout.css';

// Icons as components
const HomeIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
        <polyline points="9 22 9 12 15 12 15 22"></polyline>
    </svg>
);

const PlusIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
    </svg>
);

const ListIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <line x1="8" y1="6" x2="21" y2="6"></line>
        <line x1="8" y1="12" x2="21" y2="12"></line>
        <line x1="8" y1="18" x2="21" y2="18"></line>
        <line x1="3" y1="6" x2="3.01" y2="6"></line>
        <line x1="3" y1="12" x2="3.01" y2="12"></line>
        <line x1="3" y1="18" x2="3.01" y2="18"></line>
    </svg>
);

const BellIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
    </svg>
);

const UserIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
    </svg>
);

const LogoutIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
        <polyline points="16 17 21 12 16 7"></polyline>
        <line x1="21" y1="12" x2="9" y2="12"></line>
    </svg>
);

const WrenchIcon = () => (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"></path>
    </svg>
);

function MainLayout() {
    const { user, logout, isAuthenticated } = useAuthStore();
    const { unreadCount, fetchNotifications } = useNotificationStore();
    const location = useLocation();
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated) {
            fetchNotifications();
        }
    }, [isAuthenticated, fetchNotifications]);

    const handleLogout = async () => {
        await logout();
        navigate('/login');
    };

    const isActive = (path) => location.pathname === path;

    const navItems = [
        { path: '/dashboard', icon: HomeIcon, label: 'Dashboard' },
        { path: '/request/new', icon: PlusIcon, label: 'New Request' },
        { path: '/requests', icon: ListIcon, label: 'My Requests' },
        { path: '/notifications', icon: BellIcon, label: 'Notifications', badge: unreadCount },
        { path: '/profile', icon: UserIcon, label: 'Profile' },
    ];

    // Add helper dashboard if user is a helper
    if (user?.is_helper) {
        navItems.splice(1, 0, {
            path: '/helper/dashboard',
            icon: WrenchIcon,
            label: 'Helper Mode',
        });
    }

    return (
        <div className="main-layout">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <Link to="/dashboard" className="logo">
                        <div className="logo-icon">🚗</div>
                        <span className="logo-text">RoadAid</span>
                    </Link>
                </div>

                <nav className="sidebar-nav">
                    {navItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
                        >
                            <item.icon />
                            <span>{item.label}</span>
                            {item.badge > 0 && <span className="nav-badge">{item.badge}</span>}
                        </Link>
                    ))}
                </nav>

                {!user?.is_helper && (
                    <div className="sidebar-cta">
                        <Link to="/helper/register" className="btn btn-accent w-full">
                            Become a Helper
                        </Link>
                    </div>
                )}

                <div className="sidebar-footer">
                    <div className="user-info">
                        <div className="avatar">
                            {user?.profile_image ? (
                                <img src={user.profile_image} alt={user.full_name} />
                            ) : (
                                <span>{user?.full_name?.charAt(0) || 'U'}</span>
                            )}
                        </div>
                        <div className="user-details">
                            <span className="user-name">{user?.full_name}</span>
                            <span className="user-role">{user?.is_helper ? 'Helper' : 'User'}</span>
                        </div>
                    </div>
                    <button onClick={handleLogout} className="logout-btn" title="Logout">
                        <LogoutIcon />
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="main-content">
                <Outlet />
            </main>

            {/* Mobile Bottom Nav */}
            <nav className="mobile-nav hide-desktop">
                {navItems.slice(0, 5).map((item) => (
                    <Link
                        key={item.path}
                        to={item.path}
                        className={`mobile-nav-item ${isActive(item.path) ? 'active' : ''}`}
                    >
                        <item.icon />
                        {item.badge > 0 && <span className="mobile-badge">{item.badge}</span>}
                    </Link>
                ))}
            </nav>
        </div>
    );
}

export default MainLayout;
