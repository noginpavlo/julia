import React, { createContext, useState, useEffect, useContext, useRef } from 'react';

const UserContext = createContext();

export function UserProvider({ children }) {
  const [accessToken, setAccessTokenState] = useState(null);
  const [username, setUsernameState] = useState(null);
  const refreshIntervalRef = useRef(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('accessToken');
    if (storedToken) {
      const payload = parseJwt(storedToken);
      const isExpired = payload?.exp * 1000 < Date.now();

      if (!isExpired) {
        setAccessToken(storedToken);
        setUsernameState(payload?.username || null);
      } else {
        console.warn('Stored token is expired');
      }
    }
  }, []);

  useEffect(() => {
    const refreshAccessToken = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/users/token/refresh/', {
          method: 'POST',
          credentials: 'include',
        });

        if (response.ok) {
          const data = await response.json();
          setAccessToken(data.access);
        } else {
          console.warn('Refresh token expired or invalid');
          logout();
        }
      } catch (err) {
        console.error('Network error while refreshing access token', err);
        logout();
      }
    };

    refreshIntervalRef.current = setInterval(refreshAccessToken, 1 * 60 * 1000);

    return () => clearInterval(refreshIntervalRef.current);
  }, []);

  const setAccessToken = (token) => {
    localStorage.setItem('accessToken', token);
    setAccessTokenState(token);

    const payload = parseJwt(token);
    setUsernameState(payload?.username || null);
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    setAccessTokenState(null);
    setUsernameState(null);

    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
    }
  };

  const isLoggedIn = !!accessToken;

  return (
    <UserContext.Provider value={{ accessToken, setAccessToken, username, isLoggedIn, logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}

function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch {
    return null;
  }
}
