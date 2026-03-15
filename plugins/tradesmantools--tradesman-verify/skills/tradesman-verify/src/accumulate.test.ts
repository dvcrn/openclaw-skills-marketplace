/**
 * tradesman-verify — Accumulate client tests
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Tests use a mock RPC endpoint to avoid hitting mainnet.
 */

import { describe, it, before, after, mock } from 'node:test';
import assert from 'node:assert/strict';
import { createClient, clearCache } from './accumulate.js';
import type { AccumulateClient } from './accumulate.js';

// ── Mock HTTP server ─────────────────────────────────────────────────────────

let mockUrl: string;
let mockHandler: (body: Record<string, unknown>) => unknown;
let server: ReturnType<typeof import('node:http').createServer>;

before(async () => {
  const http = await import('node:http');
  server = http.createServer((req, res) => {
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      const parsed = JSON.parse(body);
      const result = mockHandler(parsed);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ jsonrpc: '2.0', id: parsed.id, result }));
    });
  });
  await new Promise<void>((resolve) => server.listen(0, '127.0.0.1', resolve));
  const addr = server.address() as import('node:net').AddressInfo;
  mockUrl = `http://127.0.0.1:${addr.port}`;
});

after(() => {
  server?.close();
});

// ── Tests ────────────────────────────────────────────────────────────────────

describe('createClient', () => {
  it('queryADI returns parsed ADI metadata', async () => {
    mockHandler = () => ({
      data: {
        type: 'identity',
        keyBook: { url: 'acc://test.acme/book', keys: [] },
        accounts: [{ url: 'acc://test.acme/credentials', type: 'dataAccount' }],
        creditBalance: 100,
      },
    });

    const client = createClient({ rpcUrl: mockUrl });
    clearCache();
    const adi = await client.queryADI('acc://test.acme');

    assert.equal(adi.url, 'acc://test.acme');
    assert.equal(adi.type, 'identity');
    assert.equal(adi.creditBalance, 100);
    assert.equal(adi.accounts.length, 1);
  });

  it('getDataAccount returns entries', async () => {
    mockHandler = () => ({
      data: {
        type: 'dataAccount',
        entries: [{ hash: 'abc123', data: '{}' }],
      },
    });

    const client = createClient({ rpcUrl: mockUrl });
    clearCache();
    const account = await client.getDataAccount('acc://test.acme/credentials');

    assert.notEqual(account, null);
    assert.equal(account!.entries.length, 1);
    assert.equal(account!.entries[0]!.hash, 'abc123');
  });

  it('getDataAccount returns null on error', async () => {
    mockHandler = () => {
      throw new Error('Not found');
    };

    // Override mock to return HTTP error
    const client = createClient({ rpcUrl: 'http://127.0.0.1:1' });
    clearCache();
    const account = await client.getDataAccount('acc://nonexistent.acme/data');

    assert.equal(account, null);
  });

  it('getTokenAccount returns balance', async () => {
    mockHandler = () => ({
      data: {
        type: 'tokenAccount',
        tokenUrl: 'acc://ACME',
        balance: '500000000',
      },
    });

    const client = createClient({ rpcUrl: mockUrl });
    clearCache();
    const token = await client.getTokenAccount('acc://test.acme/tokens');

    assert.notEqual(token, null);
    assert.equal(token!.balance, '500000000');
    assert.equal(token!.tokenUrl, 'acc://ACME');
  });

  it('writeData returns txid', async () => {
    mockHandler = () => ({
      txid: 'tx-abc-123',
      status: 'delivered',
    });

    const client = createClient({ rpcUrl: mockUrl });
    const result = await client.writeData({
      url: 'acc://test.acme/data',
      data: { foo: 'bar' },
    });

    assert.equal(result.txid, 'tx-abc-123');
    assert.equal(result.status, 'delivered');
    assert.equal(result.dataAccountUrl, 'acc://test.acme/data');
  });

  it('handles RPC error responses', async () => {
    // Override the server to return an error
    const http = await import('node:http');
    const errorServer = http.createServer((_req, res) => {
      let body = '';
      _req.on('data', (chunk) => (body += chunk));
      _req.on('end', () => {
        const parsed = JSON.parse(body);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          jsonrpc: '2.0',
          id: parsed.id,
          error: { code: -32000, message: 'ADI not found' },
        }));
      });
    });
    await new Promise<void>((resolve) => errorServer.listen(0, '127.0.0.1', resolve));
    const addr = errorServer.address() as import('node:net').AddressInfo;

    const client = createClient({ rpcUrl: `http://127.0.0.1:${addr.port}` });
    clearCache();

    await assert.rejects(
      () => client.queryADI('acc://nonexistent.acme'),
      (err: Error) => err.message.includes('ADI not found')
    );

    errorServer.close();
  });

  it('respects timeout configuration', async () => {
    // Create a server that never responds
    const http = await import('node:http');
    const slowServer = http.createServer(() => {
      // Intentionally never respond
    });
    await new Promise<void>((resolve) => slowServer.listen(0, '127.0.0.1', resolve));
    const addr = slowServer.address() as import('node:net').AddressInfo;

    const client = createClient({
      rpcUrl: `http://127.0.0.1:${addr.port}`,
      timeoutMs: 100, // 100ms timeout
    });
    clearCache();

    await assert.rejects(
      () => client.queryADI('acc://slow.acme'),
      (err: Error) => err.name === 'AbortError' || err.message.includes('abort')
    );

    slowServer.close();
  });

  it('caches read operations', async () => {
    let callCount = 0;
    mockHandler = () => {
      callCount++;
      return { data: { type: 'identity', accounts: [] } };
    };

    const client = createClient({ rpcUrl: mockUrl, cacheTtlMs: 10_000 });
    clearCache();

    await client.queryADI('acc://cached.acme');
    await client.queryADI('acc://cached.acme');

    assert.equal(callCount, 1, 'Second call should hit cache');
  });
});
