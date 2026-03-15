import { describe, it, expect, vi, beforeEach } from 'vitest';
import { startMockOneBotWsServer } from './helpers/mock-ws-server.js';

let mockRuntime: any;
vi.mock('../src/runtime.js', () => ({
  getOneBotRuntime: () => mockRuntime,
}));

vi.mock('../src/outbound.js', () => ({
  sendText: async () => ({ channel: 'onebot', messageId: 'm1' }),
  sendImage: async () => ({ status: 'ok', retcode: 0, data: {} }),
}));

describe('gateway parse errors', () => {
  beforeEach(() => {
    mockRuntime = {
      channel: {
        activity: { record: () => {} },
        routing: { resolveAgentRoute: () => ({ sessionKey: 's', accountId: 'default', agentId: 'a' }) },
        reply: {
          resolveEnvelopeFormatOptions: () => ({}),
          formatInboundEnvelope: (x: any) => x.body,
          finalizeInboundContext: (x: any) => x,
          resolveEffectiveMessagesConfig: () => ({ responsePrefix: '' }),
          dispatchReplyWithBufferedBlockDispatcher: async () => {},
        },
      },
    };
  });

  it('does not crash on invalid JSON message from WS', async () => {
    const wsServer = await startMockOneBotWsServer();
    const { startGateway } = await import('../src/gateway.js');

    const ac = new AbortController();
    let readyResolve!: () => void;
    const readyP = new Promise<void>((r) => (readyResolve = r));

    const runP = startGateway({
      account: {
        accountId: 'default',
        enabled: true,
        wsUrl: wsServer.wsUrl,
        httpUrl: 'http://x',
        config: {},
      },
      abortSignal: ac.signal,
      cfg: {},
      onReady: () => readyResolve(),
      log: { info: () => {}, error: () => {}, debug: () => {} },
    });

    await readyP;

    wsServer.sendRawToAll('{ this is not json');

    // Give event loop a moment
    await new Promise((r) => setTimeout(r, 50));

    expect(true).toBe(true);

    ac.abort();
    await runP;
    await wsServer.close();
  });
});
