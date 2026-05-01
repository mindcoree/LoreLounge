import Link from "next/link";
import { cookies } from "next/headers";
import MeActions from "./ui/MeActions";

async function fetchMe() {
  const cookieStore = await cookies();
  const cookie = cookieStore
    .getAll()
    .map(({ name, value }) => `${name}=${value}`)
    .join("; ");

  // Важно: это выполняется на сервере (в контейнере frontend), поэтому
  // можем обращаться к самому Next.js по docker hostname.
  const res = await fetch("http://frontend:3000/api/ll/v1/me", {
    method: "GET",
    headers: {
      cookie,
      accept: "application/json",
    },
    cache: "no-store",
  });

  const text = await res.text();
  let raw: unknown = null;
  try {
    raw = text ? JSON.parse(text) : null;
  } catch {
    raw = text;
  }

  return { ok: res.ok, status: res.status, raw };
}

export default async function MePage() {
  const me = await fetchMe();

  return (
    <div className="mx-auto w-full max-w-2xl px-6 py-12">
      <div className="mb-6 flex items-center justify-between gap-4">
        <Link className="text-sm text-zinc-600 hover:underline dark:text-zinc-400" href="/">
          ← На главную
        </Link>
        <MeActions />
      </div>

      <h1 className="text-2xl font-semibold tracking-tight text-black dark:text-zinc-50">/me</h1>
      <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
        Серверный запрос с пробросом cookie. Кнопки справа делают клиентский fetch.
      </p>

      <pre className="mt-6 overflow-auto rounded-2xl border border-black/10 bg-zinc-50 p-4 text-xs text-black dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50">
        {JSON.stringify(me, null, 2)}
      </pre>
    </div>
  );
}

