"use client";
import React, { useEffect, useState } from 'react';

export default function StatsOverview() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const session = localStorage.getItem('nova_session');

        if (!session) {
          setError("No active session. Please login via Bybit.");
          setLoading(false);
          return;
        }

        const res = await fetch('/api/v1/balance', {
          headers: {
            'Authorization': `Bearer ${session}`
          }
        });

        const result = await res.json();
        
        // Handle your backend response structure
        if (res.ok) {
          setData(result);
        } else {
          setError(result.detail || "Failed to fetch stats");
        }
      } catch (err) {
        setError("Backend Connection Error");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="text-white animate-pulse">Scanning Bybit Wallet...</div>;
  if (error) return <div className="text-red-400 bg-red-500/10 p-4 rounded-lg">{error}</div>;

  // Calculate total from your response structure
  const total_usd = data?.data?.total_equity || data?.total_usd || 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="bg-slate-800/50 border border-slate-700 p-6 rounded-2xl">
        <p className="text-slate-400 text-sm">Total Equity (USD)</p>
        <h3 className="text-3xl font-bold text-white mt-2">
          ${typeof total_usd === 'number' ? total_usd.toFixed(2) : total_usd}
        </h3>
      </div>

      <div className="bg-slate-800/50 border border-slate-700 p-6 rounded-2xl">
        <p className="text-slate-400 text-sm">Active Warrior Bots</p>
        <h3 className="text-3xl font-bold text-blue-400 mt-2">Running</h3>
      </div>

      <div className="bg-slate-800/50 border border-slate-700 p-6 rounded-2xl">
        <p className="text-slate-400 text-sm">Broker ID Status</p>
        <h3 className="text-3xl font-bold text-green-400 mt-2">Kr000820</h3>
      </div>
    </div>
  );
}
