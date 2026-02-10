import { clearTokens, getRefreshToken, getToken, setTokens } from "@/lib/auth";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type RequestOptions = {
  method?: string;
  body?: unknown;
  auth?: boolean;
};

type ApiErrorResponse = {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
  };
  detail?: string;
};

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  return requestInternal<T>(path, options, true);
}

async function requestInternal<T>(
  path: string,
  options: RequestOptions,
  allowRefreshRetry: boolean,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (options.auth) {
    const token = getToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
    cache: "no-store",
  });

  if (
    response.status === 401 &&
    options.auth &&
    allowRefreshRetry &&
    path !== "/auth/refresh"
  ) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return requestInternal<T>(path, options, false);
    }
  }

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as ApiErrorResponse | null;
    const message = payload?.error?.message ?? payload?.detail ?? `Request failed: ${response.status}`;
    const code = payload?.error?.code;
    throw new Error(code ? `[${code}] ${message}` : message);
  }

  return (await response.json()) as T;
}

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearTokens();
    return false;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
      cache: "no-store",
    });

    if (!response.ok) {
      clearTokens();
      return false;
    }

    const payload = (await response.json()) as {
      access_token: string;
      refresh_token: string;
    };
    setTokens(payload.access_token, payload.refresh_token);
    return true;
  } catch {
    clearTokens();
    return false;
  }
}

export { API_BASE_URL };
