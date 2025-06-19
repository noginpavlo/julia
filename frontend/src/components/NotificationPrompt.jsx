import React, { useEffect } from 'react';
import { useNotification } from '../context/NotificationContext';
import '../assets/css/NotificationPrompt.css';

export default function NotificationPopup() {
  const { notification, setNotification } = useNotification();

  useEffect(() => {
    if (notification) {
      const timeout = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timeout);
    }
  }, [notification]);

  if (!notification) return null;

  return (
    <div className="notification-container">
      <div className={`notification ${notification.type}`}>
        {notification.message}
      </div>
    </div>
  );
}