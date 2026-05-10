"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  LogOut,
  ChevronRight,
  ChevronDown,
  Search,
  Settings,
  Layers3,
  Menu,
  MessagesSquare,
  BookOpenText,
  Star,
  PencilLine,
  LayoutList,
  SquareDashedMousePointer,
} from "lucide-react";
import { apiFetchJson } from "@/lib/apiClient";
import Header from "@/components/Header";

interface UserProfile {
  id: string;
  email: string;
  role: string;
  coins?: number;
}

export default function ProfilePage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [moreOpen, setMoreOpen] = useState(false);
  const moreMenuRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (moreMenuRef.current && !moreMenuRef.current.contains(event.target as Node)) {
        setMoreOpen(false);
      }
    };

    if (moreOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [moreOpen]);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const result = await apiFetchJson<UserProfile>("/auth/me");
        if (result.ok) {
          setUser(result.data);
        } else {
          router.push("/");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [router]);

  const handleLogout = async () => {
    try {
      await apiFetchJson("/auth/logout", { method: "POST" });
      router.push("/");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0d0d0d] text-white flex items-center justify-center">
        <div className="text-gray-400">Загрузка...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const initials = user.email.charAt(0).toUpperCase();
  const coins = user.coins ?? 0;

  const tabs = [
    "Тайтлы",
    "Комментарии",
    "Отзывы",
    "Избранное",
    "Друзья",
    "История просмотров",
  ];

  const moreTabs = [
    "История банов",
    "Личные сообщения",
    "Добавленные тайтлы",
    "Добавленные главы",
  ];

  const lists = [
    { label: "Все", count: 0, active: false },
    { label: "Читаю", count: 0, active: true },
    { label: "В планах", count: 0, active: false },
    { label: "Брошено", count: 0, active: false },
    { label: "Прочитано", count: 0, active: false },
    { label: "Любимые", count: 0, active: false },
  ];

  const sideActions = [
    { icon: BookOpenText, label: "Тайтлы" },
    { icon: MessagesSquare, label: "Комментарии" },
    { icon: Layers3, label: "Коллекции" },
    { icon: Star, label: "Отзывы" },
  ];

  const sortItems = [
    { label: "По названию (A-Z)", active: true },
    { label: "По названию (A-Я)", active: false },
  ];

  return (
    <main className="min-h-screen bg-[#0b0b0b] text-white">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[#0b0b0b]">
        <div className="absolute left-0 top-0 h-72 w-72 rounded-full bg-[#3b82f6] opacity-10 blur-3xl" />
        <div className="absolute right-0 top-20 h-80 w-80 rounded-full bg-[#9ca3af] opacity-5 blur-3xl" />
      </div>

      <Header onOpenAuth={() => undefined} />

      <div className="mx-auto w-full max-w-[1280px] px-4 py-6 lg:py-8">
        <section className="rounded-2xl border border-white/10 bg-[#171717] shadow-[0_0_0_1px_rgba(255,255,255,0.02)]">
          <div className="flex flex-col gap-5 p-5 md:flex-row md:items-start md:justify-between md:p-6">
            <div className="flex items-start gap-4">
              <div className="relative">
                <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-br from-[#b7d4ff] to-[#6fc3a2] text-3xl font-bold text-white shadow-lg shadow-black/20 md:h-20 md:w-20">
                  {initials}
                </div>
                <span className="absolute -right-0.5 -top-0.5 h-4 w-4 rounded-full border-2 border-[#171717] bg-emerald-400" />
              </div>

              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-3">
                  <h1 className="truncate text-2xl font-semibold md:text-3xl">{user.email.split("@")[0]}</h1>
                  <span className="rounded-full bg-white/5 px-3 py-1 text-xs text-white/60">
                    Уровень 2 · Топ #Не определён
                  </span>
                </div>
                <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-white/55">
                  <span>ID: {user.id}</span>
                  <span>Роль: {user.role}</span>
                  <span className="inline-flex items-center gap-2 rounded-full bg-white/5 px-3 py-1 text-white/80">
                    <span className="h-2 w-2 rounded-full bg-emerald-400" />
                    Онлайн
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 self-start">
              <button
                onClick={() => router.push("/profile/settings")}
                className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/80 transition-colors hover:bg-white/10"
              >
                <Settings size={16} />
                Настройки
              </button>
              <button
                onClick={handleLogout}
                className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-400 transition-colors hover:bg-red-500/20"
              >
                <LogOut size={16} />
                Выйти
              </button>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-0 border-t border-white/10 px-3 md:px-4">
            {tabs.map((tab, index) => (
              <button
                key={tab}
                className={`relative px-3 py-4 text-sm transition-colors md:px-4 ${
                  index === 0 ? "text-white" : "text-white/55 hover:text-white"
                }`}
              >
                {tab}
                {index === 0 ? (
                  <span className="absolute inset-x-3 bottom-0 h-0.5 rounded-full bg-sky-500" />
                ) : null}
              </button>
            ))}

            <div ref={moreMenuRef} className="relative">
              <button
                type="button"
                onClick={() => setMoreOpen((value) => !value)}
                className="relative px-3 py-4 text-sm text-white/55 transition-colors hover:text-white md:px-4"
                aria-label="Открыть дополнительные разделы"
              >
                ...
              </button>

              {moreOpen ? (
                <div className="absolute left-0 top-full z-20 mt-2 w-64 rounded-2xl border border-white/10 bg-[#303030] p-1.5 shadow-2xl shadow-black/40">
                  {moreTabs.map((item) => (
                    <button
                      key={item}
                      type="button"
                      className="w-full rounded-xl px-4 py-3.5 text-left text-base font-medium text-white/80 transition-colors hover:bg-white/5 hover:text-white"
                      onClick={() => setMoreOpen(false)}
                    >
                      {item}
                    </button>
                  ))}
                </div>
              ) : null}
            </div>

            <div className="ml-auto flex items-center gap-2 px-3 py-3 text-sm text-white/55 md:px-4">
              <span>Информация о пользователе</span>
              <span className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-white/15 text-[11px]">i</span>
            </div>
          </div>
        </section>

        <div className="mt-5 grid gap-5 lg:grid-cols-[280px_minmax(0,1fr)]">
          <aside className="rounded-2xl border border-white/10 bg-[#171717] p-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3 text-sm text-white/70">
              <span className="inline-flex items-center gap-2 font-medium">
                <LayoutList size={15} />
                Списки
              </span>
              <PencilLine size={15} className="text-white/40" />
            </div>

            <div className="mt-2 space-y-1">
              {lists.map((item) => (
                <button
                  key={item.label}
                  className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors ${
                    item.active ? "bg-white/6 text-white" : "text-white/65 hover:bg-white/5 hover:text-white"
                  }`}
                >
                  <span>{item.label}</span>
                  <span className="text-white/40">{item.count}</span>
                </button>
              ))}

              <button className="flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm text-white/35 transition-colors hover:bg-white/5 hover:text-white/70">
                <span>Редактировать...</span>
                <PencilLine size={14} />
              </button>
            </div>

            <div className="mt-5 border-t border-white/10 pt-4">
              <div className="mb-3 flex items-center gap-2 text-sm text-white/70">
                <SquareDashedMousePointer size={15} />
                Вид
              </div>
              <div className="space-y-1">
                <button className="flex w-full items-center gap-3 rounded-lg bg-white/6 px-3 py-2 text-sm text-white">
                  <LayoutList size={15} className="text-white/70" />
                  Список
                </button>
                <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-white/55 transition-colors hover:bg-white/5 hover:text-white">
                  <Layers3 size={15} className="text-white/50" />
                  Плитка
                </button>
              </div>
            </div>

            <div className="mt-5 border-t border-white/10 pt-4">
              <div className="mb-3 flex items-center gap-2 text-sm text-white/70">
                <ChevronDown size={15} />
                Сортировка
              </div>
              <div className="space-y-2">
                {sortItems.map((item) => (
                  <label key={item.label} className="flex cursor-pointer items-center gap-3 rounded-lg px-2 py-1.5 text-sm text-white/70 hover:bg-white/5 hover:text-white">
                    <span className={`h-4 w-4 rounded-full border ${item.active ? "border-sky-500" : "border-white/30"} p-0.5`}>
                      {item.active ? <span className="block h-full w-full rounded-full bg-sky-500" /> : null}
                    </span>
                    {item.label}
                  </label>
                ))}
              </div>
            </div>
          </aside>

          <section className="rounded-2xl border border-white/10 bg-[#171717] p-4 md:p-5">
            <div className="flex flex-col gap-3 md:flex-row md:items-center">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-white/35" size={18} />
                <input
                  type="text"
                  placeholder="Фильтр по названию"
                  className="h-12 w-full rounded-xl border border-white/10 bg-[#101010] pl-12 pr-4 text-sm text-white outline-none transition-colors placeholder:text-white/30 focus:border-sky-500/50 focus:bg-[#121212]"
                />
              </div>
              <button className="flex h-12 w-12 items-center justify-center rounded-xl border border-white/10 bg-[#101010] text-white/70 transition-colors hover:bg-white/5 hover:text-white">
                <Menu size={18} />
              </button>
            </div>

            <div className="mt-4 rounded-2xl border border-white/8 bg-[#1d1d1d] px-6 py-16 text-center text-sm text-white/45 shadow-[inset_0_1px_0_rgba(255,255,255,0.03)]">
              В этом списке пока нет тайтлов
            </div>

            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              {sideActions.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.label}
                    className="flex items-center justify-between rounded-xl border border-white/10 bg-white/3 px-4 py-3 text-left transition-colors hover:bg-white/6"
                  >
                    <span className="flex items-center gap-3 text-sm text-white/80">
                      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/6 text-white/60">
                        <Icon size={16} />
                      </span>
                      {item.label}
                    </span>
                    <ChevronRight size={16} className="text-white/35" />
                  </button>
                );
              })}
            </div>

            <div className="mt-5 rounded-xl border border-white/10 bg-[#111111] px-4 py-3 text-xs text-white/45">
              Coins: {coins} · LoreLounge v1.0 · {user.email}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
