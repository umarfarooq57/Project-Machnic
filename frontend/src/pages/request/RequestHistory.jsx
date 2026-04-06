/**
 * Request History page - List of past requests.
 */
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useRequestStore } from '../../store/requestStore';
import './Request.css';

function RequestHistory() {
    const navigate = useNavigate();
    const { requests, fetchUserRequests, isLoading } = useRequestStore();

    useEffect(() => {
        fetchUserRequests();
    }, [fetchUserRequests]);

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

    return (
        <div className="request-history animate-fadeIn">
            <div className="page-header">
                <h1>Request History</h1>
                <p>View all your past and current service requests.</p>
            </div>

            {isLoading ? (
                <div className="loading-state">
                    <div className="loader"></div>
                </div>
            ) : requests.length === 0 ? (
                <div className="empty-state card">
                    <div className="empty-icon">📭</div>
                    <h3>No requests yet</h3>
                    <p>Your request history will appear here.</p>
                </div>
            ) : (
                <div className="request-history-list">
                    {requests.map((request) => (
                        <div
                            key={request.id}
                            className="history-item"
                            onClick={() => navigate(`/request/${request.id}`)}
                        >
                            <div className="history-header">
                                <div>
                                    <h3>{request.vehicle_type_name}</h3>
                                    <p style={{ color: 'var(--text-muted)' }}>
                                        {new Date(request.created_at).toLocaleDateString('en-US', {
                                            year: 'numeric',
                                            month: 'long',
                                            day: 'numeric',
                                            hour: '2-digit',
                                            minute: '2-digit',
                                        })}
                                    </p>
                                </div>
                                <span className={`badge ${getStatusColor(request.status)}`}>
                                    {request.status.replace('_', ' ')}
                                </span>
                            </div>
                            <div className="history-meta">
                                {request.helper_name && <span>🔧 {request.helper_name}</span>}
                                {request.eta_minutes && <span>🕐 {request.eta_minutes} min</span>}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default RequestHistory;
