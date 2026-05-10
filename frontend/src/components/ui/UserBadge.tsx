"use client";

import { Avatar } from "./Avatar";
import type { User, Profile } from "@/types";

interface UserBadgeProps {
  user: User | null;
  profile: Profile | null;
  avatarUrl: string | null;
  avatarError: boolean;
}

export function UserBadge({ user, profile, avatarUrl, avatarError }: UserBadgeProps) {
  const displayName = profile?.name || user?.email?.split("@")[0] || "Пользователь";

  return (
    <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-[#202020] p-3">
      <Avatar
        src={avatarUrl}
        fallback={displayName}
        size="lg"
        onError={() => {}}
      />
      <div className="min-w-0">
        <div className="truncate text-sm font-semibold text-white/95">{displayName}</div>
      </div>
    </div>
  );
}