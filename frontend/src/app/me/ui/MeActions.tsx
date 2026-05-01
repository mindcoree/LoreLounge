"use client";

import { useState } from "react";
import { llFetchJson } from "@/lib/llApi";

export default function MeActions() {
  const [pending, setPending] = useState(false);
  const [last, setLast] = useState<unknown>(null);

  async function refresh() {
    setPending(true);
    try {
      const res = await llFetchJson<unknown>("/auth/me", { method: "GET" });
      setLast(res);
    } finally {
      setPending(false);
    }
  }

  async function logout() {
    setPending(true);
    try {
      const res = await llFetchJson<void>("/auth/logout", { method: "POST" });
      setLast(res);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex items-center gap-2">
      <button
        disabled={pending}
        onClick={() => void refresh()}
        className="inline-flex h-10 items-center justify-center rounded-xl border border-black/10 bg-white px-4 text-sm text-black disabled:opacity-60 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50"
      >
        Обновить
      </button>
      <button
        disabled={pending}
        onClick={() => void logout()}
        className="inline-flex h-10 items-center justify-center rounded-xl bg-black px-4 text-sm font-medium text-white disabled:opacity-60 dark:bg-white dark:text-black"
      >
        Logout
      </button>
      {last ? (
        <details className="hidden sm:block">
          <summary className="cursor-pointer select-none text-xs text-zinc-600 dark:text-zinc-400">
            last
          </summary>
          <pre className="mt-2 max-w-[520px] overflow-auto rounded-xl border border-black/10 bg-zinc-50 p-3 text-[11px] text-black dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50">
            {JSON.stringify(last, null, 2)}
          </pre>
        </details>
      ) : null}
    </div>
  );
}

