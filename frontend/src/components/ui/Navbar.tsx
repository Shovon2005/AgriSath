'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Sprout, History, PlusCircle, Wifi, WifiOff } from 'lucide-react';
import { api } from '@/lib/api';

export function Navbar() {
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');
  const [apiVersion, setApiVersion] = useState<string>('');

  useEffect(() => {
    let isMounted = true;
    const verifyConnection = async () => {
      try {
        const res = await api.checkHealth();
        if (isMounted) {
          if (res.status === 'healthy' || res.status === 'success' || res.model_loaded) {
            setApiStatus('connected');
            setApiVersion(res.version ? `v${res.version}` : 'v1.0.0');
          } else {
            setApiStatus('disconnected');
          }
        }
      } catch {
        if (isMounted) {
          setApiStatus('disconnected');
        }
      }
    };

    verifyConnection();
    const interval = setInterval(verifyConnection, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

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

          {/* Live Communication Status Badge */}
          {apiStatus === 'connected' ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200/70 text-emerald-800 text-xs font-bold shadow-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <Wifi className="w-3.5 h-3.5 text-emerald-600" />
              <span className="hidden sm:inline">Backend Linked {apiVersion && `(${apiVersion})`}</span>
              <span className="sm:hidden">Linked</span>
            </div>
          ) : apiStatus === 'checking' ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-50 border border-amber-200/70 text-amber-800 text-xs font-bold shadow-xs">
              <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <span className="hidden sm:inline">Connecting API...</span>
              <span className="sm:hidden">Connecting</span>
            </div>
          ) : (
            <div
              className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-rose-50 border border-rose-200/70 text-rose-800 text-xs font-bold shadow-xs"
              title="Ensure Flask backend is running on http://127.0.0.1:5001"
            >
              <WifiOff className="w-3.5 h-3.5 text-rose-600" />
              <span className="hidden sm:inline">Backend Offline (Port 5001)</span>
              <span className="sm:hidden">Offline</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
