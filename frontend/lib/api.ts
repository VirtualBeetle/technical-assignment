// All requests are same-origin, relative paths (e.g. "/api/auth/login").
// next.config.js rewrites /api/* server-side to wherever the backend
// actually lives (see its comment for why), so the browser never needs to
// know the backend's URL and there is no cross-origin request in play.

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("senus_token");
}

export function setToken(token: string) {
  window.localStorage.setItem("senus_token", token);
}

export function clearToken() {
  window.localStorage.removeItem("senus_token");
}

async function request(path: string, options: RequestInit = {}) {
  const token = getToken();
  const res = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Request failed (${res.status}): ${text}`);
  }
  return res.json();
}

export async function login(email: string, password: string) {
  const data = await request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  return data;
}

export const api = {
  company: () => request("/api/company"),
  directors: () => request("/api/company/directors"),
  periods: () => request("/api/company/periods"),
  metrics: (category: string, period?: string) =>
    request(`/api/metrics/${category}${period ? `?period=${period}` : ""}`),
  insights: (period: string) => request(`/api/insights?period=${period}`),
};

export type Period = {
  period_key: string;
  label: string;
  period_type: string;
  start_date: string;
  end_date: string;
  consolidation: string;
  audited: boolean;
  source_document: string | null;
};
