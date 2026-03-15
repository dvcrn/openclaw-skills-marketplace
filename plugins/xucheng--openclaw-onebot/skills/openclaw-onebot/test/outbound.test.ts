import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { sendText, sendImage, sendRecord, uploadFile } from '../src/outbound.js';
import type { ResolvedOneBotAccount } from '../src/types.js';

function mkAccount(overrides?: Partial<ResolvedOneBotAccount>): ResolvedOneBotAccount {
  return {
    accountId: 'default',
    enabled: true,
    wsUrl: 'ws://x',
    httpUrl: 'http://127.0.0.1:1',
    config: {},
    ...overrides,
  } as any;
}

describe('outbound', () => {
  const oldFetch = globalThis.fetch;

  beforeEach(() => {
    globalThis.fetch = vi.fn();
  });

  afterEach(() => {
    globalThis.fetch = oldFetch;
    vi.restoreAllMocks();
  });

  it('sendText: defaults raw number target to private', async () => {
    (globalThis.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => ({ status: 'ok', retcode: 0, data: { message_id: 9 } }),
    });

    const res = await sendText({ to: '123', text: 'hi', account: mkAccount() });
    expect(res.error).toBeUndefined();

    const [url, init] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toMatch(/send_private_msg$/);
    const body = JSON.parse(init.body);
    expect(body.user_id).toBe(123);
    expect(body.message[0].type).toBe('text');
  });

  it('sendText: private:123 uses send_private_msg', async () => {
    (globalThis.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => ({ status: 'ok', retcode: 0, data: { message_id: 1 } }),
    });

    await sendText({ to: 'private:123', text: 'hello', account: mkAccount() });
    const [url, init] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toMatch(/send_private_msg$/);
    const body = JSON.parse(init.body);
    expect(body.user_id).toBe(123);
  });

  it('sendText: onebot:group:456 uses send_group_msg', async () => {
    (globalThis.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => ({ status: 'ok', retcode: 0, data: { message_id: 2 } }),
    });

    await sendText({ to: 'onebot:group:456', text: 'yo', account: mkAccount() });
    const [url, init] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toMatch(/send_group_msg$/);
    const body = JSON.parse(init.body);
    expect(body.group_id).toBe(456);
  });

  it('sendText: handles API retcode != 0', async () => {
    (globalThis.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => ({ status: 'failed', retcode: 100, data: null, message: 'bad' }),
    });

    const res = await sendText({ to: 'private:1', text: 'x', account: mkAccount() });
    expect(res.error).toMatch(/returned error/);
  });

  it('sendText: handles non-200 response', async () => {
    (globalThis.fetch as any).mockResolvedValue({
      ok: false,
      status: 500,
      statusText: 'Oops',
      json: async () => ({}),
    });

    const res = await sendText({ to: 'private:1', text: 'x', account: mkAccount() });
    expect(res.error).toMatch(/500/);
  });

  it('sendText: handles network error', async () => {
    (globalThis.fetch as any).mockRejectedValue(new Error('net down'));
    const res = await sendText({ to: 'private:1', text: 'x', account: mkAccount() });
    expect(res.error).toMatch(/net down/);
  });

  it('sendText: missing httpUrl returns error', async () => {
    const res = await sendText({ to: 'private:1', text: 'x', account: mkAccount({ httpUrl: '' }) });
    expect(res.error).toMatch(/missing httpUrl/);
  });

  it('sendImage: adds file:// prefix if missing', async () => {
    (globalThis.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => ({ status: 'ok', retcode: 0, data: { message_id: 3 } }),
    });

    await sendImage(mkAccount(), 'private', 1, '/tmp/a.png');
    const [, init] = (globalThis.fetch as any).mock.calls[0];
    const body = JSON.parse(init.body);
    expect(body.user_id).toBe(1);
    expect(body.message[0].type).toBe('image');
    expect(body.message[0].data.file).toBe('file:///tmp/a.png');
  });

  it('sendRecord: sends record segment', async () => {
    (globalThis.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => ({ status: 'ok', retcode: 0, data: { message_id: 4 } }),
    });

    await sendRecord(mkAccount(), 'group', 9, 'file:///tmp/a.mp3');
    const [url, init] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toMatch(/send_group_msg$/);
    const body = JSON.parse(init.body);
    expect(body.group_id).toBe(9);
    expect(body.message[0].type).toBe('record');
  });

  it('uploadFile: calls upload_group_file', async () => {
    (globalThis.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => ({ status: 'ok', retcode: 0, data: {} }),
    });

    await uploadFile(mkAccount(), 'group', 9, '/tmp/f.zip', 'f.zip');
    const [url, init] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toMatch(/upload_group_file$/);
    const body = JSON.parse(init.body);
    expect(body.group_id).toBe(9);
    expect(body.file).toBe('/tmp/f.zip');
    expect(body.name).toBe('f.zip');
  });

  it('sendText: includes Authorization header when accessToken set', async () => {
    (globalThis.fetch as any).mockResolvedValue({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => ({ status: 'ok', retcode: 0, data: { message_id: 10 } }),
    });

    await sendText({ to: 'private:1', text: 'x', account: mkAccount({ accessToken: 'AT' }) });
    const [, init] = (globalThis.fetch as any).mock.calls[0];
    expect(init.headers.Authorization).toBe('Bearer AT');
  });
  it('sendImage: targetType group works and prefixes file', async () => {
    (globalThis.fetch as any).mockResolvedValue({ ok: true, status: 200, json: async () => ({ status: 'ok', retcode: 0, data: { message_id: 3 } }) });
    await sendImage(mkAccount(), 'group', 1, 'a.png');
    const [, init] = (globalThis.fetch as any).mock.calls[0];
    const body = JSON.parse(init.body);
    expect(body.group_id).toBe(1);
    expect(body.message[0].type).toBe('image');
    expect(body.message[0].data.file).toBe('file://a.png');
  });

  it('sendRecord: targetType private works without file:// prefix', async () => {
    (globalThis.fetch as any).mockResolvedValue({ ok: true, status: 200, json: async () => ({ status: 'ok', retcode: 0, data: { message_id: 4 } }) });
    await sendRecord(mkAccount(), 'private', 9, 'a.mp3');
    const [url, init] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toMatch(/send_private_msg$/);
    const body = JSON.parse(init.body);
    expect(body.user_id).toBe(9);
    expect(body.message[0].type).toBe('record');
    expect(body.message[0].data.file).toBe('file://a.mp3');
  });

  it('uploadFile: calls upload_private_file', async () => {
    (globalThis.fetch as any).mockResolvedValue({ ok: true, status: 200, json: async () => ({ status: 'ok', retcode: 0, data: {} }) });
    await uploadFile(mkAccount(), 'private', 9, '/tmp/f.zip', 'f.zip');
    const [url, init] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toMatch(/upload_private_file$/);
    const body = JSON.parse(init.body);
    expect(body.user_id).toBe(9);
  });
});
