import type {
  CalculateRequest,
  CalculateResponseWithSession,
  RecalculateRequest,
  SessionDetail,
  SessionSummary,
  TransactionResponse,
} from "./types";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function parseCSV(file: File): Promise<TransactionResponse[]> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch("/api/parse", { method: "POST", body: formData });
  return handleResponse<TransactionResponse[]>(res);
}

export async function calculate(
  req: CalculateRequest
): Promise<CalculateResponseWithSession> {
  const res = await fetch("/api/calculate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
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
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  return handleResponse<CalculateResponseWithSession>(res);
}

export async function downloadCSV(req: CalculateRequest): Promise<Blob> {
  const res = await fetch("/api/report/csv", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`CSV download failed: ${res.statusText}`);
  return res.blob();
}

export async function downloadPDF(req: CalculateRequest): Promise<Blob> {
  const res = await fetch("/api/report/pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`PDF download failed: ${res.statusText}`);
  return res.blob();
}

export async function getHistory(year?: number): Promise<SessionSummary[]> {
  const url = year ? `/api/history?year=${year}` : "/api/history";
  const res = await fetch(url);
  return handleResponse<SessionSummary[]>(res);
}

export async function getAvailableYears(): Promise<number[]> {
  const res = await fetch("/api/history/years");
  return handleResponse<number[]>(res);
}

export async function getSessionDetail(id: number): Promise<SessionDetail> {
  const res = await fetch(`/api/history/${id}`);
  return handleResponse<SessionDetail>(res);
}

export async function getDashboard(sessionId?: number): Promise<import("./types").DashboardData> {
  const url = sessionId ? `/api/dashboard?session_id=${sessionId}` : "/api/dashboard";
  const res = await fetch(url);
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
