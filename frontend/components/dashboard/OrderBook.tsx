"use client";
import React, { useEffect, useState } from 'react';

interface Order {
  price: number;
  size: number;
}

export default function OrderBook() {
  const [asks, setAsks] = useState<Order[]>([]);
  const [bids, setBids] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrderBook = async () => {
      try {
        const res = await fetch('/api/v1/market/orderbook?symbol=BTCUSDT');
        const data = await res.json();
        if (data.result) {
          setAsks(data.result.asks.slice(0, 8).map((a: any[]) => ({ 
            price: parseFloat(a[0]), 
            size: parseFloat(a[1]) 
          })));
          setBids(data.result.bids.slice(0, 8).map((b: any[]) => ({ 
            price: parseFloat(b[0]), 
            size: parseFloat(b[1]) 
          })));
        }
      } catch (e) { 
        console.error(e);
        // Fallback mock data if API fails
        setAsks([
          { price: 64230.50, size: 1.24 },
          { price: 64229.00, size: 0.85 }
        ]);
        setBids([
          { price: 64225.00, size: 0.95 },
          { price: 64224.20, size: 1.15 }
        ]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchOrderBook();
    const interval = setInterval(fetchOrderBook, 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="text-gray-500 text-center py-4">Loading order book...</div>;

  return (
    <div className="text-[11px] font-mono">
      <div className="flex justify-between text-gray-500 mb-1 px-2 border-b border-gray-800 pb-1">
        <span>Price (USDT)</span>
        <span>Size (BTC)</span>
      </div>
      {/* Asks */}
      <div className="space-y-[2px] mb-2">
        {asks.map((ask, i) => (
          <div key={i} className="flex justify-between px-2 text-red-500 hover:bg-red-500/10 cursor-pointer">
            <span>{ask.price.toFixed(1)}</span>
            <span className="text-gray-300">{ask.size.toFixed(3)}</span>
          </div>
        ))}
      </div>
      {/* Bids */}
      <div className="space-y-[2px]">
        {bids.map((bid, i) => (
          <div key={i} className="flex justify-between px-2 text-green-500 hover:bg-green-500/10 cursor-pointer">
            <span>{bid.price.toFixed(1)}</span>
            <span className="text-gray-300">{bid.size.toFixed(3)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
