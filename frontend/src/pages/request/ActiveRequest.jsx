/**
 * Active Request page - Shows status and map for an ongoing request.
 */
import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useRequestStore } from '../../store/requestStore';
import { useChatStore } from '../../store/chatStore';
import { useAuthStore } from '../../store/authStore';
import toast from 'react-hot-toast';
import './Request.css';

function ActiveRequest() {
    const { requestId } = useParams();
    const navigate = useNavigate();
    const { activeRequest, fetchRequest, updateStatus, cancelRequest, isLoading } = useRequestStore();
    const { fetchChatRoom, currentRoom } = useChatStore();
    const { user } = useAuthStore();
    const [ws, setWs] = useState(null);

    useEffect(() => {
        fetchRequest(requestId);
        fetchChatRoom(requestId);

        // Setup WebSocket for real-time updates
        const wsUrl = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}/requests/${requestId}/`;
        const socket = new WebSocket(wsUrl);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'request_update') {
                fetchRequest(requestId);
                toast.success(`Status: ${data.status.replace('_', ' ')}`);
            }
        };

        setWs(socket);

        return () => socket.close();
    }, [requestId]);

    const handleStatusUpdate = async (newStatus) => {
        const result = await updateStatus(requestId, newStatus);
        if (result.success) {
            toast.success(`Status updated to ${newStatus.replace('_', ' ')}`);
        } else {
            toast.error('Failed to update status');
        }
    };

    const handleCancel = async () => {
        if (confirm('Are you sure you want to cancel this request?')) {
            const result = await cancelRequest(requestId);
            if (result.success) {
                toast.success('Request cancelled');
                navigate('/dashboard');
            } else {
                toast.error('Failed to cancel request');
            }
        }
    };

    if (isLoading || !activeRequest) {
        return (
            <div className="loading-state" style={{ height: '50vh' }}>
                <div className="loader"></div>
            </div>
        );
    }

    const isUser = activeRequest.user?.id === user?.id;
    const isHelper = activeRequest.helper?.user?.id === user?.id;

    const getStatusMessage = (status) => {
        const messages = {
            pending: 'Looking for available helpers...',
            searching: 'Searching for nearby helpers...',
            accepted: 'Helper accepted! On the way.',
            en_route: 'Helper is on the way!',
            arrived: 'Helper has arrived!',
            in_progress: 'Service in progress...',
            completed: 'Service completed!',
            cancelled: 'Request was cancelled.',
        };
        return messages[status] || status;
    };

    return (
        <div className="active-request animate-fadeIn">
            <div className="page-header">
                <h1>Request Details</h1>
                <p>{activeRequest.vehicle_type?.name} - {activeRequest.issue_description?.slice(0, 50)}...</p>
            </div>

            <div className="active-request-page">
                {/* Map */}
                <div className="map-container">
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        height: '100%',
                        color: 'var(--text-muted)'
                    }}>
                        🗺️ Map View (Leaflet integration ready)
                    </div>
                </div>

                {/* Status Panel */}
                <div className="request-panel">
                    {/* Status Card */}
                    <div className="status-card">
                        <div className="status-header">
                            <div className="status-indicator">
                                <div className={`status-dot ${activeRequest.status}`}></div>
                                <span style={{ fontWeight: 600 }}>{activeRequest.status.replace('_', ' ')}</span>
                            </div>
                            <span className={`badge ${activeRequest.urgency === 'emergency' ? 'badge-error' : 'badge-warning'}`}>
                                {activeRequest.urgency}
                            </span>
                        </div>
                        <p style={{ color: 'var(--text-secondary)' }}>{getStatusMessage(activeRequest.status)}</p>
                    </div>

                    {/* ETA */}
                    {activeRequest.eta_minutes && activeRequest.status !== 'completed' && (
                        <div className="eta-display">
                            <div className="eta-value">{activeRequest.eta_minutes}</div>
                            <div className="eta-label">minutes ETA</div>
                        </div>
                    )}

                    {/* Helper Info */}
                    {activeRequest.helper && (
                        <div className="status-card">
                            <h3 style={{ marginBottom: 'var(--space-4)' }}>Your Helper</h3>
                            <div className="helper-info">
                                <div className="helper-avatar">
                                    {activeRequest.helper.user?.full_name?.charAt(0) || 'H'}
                                </div>
                                <div className="helper-details">
                                    <h4>{activeRequest.helper.user?.full_name}</h4>
                                    <p>⭐ {activeRequest.helper.rating_avg?.toFixed(1)} • {activeRequest.helper.total_jobs} jobs</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="action-buttons">
                        {currentRoom && (
                            <Link to={`/chat/${currentRoom.id}`} className="btn btn-primary">
                                💬 Chat with {isUser ? 'Helper' : 'User'}
                            </Link>
                        )}

                        {/* Helper actions */}
                        {isHelper && (
                            <>
                                {activeRequest.status === 'accepted' && (
                                    <button className="btn btn-success" onClick={() => handleStatusUpdate('en_route')}>
                                        🚗 Start Driving
                                    </button>
                                )}
                                {activeRequest.status === 'en_route' && (
                                    <button className="btn btn-success" onClick={() => handleStatusUpdate('arrived')}>
                                        📍 I've Arrived
                                    </button>
                                )}
                                {activeRequest.status === 'arrived' && (
                                    <button className="btn btn-success" onClick={() => handleStatusUpdate('in_progress')}>
                                        🔧 Start Service
                                    </button>
                                )}
                                {activeRequest.status === 'in_progress' && (
                                    <button className="btn btn-success" onClick={() => handleStatusUpdate('completed')}>
                                        ✅ Complete Service
                                    </button>
                                )}
                            </>
                        )}

                        {/* Payment button for completed requests */}
                        {activeRequest.status === 'completed' && isUser && (
                            <Link to={`/payment/${requestId}`} className="btn btn-accent">
                                💳 Complete Payment
                            </Link>
                        )}

                        {/* Cancel button */}
                        {!['completed', 'cancelled'].includes(activeRequest.status) && (
                            <button className="btn btn-secondary" onClick={handleCancel}>
                                Cancel Request
                            </button>
                        )}

                        <Link to="/dashboard" className="btn btn-secondary">
                            ← Back to Dashboard
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ActiveRequest;
