'use strict';

const { computeNonceComponents, resolveExpiry, checkPrecision } = require('../helpers');

// --- computeNonceComponents ---
// Permit2 invalidateUnorderedNonces(wordPos, mask):
//   wordPos = nonce >> 8n   (which 256-bit word)
//   mask    = 1n << (nonce & 0xFFn)  (which bit within the word)

describe('computeNonceComponents', () => {
  test('nonce 0 → wordPos 0, mask 1', () => {
    const { wordPos, mask } = computeNonceComponents(0n);
    expect(wordPos).toBe(0n);
    expect(mask).toBe(1n);
  });

  test('nonce 1 → wordPos 0, mask 2', () => {
    const { wordPos, mask } = computeNonceComponents(1n);
    expect(wordPos).toBe(0n);
    expect(mask).toBe(2n);
  });

  test('nonce 255 → wordPos 0, mask 2^255', () => {
    const { wordPos, mask } = computeNonceComponents(255n);
    expect(wordPos).toBe(0n);
    expect(mask).toBe(2n ** 255n);
  });

  test('nonce 256 → wordPos 1, mask 1', () => {
    const { wordPos, mask } = computeNonceComponents(256n);
    expect(wordPos).toBe(1n);
    expect(mask).toBe(1n);
  });

  test('nonce 257 → wordPos 1, mask 2', () => {
    const { wordPos, mask } = computeNonceComponents(257n);
    expect(wordPos).toBe(1n);
    expect(mask).toBe(2n);
  });
});

// --- resolveExpiry ---

describe('resolveExpiry', () => {
  const limits = { defaultSeconds: 86400, minSeconds: 300, maxSeconds: 2592000 };

  test('null → default', () => {
    expect(resolveExpiry(null, limits)).toBe(86400);
  });

  test('undefined → default', () => {
    expect(resolveExpiry(undefined, limits)).toBe(86400);
  });

  test('value within range → unchanged', () => {
    expect(resolveExpiry(3600, limits)).toBe(3600);
  });

  test('below min → clamped to min', () => {
    expect(resolveExpiry(60, limits)).toBe(300);
  });

  test('above max → clamped to max', () => {
    expect(resolveExpiry(9999999, limits)).toBe(2592000);
  });

  test('exactly min → allowed', () => {
    expect(resolveExpiry(300, limits)).toBe(300);
  });

  test('exactly max → allowed', () => {
    expect(resolveExpiry(2592000, limits)).toBe(2592000);
  });
});

// --- checkPrecision ---

describe('checkPrecision', () => {
  test('integer → valid', () => {
    expect(checkPrecision('1000000', 6)).toBe(true);
  });

  test('exactly 6 decimals → valid', () => {
    expect(checkPrecision('0.000001', 6)).toBe(true);
  });

  test('7 decimals → invalid', () => {
    expect(checkPrecision('0.0000001', 6)).toBe(false);
  });

  test('no dot → valid', () => {
    expect(checkPrecision('42', 6)).toBe(true);
  });

  test('5 decimals → valid', () => {
    expect(checkPrecision('1.12345', 6)).toBe(true);
  });

  test('boundary: maxDecimals=0 integer → valid', () => {
    expect(checkPrecision('5', 0)).toBe(true);
  });
});
