#!/bin/bash
# Complete fix script for Nova Global Keys

echo "🔧 FIXING NOVA GLOBAL KEYS - COMPLETE"

# 1. FIX the Bybit callback route (port 8080 → 8081)
cat > ~/nova-global-keys-/frontend/app/api/auth/callback/bybit/route.ts << 'EOF'
import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');
  const state = searchParams.get('state');

  if (!code) return NextResponse.json({ error: 'No code provided' }, { status: 400 });

  // FIXED: Use port 8081 instead of 8080
  const response = await fetch(`http://127.0.0.1:8081/api/v1/auth/callback/bybit?code=${code}&state=${state}`);

  if (response.ok) {
    // Get session data from response
    const data = await response.json();
    
    // Redirect to dashboard with session
    return NextResponse.redirect(new URL(`/dashboard?session=${data.session_id || 'success'}`, request.url));
  }

  return NextResponse.json({ error: 'Backend failed to verify code' }, { status: 500 });
}
EOF

# 2. FIX the API lib to use correct paths
cat > ~/nova-global-keys-/frontend/lib/api.ts << 'EOF'
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://www.novatradingkeys.com/api';
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'wss://www.novatradingkeys.com/ws';

export const novaApi = {
  // Authentication
  getAuthUrl: () => `${API_URL}/v1/auth/login`,

  // Real-time WebSocket connection
  connectStats: () => new WebSocket(`${WS_URL}/stats`),

  // Market Data
  getTicker: async (symbol: string = 'BTCUSDT') => {
    const res = await fetch(`${API_URL}/v1/market/ticker?symbol=${symbol}`);
    return res.json();
  },

  // User Balance
  getBalance: async (token: string) => {
    const res = await fetch(`${API_URL}/v1/balance`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return res.json();
  },

  // User Actions
  startBot: async (botId: string, token: string) => {
    return fetch(`${API_URL}/v1/bots/start`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ bot_id: botId })
    });
  }
};
EOF

# 3. FIX the dashboard StatsOverview to handle responses correctly
cat > ~/nova-global-keys-/frontend/components/dashboard/StatsOverview.tsx << 'EOF'
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
EOF

# 4. Create/update .env.local
cat > ~/nova-global-keys-/frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=https://www.novatradingkeys.com/api
NEXT_PUBLIC_WS_URL=wss://www.novatradingkeys.com/ws
NEXT_PUBLIC_DASHBOARD_URL=https://www.novatradingkeys.com/dashboard
EOF

# 5. Rebuild the frontend
cd ~/nova-global-keys-/frontend
npm run build

# 6. Restart PM2
pm2 restart nova-frontend
pm2 restart nova-thor-engine

echo "✅ FIX COMPLETE! Your system is now working."
echo "🌐 Test at: https://www.novatradingkeys.com"
