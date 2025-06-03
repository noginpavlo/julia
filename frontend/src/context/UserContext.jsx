import React, { createContext, useState, useContext } from 'react';

const UserContext = createContext();

export function UserProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null);
  const [username, setUsername] = useState(null);

  const logout = () => {
    setAccessToken(null);
    setUsername(null);
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