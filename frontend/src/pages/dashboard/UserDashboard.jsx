/**
 * User Dashboard - Main landing page for users.
 */
import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useRequestStore } from '../../store/requestStore';
import './Dashboard.css';

function UserDashboard() {
    const { user } = useAuthStore();
    const { requests, fetchUserRequests, isLoading } = useRequestStore();
    const navigate = useNavigate();
    const [activeRequest, setActiveRequest] = useState(null);

    useEffect(() => {
        fetchUserRequests();
    }, [fetchUserRequests]);

    useEffect(() => {
        // Find any active request
        const active = requests.find((r) =>
            ['pending', 'searching', 'accepted', 'en_route', 'arrived', 'in_progress'].includes(r.status)
        );
        setActiveRequest(active);
    }, [requests]);

    const getStatusColor = (status) => {
        const colors = {
            pending: 'badge-warning',
            searching: 'badge-info',
            accepted: 'badge-primary',
            en_route: 'badge-primary',
            arrived: 'badge-success',
            in_progress: 'badge-success',
            completed: 'badge-success',
            cancelled: 'badge-error',
        };
        return colors[status] || 'badge-primary';
    };

    const stats = [
        { label: 'Total Requests', value: requests.length, icon: '📋' },
        { label: 'Completed', value: requests.filter((r) => r.status === 'completed').length, icon: '✅' },
        { label: 'Active', value: requests.filter((r) => !['completed', 'cancelled'].includes(r.status)).length, icon: '🔄' },
    ];

    return (
        <div className="dashboard animate-fadeIn">
            {/* Welcome Section */}
            <div className="dashboard-header">
                <div>
                    <h1>Welcome back, {user?.full_name?.split(' ')[0]}! 👋</h1>
                    <p>Need roadside assistance? We've got you covered.</p>
                </div>
                <Link to="/request/new" className="btn btn-primary btn-lg">
                    <span>🚨</span>
                    Get Help Now
                </Link>
            </div>

            {/* Active Request Banner */}
            {activeRequest && (
                <div
                    className="active-request-banner"
                    onClick={() => navigate(`/request/${activeRequest.id}`)}
                >
                    <div className="banner-content">
                        <div className="banner-icon">🔔</div>
                        <div className="banner-text">
                            <h3>Active Request</h3>
                            <p>Status: {activeRequest.status.replace('_', ' ')}</p>
                        </div>
                    </div>
                    <span className={`badge ${getStatusColor(activeRequest.status)}`}>
                        {activeRequest.status.replace('_', ' ')}
                    </span>
                </div>
            )}

            {/* Stats Grid */}
            <div className="stats-grid">
                {stats.map((stat) => (
                    <div key={stat.label} className="stat-card card">
                        <div className="stat-icon">{stat.icon}</div>
                        <div className="stat-info">
                            <span className="stat-value">{stat.value}</span>
                            <span className="stat-label">{stat.label}</span>
                        </div>
                    </div>
                ))}
            </div>

            {/* Quick Actions */}
            <div className="quick-actions">
                <h2>Quick Actions</h2>
                <div className="actions-grid">
                    <Link to="/request/new" className="action-card">
                        <div className="action-icon">🚗</div>
                        <span>Flat Tire</span>
                    </Link>
                    <Link to="/request/new" className="action-card">
                        <div className="action-icon">🔋</div>
                        <span>Dead Battery</span>
                    </Link>
                    <Link to="/request/new" className="action-card">
                        <div className="action-icon">⛽</div>
                        <span>Out of Fuel</span>
                    </Link>
                    <Link to="/request/new" className="action-card">
                        <div className="action-icon">🔧</div>
                        <span>Other Issue</span>
                    </Link>
                </div>
            </div>

            {/* Recent Requests */}
            <div className="recent-requests">
                <div className="section-header">
                    <h2>Recent Requests</h2>
                    <Link to="/requests" className="btn btn-secondary btn-sm">View All</Link>
                </div>

                {isLoading ? (
                    <div className="loading-state">
                        <div className="loader"></div>
                    </div>
                ) : requests.length === 0 ? (
                    <div className="empty-state card">
                        <div className="empty-icon">📭</div>
                        <h3>No requests yet</h3>
                        <p>When you need help, create a request and we'll connect you with nearby helpers.</p>
                        <Link to="/request/new" className="btn btn-primary">Create Your First Request</Link>
                    </div>
                ) : (
                    <div className="requests-list">
                        {requests.slice(0, 5).map((request) => (
                            <div
                                key={request.id}
                                className="request-item card"
                                onClick={() => navigate(`/request/${request.id}`)}
                            >
                                <div className="request-info">
                                    <h4>{request.vehicle_type_name}</h4>
                                    <p>{new Date(request.created_at).toLocaleDateString()}</p>
                                </div>
                                <span className={`badge ${getStatusColor(request.status)}`}>
                                    {request.status.replace('_', ' ')}
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Become a Helper CTA */}
            {!user?.is_helper && (
                <div className="helper-cta card-glass">
                    <div className="cta-content">
                        <h3>🔧 Want to help others?</h3>
                        <p>Register as a helper and earn money by assisting stranded drivers.</p>
                    </div>
                    <Link to="/helper/register" className="btn btn-accent">Become a Helper</Link>
                </div>
            )}
        </div>
    );
}

export default UserDashboard;
