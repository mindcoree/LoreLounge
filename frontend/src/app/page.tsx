export default function Home() {
  return (
    <div className="flex flex-col flex-1 items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex flex-1 w-full max-w-3xl flex-col gap-10 py-20 px-6 bg-white dark:bg-black sm:px-10">
        <header className="flex flex-col gap-3">
          <h1 className="text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
            LoreLounge
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400">
            Мини-фронт для проверки авторизации (cookie, /me, logout) через
            API Gateway.
          </p>
        </header>

        <section className="grid gap-3 sm:grid-cols-2">
          <a
            className="rounded-2xl border border-black/10 bg-white px-5 py-4 text-black shadow-sm transition hover:bg-zinc-50 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900"
            href="/auth/login"
          >
            <div className="font-medium">Вход</div>
            <div className="text-sm text-zinc-600 dark:text-zinc-400">
              POST /api/auth/login (form) + cookie
            </div>
          </a>
          <a
            className="rounded-2xl border border-black/10 bg-white px-5 py-4 text-black shadow-sm transition hover:bg-zinc-50 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900"
            href="/auth/register"
          >
            <div className="font-medium">Регистрация</div>
            <div className="text-sm text-zinc-600 dark:text-zinc-400">
              POST /api/auth/register (form)
            </div>
          </a>
          <a
            className="rounded-2xl border border-black/10 bg-white px-5 py-4 text-black shadow-sm transition hover:bg-zinc-50 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900"
            href="/me"
          >
            <div className="font-medium">Профиль (/me)</div>
            <div className="text-sm text-zinc-600 dark:text-zinc-400">
              GET /api/auth/me (cookie)
            </div>
          </a>
          <a
            className="rounded-2xl border border-black/10 bg-white px-5 py-4 text-black shadow-sm transition hover:bg-zinc-50 dark:border-white/10 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900"
            href="/debug"
          >
            <div className="font-medium">Debug API</div>
            <div className="text-sm text-zinc-600 dark:text-zinc-400">
              Ручной вызов эндпоинтов
            </div>
          </a>
        </section>

        <footer className="text-xs text-zinc-500 dark:text-zinc-500">
          API вызывается через `http://localhost/api/auth/*` (Nginx → KrakenD → auth).
        </footer>
      </main>
    </div>
  );
}
