"use client";
import React, { useState } from 'react';
import { novaApi } from '@/lib/api';

export default function OrderPanel() {
  const [side, setSide] = useState<'Buy' | 'Sell'>('Buy');
  const [orderType, setOrderType] = useState('Limit');
  const [price, setPrice] = useState('');
  const [qty, setQty] = useState('');
  const [loading, setLoading] = useState(false);

  const handleTrade = async () => {
    setLoading(true);
    const token = localStorage.getItem('nova_session');
    
    // Constructing the Bybit V5 Payload
    const payload = {
      category: "spot",
      symbol: "BTCUSDT",
      side: side,
      orderType: orderType,
      qty: qty,
      price: orderType === 'Limit' ? price : undefined,
      timeInForce: "GTC"
    };

    try {
      const res = await fetch('/api/v1/trade/order', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        },
        body: JSON.stringify(payload)
      });
      
      const result = await res.json();
      if (result.retCode === 0) {
        alert(`Order Placed: ${side} ${qty} BTC`);
      } else {
        alert(`Order Failed: ${result.retMsg}`);
      }
    } catch (err) {
      console.error("Trade Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#161a1e] border border-gray-800 rounded-xl p-4 shadow-xl flex flex-col h-full">
      {/* BUY/SELL TOGGLE */}
      <div className="flex gap-1 bg-[#0b0e11] p-1 rounded-lg mb-4">
        <button 
          onClick={() => setSide('Buy')}
          className={`flex-1 py-2 rounded font-bold uppercase text-[10px] transition-all ${side === 'Buy' ? 'bg-green-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
        >
          Buy
        </button>
        <button 
          onClick={() => setSide('Sell')}
          className={`flex-1 py-2 rounded font-bold uppercase text-[10px] transition-all ${side === 'Sell' ? 'bg-red-600 text-white shadow-lg' : 'text-gray-500 hover:text-gray-300'}`}
        >
          Sell
        </button>
      </div>

      {/* ORDER SETTINGS */}
      <div className="space-y-4 flex-grow">
        <div className="flex justify-between items-center text-[10px] text-gray-500 uppercase font-bold">
          <span>Order Type</span>
          <div className="flex gap-3">
            {['Limit', 'Market'].map(t => (
              <span 
                key={t} 
                onClick={() => setOrderType(t)}
                className={`cursor-pointer transition-colors ${orderType === t ? 'text-blue-500' : 'hover:text-gray-300'}`}
              >{t}</span>
            ))}
          </div>
        </div>

        {/* PRICE INPUT (Hidden if Market) */}
        {orderType === 'Limit' && (
          <div>
            <div className="flex justify-between text-[9px] text-gray-500 mb-1 px-1">
              <span>Price</span>
              <span>USDT</span>
            </div>
            <input 
              type="number" 
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="w-full bg-[#0b0e11] border border-gray-700 rounded p-2 text-sm text-white outline-none focus:border-blue-500/50" 
              placeholder="0.00" 
            />
          </div>
        )}

        {/* QUANTITY INPUT */}
        <div>
          <div className="flex justify-between text-[9px] text-gray-500 mb-1 px-1">
            <span>Quantity</span>
            <span>BTC</span>
          </div>
          <input 
            type="number" 
            value={qty}
            onChange={(e) => setQty(e.target.value)}
            className="w-full bg-[#0b0e11] border border-gray-700 rounded p-2 text-sm text-white outline-none focus:border-blue-500/50" 
            placeholder="0.000" 
          />
        </div>

        {/* SLIDER PLACEHOLDER (Visual Only for now) */}
        <div className="flex justify-between gap-1 px-1">
          {[25, 50, 75, 100].map(pct => (
            <div key={pct} className="h-1 flex-1 bg-gray-800 rounded-full cursor-pointer hover:bg-gray-600 transition-colors"></div>
          ))}
        </div>
      </div>

      {/* EXECUTE BUTTON */}
      <div className="mt-6">
        <button 
          onClick={handleTrade}
          disabled={loading || !qty}
          className={`w-full py-4 rounded-lg font-black uppercase tracking-widest text-xs transition-all shadow-xl ${
            side === 'Buy' 
            ? 'bg-green-600 hover:bg-green-500 shadow-green-900/20' 
            : 'bg-red-600 hover:bg-red-500 shadow-red-900/20'
          } ${loading ? 'opacity-50 cursor-wait' : ''}`}
        >
          {loading ? 'Transmitting...' : `${side} BTC`}
        </button>
      </div>
    </div>
  );
}
