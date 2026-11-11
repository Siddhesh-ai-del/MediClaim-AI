export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

export function setToken(t: string) {
  localStorage.setItem("access_token", t);
}

export function clearToken() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export async function api(path: string, opts: RequestInit = {}) {
  const token = getToken();
  const headers: Record<string, string> = { "Content-Type": "application/json", ...(opts.headers as any) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_BASE}/api/v1${path}`, { ...opts, headers });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || res.statusText);
  }
  if (res.status === 204) return null;
  return res.json();
}

export async function login(email: string, password: string) {
  const res = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error("login failed");
  const data = await res.json();
  setToken(data.access_token);
  localStorage.setItem("refresh_token", data.refresh_token);
  return data;
}