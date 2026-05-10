"use client";

import { UserRound, Lock, Bell, ShieldBan } from "lucide-react";
import { useRouter } from "next/navigation";

interface NavItemProps {
  icon: React.ReactNode;
  title: string;
  desc: string;
  active?: boolean;
  onClick?: () => void;
}

function NavItem({ icon, title, desc, active = false, onClick }: NavItemProps) {
  return (
    <button
      onClick={onClick}
      className={`w-full rounded-xl border px-3 py-2.5 text-left transition-colors ${
        active
          ? "border-white/20 bg-white/10 text-white"
          : "border-white/10 bg-[#202020] text-white/85 hover:bg-white/8"
      }`}
    >
      <div className="flex items-start gap-2.5">
        <span className="mt-0.5 text-white/65">{icon}</span>
        <span className="min-w-0">
          <span className="block text-sm font-semibold leading-5">{title}</span>
          <span className="block text-xs text-white/50">{desc}</span>
        </span>
      </div>
    </button>
  );
}

interface SidebarNavProps {
  activePath?: string;
}

export function SidebarNav({ activePath }: SidebarNavProps) {
  const router = useRouter();

  const items = [
    { icon: <UserRound size={16} />, title: "Профиль", desc: "Никнейм, о себе, день рождения, пол", path: "/profile/settings" },
    { icon: <Lock size={16} />, title: "Безопасность и вход в аккаунт", desc: "Смена почты и пароля, 2fa", path: "/profile/settings/security" },
    { icon: <Bell size={16} />, title: "Уведомления", desc: "Получение наград и активности", path: null },
    { icon: <ShieldBan size={16} />, title: "Блокировки", desc: "Аккаунтов, комментариев и постов", path: null },
  ];

  return (
    <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-1">
      {items.map((item) => (
        <NavItem
          key={item.path || item.title}
          icon={item.icon}
          title={item.title}
          desc={item.desc}
          active={activePath === item.path}
          onClick={() => item.path && router.push(item.path)}
        />
      ))}
    </div>
  );
}