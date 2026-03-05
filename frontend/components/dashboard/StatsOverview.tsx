"use client";
import React, { useEffect, useState } from 'react';

interface BalanceData {
  total_usd: number;
  balances: Record<string, { balance: number; usd_value: number }>;
}

export default function StatsOverview() {
  const [data, setData] = useState<BalanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBalance = async () => {
      try {
        // Get the session from localStorage (stored by dashboard)
        const session = localStorage.getItem('nova_session');
        
        if (!session) {
          setError("Not connected. Please login via Bybit.");
          setLoading(false);
          return;
        }

        // Fetch balance using the session as Bearer token
        const res = await fetch('/api/v1/balance', {
          headers: {
            'Authorization': `Bearer ${session}`
          }
        });

        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }

        const result = await res.json();
        
        if (result.success) {
          setData({
            total_usd: result.total_usd,
            balances: result.balances
          });
        } else {
          setError(result.error || "Failed to fetch balance");
        }
      } catch (err) {
        console.error("Balance fetch error:", err);
        setError("Could not connect to Thor Engine");
      } finally {
        setLoading(false);
      }
    };

    fetchBalance();
    // Refresh every 30 seconds
    const interval = setInterval(fetchBalance, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1,2,3].map((i) => (
          <div key={i} className="bg-slate-800/50 border border-slate-700 p-6 rounded-2xl animate-pulse">
            <div className="h-4 bg-slate-700 rounded w-24 mb-4"></div>
            <div className="h-8 bg-slate-700 rounded w-32"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/20 p-6 rounded-2xl">
        <p className="text-red-400 text-center">{error}</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Total Equity Card */}
      <div className="bg-slate-800/50 border border-slate-700 p-6 rounded-2xl">
        <p className="text-slate-400 text-sm mb-2">Total Equity (USD)</p>
        <h3 className="text-3xl font-bold text-white">
          ${data?.total_usd?.toFixed(2) || "0.00"}
        </h3>
        <p className="text-xs text-slate-500 mt-2">Across {Object.keys(data?.balances || {}).length} assets</p>
      </div>

      {/* Active Warrior Bots Card */}
      <div className="bg-slate-800/50 border border-slate-700 p-6 rounded-2xl">
        <p className="text-slate-400 text-sm mb-2">Active Warrior Bots</p>
        <h3 className="text-3xl font-bold text-blue-400">Running</h3>
        <p className="text-xs text-slate-500 mt-2">Thor Engine v5.6</p>
      </div>

      {/* Broker ID Card */}
      <div className="bg-slate-800/50 border border-slate-700 p-6 rounded-2xl">
        <p className="text-slate-400 text-sm mb-2">Broker ID Status</p>
        <h3 className="text-3xl font-bold text-green-400">Kr000820</h3>
        <p className="text-xs text-slate-500 mt-2">Level 3 • Rebates Active</p>
      </div>
    </div>
  );
}
