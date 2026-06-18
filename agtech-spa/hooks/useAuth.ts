"use client";

import { useState, useCallback, useEffect } from "react";
import { api, AgTechError } from "@/lib/api";
import {
  saveTokens,
  clearTokens,
  saveAccessToken,
  getAccessToken,
  getRefreshToken,
} from "@/lib/auth";

interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  expiresIn: number;
}

interface JwtRawPayload {
  exp?: number;
  [key: string]: unknown;
}

interface AuthState {
  isLoading: boolean;
  error: string | null;
}

const MOCK_ENABLED = process.env.NEXT_PUBLIC_MOCK_AUTH === "true";

const MOCK_USER = {
  email: "test@agtechuns.com",
  password: "12345678",
};

function btoaSafe(s: string): string {
  return btoa(s).replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");
}

function createMockToken() {
  const header = { alg: "HS256", typ: "JWT" };
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    sub: "mock-user-001",
    email: MOCK_USER.email,
    role: "ADMIN",
    name: "Usuario de Prueba",
    iat: now,
    exp: now + 86400,
  };
  const accessToken = [
    btoaSafe(JSON.stringify(header)),
    btoaSafe(JSON.stringify(payload)),
    "mocksignature",
  ].join(".");
  return { accessToken, refreshToken: accessToken, expiresIn: 86400 };
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    isLoading: false,
    error: null,
  });
  const [expiresAt, setExpiresAt] = useState<number | null>(null);

  // Lee expiresAt del token guardado al montar (para el caso en que ya había sesión)
  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;
    import("jwt-decode").then(({ jwtDecode }) => {
      try {
        const raw = jwtDecode<JwtRawPayload>(token);
        if (raw.exp) setExpiresAt(raw.exp);
      } catch {}
    });
  }, []);

  const login = useCallback(async (emailUsuario: string, password: string) => {
    setState({ isLoading: true, error: null });

    if (MOCK_ENABLED) {
      await new Promise((r) => setTimeout(r, 800));
      if (emailUsuario === MOCK_USER.email && password === MOCK_USER.password) {
        const tokens = createMockToken();
        saveTokens(tokens.accessToken, tokens.refreshToken);
        window.location.href = "/dashboard";
        return;
      }
      setState({ isLoading: false, error: "CREDENTIALS_INVALID" });
      return;
    }

    try {
      const data = await api.post<LoginResponse>("/auth/login", {
        emailUsuario,
        password,
      });

      saveTokens(data.accessToken, data.refreshToken);
      window.location.href = "/dashboard";
    } catch (err) {
      const message =
        err instanceof AgTechError
          ? err.apiError.code
          : "ERROR_DESCONOCIDO";
      setState({ isLoading: false, error: message });
    }
  }, []);

  const logout = useCallback(() => {
    clearTokens();
    window.location.href = "/login";
  }, []);

  // Renovación proactiva: dispara 10 segundos antes de que expire el token
  useEffect(() => {
    if (!expiresAt || MOCK_ENABLED) return;

    const delay = (expiresAt - 10) - Math.floor(Date.now() / 1000);
    console.log("[Refresh] expiresAt:", expiresAt, "delay calculado:", delay, "segundos");

    if (delay <= 0) {
      console.log("[Refresh] delay <= 0, llamando logout");
      logout();
      return;
    }

    const id = setTimeout(async () => {
      console.log("[Refresh] setTimeout disparado, intentando refresh...");
      const refreshToken = getRefreshToken();
      console.log("[Refresh] refreshToken existe:", !!refreshToken);
      if (!refreshToken) {
        logout();
        return;
      }
      try {
        const data = await api.post<{ accessToken: string }>("/auth/refresh", { refreshToken });
        console.log("[Refresh] éxito, nuevo token recibido");
        saveAccessToken(data.accessToken);
        const { jwtDecode } = await import("jwt-decode");
        const raw = jwtDecode<JwtRawPayload>(data.accessToken);
        if (raw.exp) setExpiresAt(raw.exp);
      } catch (e) {
        console.log("[Refresh] falló:", e);
        logout();
      }
    }, delay * 1000);

    return () => clearTimeout(id);
  }, [expiresAt, logout]);

  return { ...state, login, logout };
}
