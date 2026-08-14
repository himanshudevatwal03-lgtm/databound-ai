import { createContext, useContext, useEffect, useState } from "react";
import * as api from "../services/api.js";

/**
 * AuthContext
 *
 * Makes "who is logged in" available to any component via useAuth(),
 * instead of passing user/login/logout down through props everywhere.
 *
 * On mount, if a token is already stored (from a previous session), it
 * verifies that token against GET /api/auth/me rather than trusting it
 * blindly — an expired or tampered token gets cleared automatically.
 */
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // true while we check for an existing session

  useEffect(() => {
    const token = api.getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .getMe()
      .then(setUser)
      .catch(() => api.clearToken())
      .finally(() => setLoading(false));
  }, []);

  async function login(credentials) {
    const data = await api.login(credentials);
    api.setToken(data.access_token);
    setUser(data.user);
    return data.user;
  }

  async function register(details) {
    const data = await api.register(details);
    api.setToken(data.access_token);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    api.clearToken();
    setUser(null);
  }

  const value = { user, loading, login, register, logout, isAuthenticated: !!user };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
