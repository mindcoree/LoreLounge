"use client";

import { useState } from "react";
import Header from "@/components/Header";
import AuthModal from "@/components/AuthModal";

export default function Home() {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  return (
    <>
      <div className="pointer-events-none absolute inset-0 -z-10 bg-[#0d0d0d]">
        <div className="absolute -left-20 -top-28 h-72 w-72 rounded-full bg-[#ffd28a] opacity-20 blur-3xl" />
        <div className="absolute bottom-0 right-0 h-96 w-96 rounded-full bg-[#3b82f6] opacity-15 blur-3xl" />
        <div className="absolute left-1/2 top-1/2 h-[420px] w-[420px] -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/5" />
      </div>

      <Header onOpenAuth={() => setIsAuthModalOpen(true)} />
      
      <main className="relative min-h-screen text-white">
        <div className="max-w-[1440px] mx-auto w-full px-4 py-12">
          <h1 className="text-3xl font-bold">Добро пожаловать в LoreLounge</h1>
          <p className="mt-2 text-gray-400">Платформа для чтения веб-новелл</p>
        </div>
      </main>

      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
    </>
  );
}