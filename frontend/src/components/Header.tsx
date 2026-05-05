"use client";

import { useEffect, useState } from "react";
import { Search, Bell, MoreHorizontal, LayoutGrid, Trophy, MessageSquare, ChevronDown, Menu } from "lucide-react";
import ProfileMenu from "./ProfileMenu";
import { apiFetchJson } from "@/lib/apiClient";

interface UserData {
  id: string;
  email: string;
}

const Header = ({ onOpenAuth }: { onOpenAuth?: () => void }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<UserData | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  // Проверяем аутентификацию при загрузке
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const result = await apiFetchJson<UserData>("/auth/me");
        if (result.ok) {
          setUser(result.data);
          setIsAuthenticated(true);
        }
      } finally {
        setCheckingAuth(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogout = () => {
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <header className="w-full bg-[#0d0d0d] text-white sticky top-0 z-50">
      <div className="max-w-[1440px] mx-auto w-full px-4 py-3 flex items-center justify-between gap-2">
        
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center cursor-pointer transition-transform active:scale-95">
            <span className="text-black font-bold text-xl leading-none">L</span>
          </div>

          <nav className="hidden xl:flex items-center gap-2">
            <button className="relative inline-flex items-center justify-center box-border appearance-none select-none whitespace-nowrap font-medium subpixel-antialiased transition-all tap-highlight-transparent rounded-full h-9 text-sm text-gray-300 bg-[#1a1a1a] hover:bg-[#252525] data-[pressed=true]:scale-[0.97] py-2 px-5">
              <LayoutGrid size={18} className="mr-2" />
              <span>Каталог</span>
              <ChevronDown size={14} className="ml-1 opacity-50" />
            </button>
            
            <button className="relative inline-flex items-center justify-center box-border appearance-none select-none whitespace-nowrap font-medium subpixel-antialiased transition-all tap-highlight-transparent rounded-full h-9 text-sm text-gray-300 bg-[#1a1a1a] hover:bg-[#252525] data-[pressed=true]:scale-[0.97] py-2 px-5">
              <Trophy size={18} className="mr-2" />
              <span>Топы</span>
            </button>
            
            <button className="relative inline-flex items-center justify-center box-border appearance-none select-none whitespace-nowrap font-medium subpixel-antialiased transition-all tap-highlight-transparent rounded-full h-9 text-sm text-gray-300 bg-[#1a1a1a] hover:bg-[#252525] data-[pressed=true]:scale-[0.97] py-2 px-5">
              <MessageSquare size={18} className="mr-2" />
              <span>Форум</span>
            </button>

            <div className="w-[1px] h-6 bg-white/10 mx-1" />

            <button className="relative p-2.5 inline-flex items-center justify-center box-border appearance-none select-none whitespace-nowrap font-medium subpixel-antialiased transition-all tap-highlight-transparent rounded-full h-9 text-sm text-gray-300 bg-[#1a1a1a] hover:bg-[#252525] data-[pressed=true]:scale-[0.97]">
              <MoreHorizontal size={20} />
            </button>
          </nav>
          
          <button className="xl:hidden p-2 bg-[#1a1a1a] rounded-full">
            <Menu size={20} />
          </button>
        </div>

        <div className="hidden sm:flex flex-1 max-w-xl mx-2 lg:mx-6">
          <div className="relative group w-full">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-blue-500 transition-colors" size={18} />
            <input 
              type="text" 
              placeholder="Что ищем, семпай?" 
              className="w-full bg-[#1a1a1a] border border-transparent focus:border-white/10 rounded-full py-2.5 pl-12 pr-4 text-sm outline-none transition-all placeholder:text-gray-500 focus:bg-[#222]"
            />
          </div>
        </div>

        <div className="flex items-center gap-2 lg:gap-4">
          <button className="relative text-gray-400 hover:text-white transition-colors p-2 group">
            <Bell size={24} />
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-blue-500 text-white text-xs font-bold rounded-full flex items-center justify-center group-hover:bg-blue-600 transition-colors">2</span>
          </button>

          {!checkingAuth && (
            isAuthenticated ? (
              <ProfileMenu isAuthenticated={isAuthenticated} onLogout={handleLogout} />
            ) : (
              <button 
                onClick={onOpenAuth}
                className="bg-[#3b82f6] hover:bg-[#2563eb] text-white px-4 lg:px-7 py-2 lg:py-2.5 rounded-full font-bold text-xs lg:text-sm transition-all shadow-lg shadow-blue-500/10 active:scale-95"
              >
                <span className="hidden lg:inline">Вход / Регистрация</span>
                <span className="lg:hidden">Вход</span>
              </button>
            )
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;