/**
 * tradesman-verify — Accumulate Protocol RPC client
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Read + write client for the Accumulate blockchain.
 * Write operations accept an optional Signer — if omitted, transactions are
 * submitted unsigned (suitable for dev/test environments only).
 *
 * API reference: https://docs.accumulatenetwork.io/
 */

import type {
  AccumulateClientConfig,
  ADIMetadata,
  DataAccount,
  TokenAccount,
  Signer,
} from './types.js';

// ── Cache ─────────────────────────────────────────────────────────────────────

interface CacheEntry<T> {
  data: T;
  ts: number;
}

const _cache = new Map<string, CacheEntry<unknown>>();

function _getCached<T>(key: string, ttlMs: number): T | null {
  const entry = _cache.get(key);
  if (!entry) return null;
  if (Date.now() - entry.ts > ttlMs) {
    _cache.delete(key);
    return null;
  }
  return entry.data as T;
}

function _setCache<T>(key: string, data: T): void {
  _cache.set(key, { data, ts: Date.now() });
}

export function clearCache(): void {
  _cache.clear();
}

// ── Client interface ──────────────────────────────────────────────────────────

export interface WriteDataParams {
  url: string;                      // data account URL
  data: Record<string, unknown>;    // entry payload (will be JSON-encoded)
  createAccount?: boolean;
  signer?: Signer;
}

export interface WriteDataResult {
  txid: string;
  status: string;
  dataAccountUrl: string;
  timestamp: string;
}

export interface AccumulateClient {
  // ── Read ──
  queryADI(adiUrl: string): Promise<ADIMetadata>;
  getDataAccount(dataAccountUrl: string): Promise<DataAccount | null>;
  getTokenAccount(tokenAccountUrl: string): Promise<TokenAccount | null>;

  // ── Write ──
  /**
   * Write a data entry to an Accumulate data account.
   * Provide a Signer for production — unsigned submissions are dev/test only.
   */
  writeData(params: WriteDataParams): Promise<WriteDataResult>;
}

// ── Client factory ────────────────────────────────────────────────────────────

