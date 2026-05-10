"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Bell, Lock, ShieldBan, UserRound, ArrowLeft, KeyRound, Eye, EyeOff } from "lucide-react";
import Header from "@/components/Header";
import { apiFetchJson } from "@/lib/apiClient";

type UserProfile = {
  id: string;
  email: string;
  role: string;
};

type ProfileData = {
  name: string;
  avatar_url: string | null;
};

export default function SecuritySettingsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const [user, setUser] = useState<UserProfile | null>(null);
  const [nickname, setNickname] = useState("");
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [avatarError, setAvatarError] = useState(false);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");

  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showRepeatPassword, setShowRepeatPassword] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const me = await apiFetchJson<UserProfile>("/auth/me");
        if (!me.ok) {
          router.push("/");
          return;
        }

        setUser(me.data);

        const profile = await apiFetchJson<ProfileData>("/profile/me");
        if (profile.ok) {
          setNickname(profile.data.name ?? "");
          if (profile.data.avatar_url) {
            setAvatarUrl(profile.data.avatar_url);
            setAvatarError(false);
          }
        } else if (profile.status === 404) {
          setNickname(me.data.email.split("@")[0] ?? "");
        }
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, [router]);

  const initials = useMemo(() => {
    const source = (nickname || user?.email || "U").trim();
    return source.charAt(0).toUpperCase();
  }, [nickname, user]);

  const [resetting, setResetting] = useState(false);
  const [resetStatus, setResetStatus] = useState<string | null>(null);

  const handlePasswordResetRequest = async () => {
    if (!user?.email) return;
    setResetting(true);
    setResetStatus(null);
    try {
      const res = await apiFetchJson<{ detail?: string }>("/auth/password-reset-request", {
        method: "POST",
        body: JSON.stringify({ email: user.email }),
      });
      if (res.ok) {
        setResetStatus("Письмо с инструкциями отправлено на вашу почту");
      } else {
        setResetStatus(res.error || "Не удалось отправить письмо");
      }
    } catch (error) {
      setResetStatus("Произошла ошибка при отправке");
    } finally {
      setResetting(false);
    }
  };

  const [sendingVerification, setSendingVerification] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState<string | null>(null);

  const handleEmailVerificationRequest = async () => {
    if (!user?.email) return;
    setSendingVerification(true);
    setVerificationStatus(null);
    try {
      const res = await apiFetchJson<{ detail?: string }>("/auth/email-verification-request", {
        method: "POST",
        body: JSON.stringify({ email: user.email }),
      });
      if (res.ok) {
        setVerificationStatus("Письмо с подтверждением отправлено на вашу почту");
      } else {
        setVerificationStatus(res.error || "Не удалось отправить письмо");
      }
    } catch (error) {
      setVerificationStatus("Произошла ошибка при отправке");
    } finally {
      setSendingVerification(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!currentPassword || !newPassword || !repeatPassword) {
      setIsSuccess(false);
      setStatus("Пожалуйста, заполните все поля");
      return;
    }
    
    if (newPassword !== repeatPassword) {
      setIsSuccess(false);
      setStatus("Новые пароли не совпадают");
      return;
    }

    if (newPassword.length < 8) {
      setIsSuccess(false);
      setStatus("Новый пароль должен содержать минимум 8 символов");
      return;
    }

    setSaving(true);
    setStatus(null);
    setIsSuccess(false);

    try {
      const payload = {
        current_password: currentPassword,
        new_password: newPassword,
        repeat_password: repeatPassword,
      };

      const res = await apiFetchJson<{ detail?: string }>("/auth/password-change", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        setIsSuccess(true);
        setStatus("Пароль успешно изменён");
        setCurrentPassword("");
        setNewPassword("");
        setRepeatPassword("");
      } else {
        setIsSuccess(false);
        setStatus(res.error || "Не удалось изменить пароль");
      }
    } catch (error) {
      setIsSuccess(false);
      setStatus("Произошла неизвестная ошибка");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-[#0b0b0b] text-white">
        <Header onOpenAuth={() => undefined} />
        <div className="mx-auto max-w-[1280px] px-4 py-10">
          <div className="grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
            <aside className="rounded-2xl border border-white/10 bg-[#171717] p-3 sm:p-4 min-h-[200px]" />
            <section className="min-h-[200px]" />
          </div>
        </div>
      </main>
    );
  }

  if (!user) {
    return null;
  }

  const displayName = nickname.trim() || user.email.split("@")[0] || "Пользователь";

  return (
    <main className="min-h-screen bg-[#0b0b0b] text-white">
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[#0b0b0b]">
        <div className="absolute left-0 top-0 h-72 w-72 rounded-full bg-[#3b82f6] opacity-10 blur-3xl" />
        <div className="absolute right-0 top-20 h-80 w-80 rounded-full bg-[#9ca3af] opacity-5 blur-3xl" />
      </div>

      <Header onOpenAuth={() => undefined} />

      <div className="mx-auto w-full max-w-[1280px] px-3 py-4 sm:px-4 sm:py-6">
        <div className="mb-4">
          <button
            onClick={() => router.push("/profile")}
            className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-2 text-sm text-white/80 transition-colors hover:bg-white/10"
          >
            <ArrowLeft size={16} />
            Назад к профилю
          </button>
        </div>

        <div className="grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
          <aside className="rounded-2xl border border-white/10 bg-[#171717] p-3 sm:p-4">
            <div className="mb-3 flex items-center gap-3 rounded-2xl border border-white/10 bg-[#202020] p-3">
              {avatarUrl && !avatarError ? (
                <img
                  src={avatarUrl}
                  alt="Аватар"
                  className="h-11 w-11 rounded-xl object-cover"
                  onError={() => setAvatarError(true)}
                />
              ) : (
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-[#b7d4ff] to-[#6fc3a2] font-bold text-white">
                  {initials}
                </div>
              )}
              <div className="min-w-0">
                <div className="truncate text-sm font-semibold text-white/95">{displayName}</div>
              </div>
            </div>

            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-1">
              <NavItem icon={<UserRound size={16} />} title="Профиль" desc="Никнейм, о себе, день рождения, пол" onClick={() => router.push("/profile/settings")} />
              <NavItem icon={<Lock size={16} />} title="Безопасность и вход в аккаунт" desc="Смена почты и пароля, 2fa" active onClick={() => router.push("/profile/settings/security")} />
              <NavItem icon={<Bell size={16} />} title="Уведомления" desc="Получение наград и активности" />
              <NavItem icon={<ShieldBan size={16} />} title="Блокировки" desc="Аккаунтов, комментариев и постов" />
            </div>
          </aside>

          <section className="space-y-6">
            <div className="rounded-2xl border border-white/10 bg-[#171717] p-4 sm:p-5 lg:p-6">
              <div className="mb-6 border-b border-white/10 pb-4">
                <h2 className="text-xl font-bold text-white/95">Смена пароля</h2>
              </div>

              <form onSubmit={handleChangePassword} className="max-w-full space-y-5">
                <div>
                  <label className="mb-1.5 block text-sm text-white/60">Текущий пароль</label>
                  <div className="relative">
                    <input
                      type={showCurrentPassword ? "text" : "password"}
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      className="h-11 w-full rounded-xl border border-white/10 bg-[#101010] px-4 pr-11 text-sm text-white outline-none transition-colors focus:border-sky-500/50"
                    />
                    <button
                      type="button"
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-white/50 hover:text-white/80"
                    >
                      {showCurrentPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="mb-1.5 block text-sm text-white/60">Новый пароль</label>
                  <div className="relative">
                    <input
                      type={showNewPassword ? "text" : "password"}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="h-11 w-full rounded-xl border border-white/10 bg-[#101010] px-4 pr-11 text-sm text-white outline-none transition-colors focus:border-sky-500/50"
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-white/50 hover:text-white/80"
                    >
                      {showNewPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>

                <div>
                  <label className="mb-1.5 block text-sm text-white/60">Подтверждение нового пароля</label>
                  <div className="relative">
                    <input
                      type={showRepeatPassword ? "text" : "password"}
                      value={repeatPassword}
                      onChange={(e) => setRepeatPassword(e.target.value)}
                      className="h-11 w-full rounded-xl border border-white/10 bg-[#101010] px-4 pr-11 text-sm text-white outline-none transition-colors focus:border-sky-500/50"
                    />
                    <button
                      type="button"
                      onClick={() => setShowRepeatPassword(!showRepeatPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-white/50 hover:text-white/80"
                    >
                      {showRepeatPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </div>

                <div className="rounded-xl bg-[#202632] p-4 text-sm text-sky-200/80">
                  Если вы не помните текущий пароль, то воспользуйтесь <button type="button" onClick={handlePasswordResetRequest} className="text-sky-400 underline hover:text-sky-300">сбросом пароля</button>
                </div>
                {resetStatus && (
                  <p className={`mt-2 text-xs ${resetting ? "text-sky-300" : "text-green-400"}`}>{resetStatus}</p>
                )}

                {status ? (
                  <div className={`rounded-xl border px-3 py-2 text-sm ${isSuccess ? "border-green-500/20 bg-green-500/10 text-green-400" : "border-red-500/20 bg-red-500/10 text-red-400"}`}>
                    {status}
                  </div>
                ) : null}

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={saving}
                    className="rounded-xl border border-white/10 bg-transparent px-6 py-2.5 text-sm font-semibold text-white/80 transition-colors hover:bg-white/5 disabled:opacity-60"
                  >
                    {saving ? "Изменение..." : "Сохранить изменения"}
                  </button>
                </div>
              </form>
            </div>

            <div className="rounded-2xl border border-white/10 bg-[#171717] p-4 sm:p-5 lg:p-6">
              <h2 className="mb-4 text-lg font-bold text-white/95">Электронная почта</h2>
              <div className="max-w-full">
                <input
                  type="text"
                  value={user.email}
                  disabled
                  className="h-11 w-full rounded-xl border border-white/10 bg-[#101010] px-4 text-sm text-white/60 outline-none cursor-not-allowed"
                />
                <div className="mt-4 rounded-xl bg-[#202632] border border-transparent p-4">
                  <p className="text-sm text-sky-200/80 mb-3">
                    Ваш аккаунт не подтверждён. Нажмите «Отправить подтверждение» после чего проследуйте инструкциям в письме
                  </p>
                  <button
                    type="button"
                    onClick={handleEmailVerificationRequest}
                    disabled={sendingVerification}
                    className="rounded-lg border border-sky-500/30 bg-transparent px-4 py-2 text-sm font-medium text-sky-200/80 transition-colors hover:bg-sky-500/10 disabled:opacity-60"
                  >
                    {sendingVerification ? "Отправка..." : "Отправить подтверждение"}
                  </button>
                  {verificationStatus && (
                    <p className="mt-3 text-xs text-sky-300">{verificationStatus}</p>
                  )}
                </div>
                
                <div className="mt-4 pt-2">
                  <button
                    type="button"
                    disabled
                    className="rounded-xl border border-white/10 bg-transparent px-6 py-2.5 text-sm font-semibold text-white/50 transition-colors cursor-not-allowed"
                  >
                    Сохранить изменения
                  </button>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}

function NavItem({
  icon,
  title,
  desc,
  active = false,
  onClick,
}: {
  icon: React.ReactNode;
  title: string;
  desc: string;
  active?: boolean;
  onClick?: () => void;
}) {
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
