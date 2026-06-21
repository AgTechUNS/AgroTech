"use client";

import { useState, useCallback } from "react";
import { clearTokens } from "@/lib/auth";
import { loginApi } from "@/lib/services/auth";
import { saveTokens } from "@/lib/auth";

interface AuthState {
  isLoading: boolean;
  error: string | null;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    isLoading: false,
    error: null,
  });

  const login = useCallback(async (emailUsuario: string, password: string) => {
    setState({ isLoading: true, error: null });

    try {
      const data = await loginApi(emailUsuario, password);
      saveTokens(data.accessToken, data.refreshToken);
      window.location.href = "/dashboard";
    } catch (err) {
      const message = err instanceof Error ? err.message : "ERROR_DESCONOCIDO";
      setState({ isLoading: false, error: message });
    }
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    window.location.href = "/login";
  }, []);

  return { ...state, login, logout };
}
