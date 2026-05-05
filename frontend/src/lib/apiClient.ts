export type ApiResult<T> =
  | { ok: true; status: number; data: T; raw: unknown }
  | { ok: false; status: number; error: string; raw: unknown };

function extractDetail(raw: unknown): string | null {
  if (!raw || typeof raw !== "object") return null;
  if (!("detail" in raw)) return null;
  const detail = (raw as Record<string, unknown>).detail;
  return typeof detail === "string" ? detail : null;
}

async function parseJsonSafe(res: Response): Promise<unknown> {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function apiFetchJson<T>(
  path: string,
  init?: RequestInit & { form?: Record<string, string> },
): Promise<ApiResult<T>> {
  const isServer = typeof window === "undefined";
  const baseUrl = isServer
    ? process.env.LORELOUNGE_API_BASE?.replace(/\/$/, "") ?? "http://krakend:8080/api"
    : "/api";

  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const url = `${baseUrl}${cleanPath}`;

  const headers = new Headers(init?.headers);
  let cookieHeader: string | undefined;

  if (isServer) {
    try {
      const { cookies } = await import("next/headers");
      const cookieStore = await cookies();
      const cookieString = cookieStore
        .getAll()
        .map(({ name, value }) => `${name}=${value}`)
        .join("; ");
      if (cookieString) {
        headers.set("cookie", cookieString);
        cookieHeader = cookieString;
      }
    } catch {
      // Игнорируем ошибки
    }
  }

  let body = init?.body;

  if (init?.form) {
    body = new URLSearchParams(init.form);
    headers.set("content-type", "application/x-www-form-urlencoded;charset=UTF-8");
  } else if (body && typeof body === "string" && !headers.has("content-type")) {
    headers.set("content-type", "application/json");
  }

  const doFetch = async () =>
    fetch(url, {
      ...init,
      headers,
      body,
      credentials: "include",
    });

  let res = await doFetch();

  if (
    res.status === 401 &&
    !isServer &&
    cleanPath !== "/auth/refresh" &&
    cleanPath !== "/auth/login"
  ) {
    const refreshHeaders = new Headers();
    if (cookieHeader) refreshHeaders.set("cookie", cookieHeader);

    const refreshRes = await fetch(`${baseUrl}/auth/refresh`, {
      method: "POST",
      headers: refreshHeaders,
      credentials: "include",
    });

    if (refreshRes.ok) {
      res = await doFetch();
    }
  }

  const raw = await parseJsonSafe(res);
  if (res.ok) return { ok: true, status: res.status, data: raw as T, raw };

  const error = extractDetail(raw) ?? `HTTP ${res.status}`;

  return { ok: false, status: res.status, error, raw };
}