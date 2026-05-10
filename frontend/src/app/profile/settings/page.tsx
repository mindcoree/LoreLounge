"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Bell, Lock, ShieldBan, UserRound, ArrowLeft, X, ChevronLeft, ChevronRight, ChevronDown } from "lucide-react";
import Header from "@/components/Header";
import { apiFetchJson } from "@/lib/apiClient";

type UserProfile = {
  id: string;
  email: string;
  role: string;
};

type ProfileData = {
  name: string;
  bio: string | null;
  avatar_url: string | null;
  birth_date: string | null;
  gender: Gender | null;
};

type Gender = "unspecified" | "male" | "female";

const RU_MONTHS = [
  "январь",
  "февраль",
  "март",
  "апрель",
  "май",
  "июнь",
  "июль",
  "август",
  "сентябрь",
  "октябрь",
  "ноябрь",
  "декабрь",
];

const WEEKDAY_SHORT = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"];

export default function ProfileSettingsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [deleteModalRendered, setDeleteModalRendered] = useState(false);
  const [deleteConfirmText, setDeleteConfirmText] = useState("");

  const [user, setUser] = useState<UserProfile | null>(null);
  const [nickname, setNickname] = useState("");
  const [about, setAbout] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [birthDatePickerOpen, setBirthDatePickerOpen] = useState(false);
  const [calendarMonth, setCalendarMonth] = useState(() => new Date().getMonth());
  const [calendarYear, setCalendarYear] = useState(() => new Date().getFullYear());
  const [gender, setGender] = useState<Gender>("unspecified");

  const [allowExchanges, setAllowExchanges] = useState(true);
  const [privateProfile, setPrivateProfile] = useState(false);
  const [extendedCatalog, setExtendedCatalog] = useState(false);

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
          setAbout(profile.data.bio ?? "");
          setBirthDate(profile.data.birth_date ?? "");
          setGender(profile.data.gender ?? "unspecified");

          if (profile.data.birth_date) {
            const parsedDate = new Date(`${profile.data.birth_date}T00:00:00`);
            if (!Number.isNaN(parsedDate.getTime())) {
              setCalendarMonth(parsedDate.getMonth());
              setCalendarYear(parsedDate.getFullYear());
            }
          }
        } else if (profile.status === 404) {
          setNickname(me.data.email.split("@")[0] ?? "");
          setAbout("");
          setBirthDate("");
          setGender("unspecified");
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

  const handleSave = async () => {
    if (!nickname.trim()) {
      setStatus("Никнейм не может быть пустым");
      return;
    }

    setSaving(true);
    setStatus(null);

    const payload = {
      name: nickname.trim(),
      bio: about.trim() || null,
      birth_date: birthDate || null,
      gender,
    };

    try {
      const patchRes = await apiFetchJson<unknown>("/profile/me", {
        method: "PATCH",
        body: JSON.stringify(payload),
      });

      if (!patchRes.ok && patchRes.status === 404) {
        const putRes = await apiFetchJson<unknown>("/profile/me", {
          method: "PUT",
          body: JSON.stringify(payload),
        });
        setStatus(putRes.ok ? "Изменения сохранены" : putRes.error);
        return;
      }

      setStatus(patchRes.ok ? "Изменения сохранены" : patchRes.error);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    setDeleting(true);
    setStatus(null);
    try {
      const res = await apiFetchJson<unknown>("/auth/me", { method: "DELETE" });
      if (!res.ok) {
        setStatus(res.error || "Не удалось удалить аккаунт");
        return;
      }
      router.push("/");
      router.refresh();
    } finally {
      setDeleting(false);
    }
  };

  const canConfirmDelete = deleteConfirmText.trim().toLowerCase() === "удалить аккаунт";

  const openDeleteModal = () => {
    setDeleteConfirmText("");
    setDeleteModalRendered(true);
    requestAnimationFrame(() => setDeleteModalVisible(true));
  };

  const closeDeleteModal = () => {
    setDeleteModalVisible(false);
    window.setTimeout(() => {
      setDeleteModalRendered(false);
    }, 220);
  };

  const openBirthDatePicker = () => {
    if (birthDate) {
      const parsedDate = new Date(`${birthDate}T00:00:00`);
      if (!Number.isNaN(parsedDate.getTime())) {
        setCalendarMonth(parsedDate.getMonth());
        setCalendarYear(parsedDate.getFullYear());
      }
    }
    setBirthDatePickerOpen(true);
  };

  const formatBirthDateLabel = (value: string) => {
    if (!value) return "Выберите дату";
    const parsed = new Date(`${value}T00:00:00`);
    if (Number.isNaN(parsed.getTime())) return "Выберите дату";
    return parsed.toLocaleDateString("ru-RU", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-[#0b0b0b] text-white">
        <Header onOpenAuth={() => undefined} />
        <div className="mx-auto max-w-[1280px] px-4 py-10 text-white/60">Загрузка настроек...</div>
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
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-[#b7d4ff] to-[#6fc3a2] font-bold text-white">
                {initials}
              </div>
              <div className="min-w-0">
                <div className="truncate text-sm font-semibold text-white/95">{displayName}</div>
              </div>
            </div>

            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-1">
              <NavItem icon={<UserRound size={16} />} title="Профиль" desc="Никнейм, о себе, день рождения, пол" active />
              <NavItem icon={<Lock size={16} />} title="Безопасность и вход в аккаунт" desc="Смена почты и пароля, 2fa" />
              <NavItem icon={<Bell size={16} />} title="Уведомления" desc="Получение наград и активности" />
              <NavItem icon={<ShieldBan size={16} />} title="Блокировки" desc="Аккаунтов, комментариев и постов" />
            </div>

            <button
              onClick={openDeleteModal}
              disabled={deleting}
              className="mt-3 w-full rounded-xl border border-red-500/30 bg-red-500/10 py-2.5 text-sm font-semibold text-red-400 transition-colors hover:bg-red-500/20 disabled:opacity-60"
            >
              {deleting ? "Удаляем..." : "Деактивация"}
            </button>
          </aside>

          <section className="rounded-2xl border border-white/10 bg-[#171717] p-4 sm:p-5 lg:p-6">
            <div className="grid gap-4 md:grid-cols-[196px_minmax(0,1fr)]">
              <div>
                <div className="mb-2 text-sm font-semibold text-white/85">Аватарка</div>
                <div className="relative h-44 w-full overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-[#a6bf79] to-[#6ead72]">
                  <button className="absolute right-2 top-2 rounded-full bg-[#131722] px-3 py-1 text-xs font-semibold text-white/90">
                    Изменить
                  </button>
                  <div className="grid h-full place-items-center text-xl font-semibold text-white/85">{initials}</div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="mb-1.5 block text-sm font-semibold text-white/85">Никнейм</label>
                  <input
                    value={nickname}
                    onChange={(e) => setNickname(e.target.value)}
                    className="h-11 w-full rounded-xl border border-white/10 bg-[#101010] px-4 text-sm text-white outline-none transition-colors focus:border-sky-500/50"
                    placeholder="Введите никнейм"
                    maxLength={100}
                  />
                  <p className="mt-1 text-xs text-white/45">Допустимы буквы, цифры и символы @ . / + - _</p>
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-semibold text-white/85">О себе</label>
                  <textarea
                    value={about}
                    onChange={(e) => setAbout(e.target.value)}
                    className="min-h-28 w-full rounded-xl border border-white/10 bg-[#101010] px-4 py-3 text-sm text-white outline-none transition-colors focus:border-sky-500/50"
                    placeholder="Расскажите немного о себе"
                    maxLength={500}
                  />
                </div>

                <div>
                  <label className="mb-1.5 block text-sm font-semibold text-white/85">День рождения</label>
                  <div className="relative w-full max-w-xs">
                    <button
                      type="button"
                      onClick={openBirthDatePicker}
                      className="inline-flex h-11 items-center gap-2 rounded-full border border-white/10 bg-[#202020] px-4 text-sm font-semibold text-white/90 transition-colors hover:bg-[#272727]"
                    >
                      {formatBirthDateLabel(birthDate)}
                    </button>

                    {birthDatePickerOpen ? (
                      <DatePickerPanel
                        month={calendarMonth}
                        year={calendarYear}
                        selectedDate={birthDate}
                        onMonthChange={setCalendarMonth}
                        onYearChange={setCalendarYear}
                        onSelectDate={(value) => {
                          setBirthDate(value);
                          setBirthDatePickerOpen(false);
                        }}
                        onClose={() => setBirthDatePickerOpen(false)}
                      />
                    ) : null}
                  </div>
                  <p className="mt-1 text-xs text-white/45">Можно указать только один раз.</p>
                </div>

                <RadioGroup
                  label="Пол"
                  value={gender}
                  options={[
                    { value: "unspecified", label: "Не определено" },
                    { value: "male", label: "Мужской" },
                    { value: "female", label: "Женский" },
                  ]}
                  onChange={(value) => setGender(value as Gender)}
                />

                <div className="space-y-3 border-t border-white/10 pt-4">
                  <ToggleRow
                    title="Разрешать предлагать обмены"
                    description="Если выключить, вам не смогут предложить обмен карточками."
                    enabled={allowExchanges}
                    onChange={setAllowExchanges}
                  />
                  <ToggleRow
                    title="Закрытый профиль"
                    description="Другие увидят только базовую информацию профиля."
                    enabled={privateProfile}
                    onChange={setPrivateProfile}
                  />
                  <ToggleRow
                    title="Расширенный каталог"
                    description="Показывать произведения с внешних источников."
                    enabled={extendedCatalog}
                    onChange={setExtendedCatalog}
                  />
                </div>

                {status ? (
                  <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white/80">{status}</div>
                ) : null}

                <div className="pt-1">
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="rounded-full bg-[#3b82f6] px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#2563eb] disabled:opacity-60"
                  >
                    {saving ? "Сохраняем..." : "Сохранить изменения"}
                  </button>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>

      {deleteModalRendered ? (
        <div className="fixed inset-0 z-[70] flex items-center justify-center p-4">
          <button
            type="button"
            className={`absolute inset-0 bg-black/70 backdrop-blur-sm transition-opacity duration-200 ${
              deleteModalVisible ? "opacity-100" : "opacity-0"
            }`}
            onClick={closeDeleteModal}
            aria-label="Закрыть окно удаления"
          />

          <div
            className={`relative w-full max-w-[560px] rounded-3xl border border-white/10 bg-[#131a25] px-5 py-5 shadow-[0_30px_120px_rgba(0,0,0,0.65)] transition-all duration-200 sm:px-7 ${
              deleteModalVisible ? "translate-y-0 scale-100 opacity-100" : "translate-y-2 scale-[0.98] opacity-0"
            }`}
          >
            <button
              type="button"
              onClick={closeDeleteModal}
              className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-white/5 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
              aria-label="Закрыть"
            >
              <X size={16} />
            </button>

            <div className="text-center">
              <h3 className="text-2xl font-bold text-white">Удалить аккаунт? 🥺</h3>
              <p className="mx-auto mt-3 max-w-[420px] text-sm text-white/70 sm:text-base">
                В дальнейшем восстановление аккаунта будет возможно только через модерацию.
              </p>
              <p className="mt-5 text-sm font-semibold text-white/80">Введите "удалить аккаунт" для подтверждения</p>
            </div>

            <div className="mt-3">
              <input
                value={deleteConfirmText}
                onChange={(e) => setDeleteConfirmText(e.target.value)}
                placeholder='Напишите "удалить аккаунт"'
                className="h-12 w-full rounded-2xl border border-white/10 bg-white/5 px-4 text-sm text-white outline-none transition-colors placeholder:text-white/35 focus:border-red-400/50 focus:bg-white/10"
              />
            </div>

            <div className="mt-5 flex flex-col gap-2 sm:flex-row sm:justify-center">
              <button
                type="button"
                onClick={closeDeleteModal}
                className="rounded-full bg-white/8 px-6 py-2.5 text-sm font-semibold text-white/85 transition-colors hover:bg-white/15"
              >
                Назад
              </button>
              <button
                type="button"
                onClick={() => {
                  if (!canConfirmDelete || deleting) {
                    return;
                  }
                  closeDeleteModal();
                  void handleDeleteAccount();
                }}
                disabled={!canConfirmDelete || deleting}
                className="rounded-full bg-[#c53d3d] px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#b23333] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {deleting ? "Удаляем..." : "Подтвердить удаление"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </main>
  );
}

function DatePickerPanel({
  month,
  year,
  selectedDate,
  onMonthChange,
  onYearChange,
  onSelectDate,
  onClose,
}: {
  month: number;
  year: number;
  selectedDate: string;
  onMonthChange: (nextMonth: number) => void;
  onYearChange: (nextYear: number) => void;
  onSelectDate: (value: string) => void;
  onClose: () => void;
}) {
  const firstDay = new Date(year, month, 1);
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const weekDayOffset = (firstDay.getDay() + 6) % 7;

  const daysInPrevMonth = new Date(year, month, 0).getDate();
  const cells: Array<{ day: number; monthOffset: -1 | 0 | 1 }> = [];

  for (let i = weekDayOffset - 1; i >= 0; i -= 1) {
    cells.push({ day: daysInPrevMonth - i, monthOffset: -1 });
  }

  for (let day = 1; day <= daysInMonth; day += 1) {
    cells.push({ day, monthOffset: 0 });
  }

  while (cells.length % 7 !== 0 || cells.length < 42) {
    const day = cells.length - (weekDayOffset + daysInMonth) + 1;
    cells.push({ day, monthOffset: 1 });
  }

  const selected = selectedDate ? new Date(`${selectedDate}T00:00:00`) : null;
  const isSelected = (day: number, offset: -1 | 0 | 1) => {
    if (!selected) return false;
    return (
      selected.getFullYear() === year &&
      selected.getMonth() === month + offset &&
      selected.getDate() === day
    );
  };

  const toDateValue = (day: number, offset: -1 | 0 | 1) => {
    const d = new Date(year, month + offset, day);
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const dd = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${dd}`;
  };

  const goPrevMonth = () => {
    if (month === 0) {
      onMonthChange(11);
      onYearChange(year - 1);
      return;
    }
    onMonthChange(month - 1);
  };

  const goNextMonth = () => {
    if (month === 11) {
      onMonthChange(0);
      onYearChange(year + 1);
      return;
    }
    onMonthChange(month + 1);
  };

  const years = Array.from({ length: 101 }, (_, idx) => new Date().getFullYear() - 80 + idx);

  return (
    <div className="absolute left-0 top-[52px] z-30 w-[290px] rounded-3xl border border-white/10 bg-[#131722] p-4 shadow-[0_20px_70px_rgba(0,0,0,0.55)]">
      <div className="mb-3 flex items-center justify-between">
        <button
          type="button"
          onClick={goPrevMonth}
          className="rounded-full p-1.5 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
          aria-label="Предыдущий месяц"
        >
          <ChevronLeft size={16} />
        </button>
        <div className="text-sm font-semibold text-white/90">{RU_MONTHS[month]} {year}</div>
        <button
          type="button"
          onClick={goNextMonth}
          className="rounded-full p-1.5 text-white/60 transition-colors hover:bg-white/10 hover:text-white"
          aria-label="Следующий месяц"
        >
          <ChevronRight size={16} />
        </button>
      </div>

      <div className="mb-3 grid grid-cols-2 gap-2">
        <div className="relative">
          <select
            value={month}
            onChange={(e) => onMonthChange(Number(e.target.value))}
            className="h-9 w-full appearance-none rounded-full border border-white/10 bg-[#1a1f2b] px-3 text-sm text-white/90 outline-none"
          >
            {RU_MONTHS.map((m, idx) => (
              <option key={m} value={idx}>
                {m}
              </option>
            ))}
          </select>
          <ChevronDown size={14} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-white/50" />
        </div>

        <div className="relative">
          <select
            value={year}
            onChange={(e) => onYearChange(Number(e.target.value))}
            className="h-9 w-full appearance-none rounded-full border border-white/10 bg-[#1a1f2b] px-3 text-sm text-white/90 outline-none"
          >
            {years.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
          <ChevronDown size={14} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-white/50" />
        </div>
      </div>

      <div className="mb-2 grid grid-cols-7 gap-1.5 text-center text-xs uppercase text-white/45">
        {WEEKDAY_SHORT.map((label) => (
          <div key={label}>{label}</div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1.5">
        {cells.map((cell, index) => {
          const muted = cell.monthOffset !== 0;
          const selectedCell = isSelected(cell.day, cell.monthOffset);
          return (
            <button
              type="button"
              key={`${cell.monthOffset}-${cell.day}-${index}`}
              onClick={() => onSelectDate(toDateValue(cell.day, cell.monthOffset))}
              className={`h-8 w-8 rounded-full text-sm transition-colors ${
                selectedCell
                  ? "bg-[#2f5ec6] text-white"
                  : muted
                    ? "text-white/25 hover:bg-white/5"
                    : "text-white/85 hover:bg-white/10"
              }`}
            >
              {cell.day}
            </button>
          );
        })}
      </div>

      <div className="mt-3 flex justify-end">
        <button
          type="button"
          onClick={onClose}
          className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-white/80 transition-colors hover:bg-white/10"
        >
          Закрыть
        </button>
      </div>
    </div>
  );
}

function NavItem({
  icon,
  title,
  desc,
  active = false,
}: {
  icon: React.ReactNode;
  title: string;
  desc: string;
  active?: boolean;
}) {
  return (
    <button
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

function RadioGroup({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: Array<{ value: string; label: string }>;
  onChange: (value: string) => void;
}) {
  return (
    <div>
      <div className="mb-2 text-sm font-semibold text-white/85">{label}</div>
      <div className="space-y-2">
        {options.map((item) => (
          <label key={item.value} className="flex cursor-pointer items-center gap-2.5 text-sm text-white/80">
            <input
              type="radio"
              name={label}
              value={item.value}
              checked={value === item.value}
              onChange={(e) => onChange(e.target.value)}
              className="h-4 w-4 accent-[#3b82f6]"
            />
            {item.label}
          </label>
        ))}
      </div>
    </div>
  );
}

function ToggleRow({
  title,
  description,
  enabled,
  onChange,
}: {
  title: string;
  description: string;
  enabled: boolean;
  onChange: (next: boolean) => void;
}) {
  return (
    <div className="flex items-start justify-between gap-4">
      <div>
        <div className="text-sm font-medium text-white/88">{title}</div>
        <div className="text-xs text-white/45">{description}</div>
      </div>
      <button
        type="button"
        onClick={() => onChange(!enabled)}
        className={`relative h-7 w-12 flex-shrink-0 rounded-full transition-colors ${enabled ? "bg-[#3b82f6]" : "bg-white/15"}`}
        aria-label={title}
      >
        <span
          className={`absolute top-0.5 h-6 w-6 rounded-full bg-[#0f141f] transition-transform ${enabled ? "translate-x-5" : "translate-x-0.5"}`}
        />
      </button>
    </div>
  );
}