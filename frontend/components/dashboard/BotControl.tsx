"use client";
import React, { useState, useEffect } from 'react';

interface BotControlProps {
  selectedBot?: any;
}

export default function BotControl({ selectedBot }: BotControlProps) {
  const [status, setStatus] = useState('IDLE');
  const [loading, setLoading] = useState(false);
  const [botName, setBotName] = useState('selectedBot?.name ? selectedBot.name.toUpperCase().replace(/\s+/g, "_") : "selectedBot?.name ? selectedBot.name.toUpperCase().replace(/\s+/g, "_") : "WARRIOR_V5""');

  // Use selectedBot if available
  useEffect(() => {
    if (selectedBot) {
      setBotName(selectedBot.name.toUpperCase().replace(/\s+/g, '_'));
    }
  }, [selectedBot]);

  const startWarrior = async () => {
    setLoading(true);
    const token = localStorage.getItem('nova_session');

    if (!token) {
      alert("No active session. Please re-login.");
      setLoading(false);
      return;
    }

    try {
      // Use dynamic bot name from selected bot
      const res = await fetch('/api/trade/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          bot_id: botName,
          symbol: 'BTCUSDT',
          broker: 'Kr000820'
        })
      });

      if (res.status === 200) {
        setStatus('RUNNING');
        console.log(`Thor Engine: ${botName} Activated`);
      } else if (res.status === 404) {
        alert("Path /api/trade/start not found. Trying fallback path...");
        const fallbackRes = await fetch('/api/v1/bots/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ bot_id: botName })
        });
        if (fallbackRes.ok) setStatus('RUNNING');
      } else {
        const errorMsg = await res.text();
        alert(`Failed to start: ${errorMsg || 'Check API permissions'}`);
      }
    } catch (err) {
      console.error("Connection Error:", err);
      alert("Terminal could not reach Thor Engine.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#161a1e] border border-gray-800 rounded-xl p-6 shadow-xl flex flex-col h-full">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xs font-black text-white uppercase tracking-widest">Bot Control</h2>
          <p className="text-[9px] text-gray-500 uppercase mt-1">Thor Engine Integration</p>
          {selectedBot && (
            <p className="text-[10px] text-blue-400 mt-2">Selected: {selectedBot.name}</p>
          )}
        </div>
        <div className="flex flex-col items-end">
          <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold tracking-tighter ${status === 'RUNNING' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'}`}>
            {status === 'RUNNING' ? '● LIVE' : '○ STANDBY'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-[10px] text-gray-500 uppercase font-bold block mb-1.5">Strategy</label>
          <select className="w-full bg-[#0b0e11] border border-gray-700 rounded p-2 text-xs text-white outline-none focus:border-blue-500/50 transition-colors">
            <option>Warrior V5 (Scalper)</option>
            <option>Guardian V2 (Trend)</option>
          </select>
        </div>
        <div>
          <label className="text-[10px] text-gray-500 uppercase font-bold block mb-1.5">Risk Level</label>
          <select className="w-full bg-[#0b0e11] border border-gray-700 rounded p-2 text-xs text-white outline-none focus:border-blue-500/50 transition-colors">
            <option>1.0x (Standard)</option>
            <option>2.0x (Aggressive)</option>
            <option>0.5x (Safe)</option>
          </select>
        </div>
      </div>

      <div className="mt-auto pt-6">
        <button
          onClick={startWarrior}
          disabled={loading || status === 'RUNNING'}
          className={`w-full py-3.5 rounded-lg font-black uppercase tracking-[0.2em] text-[10px] transition-all duration-300 ${
            status === 'RUNNING'
            ? 'bg-gray-800 text-gray-500 cursor-not-allowed border border-gray-700'
            : 'bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white shadow-lg shadow-blue-500/20 hover:scale-[1.01]'
          }`}
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Initializing...
            </span>
          ) : status === 'RUNNING' ? 'System Running' : 'Engage Warrior'}
        </button>
      </div>
    </div>
  );
}
