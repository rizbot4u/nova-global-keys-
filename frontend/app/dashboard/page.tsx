"use client";
import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import StatsOverview from '../../components/dashboard/StatsOverview';

// 1. This handles the searchParams logic
function DashboardContent() {
  const searchParams = useSearchParams();
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const session = searchParams.get('session');
    if (session) {
      localStorage.setItem('nova_session', session);
      window.history.replaceState({}, document.title, "/dashboard");
    }
    setIsReady(true);
  }, [searchParams]);

  if (!isReady) return <div className="text-slate-500">Loading Session...</div>;

  return (
    <div className="max-w-7xl mx-auto px-6">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-white">Warrior Dashboard</h1>
          <p className="text-slate-400 mt-2">Connected via Bybit Broker Level 3</p>
        </div>
        <div className="px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-lg">
          <span className="text-green-400 text-sm font-mono">System: Operational</span>
        </div>
      </header>
      <StatsOverview />
    </div>
  );
}

// 2. The main page wraps everything in Suspense to satisfy the build worker
export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-slate-900 pt-24">
      <Suspense fallback={
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="text-blue-400 animate-pulse font-mono">INITIALIZING WARRIOR INTERFACE...</div>
        </div>
      }>
        <DashboardContent />
      </Suspense>
    </div>
  );
}
