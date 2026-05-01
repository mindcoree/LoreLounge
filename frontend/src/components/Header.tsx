"use client";

import { Search, Moon, MoreHorizontal, LayoutGrid, Trophy, MessageSquare, ChevronDown, Menu } from "lucide-react";

const Header = ({ onOpenAuth }: { onOpenAuth?: () => void }) => {
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
          <button className="text-gray-400 hover:text-white transition-colors p-2">
            <Moon size={24} />
          </button>
          
          <button 
            onClick={onOpenAuth}
            className="bg-[#3b82f6] hover:bg-[#2563eb] text-white px-4 lg:px-7 py-2 lg:py-2.5 rounded-full font-bold text-xs lg:text-sm transition-all shadow-lg shadow-blue-500/10 active:scale-95"
          >
            <span className="hidden lg:inline">Вход / Регистрация</span>
            <span className="lg:hidden">Вход</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;