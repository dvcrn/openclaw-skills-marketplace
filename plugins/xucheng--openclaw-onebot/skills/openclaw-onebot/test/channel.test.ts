import { describe, it, expect } from 'vitest';
import { onebotPlugin } from '../src/channel.js';

// Note: ChannelPlugin is type-only in src, so runtime import doesn't require clawdbot/plugin-sdk.

describe('channel plugin shape', () => {
  it('has correct id and meta', () => {
    expect(onebotPlugin.id).toBe('onebot');
    expect(onebotPlugin.meta.id).toBe('onebot');
    expect(onebotPlugin.meta.label).toMatch(/OneBot/);
  });

  it('capabilities: media=true, reactions=false', () => {
    expect(onebotPlugin.capabilities.media).toBe(true);
    expect(onebotPlugin.capabilities.reactions).toBe(false);
  });

  it('normalizeTarget strips onebot: prefix', () => {
    const res = onebotPlugin.messaging!.normalizeTarget('onebot:private:123');
    expect(res.ok).toBe(true);
    expect(res.to).toBe('private:123');
  });

  it('looksLikeId recognizes valid ids', () => {
    const looks = onebotPlugin.messaging!.targetResolver!.looksLikeId;
    expect(looks('private:123')).toBe(true);
    expect(looks('group:456')).toBe(true);
    expect(looks('onebot:private:123')).toBe(true);
    expect(looks('789')).toBe(true);
  });

  it('looksLikeId rejects invalid ids', () => {
    const looks = onebotPlugin.messaging!.targetResolver!.looksLikeId;
    expect(looks('abc')).toBe(false);
    expect(looks('private:abc')).toBe(false);
    expect(looks('group:')).toBe(false);
  });

  it('isConfigured requires wsUrl and httpUrl', () => {
    const isConfigured = onebotPlugin.config!.isConfigured;
    expect(isConfigured({ wsUrl: 'ws://x', httpUrl: 'http://y' } as any)).toBe(true);
    expect(isConfigured({ wsUrl: 'ws://x' } as any)).toBe(false);
    expect(isConfigured({ httpUrl: 'http://y' } as any)).toBe(false);
  });

  it('describeAccount returns expected snapshot fields', () => {
    const snap = onebotPlugin.config!.describeAccount({
      accountId: 'default',
      name: 'QQ',
      enabled: true,
      wsUrl: 'ws://x',
      httpUrl: 'http://y',
    } as any);

    expect(snap.accountId).toBe('default');
    expect(snap.enabled).toBe(true);
    expect(snap.configured).toBe(true);
  });
  it('setup.validateInput checks token or useEnv', () => {
    const validate = onebotPlugin.setup!.validateInput!;
    expect(validate({ input: {} } as any)).toMatch(/requires --token/);
    expect(validate({ input: { token: 'ws,http' } } as any)).toBeNull();
    expect(validate({ input: { useEnv: true } } as any)).toBeNull();
  });

  it('setup.applyAccountConfig splits token and passes to config', () => {
    const apply = onebotPlugin.setup!.applyAccountConfig!;
    const res1 = apply({ cfg: {}, accountId: 'default', input: { token: 'ws://a,http://b' } } as any);
    expect((res1 as any).channels.onebot.wsUrl).toBe('ws://a');
    const res2 = apply({ cfg: {}, accountId: 'default', input: { token: 'ws://a,http://b,TOKEN123', name: 'QQBot' } } as any);
    expect((res2 as any).channels.onebot.accessToken).toBe('TOKEN123');
    expect((res2 as any).channels.onebot.name).toBe('QQBot');
  });
});
