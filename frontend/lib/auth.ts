const ACCESS_TOKEN_KEY = "secondhand_access_token";
const REFRESH_TOKEN_KEY = "secondhand_refresh_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  setToken(accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearToken(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
}

export function clearTokens(): void {
  clearToken();
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}
