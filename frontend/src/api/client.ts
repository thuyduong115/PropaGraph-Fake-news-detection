// Client gọi backend. Chỉ gọi /api/*, không đọc artifacts trực tiếp (AGENTS.md).
// Phiên đăng nhập là cookie httpOnly cùng origin (dev: proxy Vite, prod: nginx).

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

/** Phát khi API trả 401 để AuthProvider đưa người dùng về trang đăng nhập. */
export const UNAUTHORIZED_EVENT = "propagraph:unauthorized";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`/api${path}`, { credentials: "same-origin", ...init });
  if (!resp.ok) {
    let message = resp.statusText;
    try {
      const body = await resp.json();
      if (typeof body?.detail === "string") message = body.detail;
    } catch {
      /* body không phải JSON */
    }
    if (resp.status === 401 && !path.startsWith("/auth/")) {
      window.dispatchEvent(new Event(UNAUTHORIZED_EVENT));
    }
    throw new ApiError(resp.status, message);
  }
  if (resp.status === 204) return undefined as T;
  return (await resp.json()) as T;
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

export function query(params: Record<string, string | number | null | undefined>): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== null && v !== undefined && v !== "") q.set(k, String(v));
  }
  const s = q.toString();
  return s ? `?${s}` : "";
}
