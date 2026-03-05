"use client";
import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import StatsOverview from '@/components/dashboard/StatsOverview';
import TradingChart from '@/components/dashboard/TradingChart';
import OrderBook from '@/components/dashboard/OrderBook';
import TopGainers from '@/components/dashboard/TopGainers';
import TickerTape from '@/components/dashboard/TickerTape';
import BotControl from '@/components/dashboard/BotControl';
import OrderPanel from '@/components/dashboard/OrderPanel';

function DashboardContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const session = searchParams.get('session');
    if (session) {
      // // localStorage.setItem('nova_session', session);
      window.history.replaceState({}, document.title, "/dashboard");
    }
    setIsReady(true);
  }, [searchParams]);

  const handleLogout = () => {
    localStorage.removeItem('nova_session');
    router.push('/');
    router.refresh();
  };

  if (!isReady) return (
    <div className="flex items-center justify-center min-h-screen bg-[#0b0e11]">
      <div className="text-blue-500 animate-pulse font-mono tracking-widest uppercase">
        Establishing Secure Link...
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0b0e11] text-white">
      <TickerTape />
      <div className="max-w-[1800px] mx-auto px-4 pb-10">
        <header className="flex justify-between items-center mb-6 py-4 border-b border-gray-800/50">
          <div>
            <h1 className="text-2xl font-black italic tracking-tighter text-white">
              NOVA<span className="text-blue-500">TERMINAL</span>
            </h1>
            <p className="text-[10px] text-gray-500 uppercase tracking-[0.2em]">
              Institutional Grade Execution v5.0
            </p>
          </div>
          <div className="flex items-center gap-6">
            <div className="hidden md:block text-right">
              <p className="text-[10px] text-gray-500 uppercase">System Status</p>
              <p className="text-xs font-bold text-green-500 flex items-center gap-1 justify-end">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-ping"></span> OPERATIONAL
              </p>
            </div>
            <button 
              onClick={handleLogout}
              className="px-4 py-2 bg-transparent border border-gray-700 hover:border-red-500/50 hover:text-red-500 text-gray-400 text-[10px] font-bold uppercase transition-all rounded"
            >
              Logout
            </button>
          </div>
        </header>

        <div className="mb-6">
          <StatsOverview />
        </div>

        <div className="grid grid-cols-12 gap-4">
          <aside className="col-span-12 lg:col-span-2 space-y-4">
            <div className="bg-[#161a1e] border border-gray-800 rounded-lg p-3">
              <h3 className="text-[10px] font-bold text-gray-500 uppercase mb-4 border-b border-gray-800 pb-2">
                Hot Markets
              </h3>
              <TopGainers />
            </div>
          </aside>

          <section className="col-span-12 lg:col-span-7 space-y-4">
            <div className="bg-[#161a1e] border border-gray-800 rounded-lg overflow-hidden shadow-2xl">
              <TradingChart />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <BotControl />
              <OrderPanel />
            </div>
          </section>

          <aside className="col-span-12 lg:col-span-3">
            <div className="bg-[#161a1e] border border-gray-800 rounded-lg p-1 h-full min-h-[600px] shadow-xl">
              <h3 className="text-[10px] font-bold text-gray-500 uppercase p-3 border-b border-gray-800 mb-2">
                Live Order Book (BTC/USDT)
              </h3>
              <OrderBook />
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-[#0b0e11] pt-16">
      <Suspense fallback={null}>
        <DashboardContent />
      </Suspense>
    </div>
  );
}
