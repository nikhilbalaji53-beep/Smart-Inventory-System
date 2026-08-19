import React, { useState, useEffect } from 'react';

const NotificationCenter = ({ isOpen, onClose }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const API_BASE_URL = 'http://localhost:8000';

  const getAuthToken = () => localStorage.getItem('token');
  const getAuthHeader = () => ({
    'Authorization': `Bearer ${getAuthToken()}`,
    'Content-Type': 'application/json'
  });

  // Fetch notifications
  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${API_BASE_URL}/notifications/?limit=20`,
        { headers: getAuthHeader() }
      );
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch unread count
  const fetchUnreadCount = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/notifications/unread-count`,
        { headers: getAuthHeader() }
      );
      
      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Error fetching unread count:', error);
    }
  };

  // Mark notification as read
  const markAsRead = async (notificationId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/notifications/${notificationId}/read`,
        {
          method: 'PATCH',
          headers: getAuthHeader()
        }
      );
      
      if (response.ok) {
        fetchNotifications();
        fetchUnreadCount();
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  // Mark all as read
  const markAllAsRead = async () => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/notifications/read-all`,
        {
          method: 'PATCH',
          headers: getAuthHeader()
        }
      );
      
      if (response.ok) {
        fetchNotifications();
        fetchUnreadCount();
      }
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  // Delete notification
  const deleteNotification = async (notificationId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/notifications/${notificationId}`,
        {
          method: 'DELETE',
          headers: getAuthHeader()
        }
      );
      
      if (response.ok) {
        fetchNotifications();
        fetchUnreadCount();
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  // Refresh notifications every 30 seconds (polling)
  useEffect(() => {
    if (isOpen) {
      fetchNotifications();
      fetchUnreadCount();
      
      const interval = setInterval(() => {
        fetchUnreadCount();
      }, 30000);
      
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return '#f44336';
      case 'WARNING':
        return '#ff9800';
      case 'INFO':
        return '#2196F3';
      default:
        return '#757575';
    }
  };

  const getAlertIcon = (alertType) => {
    switch (alertType) {
      case 'LOW_STOCK':
        return '📉';
      case 'EXPIRY':
        return '⏰';
      case 'DEMAND':
        return '📈';
      case 'EXPIRED':
        return '💀';
      default:
        return '🔔';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="notification-center">
      <div className="notification-overlay" onClick={onClose}></div>
      
      <div className="notification-panel">
        <div className="notification-header">
          <h2>🔔 Notifications</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="notification-toolbar">
          <span className="unread-badge">
            {unreadCount > 0 ? `${unreadCount} Unread` : 'All Read'}
          </span>
          {unreadCount > 0 && (
            <button 
              className="mark-all-btn"
              onClick={markAllAsRead}
            >
              Mark All as Read
            </button>
          )}
        </div>

        <div className="notification-list">
          {loading ? (
            <div className="loading">Loading notifications...</div>
          ) : notifications.length === 0 ? (
            <div className="empty-state">
              <p>✨ No notifications yet</p>
              <p className="text-sm">You're all caught up!</p>
            </div>
          ) : (
            notifications.map((notification) => (
              <div
                key={notification.id}
                className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
                style={{
                  borderLeftColor: getSeverityColor(notification.severity)
                }}
              >
                <div className="notification-icon">
                  {getAlertIcon(notification.alert_type)}
                </div>

                <div className="notification-content">
                  <div className="notification-title">
                    {notification.title}
                  </div>
                  <div className="notification-message">
                    {notification.message}
                  </div>
                  <div className="notification-meta">
                    <span className="severity-badge" style={{
                      backgroundColor: getSeverityColor(notification.severity)
                    }}>
                      {notification.severity}
                    </span>
                    <span className="timestamp">
                      {new Date(notification.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                <div className="notification-actions">
                  {!notification.is_read && (
                    <button
                      className="action-btn mark-read"
                      onClick={() => markAsRead(notification.id)}
                      title="Mark as read"
                    >
                      ✓
                    </button>
                  )}
                  <button
                    className="action-btn delete"
                    onClick={() => deleteNotification(notification.id)}
                    title="Delete"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default NotificationCenter;
