"use client";

import { createContext, useContext, ReactNode, useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { getAccessToken } from "@/lib/auth";
import { JwtPayload } from "@/lib/types";

interface AuthContextValue {
  user: JwtPayload | null;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function decodeUser(): JwtPayload | null {
  const token = getAccessToken();
  if (!token) return null;
  try {
    const base64 = token.split(".")[1];
    const json = atob(base64.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json) as JwtPayload;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const { isLoading, error, login, logout } = useAuth();
  const [user, setUser] = useState<JwtPayload | null>(null);

  useEffect(() => {
    setUser(decodeUser());
  }, [isLoading]);

  return (
    <AuthContext.Provider value={{ user, isLoading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuthContext debe usarse dentro de un AuthProvider");
  return ctx;
}
