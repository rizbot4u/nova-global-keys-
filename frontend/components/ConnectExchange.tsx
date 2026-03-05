"use client";

import React, { useState } from 'react';
import { Key, ShieldCheck, Plus, AlertCircle } from 'lucide-react';

export default function ConnectExchange() {
  const [exchange, setExchange] = useState('Bybit');
  const [apiKey, setApiKey] = useState('');
  const [apiSecret, setApiSecret] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');

    try {
      const token = localStorage.getItem('token'); // Get the Brain's token
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/keys/connect`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify({ exchange, api_key: apiKey, api_secret: apiSecret }),
      });

      if (response.ok) {
        setStatus('success');
        setApiKey('');
        setApiSecret('');
      } else {
        setStatus('error');
      }
    } catch (err) {
      setStatus('error');
    }
  };

  return (
    <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-2xl max-w-lg">
      <div className="flex items-center space-x-3 mb-6">
        <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
          <Key size={24} />
        </div>
        <h2 className="text-xl font-bold text-white">Connect Exchange</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-slate-400 mb-2">Select Exchange</label>
          <select 
            className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-white outline-none focus:border-blue-500"
            value={exchange}
            onChange={(e) => setExchange(e.target.value)}
          >
            <option>Bybit</option>
            <option>Binance</option>
          </select>
        </div>

        <input
          type="text"
          placeholder="API Key"
          className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-white"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="API Secret"
          className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 text-white"
          value={apiSecret}
          onChange={(e) => setApiSecret(e.target.value)}
          required
        />

        <button
          type="submit"
          disabled={status === 'loading'}
          className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-xl transition-all flex items-center justify-center space-x-2"
        >
          {status === 'loading' ? 'Encrypting...' : <><Plus size={20} /> <span>Connect Wallet</span></>}
        </button>

        {status === 'success' && (
          <div className="flex items-center space-x-2 text-green-400 bg-green-400/10 p-3 rounded-lg">
            <ShieldCheck size={18} />
            <span>Exchange connected successfully!</span>
          </div>
        )}
      </form>
    </div>
  );
}
