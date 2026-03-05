import { io } from 'socket.io-client';

export const socket = io(process.env.NEXT_PUBLIC_WS_URL || 'wss://www.novatradingkeys.com');

export const subscribeToPrice = (symbol: string, callback: (price: number) => void) => {
  socket.emit('subscribe', { symbol });
  socket.on('price', callback);
};
