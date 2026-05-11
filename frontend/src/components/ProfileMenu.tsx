"use client";

import { useEffect, useRef, useState } from "react";
import {
  BadgePlus,
  BookOpenText,
  ChevronDown,
  ChevronUp,
  History,
  LogOut,
  MessageCircle,
  MessageSquare,
  Moon,
  ReceiptText,
  Repeat2,
  RotateCcw,
  Settings,
  ShoppingBag,
  Ticket,
  Zap,
} from "lucide-react";
import { useRouter } from "next/navigation";
import { useUser } from "@/hooks/useUser";
import { Avatar } from "@/components/ui/Avatar";

const ProfileMenu = ({ isAuthenticated, onLogout }: { isAuthenticated: boolean; onLogout?: () => void }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const [darkThemeOn, setDarkThemeOn] = useState(true);
  const { user, profile, avatarUrl, avatarError, loading, refetch, logout } = useUser();
  const menuRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setMoreOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen]);

  const handleLogout = async () => {
    setIsOpen(false);
    setMoreOpen(false);
    await logout();
    onLogout?.();
    router.push("/");
    router.refresh();
  };

  const handleProfileClick = () => {
    setIsOpen(false);
    setMoreOpen(false);
    router.push("/profile");
  };

  if (!isAuthenticated || loading) {
    return null;
  }

  const initials = profile?.name?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase() || "U";
  const displayName = profile?.name || user?.email || "Пользователь";

  return (
    <div ref={menuRef} className="relative">
      <button
        onClick={() => {
          if (!isOpen) refetch();
          setIsOpen((value) => !value);
        }}
        className="flex items-center gap-2 rounded-full p-2 transition-colors hover:bg-[#1a1a1a]"
        aria-label="Профиль"
      >
        <Avatar src={avatarUrl} fallback={initials} size="md" />
        {isOpen ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
      </button>

      {isOpen ? (
        <div className="absolute right-0 mt-2 flex w-[360px] max-h-[calc(100vh-110px)] flex-col overflow-hidden rounded-[22px] border border-white/10 bg-[#1a1a1a] shadow-[0_24px_80px_rgba(0,0,0,0.62)] animate-in fade-in slide-in-from-top-2">
          <button
            onClick={handleProfileClick}
            className="mx-3 mt-3 rounded-[22px] border border-white/10 bg-[#202020] p-4 text-left transition-colors hover:bg-white/[0.035]"
          >
            <div className="flex items-start gap-4">
              <Avatar src={avatarUrl} fallback={initials} size="xl" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-[19px] font-semibold leading-6 text-white">{displayName}</p>
                <div className="mt-6 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2 text-[17px] font-semibold text-white">
                    <span className="flex h-6 w-6 items-center justify-center rounded-full bg-[#ffcc33] text-[#111111] shadow-[inset_0_-2px_0_rgba(0,0,0,0.18)]">
                      <span className="text-[13px] leading-none">●</span>
                    </span>
                    <span>{user?.coins ?? 0} монет</span>
                  </div>
                  <button className="rounded-full bg-[#3f83f8] px-6 py-2.5 text-[16px] font-semibold text-white transition-colors hover:bg-[#3274ea]">
                    Пополнить
                  </button>
                </div>
              </div>
            </div>
          </button>

          <div className="px-3 pb-2 pt-4">
            <button className="relative h-[88px] w-full overflow-hidden rounded-[18px] bg-[linear-gradient(180deg,#4e86f2_0%,#3d73e2_100%)] text-left shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]">
              <div className="absolute -right-6 -top-4 h-24 w-24 rounded-full bg-white/10" />
              <div className="absolute right-8 top-4 h-16 w-16 rotate-12 rounded-full bg-white/8" />
              <div className="absolute left-4 top-2 h-20 w-20 -rotate-12 rounded-full bg-white/10" />
              <div className="relative z-10 flex h-full flex-col justify-center px-5 text-white">
                <span className="text-[20px] font-semibold leading-none">Активировать Premium</span>
                <span className="mt-1 text-[15px] text-white/90">Попробовать 7 дней бесплатно</span>
              </div>
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-3 pb-2 pt-1">
            <MenuItem icon={<MessageSquare size={18} />} label="Re: Pass" />
            <MenuItem icon={<History size={18} />} label="История чтения" />
            <MenuItem icon={<BadgePlus size={18} />} label="Мои заявки" />
            <MenuItem icon={<Settings size={18} />} label="Добавить контент" hasChevron />
            <div className="my-2 border-t border-white/10" />
            <MenuItem icon={<ShoppingBag size={18} />} label="Магазин" />
            <MenuItem icon={<ReceiptText size={18} />} label="Транзакции" />
            <div className="my-2 border-t border-white/10" />
            <button
              type="button"
              onClick={() => setMoreOpen((value) => !value)}
              className="flex w-full items-center justify-between rounded-xl px-6 py-3.5 text-[17px] text-white/80 transition-colors hover:bg-white/5 hover:text-white"
            >
              <span>Другое</span>
              {moreOpen ? <ChevronUp size={18} className="text-white/70" /> : <ChevronDown size={18} className="text-white/70" />}
            </button>
            {moreOpen ? (
              <div className="mt-1 rounded-[18px] border border-white/10 bg-[#202020] px-1.5 py-1.5">
                <MenuItem icon={<Settings size={18} />} label="Настройки" />
                <div className="flex w-full items-center justify-between rounded-xl px-6 py-3.5 text-[17px] text-white/80 transition-colors hover:bg-white/5 hover:text-white">
                  <span className="flex items-center gap-3">
                    <Moon size={18} className="text-gray-400" />
                    <span>Тёмная тема</span>
                  </span>
                  <button
                    type="button"
                    onClick={() => setDarkThemeOn((value) => !value)}
                    className={`relative h-8 w-14 rounded-full transition-colors ${darkThemeOn ? "bg-[#3f83f8]" : "bg-white/15"}`}
                  >
                    <span className={`absolute top-1 h-6 w-6 rounded-full bg-[#0f1115] shadow-md transition-transform ${darkThemeOn ? "translate-x-7" : "translate-x-1"}`} />
                  </button>
                </div>
                <MenuItem icon={<MessageCircle size={18} />} label="Обратная связь" />
                <MenuItem icon={<BookOpenText size={18} />} label="Пройти гайд" />
                <MenuItem icon={<RotateCcw size={18} />} label="Вернуться на старую версию" />
              </div>
            ) : null}
          </div>

          <button
            onClick={handleLogout}
            className="flex w-full items-center justify-between border-t border-white/10 px-6 py-5 text-[16px] text-red-500 transition-colors hover:bg-white/5 hover:text-red-400"
          >
            <span>Выйти</span>
            <LogOut size={20} />
          </button>
        </div>
      ) : null}
    </div>
  );
};

interface MenuItemProps {
  icon: React.ReactNode;
  label: string;
  hasChevron?: boolean;
}

const MenuItem = ({ icon, label, hasChevron }: MenuItemProps) => {
  return (
    <button className="flex w-full items-center justify-between rounded-xl px-6 py-3.5 text-[17px] text-white/80 transition-colors hover:bg-white/5 hover:text-white">
      <span className="flex items-center gap-3">
        <span className="text-gray-400">{icon}</span>
        <span>{label}</span>
      </span>
      {hasChevron ? <ChevronDown size={16} className="text-gray-500" /> : null}
    </button>
  );
};

export default ProfileMenu;