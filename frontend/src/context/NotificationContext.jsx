import React, { createContext, useContext, useEffect, useState } from 'react';
import { useUser } from '../context/UserContext.jsx';

const NotificationContext = createContext();

export function useNotification() {
  return useContext(NotificationContext);
}

export function NotificationProvider({ children }) {
  const { accessToken } = useUser();
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    if (!accessToken) return; // Don't open socket without token

    // Force http/ws protocols for development/local usage
    const backendHost =
      process.env.NODE_ENV === 'development'
        ? 'localhost:8000'
        : window.location.host;

    // Force http for backendHost URL if needed:
    // (usually window.location.host is host:port, so just use it directly)
    const httpUrl = `http://${backendHost}`;

    // Force ws for websocket
    const wsUrl = `ws://${backendHost}/ws/cards/`;

    // Use the access token as a subprotocol
    const socket = new WebSocket(wsUrl, [`access-token.${accessToken}`]);

    socket.onopen = () => console.log('✅ WebSocket connected with subprotocol token');
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.message && data.type) {
          setNotification({ message: data.message, type: data.type });
        }
      } catch (e) {
        console.error('WebSocket message parse error', e);
      }
    };
    socket.onerror = (error) => console.error('❌ WebSocket error:', error);
    socket.onclose = () => console.warn('⚠️ WebSocket closed');

    return () => socket.close();
  }, [accessToken]);

  return (
    <NotificationContext.Provider value={{ notification, setNotification }}>
      {children}
    </NotificationContext.Provider>
  );
}
