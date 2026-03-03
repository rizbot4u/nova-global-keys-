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
