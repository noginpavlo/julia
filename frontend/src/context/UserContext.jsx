import React, {
  createContext,
  useState,
  useEffect,
  useContext,
  useRef,
} from "react";

const UserContext = createContext();

export function UserProvider({ children }) {
  const [accessToken, setAccessTokenState] = useState(null);
  const [username, setUsernameState] = useState(null);
  const refreshIntervalRef = useRef(null);

  // Helpers for localStorage
  const saveToStorage = (key, value) =>
    value ? localStorage.setItem(key, value) : localStorage.removeItem(key);

  const loadFromStorage = (key) => localStorage.getItem(key);

  // Load initial state from localStorage
  useEffect(() => {
    const token = loadFromStorage("accessToken");
    const name = loadFromStorage("username");

    if (token) setAccessTokenState(token);
    if (name) setUsernameState(name);
  }, []);

  // Token refresh effect
  useEffect(() => {
    if (!accessToken) return;

    const refreshToken = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/users/token/refresh/", {
          method: "POST",
          credentials: "include",
        });

        if (response.ok) {
          const data = await response.json();
          setAccessToken(data.access);
        } else {
          console.warn("Refresh token expired or invalid");
          logout();
        }
      } catch (err) {
        console.error("Network error while refreshing token:", err);
        logout();
      }
    };

    // Refresh every 2 minutes
    refreshIntervalRef.current = setInterval(refreshToken, 20 * 60 * 1000);

    if (import.meta.env.DEV) {
      console.log("🔁 Token refresh interval started");
    }

    return () => {
      clearInterval(refreshIntervalRef.current);
      if (import.meta.env.DEV) {
        console.log("🧹 Cleared token refresh interval");
      }
    };
  }, [accessToken]);

  const setAccessToken = (token) => {
    saveToStorage("accessToken", token);
    setAccessTokenState(token);
  };

  const setContextUsername = (name) => {
    saveToStorage("username", name);
    setUsernameState(name);
  };

  const logout = () => {
    setAccessToken(null);
    setContextUsername(null);

    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
      refreshIntervalRef.current = null;
    }

    if (import.meta.env.DEV) {
      console.log("🚪 Logged out and cleared user data");
    }
  };

  const isLoggedIn = !!accessToken;

  return (
    <UserContext.Provider
      value={{
        accessToken,
        setAccessToken,
        username,
        setContextUsername,
        isLoggedIn,
        logout,
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
