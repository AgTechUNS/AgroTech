"use client";

import { createContext, useContext, useState, useCallback, useEffect } from "react";
import { jwtDecode } from "jwt-decode";
import { getAccessToken, clearTokens } from "@/lib/auth";
import { JwtPayload } from "@/lib/types";

interface AuthContextType {
  user: JwtPayload | null;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<JwtPayload | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    if (token) {
      try {
        const decoded = jwtDecode<JwtPayload>(token);
        setUser(decoded);
      } catch {
        setUser(null);
      }
    }
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
    window.location.href = "/login";
  }, []);

  return (
    <AuthContext.Provider value={{ user, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  return useContext(AuthContext);
}
