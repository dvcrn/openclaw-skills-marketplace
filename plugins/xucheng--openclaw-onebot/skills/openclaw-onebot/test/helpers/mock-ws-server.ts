import { WebSocketServer } from 'ws';
import type http from 'node:http';

export interface MockWsServer {
  wsUrl: string;
  connectionUrls: string[];
  sendToAll: (obj: unknown) => void;
  sendRawToAll: (data: string) => void;
  closeAllClients: (code?: number, reason?: string) => void;
  close: () => Promise<void>;
  getClientCount: () => number;
}

export async function startMockOneBotWsServer(): Promise<MockWsServer> {
  const wss = new WebSocketServer({ port: 0, host: '127.0.0.1' });

  const connectionUrls: string[] = [];

  wss.on('connection', (_socket, req) => {
    // req is http.IncomingMessage
    const r = req as http.IncomingMessage;
    connectionUrls.push(r.url ?? '');
  });

  await new Promise<void>((resolve) => wss.on('listening', () => resolve()));

  const address = wss.address();
  if (typeof address === 'string' || !address) throw new Error('Unexpected ws address');

  const wsUrl = `ws://127.0.0.1:${address.port}`;

  return {
    wsUrl,
    connectionUrls,
    sendToAll: (obj) => {
      const data = JSON.stringify(obj);
      for (const client of wss.clients) {
        if (client.readyState === 1) client.send(data);
      }
    },
    sendRawToAll: (data) => {
      for (const client of wss.clients) {
        if (client.readyState === 1) client.send(data);
      }
    },
    closeAllClients: (code = 4001, reason = 'test-close') => {
      for (const client of wss.clients) {
        try {
          client.close(code, reason);
        } catch {
          // ignore
        }
      }
    },
    close: () =>
      new Promise<void>((resolve) => {
        wss.close(() => resolve());
      }),
    getClientCount: () => wss.clients.size,
  };
}
