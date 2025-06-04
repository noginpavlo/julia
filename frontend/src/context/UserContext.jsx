import React, { createContext, useState, useEffect, useContext } from 'react';

const UserContext = createContext();

export function UserProvider({ children }) {
  const [accessToken, setAccessTokenState] = useState(null);
  const [username, setUsernameState] = useState(null);

  // ✅ Restore token and username on page load (no refresh)
  useEffect(() => {
    const storedToken = localStorage.getItem('accessToken');
    const storedUsername = localStorage.getItem('username');
    if (storedToken) setAccessTokenState(storedToken);
    if (storedUsername) setUsernameState(storedUsername);
  }, []);

  // ✅ Start periodic refresh loop, but don't refresh immediately
  useEffect(() => {
    const refreshAccessToken = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/users/token/refresh/', {
          method: 'POST',
          credentials: 'include', // Send HTTP-only refresh token
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

    const interval = setInterval(refreshAccessToken, 10 * 60 * 1000); // 🔁 auto-refresh every 10 minutes

    return () => clearInterval(interval); // Cleanup on unmount
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
