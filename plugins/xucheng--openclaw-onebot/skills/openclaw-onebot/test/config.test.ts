import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { listOneBotAccountIds, resolveOneBotAccount, applyOneBotAccountConfig } from '../src/config.js';

describe('config', () => {
  const oldEnv = { ...process.env };

  beforeEach(() => {
    process.env = { ...oldEnv };
    delete process.env.ONEBOT_WS_URL;
    delete process.env.ONEBOT_HTTP_URL;
    delete process.env.ONEBOT_ACCESS_TOKEN;
  });

  afterEach(() => {
    process.env = { ...oldEnv };
  });

  it('listOneBotAccountIds: empty config -> []', () => {
    expect(listOneBotAccountIds({} as any)).toEqual([]);
  });

  it('listOneBotAccountIds: default account when wsUrl/httpUrl present', () => {
    const cfg = { channels: { onebot: { wsUrl: 'ws://x', httpUrl: 'http://y' } } };
    expect(listOneBotAccountIds(cfg as any)).toEqual(['default']);
  });

  it('listOneBotAccountIds: includes named accounts with ws/http', () => {
    const cfg = {
      channels: {
        onebot: {
          accounts: {
            a: { wsUrl: 'ws://a', httpUrl: 'http://a' },
            b: { wsUrl: 'ws://b' },
            c: {},
          },
        },
      },
    };

    expect(new Set(listOneBotAccountIds(cfg as any))).toEqual(new Set(['a', 'b']));
  });

  it('resolveOneBotAccount: default env fallback', () => {
    process.env.ONEBOT_WS_URL = 'ws://env';
    process.env.ONEBOT_HTTP_URL = 'http://env';
    process.env.ONEBOT_ACCESS_TOKEN = 'tok';

    const acct = resolveOneBotAccount({} as any, 'default');
    expect(acct.wsUrl).toBe('ws://env');
    expect(acct.httpUrl).toBe('http://env');
    expect(acct.accessToken).toBe('tok');
  });

  it('resolveOneBotAccount: named account does not use env fallback', () => {
    process.env.ONEBOT_WS_URL = 'ws://env';
    const cfg = { channels: { onebot: { accounts: { a: { wsUrl: 'ws://a', httpUrl: 'http://a' } } } } };
    const acct = resolveOneBotAccount(cfg as any, 'a');
    expect(acct.wsUrl).toBe('ws://a');
  });

  it('applyOneBotAccountConfig: default account updates channels.onebot', () => {
    const next = applyOneBotAccountConfig({} as any, 'default', {
      wsUrl: 'ws://x',
      httpUrl: 'http://y',
      accessToken: 't',
      name: 'n',
    });

    expect((next as any).channels.onebot.wsUrl).toBe('ws://x');
    expect((next as any).channels.onebot.httpUrl).toBe('http://y');
    expect((next as any).channels.onebot.accessToken).toBe('t');
    expect((next as any).channels.onebot.name).toBe('n');
    expect((next as any).channels.onebot.enabled).toBe(true);
  });

  it('applyOneBotAccountConfig: named account updates channels.onebot.accounts', () => {
    const next = applyOneBotAccountConfig({} as any, 'acct1', {
      wsUrl: 'ws://a',
      httpUrl: 'http://a',
    });

    expect((next as any).channels.onebot.accounts.acct1.wsUrl).toBe('ws://a');
    expect((next as any).channels.onebot.accounts.acct1.httpUrl).toBe('http://a');
  });

  it('applyOneBotAccountConfig: partial update keeps old values', () => {
    const cfg = {
      channels: {
        onebot: {
          wsUrl: 'ws://old',
          httpUrl: 'http://old',
          accessToken: 'old',
        },
      },
    };

    const next = applyOneBotAccountConfig(cfg as any, 'default', { wsUrl: 'ws://new' });
    expect((next as any).channels.onebot.wsUrl).toBe('ws://new');
    expect((next as any).channels.onebot.httpUrl).toBe('http://old');
    expect((next as any).channels.onebot.accessToken).toBe('old');
  });
  it('resolveOneBotAccount: ignores env if explicitly configured', () => {
    process.env.ONEBOT_WS_URL = 'ws://env';
    process.env.ONEBOT_HTTP_URL = 'http://env';
    process.env.ONEBOT_ACCESS_TOKEN = 'tok';
    const cfg = { channels: { onebot: { wsUrl: 'ws://c', httpUrl: 'http://c', accessToken: 'ctok' } } };
    const acct = resolveOneBotAccount(cfg as any, 'default');
    expect(acct.wsUrl).toBe('ws://c');
    expect(acct.httpUrl).toBe('http://c');
    expect(acct.accessToken).toBe('ctok');
  });

  it('applyOneBotAccountConfig: partial update handles missing inputs', () => {
    const cfg = { channels: { onebot: { wsUrl: 'ws://old' } } };
    const next = applyOneBotAccountConfig(cfg as any, 'default', {});
    expect((next as any).channels.onebot.wsUrl).toBe('ws://old');
    const next2 = applyOneBotAccountConfig(cfg as any, 'acct1', {});
    expect((next2 as any).channels.onebot.accounts.acct1.wsUrl).toBeUndefined();
  });


  it('resolveOneBotAccount: allowFrom is passed through', () => {
    const cfg = { channels: { onebot: { wsUrl: 'ws://x', httpUrl: 'http://y', allowFrom: ['private:111', 'group:200'] } } };
    const acct = resolveOneBotAccount(cfg as any, 'default');
    expect(acct.allowFrom).toEqual(['private:111', 'group:200']);
  });

  it('resolveOneBotAccount: allowFrom undefined when not set', () => {
    const cfg = { channels: { onebot: { wsUrl: 'ws://x', httpUrl: 'http://y' } } };
    const acct = resolveOneBotAccount(cfg as any, 'default');
    expect(acct.allowFrom).toBeUndefined();
  });
});
