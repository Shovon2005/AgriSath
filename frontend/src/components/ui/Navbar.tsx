import React from 'react';
import Link from 'next/link';
import { Sprout, History, PlusCircle } from 'lucide-react';

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full bg-white/90 backdrop-blur-md border-b border-emerald-100/80 transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-agri-600 to-emerald-400 text-white flex items-center justify-center shadow-md shadow-agri-600/25 group-hover:scale-105 transition-transform duration-200">
            <Sprout className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xl font-extrabold text-agri-900 tracking-tight leading-none block">
              AgriSathi
            </span>
            <span className="text-[11px] font-bold text-agri-600 uppercase tracking-wider block mt-0.5">
              Precision Agriculture
            </span>
          </div>
        </Link>

        <div className="flex items-center gap-3 sm:gap-5">
          <Link
            href="/"
            className="hidden sm:inline-flex items-center gap-1.5 text-xs font-bold text-slate-700 hover:text-agri-700 transition-colors"
          >
            <PlusCircle className="w-4 h-4 text-agri-600" />
            <span>New Advisory</span>
          </Link>

          <Link
            href="/history"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-700 hover:text-agri-700 transition-colors"
          >
            <History className="w-4 h-4 text-agri-600" />
            <span>Past Reports</span>
          </Link>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200/70 text-emerald-800 text-xs font-bold shadow-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="hidden sm:inline">AI Decision Engine</span>
            <span className="sm:hidden">Online</span>
          </div>
        </div>
      </div>
    </header>
  );
}
