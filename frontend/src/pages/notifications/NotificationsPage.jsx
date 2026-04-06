/**
 * Notifications Page - View and manage notifications.
 */
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotificationStore } from '../../store/notificationStore';
import './Notifications.css';

function NotificationsPage() {
    const navigate = useNavigate();
    const { notifications, fetchNotifications, markAsRead, markAllAsRead, isLoading } = useNotificationStore();

    useEffect(() => {
        fetchNotifications();
    }, []);

    const handleNotificationClick = (notification) => {
        if (!notification.is_read) {
            markAsRead(notification.id);
        }

        // Navigate based on notification type
        if (notification.request) {
            navigate(`/request/${notification.request}`);
        }
    };

    const getIconForType = (type) => {
        const icons = {
            new_request: '🔔',
            request_accepted: '✅',
            helper_en_route: '🚗',
            helper_arrived: '📍',
            service_completed: '🎉',
            request_cancelled: '❌',
            new_message: '💬',
            payment_received: '💰',
            rating_received: '⭐',
            system: '📢',
        };
        return icons[type] || '📢';
    };

    return (
        <div className="notifications-page animate-fadeIn">
            <div className="page-header">
                <div>
                    <h1>🔔 Notifications</h1>
                    <p>Stay updated with your requests and messages.</p>
                </div>
                {notifications.some((n) => !n.is_read) && (
                    <button className="btn btn-secondary" onClick={markAllAsRead}>
                        Mark All Read
                    </button>
                )}
            </div>

            {isLoading ? (
                <div className="loading-state">
                    <div className="loader"></div>
                </div>
            ) : notifications.length === 0 ? (
                <div className="empty-state card">
                    <div className="empty-icon">📭</div>
                    <h3>No notifications</h3>
                    <p>You're all caught up!</p>
                </div>
            ) : (
                <div className="notifications-list">
                    {notifications.map((notification) => (
                        <div
                            key={notification.id}
                            className={`notification-item card ${!notification.is_read ? 'unread' : ''}`}
                            onClick={() => handleNotificationClick(notification)}
                        >
                            <div className="notification-icon">
                                {getIconForType(notification.notification_type)}
                            </div>
                            <div className="notification-content">
                                <h4>{notification.title}</h4>
                                <p>{notification.body}</p>
                                <span className="notification-time">
                                    {new Date(notification.created_at).toLocaleString()}
                                </span>
                            </div>
                            {!notification.is_read && <div className="unread-dot"></div>}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default NotificationsPage;
