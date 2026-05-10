"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { apiFetchJson } from "@/lib/apiClient";

type PasswordResetResponse = { detail: string };

type ResetState = {
  token: string;
  newPassword: string;
  repeatPassword: string;
};

type ResetPasswordFormProps = {
  initialToken?: string;
};

export default function ResetPasswordForm({ initialToken = "" }: ResetPasswordFormProps) {
  const [form, setForm] = useState<ResetState>({
    token: initialToken,
    newPassword: "",
    repeatPassword: "",
  });
  const [result, setResult] = useState<unknown>(null);
  const [pending, setPending] = useState(false);
  const [expiresAt, setExpiresAt] = useState<Date | null>(null);
  const [timeLeft, setTimeLeft] = useState<string>("");

  const isSuccessResult = Boolean(
    result && typeof result === "object" && "ok" in result && (result as { ok: boolean }).ok,
  );

  const resultMessage =
    result && typeof result === "object" && "ok" in result
      ? (result as { ok: boolean; error?: string; data?: PasswordResetResponse }).ok
        ? (result as { data?: PasswordResetResponse }).data?.detail ?? "Готово"
        : (result as { error?: string }).error ?? "Ошибка"
      : null;

  const canSubmit = Boolean(form.token && form.newPassword && form.repeatPassword && timeLeft !== "Просрочено");

  useEffect(() => {
    if (form.token) return;
    try {
      const params = new URLSearchParams(window.location.search);
      const tokenFromUrl = params.get("token");
      if (tokenFromUrl) {
        setForm((prev) => ({ ...prev, token: tokenFromUrl }));
      }
    } catch (e) {
      // ignore in non-browser environments
    }
  }, [form.token]);

  useEffect(() => {
    if (!form.token) return;

    const checkToken = async () => {
      const res = await apiFetchJson<{ expires_at: string; valid: boolean }>(
        `/auth/password-reset-check?token=${form.token}`,
      );
      if (res.ok && res.data.valid) {
        setExpiresAt(new Date(res.data.expires_at));
      } else {
        setResult({ ok: false, error: "Ссылка недействительна или просрочена" });
        setTimeLeft("Просрочено");
      }
    };

    void checkToken();
  }, [form.token]);

  useEffect(() => {
    if (!expiresAt) return;

    const timer = setInterval(() => {
      const now = new Date();
      const diff = expiresAt.getTime() - now.getTime();
      if (diff <= 0) {
        setTimeLeft("Просрочено");
        setResult({ ok: false, error: "Срок действия ссылки истек" });
        clearInterval(timer);
      } else {
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        setTimeLeft(`${minutes}:${seconds < 10 ? "0" : ""}${seconds}`);
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [expiresAt]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.token) {
      setResult({ ok: false, error: "Ссылка не содержит токен" });
      return;
    }
    if (timeLeft === "Просрочено") {
      setResult({ ok: false, error: "Срок действия ссылки истек" });
      return;
    }
    setPending(true);
    setResult(null);
    try {
      const res = await apiFetchJson<PasswordResetResponse>("/auth/password-reset-confirm", {
        method: "POST",
        headers: {
          "content-type": "application/json",
        },
        body: JSON.stringify({
          token: form.token,
          new_password: form.newPassword,
          repeat_password: form.repeatPassword,
        }),
      });
      setResult(res);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#f5f1e8] text-[#1e1b16] dark:bg-[#0e0f12] dark:text-zinc-50">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-20 -top-28 h-72 w-72 rounded-full bg-[#ffd28a] opacity-50 blur-3xl dark:bg-[#3a2c1d]" />
        <div className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-[#9ad4ff] opacity-40 blur-3xl dark:bg-[#16263d]" />
        <div className="absolute left-1/2 top-1/2 h-[420px] w-[420px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-black/5 dark:border-white/10" />
      </div>

      <main className="relative mx-auto flex min-h-screen w-full max-w-5xl items-center px-6 py-14">
        <div className="grid w-full gap-10 lg:grid-cols-[1.1fr_1fr]">
          <section className="flex flex-col justify-between gap-8">
            <div>
              <Link className="text-sm text-black/60 hover:underline dark:text-zinc-400" href="/">
                ← На главную
              </Link>

              <div className="mt-8 space-y-4">
                <div className="text-xs font-semibold uppercase tracking-[0.3em] text-black/50 dark:text-zinc-400">
                  LoreLounge
                </div>
                <h1 className="text-4xl font-semibold leading-tight">
                  Обновите пароль без лишних шагов
                </h1>
                <p className="text-base text-black/70 dark:text-zinc-300">
                  Перейдите по ссылке из письма и задайте новый пароль. Процесс занимает меньше
                  минуты.
                </p>
              </div>
            </div>

            <div className="grid gap-3 text-sm text-black/70 dark:text-zinc-300">
              <div className="rounded-2xl border border-black/10 bg-white/70 px-4 py-3 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/5">
                1. Откройте письмо и нажмите кнопку «Сбросить пароль».
              </div>
              <div className="rounded-2xl border border-black/10 bg-white/70 px-4 py-3 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/5">
                2. Придумайте новый пароль от 8 символов.
              </div>
              <div className="rounded-2xl border border-black/10 bg-white/70 px-4 py-3 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/5">
                3. Нажмите «Сменить пароль» и сразу входите в аккаунт.
              </div>
            </div>
          </section>

          <section className="rounded-[32px] border border-black/10 bg-white/80 p-6 shadow-[0_30px_80px_-60px_rgba(0,0,0,0.6)] backdrop-blur dark:border-white/10 dark:bg-white/5">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="text-sm font-semibold uppercase tracking-[0.2em] text-black/50 dark:text-zinc-400">
                  Reset
                </div>
                {timeLeft && (
                  <div className={`text-xs font-mono font-medium ${timeLeft === "Просрочено" ? "text-red-500" : "text-black/40 dark:text-zinc-400"}`}>
                    {timeLeft === "Просрочено" ? "Срок истек" : `Действителен: ${timeLeft}`}
                  </div>
                )}
              </div>
              <h2 className="text-2xl font-semibold">Сброс пароля</h2>
              <p className="text-sm text-black/60 dark:text-zinc-300">
                Ссылка из письма приведет вас прямо сюда.
              </p>
            </div>

            <form onSubmit={onSubmit} className="mt-6 grid gap-4">
              <label className="grid gap-2">
                <span className="text-sm font-medium">Новый пароль</span>
                <input
                  className="h-11 rounded-2xl border border-black/10 bg-white px-4 text-black outline-none focus:border-black/30 dark:border-white/10 dark:bg-black/30 dark:text-zinc-50"
                  value={form.newPassword}
                  onChange={(e) => setForm((prev) => ({ ...prev, newPassword: e.target.value }))}
                  type="password"
                  autoComplete="new-password"
                  minLength={8}
                  required
                />
              </label>

              <label className="grid gap-2">
                <span className="text-sm font-medium">Повторите пароль</span>
                <input
                  className="h-11 rounded-2xl border border-black/10 bg-white px-4 text-black outline-none focus:border-black/30 dark:border-white/10 dark:bg-black/30 dark:text-zinc-50"
                  value={form.repeatPassword}
                  onChange={(e) => setForm((prev) => ({ ...prev, repeatPassword: e.target.value }))}
                  type="password"
                  autoComplete="new-password"
                  minLength={8}
                  required
                />
              </label>

              <div className="flex flex-wrap items-center gap-3">
                <button
                  disabled={!canSubmit || pending}
                  className="inline-flex h-11 items-center justify-center rounded-2xl bg-black px-6 text-sm font-semibold text-white shadow-lg shadow-black/20 disabled:opacity-60 dark:bg-white dark:text-black"
                  type="submit"
                >
                  {pending ? "Сбрасываем…" : "Сменить пароль"}
                </button>
                <Link className="text-sm text-black/60 hover:underline dark:text-zinc-400" href="/auth/login">
                  Вход
                </Link>
                <Link className="text-sm text-black/60 hover:underline dark:text-zinc-400" href="/auth/register">
                  Регистрация
                </Link>
              </div>
            </form>

            {resultMessage && (
              <div
                className={
                  isSuccessResult
                    ? "mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900 dark:border-emerald-500/40 dark:bg-emerald-500/10 dark:text-emerald-100"
                    : "mt-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-900 dark:border-red-500/40 dark:bg-red-500/10 dark:text-red-100"
                }
              >
                {resultMessage}
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
