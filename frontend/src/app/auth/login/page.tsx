"use client";

import Link from "next/link";
import { useState } from "react";
import { llFetchJson } from "@/lib/llApi";

type TokenInfo = { access: string; refresh: string };

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [result, setResult] = useState<unknown>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setPending(true);
    setResult(null);
    try {
      const res = await llFetchJson<TokenInfo>("/auth/login", {
        method: "POST",
        form: { email, password },
      });
      setResult(res);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-xl px-6 py-12">
      <div className="mb-6">
        <Link className="text-sm text-zinc-600 hover:underline dark:text-zinc-400" href="/">
          ← На главную
        </Link>
      </div>

      <h1 className="text-2xl font-semibold tracking-tight text-black dark:text-zinc-50">Вход</h1>
      <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
        Отправляет форму на <code className="font-mono">/api/auth/login</code> и получает cookie.
      </p>

      <form onSubmit={onSubmit} className="mt-6 grid gap-4">
        <label className="grid gap-2">
          <span className="text-sm font-medium text-black dark:text-zinc-50">Email</span>
          <input
            className="h-11 rounded-xl border border-black/10 bg-white px-4 text-black outline-none ring-0 focus:border-black/20 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            inputMode="email"
            required
          />
        </label>

        <label className="grid gap-2">
          <span className="text-sm font-medium text-black dark:text-zinc-50">Пароль</span>
          <input
            className="h-11 rounded-xl border border-black/10 bg-white px-4 text-black outline-none ring-0 focus:border-black/20 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            autoComplete="current-password"
            required
          />
        </label>

        <div className="flex items-center gap-3">
          <button
            disabled={pending}
            className="inline-flex h-11 items-center justify-center rounded-xl bg-black px-5 text-sm font-medium text-white disabled:opacity-60 dark:bg-white dark:text-black"
            type="submit"
          >
            {pending ? "Входим…" : "Войти"}
          </button>
          <Link className="text-sm text-zinc-600 hover:underline dark:text-zinc-400" href="/auth/register">
            Регистрация
          </Link>
          <Link className="text-sm text-zinc-600 hover:underline dark:text-zinc-400" href="/me">
            /me
          </Link>
        </div>
      </form>

      <div className="mt-8">
        <div className="text-sm font-medium text-black dark:text-zinc-50">Ответ</div>
        <pre className="mt-2 overflow-auto rounded-2xl border border-black/10 bg-zinc-50 p-4 text-xs text-black dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50">
          {result ? JSON.stringify(result, null, 2) : "—"}
        </pre>
      </div>
    </div>
  );
}

