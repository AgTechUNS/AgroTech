const KEYS = {
  ACCESS_TOKEN: "accessToken",
  REFRESH_TOKEN: "refreshToken",
} as const;

export function saveTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEYS.ACCESS_TOKEN, accessToken);
  localStorage.setItem(KEYS.REFRESH_TOKEN, refreshToken);
  // Sincroniza con cookie para que el middleware (Edge Runtime) pueda leerlo
  document.cookie = "accessToken=1; path=/; SameSite=Lax";
}

export function saveAccessToken(accessToken: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEYS.ACCESS_TOKEN, accessToken);
  document.cookie = "accessToken=1; path=/; SameSite=Lax";
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(KEYS.ACCESS_TOKEN);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(KEYS.REFRESH_TOKEN);
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(KEYS.ACCESS_TOKEN);
  localStorage.removeItem(KEYS.REFRESH_TOKEN);
  document.cookie = "accessToken=; path=/; max-age=0";
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return Boolean(getAccessToken());
}
