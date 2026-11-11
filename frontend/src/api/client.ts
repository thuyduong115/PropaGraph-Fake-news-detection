// Client gọi backend. Kiểu dữ liệu sinh từ OpenAPI bằng `npm run gen:api` (backend đang chạy),
// ghi vào src/api/schema.d.ts. Chỉ gọi /api/*, không đọc artifacts trực tiếp (AGENTS.md).

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`/api${path}`, init);
  if (!resp.ok) throw new ApiError(resp.status, await resp.text());
  return (await resp.json()) as T;
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  return apiGet<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
