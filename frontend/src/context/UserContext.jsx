import React, { createContext, useState, useEffect, useContext, useRef } from 'react';

const UserContext = createContext();

export function UserProvider({ children }) {
  const [accessToken, setAccessTokenState] = useState(null);
  const [username, setUsernameState] = useState(null);
  const refreshIntervalRef = useRef(null); // 🆕 Ref to hold interval ID

  useEffect(() => {
    const storedToken = localStorage.getItem('accessToken');
    const storedUsername = localStorage.getItem('username');
    if (storedToken) setAccessTokenState(storedToken);
    if (storedUsername) setUsernameState(storedUsername);
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
          console.warn("Refresh token expired or invalid");
          logout();
        }
      } catch (err) {
        console.error("Network error while refreshing access token", err);
        logout();
      }
    };

    refreshIntervalRef.current = setInterval(refreshAccessToken, 10 * 60 * 1000);

    return () => clearInterval(refreshIntervalRef.current); // Clear on unmount
  }, []);

  const setAccessToken = (token) => {
    localStorage.setItem('accessToken', token);
    setAccessTokenState(token);
  };

  const setUsername = (name) => {
    localStorage.setItem('username', name);
    setUsernameState(name);
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('username');
    setAccessTokenState(null);
    setUsernameState(null);

    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
    }
  };

  return (
    <UserContext.Provider value={{ accessToken, setAccessToken, username, setUsername, logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
