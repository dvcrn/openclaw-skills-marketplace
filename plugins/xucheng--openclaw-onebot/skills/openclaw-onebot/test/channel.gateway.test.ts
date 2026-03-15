import { describe, it, expect, vi, beforeEach } from 'vitest';

let gatewayBehavior: 'ready' | 'error' = 'ready';

vi.mock('../src/gateway.js', () => {
  return {
    startGateway: async ({ onReady, onError }: any) => {
      if (gatewayBehavior === 'ready') onReady?.();
      if (gatewayBehavior === 'error') onError?.(new Error('boom'));
    },
  };
});

import { onebotPlugin } from '../src/channel.js';

describe('channel.gateway.startAccount', () => {
  beforeEach(() => {
    gatewayBehavior = 'ready';
  });

  it('updates runtime status onReady', async () => {
    const statuses: any[] = [];
    let current = {
      accountId: 'default',
      running: false,
      connected: false,
      lastConnectedAt: null,
      lastError: null,
    };

    await onebotPlugin.gateway!.startAccount({
      account: {
        accountId: 'default',
        enabled: true,
        wsUrl: 'ws://x',
        httpUrl: 'http://y',
        config: {},
      } as any,
      abortSignal: new AbortController().signal,
      cfg: {},
      log: { info: () => {}, error: () => {} },
      getStatus: () => current,
      setStatus: (s: any) => {
        current = s;
        statuses.push(s);
      },
    } as any);

    expect(statuses.length).toBeGreaterThan(0);
    expect(current.running).toBe(true);
    expect(current.connected).toBe(true);
    expect(typeof current.lastConnectedAt).toBe('number');
  });

  it('sets lastError on gateway error', async () => {
    gatewayBehavior = 'error';

    let current = {
      accountId: 'default',
      running: false,
      connected: false,
      lastConnectedAt: null,
      lastError: null,
    };

    await onebotPlugin.gateway!.startAccount({
      account: {
        accountId: 'default',
        enabled: true,
        wsUrl: 'ws://x',
        httpUrl: 'http://y',
        config: {},
      } as any,
      abortSignal: new AbortController().signal,
      cfg: {},
      log: { info: () => {}, error: () => {} },
      getStatus: () => current,
      setStatus: (s: any) => {
        current = s;
      },
    } as any);

    expect(current.lastError).toBe('boom');
  });
});
