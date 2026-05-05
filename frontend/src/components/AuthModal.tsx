"use client";

import { useState } from "react";
import { X, Mail, Lock } from "lucide-react";
import { apiFetchJson } from "@/lib/apiClient";

type AuthMode = "login" | "register" | "forgot";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [mode, setMode] = useState<AuthMode>("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ email: "", password: "", confirmPassword: "" });

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (mode === "register" && form.password !== form.confirmPassword) {
      setError("Пароли не совпадают");
      setLoading(false);
      return;
    }

    try {
      if (mode === "login") {
        const res = await apiFetchJson<{ access: string; refresh: string }>("/auth/login", {
          method: "POST",
          form: {
            email: form.email,
            password: form.password,
          },
        });

        if (res.ok) {
          window.location.reload();
        } else {
          setError(res.error || "Ошибка входа");
        }
      } else if (mode === "register") {
        const res = await apiFetchJson<{ id: string }>("/auth/register", {
          method: "POST",
          form: {
            email: form.email,
            password: form.password,
            login: form.email.split("@")[0],
          },
        });

        if (res.ok) {
          setMode("login");
          setError(null);
          alert("Аккаунт создан! Теперь войдите.");
        } else {
          setError(res.error || "Ошибка регистрации");
        }
      } else if (mode === "forgot") {
        const res = await apiFetchJson<{ detail: string }>("/auth/password-reset-request", {
          method: "POST",
          body: JSON.stringify({ email: form.email }),
        });

        if (res.ok) {
          alert("Если email зарегистрирован, инструкция отправлена.");
          setMode("login");
        } else {
          setError(res.error || "Ошибка");
        }
      }
    } catch {
      setError("Произошла ошибка");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
      
      <div className="relative bg-[#0d0d0d] w-full max-w-md sm:max-w-md rounded-[32px] p-6 sm:p-8 border border-white/5 shadow-2xl">
        <button onClick={onClose} className="absolute right-4 top-4 sm:right-6 sm:top-6 text-gray-300 hover:text-gray-100">
          <X size={20} />
        </button>

        {mode === "forgot" ? (
          <form onSubmit={handleSubmit} className="space-y-6">
            <h2 className="text-2xl font-bold text-center text-gray-100 mt-2">Забыли пароль?</h2>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
              <input 
                type="email" 
                placeholder="*Почта" 
                required
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="w-full bg-[#1a1a1a] border border-white/5 rounded-full py-2.5 sm:py-2.5 sm:py-3 pl-10 sm:pl-12 pr-4 text-gray-100 focus:border-blue-500 outline-none transition-all"
              />
            </div>
            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-[#3b82f6] hover:bg-[#2563eb] text-gray-100 py-2.5 sm:py-3 rounded-full font-bold transition-all disabled:opacity-50"
            >
              {loading ? "Отправляем..." : "Отправить письмо"}
            </button>
            <p className="text-center text-gray-300 text-sm">
              Помните свой пароль?{" "}
              <button type="button" onClick={() => { setMode("login"); setError(null); }} className="text-blue-500 hover:underline">
                Войти
              </button>
            </p>
          </form>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <h2 className="text-2xl font-bold text-center text-gray-100 mt-2">
              {mode === "login" ? "Войти в аккаунт" : "Регистрация"}
            </h2>
            
            <div className="space-y-3">
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                <input 
                  type="text" 
                  placeholder={mode === "login" ? "*Логин/почта" : "*Почта"}
                  required
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="w-full bg-[#1a1a1a] border border-white/5 rounded-full py-2.5 sm:py-2.5 sm:py-3 pl-10 sm:pl-12 pr-4 text-gray-100 focus:border-blue-500 outline-none transition-all"
                />
              </div>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                <input 
                  type="password" 
                  placeholder="*Пароль" 
                  required
                  minLength={8}
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  className="w-full bg-[#1a1a1a] border border-white/5 rounded-full py-2.5 sm:py-2.5 sm:py-3 pl-10 sm:pl-12 pr-4 text-gray-100 focus:border-blue-500 outline-none transition-all"
                />
              </div>
              {mode === "register" && (
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                  <input 
                    type="password" 
                    placeholder="*Повторите пароль" 
                    required
                    minLength={8}
                    value={form.confirmPassword}
                    onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
                    className="w-full bg-[#1a1a1a] border border-white/5 rounded-full py-2.5 sm:py-2.5 sm:py-3 pl-10 sm:pl-12 pr-4 text-gray-100 focus:border-blue-500 outline-none transition-all"
                  />
                </div>
              )}
            </div>

            {mode === "login" && (
              <div className="text-center">
                <button type="button" onClick={() => setMode("forgot")} className="text-blue-500 text-sm font-medium hover:underline">
                  Забыли пароль?
                </button>
              </div>
            )}

            {error && (
              <div className="p-3 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
                {error}
              </div>
            )}

            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-[#3b82f6] hover:bg-[#2563eb] text-gray-100 py-2.5 sm:py-3 rounded-full font-bold transition-all disabled:opacity-50"
            >
              {loading ? "Загрузка..." : mode === "login" ? "Войти" : "Создать аккаунт"}
            </button>

            <div className="relative flex items-center justify-center">
              <div className="border-t border-white/5 w-full"></div>
              <span className="bg-[#0d0d0d] px-4 text-gray-500 text-xs uppercase">или</span>
              <div className="border-t border-white/5 w-full"></div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <button type="button" className="flex justify-center items-center py-2.5 sm:py-3 bg-[#1a1a1a] hover:bg-[#2a2a2a] rounded-full transition-colors text-gray-300">
                <span className="text-sm font-medium">TG</span>
              </button>
              <button type="button" className="flex justify-center items-center py-2.5 sm:py-3 bg-[#1a1a1a] hover:bg-[#2a2a2a] rounded-full transition-colors text-gray-300">
                <span className="text-sm font-medium">YT</span>
              </button>
              <button type="button" className="flex justify-center items-center py-2.5 sm:py-3 bg-[#1a1a1a] hover:bg-[#2a2a2a] rounded-full transition-colors text-gray-300">
                <span className="text-sm font-medium">GH</span>
              </button>
            </div>

            <button type="button" className="w-full bg-[#0077FF] hover:bg-[#0066DD] text-gray-100 py-2.5 sm:py-3 rounded-full font-bold flex items-center justify-center gap-2 transition-all">
              <span className="bg-white text-[#0077FF] rounded px-1 text-xs font-black">VK</span> Войти с VK ID
            </button>

            <p className="text-center text-gray-300 text-sm">
              {mode === "login" ? "Нет учетной записи?" : "Уже есть аккаунт?"}{" "}
              <button 
                type="button"
                onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(null); }} 
                className="text-blue-500 hover:underline font-medium"
              >
                {mode === "login" ? "Зарегистрироваться" : "Войти"}
              </button>
            </p>

            <p className="text-[10px] text-center text-gray-500 leading-relaxed">
              Нажимая «Войти», вы принимаете{" "}
              <span className="text-blue-500">пользовательское соглашение</span> и{" "}
              <span className="text-blue-500">политику конфиденциальности</span>
            </p>
          </form>
        )}
      </div>
    </div>
  );
}