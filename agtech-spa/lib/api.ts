import { getAccessToken, getRefreshToken, saveAccessToken, clearTokens } from "./auth";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

export class AgTechError extends Error {
  constructor(public readonly apiError: ApiError) {
    super(apiError.message);
    this.name = "AgTechError";
  }
}

async function tryRefreshToken(): Promise<boolean> {
  if (typeof window === "undefined") return false;
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  try {
    const res = await fetch(`${BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refreshToken }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    if (typeof data?.accessToken === "string") {
      saveAccessToken(data.accessToken);
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  skipRefresh = false
): Promise<T> {
  const token = typeof window !== "undefined" ? getAccessToken() : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401 && !skipRefresh && !path.startsWith("/auth/")) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      return request<T>(path, options, true);
    }
    if (typeof window !== "undefined") {
      clearTokens();
      window.location.replace("/login");
    }
    throw new AgTechError({ code: "SESSION_EXPIRED", message: "Sesión expirada" });
  }

  if (!response.ok) {
    let apiError: ApiError = {
      code: "UNKNOWN_ERROR",
      message: `HTTP ${response.status}`,
    };

    try {
      const body = await response.json();
      if (body?.error) {
        apiError = body.error as ApiError;
      }
    } catch {
      // body no es JSON válido, usamos el error genérico
    }

    throw new AgTechError(apiError);
  }

  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string, options?: RequestInit) =>
    request<T>(path, { ...options, method: "GET" }),

  post: <T>(path: string, body: unknown, options?: RequestInit) =>
    request<T>(path, {
      ...options,
      method: "POST",
      body: JSON.stringify(body),
    }),

  put: <T>(path: string, body: unknown, options?: RequestInit) =>
    request<T>(path, {
      ...options,
      method: "PUT",
      body: JSON.stringify(body),
    }),

  delete: <T>(path: string, options?: RequestInit) =>
    request<T>(path, { ...options, method: "DELETE" }),
};
