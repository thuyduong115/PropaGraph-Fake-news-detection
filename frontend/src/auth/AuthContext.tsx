import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

import { ApiError, UNAUTHORIZED_EVENT, apiGet, apiPost } from "../api/client";
import type { Me } from "../api/types";
import { clearApiCache } from "../api/useApi";

interface AuthValue {
  me: Me | null;
  checking: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    apiGet<Me>("/auth/me")
      .then(setMe)
      .catch(() => setMe(null))
      .finally(() => setChecking(false));
  }, []);

  useEffect(() => {
    const onUnauthorized = () => {
      clearApiCache();
      setMe(null);
    };
    window.addEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
    return () => window.removeEventListener(UNAUTHORIZED_EVENT, onUnauthorized);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const result = await apiPost<Me>("/auth/login", { username, password });
    clearApiCache();
    setMe(result);
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiPost<void>("/auth/logout");
    } catch (err) {
      if (!(err instanceof ApiError)) throw err;
    }
    clearApiCache();
    // tắt đăng nhập (AUTH_REQUIRED=0): vẫn xem được như khách
    const anon = await apiGet<Me>("/auth/me").catch(() => null);
    setMe(anon);
  }, []);

  return (
    <AuthContext.Provider value={{ me, checking, login, logout }}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth phải nằm trong AuthProvider");
  return value;
}
