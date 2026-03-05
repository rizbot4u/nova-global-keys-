"use client";
import React, { useEffect } from 'react';

export default function TickerTape() {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js";
    script.async = true;
    script.innerHTML = JSON.stringify({
      "symbols": [
        { "proName": "BITSTAMP:BTCUSDT", "title": "BTC/USDT" },
        { "proName": "BITSTAMP:ETHUSDT", "title": "ETH/USDT" },
        { "proName": "BINANCE:SOLUSDT", "title": "SOL/USDT" },
        { "proName": "BINANCE:AVAXUSDT", "title": "AVAX/USDT" }
      ],
      "showSymbolLogo": true,
      "colorTheme": "dark",
      "isTransparent": true,
      "displayMode": "adaptive",
      "locale": "en"
    });
    document.getElementById("ticker-container")?.appendChild(script);
  }, []);

  return (
    <div id="ticker-container" className="tradingview-widget-container mb-4 opacity-80 hover:opacity-100 transition-opacity">
      <div className="tradingview-widget-container__widget"></div>
    </div>
  );
}
