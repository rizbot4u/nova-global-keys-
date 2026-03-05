"use client";

import React, { useEffect, useState } from 'react';
import { Server, Trash2, CheckCircle2, Globe } from 'lucide-react';

interface Exchange {
  id: number;
  exchange_name: string;
  api_key_preview: string; // e.g., "XXXX-1234"
}

export default function ExchangesList() {
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchExchanges = async () => {
      const token = localStorage.getItem('token');
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/keys/list`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setExchanges(data);
      } catch (err) {
        console.error("Failed to fetch soul data", err);
      } finally {
        setLoading(false);
      }
    };

    fetchExchanges();
  }, []);

  if (loading) return <div className="text-slate-500 animate-pulse">Scanning the vault...</div>;

  return (
    <div className="space-y-4">
      <h3 className="text-white font-semibold flex items-center gap-2">
        <Globe size={18} className="text-blue-400" />
        Your Active Connections
      </h3>
      
      {exchanges.length === 0 ? (
        <p className="text-slate-500 text-sm italic">No exchanges connected yet.</p>
      ) : (
        exchanges.map((ex) => (
          <div key={ex.id} className="flex items-center justify-between p-4 bg-slate-900/80 border border-slate-800 rounded-xl hover:border-blue-500/30 transition-all">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center text-blue-400 border border-slate-700">
                <Server size={20} />
              </div>
              <div>
                <p className="text-white font-medium">{ex.exchange_name}</p>
                <p className="text-xs text-slate-500 font-mono">{ex.api_key_preview}</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] bg-green-500/10 text-green-400 px-2 py-1 rounded-full border border-green-500/20 flex items-center gap-1">
                <CheckCircle2 size={10} /> Online
              </span>
              <button className="p-2 text-slate-500 hover:text-red-400 transition-colors">
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
