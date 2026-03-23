import type {
  AuthResponse,
  CalculateRequest,
  CalculateResponseWithSession,
  RecalculateRequest,
  SessionDetail,
  SessionSummary,
  TransactionResponse,
} from "./types";

// ── トークン管理 ──
const TOKEN_KEY = "zeitan_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

// ── 共通レスポンスハンドラ ──
async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// ── 認証API ──
export async function register(email: string, password: string, name?: string): Promise<AuthResponse> {
  const res = await fetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name }),
  });
  const data = await handleResponse<AuthResponse>(res);
  setToken(data.access_token);
  return data;
}

export async function login(email: string, password: string): Promise<AuthResponse> {
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await handleResponse<AuthResponse>(res);
  setToken(data.access_token);
  return data;
}

export async function getMe(): Promise<import("./types").UserResponse> {
  const res = await fetch("/api/auth/me", { headers: authHeaders() });
  return handleResponse<import("./types").UserResponse>(res);
}

export function logout(): void {
  removeToken();
}

// ── 既存API（認証ヘッダー自動付与） ──
export async function parseCSV(file: File): Promise<TransactionResponse[]> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch("/api/parse", { method: "POST", body: formData, headers: authHeaders() });
  return handleResponse<TransactionResponse[]>(res);
}

export async function calculate(
  req: CalculateRequest
): Promise<CalculateResponseWithSession> {
  const res = await fetch("/api/calculate", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(req),
  });
  return handleResponse<CalculateResponseWithSession>(res);
}

export async function recalculate(
  sessionId: number,
  req: RecalculateRequest
): Promise<CalculateResponseWithSession> {
  const res = await fetch(`/api/recalculate/${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(req),
  });
  return handleResponse<CalculateResponseWithSession>(res);
}

export async function downloadCSV(req: CalculateRequest): Promise<Blob> {
  const res = await fetch("/api/report/csv", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`CSV download failed: ${res.statusText}`);
  return res.blob();
}

export async function downloadPDF(req: CalculateRequest): Promise<Blob> {
  const res = await fetch("/api/report/pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`PDF download failed: ${res.statusText}`);
  return res.blob();
}

export async function getHistory(year?: number): Promise<SessionSummary[]> {
  const url = year ? `/api/history?year=${year}` : "/api/history";
  const res = await fetch(url, { headers: authHeaders() });
  return handleResponse<SessionSummary[]>(res);
}

export async function getAvailableYears(): Promise<number[]> {
  const res = await fetch("/api/history/years", { headers: authHeaders() });
  return handleResponse<number[]>(res);
}

export async function getPortfolio(): Promise<import("./types").PortfolioData> {
  const res = await fetch("/api/portfolio", { headers: authHeaders() });
  return handleResponse<import("./types").PortfolioData>(res);
}

export async function getSessionDetail(id: number): Promise<SessionDetail> {
  const res = await fetch(`/api/history/${id}`, { headers: authHeaders() });
  return handleResponse<SessionDetail>(res);
}

export async function getAlerts(sessionId: number): Promise<import("./types").AlertsResponse> {
  const res = await fetch(`/api/alerts/${sessionId}`, { headers: authHeaders() });
  return handleResponse<import("./types").AlertsResponse>(res);
}

export async function getDashboard(sessionId?: number): Promise<import("./types").DashboardData> {
  const url = sessionId ? `/api/dashboard?session_id=${sessionId}` : "/api/dashboard";
  const res = await fetch(url, { headers: authHeaders() });
  return handleResponse<import("./types").DashboardData>(res);
}

export function triggerDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
