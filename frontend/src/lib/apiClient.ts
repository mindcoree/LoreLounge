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

const inFlightRequests = new Map<string, Promise<any>>();
const requestCache = new Map<string, { result: any; expiresAt: number }>();

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
  const method = init?.method?.toUpperCase() || "GET";
  
  const cacheKey = !isServer && method === "GET" ? url : null;

  if (cacheKey) {
    const cached = requestCache.get(cacheKey);
    if (cached && cached.expiresAt > Date.now()) {
      return Promise.resolve(cached.result);
    }
    if (inFlightRequests.has(cacheKey)) {
      return inFlightRequests.get(cacheKey);
    }
  }

  const performFetch = async (): Promise<ApiResult<T>> => {
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
    let finalResult: ApiResult<T>;
    
    if (res.ok) {
      finalResult = { ok: true, status: res.status, data: raw as T, raw };
      if (cacheKey) {
        requestCache.set(cacheKey, { result: finalResult, expiresAt: Date.now() + 2000 });
      }
    } else {
      const error = extractDetail(raw) ?? `HTTP ${res.status}`;
      finalResult = { ok: false, status: res.status, error, raw };
    }

    return finalResult;
  };

  const promise = performFetch();

  if (cacheKey) {
    inFlightRequests.set(cacheKey, promise);
    promise.finally(() => {
      if (inFlightRequests.get(cacheKey) === promise) {
        inFlightRequests.delete(cacheKey);
      }
    });
  }

  return promise;
}