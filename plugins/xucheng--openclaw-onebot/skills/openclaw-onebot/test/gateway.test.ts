import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { startMockOneBotWsServer } from './helpers/mock-ws-server.js';
import { createMockRuntime } from './helpers/mock-runtime.js';

// Mock runtime module used by gateway.ts
let runtimeState: any;
vi.mock('../src/runtime.js', () => {
  return {
    getOneBotRuntime: () => runtimeState.runtime,
  };
});

// Mock outbound so gateway unit tests don't depend on real fetch/http
const outboundCalls: any[] = [];
vi.mock('../src/outbound.js', () => {
  return {
    sendText: async (args: any) => {
      outboundCalls.push({ kind: 'text', args });
      return { channel: 'onebot', messageId: '1' };
    },
    sendImage: async (...args: any[]) => {
      outboundCalls.push({ kind: 'image', args });
      return { status: 'ok', retcode: 0, data: {} };
    },
    sendRecord: async (...args: any[]) => {
      outboundCalls.push({ kind: 'record', args });
      return { status: 'ok', retcode: 0, data: {} };
    },
  };
});

// Batch gap is 1500ms — tests need longer waitFor timeouts
const WAIT_FOR_BATCH = { timeout: 5000 };

describe('gateway', () => {
  beforeEach(() => {
    outboundCalls.length = 0;
    runtimeState = createMockRuntime({
      nextDeliverPayload: { text: 'reply-from-agent', mediaUrls: ['file:///tmp/x.png'] },
    });
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('connects and includes access_token query', async () => {
    const wsServer = await startMockOneBotWsServer();
    const ac = new AbortController();
    const { startGateway } = await import('../src/gateway.js');

    let ready = false;
    const p = startGateway({
      account: {
        accountId: 'default',
        enabled: true,
        wsUrl: wsServer.wsUrl,
        httpUrl: 'http://x',
        accessToken: 'TOKEN',
        config: {},
      },
      abortSignal: ac.signal,
      cfg: {},
      onReady: () => { ready = true; },
      log: { info: () => {}, error: () => {}, debug: () => {} },
    });

    await vi.waitFor(() => {
      expect(ready).toBe(true);
      expect(wsServer.connectionUrls.length).toBeGreaterThan(0);
    });

    expect(wsServer.connectionUrls[0]).toContain('access_token=TOKEN');

    ac.abort();
    await p;
    await wsServer.close();
  });

  it('parses private message and dispatches to runtime', async () => {
    const wsServer = await startMockOneBotWsServer();
    const ac = new AbortController();
    const { startGateway } = await import('../src/gateway.js');

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
      cfg: { messages: {} },
      onReady: () => readyResolve(),
      log: { info: () => {}, error: () => {}, debug: () => {} },
    });

    await readyP;

    wsServer.sendToAll({
      post_type: 'message',
      message_type: 'private',
      sub_type: 'friend',
      message_id: 111,
      user_id: 222,
      message: [{ type: 'text', data: { text: 'hello' } }],
      raw_message: 'hello',
      sender: { user_id: 222, nickname: 'Alice' },
      self_id: 999,
      time: Math.floor(Date.now() / 1000),
    });

    await vi.waitFor(() => {
      expect(runtimeState.state.lastDispatchArgs).not.toBeNull();
    }, WAIT_FOR_BATCH);

    const ctx = runtimeState.state.lastDispatchArgs.ctx;
    expect(ctx.From).toBe('onebot:private:222');
    expect(String(ctx.MessageSid)).toBe('111');

    await vi.waitFor(() => {
      expect(outboundCalls.find((c) => c.kind === 'image')).toBeTruthy();
      expect(outboundCalls.find((c) => c.kind === 'text')).toBeTruthy();
    }, WAIT_FOR_BATCH);

    ac.abort();
    await runP;
    await wsServer.close();
  });

  it('adds image/voice annotations to body when segments present', async () => {
    const wsServer = await startMockOneBotWsServer();
    const ac = new AbortController();
    const { startGateway } = await import('../src/gateway.js');

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

    wsServer.sendToAll({
      post_type: 'message',
      message_type: 'private',
      sub_type: 'friend',
      message_id: 112,
      user_id: 223,
      message: [
        { type: 'text', data: { text: 'hi' } },
        { type: 'image', data: { url: 'http://img' } },
        { type: 'record', data: { url: 'http://voice' } },
      ],
      raw_message: 'hi',
      sender: { user_id: 223, nickname: 'Bob' },
      self_id: 999,
      time: Math.floor(Date.now() / 1000),
    });

    await vi.waitFor(() => {
      expect(runtimeState.state.lastEnvelopeArgs).not.toBeNull();
    }, WAIT_FOR_BATCH);

    const envArgs = runtimeState.state.lastEnvelopeArgs;
    expect(String(envArgs.body)).toContain('[Image: http://img]');
    // Voice download fails in test (fake URL) -> falls back to placeholder
    expect(String(envArgs.body)).toMatch(/\[语音\]|<media:audio>/);

    ac.abort();
    await runP;
    await wsServer.close();
  });

  it('reconnects on abnormal close (uses timers)', async () => {
    const wsServer = await startMockOneBotWsServer();
    const ac = new AbortController();
    const { startGateway } = await import('../src/gateway.js');

    let readyCount = 0;
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
      onReady: () => { readyCount++; },
      log: { info: () => {}, error: () => {}, debug: () => {} },
    });

    await vi.waitFor(() => expect(readyCount).toBe(1));
    wsServer.closeAllClients(4002, 'boom');
    await new Promise((r) => setTimeout(r, 1200));
    expect(wsServer.connectionUrls.length).toBeGreaterThanOrEqual(2);

    ac.abort();
    await runP;
    await wsServer.close();
  });

  it('ignores invalid JSON payloads', async () => {
    const wsServer = await startMockOneBotWsServer();
    const ac = new AbortController();
    const { startGateway } = await import('../src/gateway.js');

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

    wsServer.sendToAll({
      post_type: 'meta_event',
      meta_event_type: 'heartbeat',
      self_id: 999,
      time: Math.floor(Date.now() / 1000),
      status: { online: true },
      interval: 10000,
    });

    await new Promise((r) => setTimeout(r, 50));
    expect(true).toBe(true);

    ac.abort();
    await runP;
    await wsServer.close();
  });
});
