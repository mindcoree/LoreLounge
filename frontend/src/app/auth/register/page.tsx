"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import AuthModal from "@/components/AuthModal";

export default function RegisterPage() {
  const router = useRouter();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(true);

  useEffect(() => {
    router.replace("/");
  }, [router]);

  return (
    <>
      <Header onOpenAuth={() => setIsAuthModalOpen(true)} />
      <main className="min-h-screen bg-[#0d0d0d] text-white" />
      <AuthModal isOpen={isAuthModalOpen} onClose={() => { setIsAuthModalOpen(false); router.push("/"); }} />
    </>
  );
}