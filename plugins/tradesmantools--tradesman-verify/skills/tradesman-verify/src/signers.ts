/**
 * tradesman-verify — Signer implementations
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Built-in signer helpers for common key management patterns.
 * The library never holds private keys in memory beyond the caller's scope.
 *
 * For production deployments, implement the Signer interface directly
 * with your HSM, Vault, or cloud KMS.
 */

import { readFileSync } from 'fs';
import { sign as nodeCryptoSign, createPublicKey } from 'crypto';
import type { Signer } from './types.js';

/**
 * Load an Ed25519 signer from a PKCS#8 PEM file.
 *
 * The private key stays in memory only for the duration of signing calls.
 * The PEM content is captured in the returned closure — callers should
 * protect the file on disk (chmod 600, encrypted volume, etc.).
 *
 * Generate a key:
 *   openssl genpkey -algorithm ed25519 -out issuer.pem
 *
 * @param keyFile - Path to Ed25519 private key PEM (PKCS#8)
 * @param adiUrl  - ADI URL this signer is authorized for
 * @throws If the PEM is not a valid Ed25519 PKCS#8 key
 *
 * @example
 * ```typescript
 * import { loadSignerFromPem, issueCredential } from 'tradesman-verify';
 *
 * const signer = loadSignerFromPem('./issuer.pem', 'acc://tx-license-board.acme');
 * const result = await issueCredential({ ... }, signer);
 * ```
 */
export function loadSignerFromPem(keyFile: string, adiUrl: string): Signer {
  const pem = readFileSync(keyFile, 'utf-8');
  return loadSignerFromPemString(pem, adiUrl);
}

/**
 * Load an Ed25519 signer from a PEM string (e.g. from environment variable or secret store).
 *
 * @param pem    - PKCS#8 PEM string containing an Ed25519 private key
 * @param adiUrl - ADI URL this signer is authorized for
 * @throws If the PEM is not a valid Ed25519 PKCS#8 key
 *
 * @example
 * ```typescript
 * import { loadSignerFromPemString } from 'tradesman-verify';
 *
 * // Load from environment (e.g. Vault agent injected)
 * const signer = loadSignerFromPemString(process.env.ISSUER_KEY!, 'acc://my-org.acme');
 * ```
 */
export function loadSignerFromPemString(pem: string, adiUrl: string): Signer {
  const publicKeyObj = createPublicKey(pem);
  const publicKeyDer = publicKeyObj.export({ format: 'der', type: 'spki' }) as Buffer;
  // Last 32 bytes of SubjectPublicKeyInfo DER = raw Ed25519 public key
  const publicKey = new Uint8Array(publicKeyDer.subarray(-32));
  if (publicKey.length !== 32) {
    throw new Error(
      `Expected 32-byte Ed25519 public key, got ${publicKey.length} bytes. ` +
      `Ensure the PEM is an Ed25519 PKCS#8 key (openssl genpkey -algorithm ed25519).`
    );
  }

  return {
    adiUrl,
    publicKey,
    sign: async (data: Uint8Array): Promise<Uint8Array> => {
      return new Uint8Array(nodeCryptoSign(null, Buffer.from(data), pem));
    },
  };
}
