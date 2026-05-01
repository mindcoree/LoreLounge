"use client";

import Link from "next/link";
import { useState } from "react";
import { llFetchJson } from "@/lib/llApi";

type AuthEntityOut = { id: number; email: string; login: string; role: string };

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("reader");
  const [result, setResult] = useState<unknown>(null);
  const [pending, setPending] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setPending(true);
    setResult(null);
    try {
      const res = await llFetchJson<AuthEntityOut>("/auth/register", {
        method: "POST",
        form: { email, login, password, role },
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

      <h1 className="text-2xl font-semibold tracking-tight text-black dark:text-zinc-50">
        Регистрация
      </h1>
      <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
        Отправляет форму на <code className="font-mono">/api/auth/register</code>.
      </p>

      <form onSubmit={onSubmit} className="mt-6 grid gap-4">
        <label className="grid gap-2">
          <span className="text-sm font-medium text-black dark:text-zinc-50">Email</span>
          <input
            className="h-11 rounded-xl border border-black/10 bg-white px-4 text-black outline-none focus:border-black/20 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            inputMode="email"
            required
          />
        </label>

        <label className="grid gap-2">
          <span className="text-sm font-medium text-black dark:text-zinc-50">Логин</span>
          <input
            className="h-11 rounded-xl border border-black/10 bg-white px-4 text-black outline-none focus:border-black/20 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50"
            value={login}
            onChange={(e) => setLogin(e.target.value)}
            autoComplete="username"
            minLength={3}
            required
          />
        </label>

        <label className="grid gap-2">
          <span className="text-sm font-medium text-black dark:text-zinc-50">Пароль</span>
          <input
            className="h-11 rounded-xl border border-black/10 bg-white px-4 text-black outline-none focus:border-black/20 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            type="password"
            autoComplete="new-password"
            minLength={8}
            required
          />
        </label>

        <label className="grid gap-2">
          <span className="text-sm font-medium text-black dark:text-zinc-50">Роль (desired)</span>
          <select
            className="h-11 rounded-xl border border-black/10 bg-white px-4 text-black outline-none focus:border-black/20 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <option value="reader">reader</option>
            <option value="translator">translator</option>
            <option value="admin">admin</option>
          </select>
        </label>

        <div className="flex items-center gap-3">
          <button
            disabled={pending}
            className="inline-flex h-11 items-center justify-center rounded-xl bg-black px-5 text-sm font-medium text-white disabled:opacity-60 dark:bg-white dark:text-black"
            type="submit"
          >
            {pending ? "Создаём…" : "Создать аккаунт"}
          </button>
          <Link className="text-sm text-zinc-600 hover:underline dark:text-zinc-400" href="/auth/login">
            Вход
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