export function createClient(config: AccumulateClientConfig = {}): AccumulateClient {
  const rpcUrl =
    config.rpcUrl ??
    process.env['ACCUMULATE_RPC_URL'] ??
    'https://mainnet.accumulatenetwork.io/v2';

  const cacheTtlMs = config.cacheTtlMs ?? 60_000;
  const debug = config.debug ?? false;

  function log(msg: string): void {
    if (debug) console.debug(`[tradesman-verify] ${msg}`);
  }

  async function rpc<T = unknown>(method: string, params: unknown): Promise<T> {
    // Sort object keys so cache hits are order-independent
    const sortedKeys =
      params !== null && typeof params === 'object' && !Array.isArray(params)
        ? Object.keys(params as Record<string, unknown>).sort()
        : undefined;
    const key = `${method}:${JSON.stringify(params, sortedKeys)}`;

    // Only cache read operations
    if (method === 'query' || method === 'query-tx-history') {
      const cached = _getCached<T>(key, cacheTtlMs);
      if (cached) {
        log(`cache hit: ${method}`);
        return cached;
      }
    }

    log(`rpc: ${method}`);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), config.timeoutMs ?? 15_000);
    let res: Response;
    try {
      res = await fetch(rpcUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', id: Date.now(), method, params }),
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timeout);
    }

    if (!res.ok) {
      throw new Error(`HTTP ${res.status} from Accumulate RPC`);
    }

    const json = (await res.json()) as {
      result?: unknown;
      error?: { code: number; message: string };
    };

    if (json.error) {
      throw new Error(`Accumulate RPC error ${json.error.code}: ${json.error.message}`);
    }

    const data = json.result as T;

    if (method === 'query' || method === 'query-tx-history') {
      _setCache(key, data);
    }

    return data;
  }

  /**
   * Build a signed transaction payload.
   * Signs the SHA-256 hash of the canonical transaction body.
   *
   * Production integrators: implement a full Accumulate transaction envelope
   * per the protocol spec at https://docs.accumulatenetwork.io/
   */
  async function buildSignedPayload(
    txBody: Record<string, unknown>,
    signer?: Signer
  ): Promise<Record<string, unknown>> {
    if (!signer) {
      // Dev/test: submit unsigned. The node must have a pre-authorized key.
      return txBody;
    }

    const canonical = JSON.stringify(txBody);
    const txHash = new Uint8Array(
      await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canonical))
    );

    const sig = await signer.sign(txHash);

    return {
      ...txBody,
      signature: {
        type: 'ed25519',
        publicKey: Buffer.from(signer.publicKey).toString('hex'),
        signature: Buffer.from(sig).toString('hex'),
        signerUrl: signer.adiUrl,
      },
    };
  }

  return {
    // ── Read ──────────────────────────────────────────────────────────────────

    async queryADI(adiUrl: string): Promise<ADIMetadata> {
      const result = await rpc<Record<string, unknown>>('query', { url: adiUrl, prove: false });
      const data = (result['data'] ?? result) as Record<string, unknown>;

      return {
        url: adiUrl,
        type: (data.type as string) ?? 'identity',
        keyBook: data.keyBook as ADIMetadata['keyBook'] | undefined,
        accounts: Array.isArray(data.accounts)
          ? (data.accounts as unknown[]).map((a: unknown) => {
              const acc = a as Record<string, string>;
              return { url: acc['url'] ?? String(a), type: acc['type'] ?? 'account' };
            })
          : [],
        creditBalance:
          data.creditBalance !== undefined ? Number(data.creditBalance) : undefined,
      };
    },

    async getDataAccount(dataAccountUrl: string): Promise<DataAccount | null> {
      try {
        const result = await rpc<Record<string, unknown>>('query', {
          url: dataAccountUrl,
          prove: false,
        });
        const data = (result['data'] ?? result) as Record<string, unknown>;
        return {
          url: dataAccountUrl,
          type: (data.type as string) ?? 'dataAccount',
          entries: Array.isArray(data.entries) ? (data.entries as DataAccount['entries']) : [],
        };
      } catch {
        return null;
      }
    },

    async getTokenAccount(tokenAccountUrl: string): Promise<TokenAccount | null> {
      try {
        const result = await rpc<Record<string, unknown>>('query', {
          url: tokenAccountUrl,
          prove: false,
        });
        const data = (result['data'] ?? result) as Record<string, unknown>;
        return {
          url: tokenAccountUrl,
          type: (data.type as string) ?? 'tokenAccount',
          tokenUrl: (data.tokenUrl as string) ?? '',
          balance: data.balance?.toString() ?? '0',
          metadata: (data.metadata as Record<string, unknown>) ?? {},
        };
      } catch {
        return null;
      }
    },

    // ── Write ──────────────────────────────────────────────────────────────────

    async writeData(params: WriteDataParams): Promise<WriteDataResult> {
      const { url, data, createAccount = false, signer } = params;

      const txBody: Record<string, unknown> = {
        type: 'writeData',
        url,
        entry: { data: JSON.stringify(data) },
        createAccount,
      };

      const payload = await buildSignedPayload(txBody, signer);
      const result = await rpc<Record<string, unknown>>('execute', payload);

      // Invalidate any cached read for this account
      _cache.forEach((_, key) => {
        if (key.includes(url)) _cache.delete(key);
      });

      return {
        txid: (result.txid as string) ?? (result.transactionHash as string) ?? '',
        status: (result.status as string) ?? 'pending',
        dataAccountUrl: url,
        timestamp: new Date().toISOString(),
      };
    },
  };
}

// ── Default singleton client ───────────────────────────────────────────────────
//
// Lazy-initialized so that ACCUMULATE_RPC_URL is read at first call, not at
// import time. This matters for serverless and test environments that set
// env vars programmatically after module imports.

let _defaultClientInstance: AccumulateClient | undefined;

function _getDefaultClient(): AccumulateClient {
  return (_defaultClientInstance ??= createClient());
}

export const defaultClient: AccumulateClient = {
  queryADI: (...args) => _getDefaultClient().queryADI(...args),
  getDataAccount: (...args) => _getDefaultClient().getDataAccount(...args),
  getTokenAccount: (...args) => _getDefaultClient().getTokenAccount(...args),
  writeData: (...args) => _getDefaultClient().writeData(...args),
};
