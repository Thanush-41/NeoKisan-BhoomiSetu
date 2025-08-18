// src/utils/socket.ts
import { io, Socket } from 'socket.io-client';

const SOCKET_URL = 'https://agrixchange.onrender.com/';

let socket: Socket | null = null;

export function getSocket(token?: string): Socket {
  if (!socket) {
    socket = io(SOCKET_URL, {
      auth: token ? { token } : undefined,
      transports: ['websocket'],
      withCredentials: true,
      // Force new connection for each call to ensure auth is sent
      forceNew: true,
    });
  } else if (token) {
    // If socket exists, update auth and reconnect
    socket.auth = { token };
    socket.connect();
  }
  return socket;
}

export function disconnectSocket() {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
}
