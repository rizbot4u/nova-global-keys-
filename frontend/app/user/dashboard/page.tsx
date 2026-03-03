"use client";
import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';

// 1. Create a sub-component for the actual logic
function DashboardContent() {
  const searchParams = useSearchParams();
  const session = searchParams.get('session');
  const [balance, setBalance] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (session) {
      localStorage.setItem('nova_session', session);
      fetchBalance();
    }
  }, [session]);

  const fetchBalance = async () => {
    try {
      const res = await fetch('/api/v1/balance', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('nova_session')}` }
      });
      const data = await res.json();
      setBalance(data);
    } catch (error) {
      console.error('Failed to fetch balance');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="text-white p-8">Loading your wallet...</div>;

  return (
    <div className="min-h-screen bg-slate-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-8">Your Trading Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-800 p-6 rounded-xl">
          <p className="text-slate-400">Total Balance</p>
          <p className="text-2xl font-bold">${balance?.total_usd || '0.00'}</p>
        </div>
        <div className="bg-slate-800 p-6 rounded-xl">
          <p className="text-slate-400">Active Bots</p>
          <p className="text-2xl font-bold">3</p>
        </div>
        <div className="bg-slate-800 p-6 rounded-xl">
          <p className="text-slate-400">Today's PnL</p>
          <p className="text-2xl font-bold text-green-400">+$124.50</p>
        </div>
      </div>
    </div>
  );
}

// 2. The main export wraps everything in Suspense
export default function UserDashboard() {
  return (
    <Suspense fallback={<div className="text-white p-8">Initializing Dashboard...</div>}>
      <DashboardContent />
    </Suspense>
  );
}
