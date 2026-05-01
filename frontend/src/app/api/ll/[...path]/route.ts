const BACKEND_BASE =
  process.env.LORELOUNGE_API_BASE?.replace(/\/$/, "") ?? "http://localhost/api";

function pickHeaders(req: Request) {
  const headers = new Headers();
  const contentType = req.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);

  const accept = req.headers.get("accept");
  if (accept) headers.set("accept", accept);

  const cookie = req.headers.get("cookie");
  if (cookie) headers.set("cookie", cookie);

  const authorization = req.headers.get("authorization");
  if (authorization) headers.set("authorization", authorization);

  return headers;
}

async function proxy(req: Request, ctx: { params: Promise<{ path: string[] }> }) {
  const { path } = await ctx.params;
  const url = new URL(req.url);
  const target = `${BACKEND_BASE}/${path.map(encodeURIComponent).join("/")}${url.search}`;

  let body: BodyInit | undefined = undefined;
  if (req.method !== "GET" && req.method !== "HEAD") {
    const buf = await req.arrayBuffer();
    body = buf.byteLength ? Buffer.from(buf) : undefined;
  }

  const upstream = await fetch(target, {
    method: req.method,
    headers: pickHeaders(req),
    body,
    redirect: "manual",
  });

  // Важно: set-cookie нельзя копировать "как есть" через Headers(upstream.headers),
  // иначе значения могут склеиться и браузер их не применит.
  const headers = new Headers();
  upstream.headers.forEach((value, key) => {
    if (key.toLowerCase() === "set-cookie") return;
    headers.set(key, value);
  });

  for (const c of upstream.headers.getSetCookie()) {
    headers.append("set-cookie", c);
  }

  headers.delete("content-encoding");
  headers.delete("content-length");

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
export const OPTIONS = proxy;

