/**
 * Helper Dashboard - For mechanics/helpers to manage availability and requests.
 */
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { useRequestStore } from '../../store/requestStore';
import api from '../../api/client';
import toast from 'react-hot-toast';
import './Dashboard.css';

function HelperDashboard() {
    const { user } = useAuthStore();
    const { availableRequests, fetchAvailableRequests, fetchHelperRequests, requests, acceptRequest, isLoading } = useRequestStore();
    const navigate = useNavigate();
    const [isAvailable, setIsAvailable] = useState(false);
    const [helperProfile, setHelperProfile] = useState(null);

    useEffect(() => {
        fetchHelperProfile();
        fetchAvailableRequests();
        fetchHelperRequests();
    }, []);

    const fetchHelperProfile = async () => {
        try {
            const response = await api.get('/helpers/profile/');
            setHelperProfile(response.data);
            setIsAvailable(response.data.is_available);
        } catch (error) {
            console.error('Failed to fetch helper profile:', error);
        }
    };

    const toggleAvailability = async () => {
        try {
            const response = await api.post('/helpers/availability/', {
                is_available: !isAvailable,
            });
            setIsAvailable(response.data.is_available);
            toast.success(response.data.is_available ? 'You are now available!' : 'You are now offline');

            if (response.data.is_available) {
                fetchAvailableRequests();
            }
        } catch (error) {
            toast.error('Failed to update availability');
        }
    };

    const handleAcceptRequest = async (requestId) => {
        const result = await acceptRequest(requestId);
        if (result.success) {
            toast.success('Request accepted!');
            navigate(`/request/${requestId}`);
        } else {
            toast.error(result.error || 'Failed to accept request');
        }
    };

    const activeJobs = requests.filter((r) =>
        ['accepted', 'en_route', 'arrived', 'in_progress'].includes(r.status)
    );

    const stats = [
        { label: 'Rating', value: helperProfile?.rating_avg?.toFixed(1) || '0.0', icon: '⭐' },
        { label: 'Total Jobs', value: helperProfile?.total_jobs || 0, icon: '✅' },
        { label: 'Active Jobs', value: activeJobs.length, icon: '🔄' },
    ];

    return (
        <div className="dashboard helper-dashboard animate-fadeIn">
            {/* Header */}
            <div className="dashboard-header">
                <div>
                    <h1>Helper Dashboard 🔧</h1>
                    <p>Manage your availability and accept requests.</p>
                </div>
            </div>

            {/* Availability Toggle */}
            <div className="mode-toggle">
                <div
                    className={`toggle-switch ${isAvailable ? 'active' : ''}`}
                    onClick={toggleAvailability}
                ></div>
                <div>
                    <h3>{isAvailable ? 'Available' : 'Offline'}</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>
                        {isAvailable ? 'You will receive new request notifications' : 'Toggle to start receiving requests'}
                    </p>
                </div>
            </div>

            {/* Stats */}
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

            {/* Active Jobs */}
            {activeJobs.length > 0 && (
                <div className="active-jobs">
                    <h2>Active Jobs</h2>
                    <div className="requests-list">
                        {activeJobs.map((job) => (
                            <div
                                key={job.id}
                                className="request-card"
                                onClick={() => navigate(`/request/${job.id}`)}
                            >
                                <div className="request-card-header">
                                    <div>
                                        <h4>{job.vehicle_type_name}</h4>
                                        <p style={{ color: 'var(--text-muted)' }}>{job.user_name}</p>
                                    </div>
                                    <span className="badge badge-primary">{job.status.replace('_', ' ')}</span>
                                </div>
                                <div className="request-meta">
                                    <span>📍 View on map</span>
                                    {job.eta_minutes && <span>🕐 {job.eta_minutes} min ETA</span>}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Available Requests */}
            <div className="available-requests">
                <h2>Available Requests</h2>

                {!isAvailable ? (
                    <div className="empty-state card">
                        <div className="empty-icon">🔴</div>
                        <h3>You're Offline</h3>
                        <p>Toggle your availability to see and accept requests.</p>
                    </div>
                ) : isLoading ? (
                    <div className="loading-state">
                        <div className="loader"></div>
                    </div>
                ) : availableRequests.length === 0 ? (
                    <div className="empty-state card">
                        <div className="empty-icon">📭</div>
                        <h3>No requests nearby</h3>
                        <p>New requests will appear here when users need help in your area.</p>
                    </div>
                ) : (
                    <div className="requests-list">
                        {availableRequests.map((request) => (
                            <div key={request.id} className="request-card">
                                <div className="request-card-header">
                                    <div>
                                        <h4>{request.vehicle_type_name}</h4>
                                        <p style={{ color: 'var(--text-muted)' }}>{request.user_name}</p>
                                    </div>
                                    <span className={`badge ${request.urgency === 'emergency' ? 'badge-error' : 'badge-warning'}`}>
                                        {request.urgency}
                                    </span>
                                </div>
                                <div className="request-card-body">
                                    <div className="request-meta">
                                        <span>📍 {request.distance_km?.toFixed(1) || '?'} km away</span>
                                        <span>🕐 {request.eta_minutes || '?'} min</span>
                                    </div>
                                </div>
                                <div className="request-card-footer">
                                    <span style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>
                                        {new Date(request.created_at).toLocaleTimeString()}
                                    </span>
                                    <button
                                        className="btn btn-success"
                                        onClick={() => handleAcceptRequest(request.id)}
                                    >
                                        Accept Request
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default HelperDashboard;
