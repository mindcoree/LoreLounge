"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { llFetchJson } from "@/lib/llApi";

export default function DebugPage() {
  const [path, setPath] = useState("/v1/me");
  const [method, setMethod] = useState<"GET" | "POST">("GET");
  const [form, setForm] = useState(`{}`);
  const [result, setResult] = useState<unknown>(null);
  const [pending, setPending] = useState(false);

  const parsedForm = useMemo(() => {
    try {
      const obj = JSON.parse(form);
      if (!obj || typeof obj !== "object") return null;
      return obj as Record<string, string>;
    } catch {
      return null;
    }
  }, [form]);

  async function run() {
    setPending(true);
    setResult(null);
    try {
      const res = await llFetchJson<unknown>(path, {
        method,
        form: method === "POST" ? parsedForm ?? undefined : undefined,
      });
      setResult(res);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-6 py-12">
      <div className="mb-6">
        <Link className="text-sm text-zinc-600 hover:underline dark:text-zinc-400" href="/">
          ← На главную
        </Link>
      </div>

      <h1 className="text-2xl font-semibold tracking-tight text-black dark:text-zinc-50">
        Debug API
      </h1>
      <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
        Это вызывает Next.js прокси <code className="font-mono">/api/ll*</code> →{" "}
        <code className="font-mono">http://localhost/api*</code> с cookies.
      </p>

      <div className="mt-6 grid gap-3 rounded-2xl border border-black/10 bg-white p-4 dark:border-white/10 dark:bg-zinc-950">
        <div className="grid gap-2 sm:grid-cols-3">
          <label className="grid gap-2">
            <span className="text-xs font-medium text-zinc-600 dark:text-zinc-400">METHOD</span>
            <select
              className="h-10 rounded-xl border border-black/10 bg-white px-3 text-sm text-black dark:border-white/10 dark:bg-black dark:text-zinc-50"
              value={method}
              onChange={(e) => setMethod(e.target.value === "POST" ? "POST" : "GET")}
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
            </select>
          </label>

          <label className="grid gap-2 sm:col-span-2">
            <span className="text-xs font-medium text-zinc-600 dark:text-zinc-400">PATH</span>
            <input
              className="h-10 rounded-xl border border-black/10 bg-white px-3 text-sm text-black dark:border-white/10 dark:bg-black dark:text-zinc-50"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              placeholder="/v1/me"
            />
          </label>
        </div>

        <label className="grid gap-2">
          <span className="text-xs font-medium text-zinc-600 dark:text-zinc-400">
            FORM JSON (только для POST)
          </span>
          <textarea
            className="min-h-28 rounded-xl border border-black/10 bg-white p-3 font-mono text-xs text-black dark:border-white/10 dark:bg-black dark:text-zinc-50"
            value={form}
            onChange={(e) => setForm(e.target.value)}
            spellCheck={false}
          />
          {method === "POST" && parsedForm === null ? (
            <div className="text-xs text-red-600 dark:text-red-400">
              JSON не парсится или не объект.
            </div>
          ) : null}
        </label>

        <div className="flex items-center gap-3">
          <button
            disabled={pending || (method === "POST" && parsedForm === null)}
            onClick={() => void run()}
            className="inline-flex h-10 items-center justify-center rounded-xl bg-black px-4 text-sm font-medium text-white disabled:opacity-60 dark:bg-white dark:text-black"
          >
            {pending ? "Выполняю…" : "Выполнить"}
          </button>
          <Link className="text-sm text-zinc-600 hover:underline dark:text-zinc-400" href="/auth/login">
            login
          </Link>
          <Link className="text-sm text-zinc-600 hover:underline dark:text-zinc-400" href="/me">
            /me
          </Link>
        </div>
      </div>

      <div className="mt-8">
        <div className="text-sm font-medium text-black dark:text-zinc-50">Ответ</div>
        <pre className="mt-2 overflow-auto rounded-2xl border border-black/10 bg-zinc-50 p-4 text-xs text-black dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50">
          {result ? JSON.stringify(result, null, 2) : "—"}
        </pre>
      </div>
    </div>
  );
}

