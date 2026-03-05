"use client";
import React, { useEffect, useState } from 'react';

export default function TopGainers() {
  const [coins, setCoins] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTickers = async () => {
      try {
        const res = await fetch('/api/v1/market/tickers?category=spot');
        const data = await res.json();
        if (data.result?.list) {
          setCoins(data.result.list
            .filter((t: any) => t.symbol.endsWith('USDT'))
            .slice(0, 12)
            .map((t: any) => ({
              pair: t.symbol.replace('USDT', '/USDT'),
              price: parseFloat(t.lastPrice).toFixed(2),
              change: (parseFloat(t.price24hPcnt) * 100).toFixed(2) + '%'
            })));
        }
      } catch (e) { 
        console.error(e);
        // Fallback mock data
        setCoins([
          { pair: "BTC/USDT", price: "64,226", change: "+4.2%" },
          { pair: "ETH/USDT", price: "3,450", change: "+2.8%" }
        ]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchTickers();
    const interval = setInterval(fetchTickers, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="text-gray-500 text-center py-4">Loading markets...</div>;

  return (
    <div className="space-y-1 max-h-[550px] overflow-y-auto">
      {coins.map((coin, i) => (
        <div key={i} className="flex justify-between items-center p-3 hover:bg-[#2b3139] rounded transition cursor-pointer">
          <span className="font-medium text-[11px] text-white">{coin.pair}</span>
          <div className="text-right">
            <div className="text-white font-bold text-[11px]">${coin.price}</div>
            <div className={`text-[10px] ${coin.change.startsWith('-') ? 'text-red-400' : 'text-green-400'}`}>
              {coin.change}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
