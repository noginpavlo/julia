import React, { createContext, useContext, useEffect, useState } from 'react';
import { useUser } from '../context/UserContext.jsx';

const NotificationContext = createContext();

export function useNotification() {
  return useContext(NotificationContext);
}

export function NotificationProvider({ children }) {
  const { accessToken } = useUser();
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    if (!accessToken) return;

    const backendHost =
      process.env.NODE_ENV === 'development'
        ? 'localhost:8000'
        : window.location.host;

    const wsUrl = `ws://${backendHost}/ws/cards/`;
    const socket = new WebSocket(wsUrl, [`access-token.${accessToken}`]);

    socket.onopen = () => console.log('✅ WebSocket connected');
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const content = data.content || data; // <- 👈 Fix here

        if (content && content.message && content.type) {
          console.log('WebSocket message content:', content);

          const { message, type } = content;

          let notifType = 'info';
          if (type === 'card_created') notifType = 'success';
          else if (type === 'word_not_found' || type === 'exception') notifType = 'error';

          addNotification({ message, type: notifType });
        } else {
          console.log('WebSocket message missing expected keys:', data);
        }
      } catch (e) {
        console.error('WebSocket message parse error', e);
      }
    };

    socket.onerror = (error) => console.error('❌ WebSocket error:', error);
    socket.onclose = () => console.warn('⚠️ WebSocket closed');

    return () => socket.close();
  }, [accessToken]);

  const addNotification = ({ message, type }) => {
  const id = Date.now() + Math.random();

  const notification = {
        id,
        message,
        type,
      };

      setNotifications((prev) => [...prev, notification]);

      // Auto-remove after 5 seconds
      setTimeout(() => {
        removeNotification(id);
      }, 5000);
    };

  const removeNotification = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        addNotification,
        removeNotification,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
}
