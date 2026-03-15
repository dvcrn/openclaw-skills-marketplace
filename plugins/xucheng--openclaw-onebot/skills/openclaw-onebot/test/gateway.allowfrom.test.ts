import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { startMockOneBotWsServer } from './helpers/mock-ws-server.js';

let mockRuntime: any;
let dispatchCount = 0;

vi.mock('../src/runtime.js', () => ({
  getOneBotRuntime: () => mockRuntime,
}));

vi.mock('../src/outbound.js', () => ({
  sendText: async () => ({ channel: 'onebot', messageId: 'm1' }),
  sendImage: async () => ({ status: 'ok', retcode: 0, data: {} }),
  sendRecord: async () => ({ status: 'ok', retcode: 0, data: {} }),
}));

function makePrivateMsg(userId: number, text: string) {
  return {
    post_type: 'message',
    message_type: 'private',
    sub_type: 'friend',
    message_id: Math.floor(Math.random() * 100000),
    user_id: userId,
    message: [{ type: 'text', data: { text } }],
    raw_message: text,
    sender: { user_id: userId, nickname: `User${userId}` },
    self_id: 999,
    time: Math.floor(Date.now() / 1000),
  };
}

function makeGroupMsg(userId: number, groupId: number, text: string) {
  return {
    post_type: 'message',
    message_type: 'group',
    sub_type: 'normal',
    message_id: Math.floor(Math.random() * 100000),
    user_id: userId,
    group_id: groupId,
    message: [{ type: 'text', data: { text } }],
    raw_message: text,
    sender: { user_id: userId, nickname: `User${userId}` },
    self_id: 999,
    time: Math.floor(Date.now() / 1000),
  };
}

describe('gateway allowFrom', () => {
  beforeEach(() => {
    dispatchCount = 0;
    mockRuntime = {
      channel: {
        activity: { record: () => {} },
        routing: { resolveAgentRoute: () => ({ sessionKey: 's', accountId: 'default', agentId: 'a' }) },
        reply: {
          resolveEnvelopeFormatOptions: () => ({}),
          formatInboundEnvelope: (x: any) => x.body,
          finalizeInboundContext: (x: any) => x,
          resolveEffectiveMessagesConfig: () => ({ responsePrefix: '' }),
          dispatchReplyWithBufferedBlockDispatcher: async ({ dispatcherOptions }: any) => {
            dispatchCount++;
            await dispatcherOptions.deliver({ text: 'ok' }, { kind: 'final' });
          },
        },
      },
    };
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('allows all when allowFrom is empty/undefined', async () => {
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
        // no allowFrom
      },
      abortSignal: ac.signal,
      cfg: {},
      onReady: () => readyResolve(),
      log: { info: () => {}, error: () => {}, debug: () => {} },
    });

    await readyP;
    wsServer.sendToAll(makePrivateMsg(888, 'anyone'));

    await vi.waitFor(() => expect(dispatchCount).toBe(1), { timeout: 5000 });

    ac.abort();
    await runP;
    await wsServer.close();
  });

  it('blocks unlisted private sender', async () => {
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
        allowFrom: ['private:111'],
        config: {},
      },
      abortSignal: ac.signal,
      cfg: {},
      onReady: () => readyResolve(),
      log: { info: () => {}, error: () => {}, debug: () => {} },
    });

    await readyP;
    wsServer.sendToAll(makePrivateMsg(222, 'blocked'));

    // Wait a bit — should NOT dispatch
    await new Promise((r) => setTimeout(r, 2500));
    expect(dispatchCount).toBe(0);

    ac.abort();
    await runP;
    await wsServer.close();
  });

  it('allows listed private sender', async () => {
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
        allowFrom: ['private:111'],
        config: {},
      },
      abortSignal: ac.signal,
      cfg: {},
      onReady: () => readyResolve(),
      log: { info: () => {}, error: () => {}, debug: () => {} },
    });

    await readyP;
    wsServer.sendToAll(makePrivateMsg(111, 'allowed'));

    await vi.waitFor(() => expect(dispatchCount).toBe(1), { timeout: 5000 });

    ac.abort();
    await runP;
    await wsServer.close();
  });

  it('blocks unlisted group', async () => {
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
        allowFrom: ['group:100'],
        config: {},
      },
      abortSignal: ac.signal,
      cfg: {},
      onReady: () => readyResolve(),
      log: { info: () => {}, error: () => {}, debug: () => {} },
    });

    await readyP;
    wsServer.sendToAll(makeGroupMsg(1, 200, 'blocked group'));

    await new Promise((r) => setTimeout(r, 2500));
    expect(dispatchCount).toBe(0);

    ac.abort();
    await runP;
    await wsServer.close();
  });

  it('allows listed group', async () => {
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
        allowFrom: ['group:100'],
        config: {},
      },
      abortSignal: ac.signal,
      cfg: {},
      onReady: () => readyResolve(),
      log: { info: () => {}, error: () => {}, debug: () => {} },
    });

    await readyP;
    wsServer.sendToAll(makeGroupMsg(1, 100, 'allowed group'));

    await vi.waitFor(() => expect(dispatchCount).toBe(1), { timeout: 5000 });

    ac.abort();
    await runP;
    await wsServer.close();
  });

  it('wildcard * allows everyone', async () => {
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
        allowFrom: ['*'],
        config: {},
      },
      abortSignal: ac.signal,
      cfg: {},
      onReady: () => readyResolve(),
      log: { info: () => {}, error: () => {}, debug: () => {} },
    });

    await readyP;
    wsServer.sendToAll(makePrivateMsg(888, 'wildcard'));

    await vi.waitFor(() => expect(dispatchCount).toBe(1), { timeout: 5000 });

    ac.abort();
    await runP;
    await wsServer.close();
  });

  it('mixed allowFrom: private + group', async () => {
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
        allowFrom: ['private:111', 'group:200'],
        config: {},
      },
      abortSignal: ac.signal,
      cfg: {},
      onReady: () => readyResolve(),
      log: { info: () => {}, error: () => {}, debug: () => {} },
    });

    await readyP;

    // Allowed private
    wsServer.sendToAll(makePrivateMsg(111, 'ok'));
    await vi.waitFor(() => expect(dispatchCount).toBe(1), { timeout: 5000 });

    // Blocked private
    wsServer.sendToAll(makePrivateMsg(222, 'no'));
    await new Promise((r) => setTimeout(r, 2500));
    expect(dispatchCount).toBe(1); // still 1

    // Allowed group
    wsServer.sendToAll(makeGroupMsg(333, 200, 'ok'));
    await vi.waitFor(() => expect(dispatchCount).toBe(2), { timeout: 5000 });

    // Blocked group
    wsServer.sendToAll(makeGroupMsg(333, 300, 'no'));
    await new Promise((r) => setTimeout(r, 2500));
    expect(dispatchCount).toBe(2); // still 2

    ac.abort();
    await runP;
    await wsServer.close();
  });
});
