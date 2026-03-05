"use client";
import React, { useEffect, useRef } from 'react';

export default function TradingChart() {
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/tv.js";
    script.async = true;
    script.onload = () => {
      if (container.current && (window as any).TradingView) {
        new (window as any).TradingView.widget({
          "autosize": true,
          "symbol": "BYBIT:BTCUSDT",
          "interval": "15",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "enable_publishing": false,
          "allow_symbol_change": true,
          "container_id": "tradingview_chart"
        });
      }
    };
    document.head.appendChild(script);
  }, []);

  return (
    <div className="w-full h-full border border-gray-800 rounded-lg overflow-hidden bg-[#161a1e]">
      <div id="tradingview_chart" ref={container} className="h-[500px]" />
    </div>
  );
}
