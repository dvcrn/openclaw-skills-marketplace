"use strict";
/**
 * crypto.js — Symmetric encryption for memory payloads
 *
 * SECURITY NOTES:
 *  - Uses AES-256-GCM (authenticated encryption) — provides confidentiality + integrity
 *  - Key derivation uses scrypt with dynamic salt derived from wallet address + timestamp
 *  - Salt = keccak256(address + timestamp) so each file gets a unique key even
 *    if the same wallet stores the same content at different times
 *  - GCM auth tag (16 bytes) is verified on decrypt — tamper detection
 *  - Never use the same (key, IV) pair twice — IV is randomly generated each encrypt
 */

const crypto  = require("crypto");
const { ethers } = require("ethers");

const SCRYPT_N  = 2 ** 13; // CPU/mem cost (32768 — balanced for client use)
const SCRYPT_R  = 8;
const SCRYPT_P  = 1;
const KEY_LEN   = 32;      // AES-256
const IV_LEN    = 12;      // GCM nonce (96 bits recommended)
const TAG_LEN   = 16;      // GCM auth tag

/**
 * Derive a 32-byte AES key from a private key + wallet address + timestamp.
 *
 * @param {string} privateKey   Hex private key (with or without 0x prefix)
 * @param {string} walletAddress Checksummed EVM address
 * @param {number} timestamp    Unix timestamp (seconds) — baked into the salt
 * @returns {Buffer} 32-byte key
 */
function deriveKey(privateKey, walletAddress, timestamp) {
  // SECURITY: salt = keccak256(addr ++ timestamp) — dynamic per file/time
  // Using ethers.keccak256 to stay consistent with on-chain Keccak-256 usage
  const saltInput = ethers.solidityPacked(
    ["address", "uint256"],
    [walletAddress, timestamp]
  );
  // ethers returns a 0x-prefixed hex string; strip prefix for use as Buffer
  const saltHex = ethers.keccak256(saltInput).slice(2);
  const salt    = Buffer.from(saltHex, "hex");

  // Password = raw private key bytes (stripped of 0x if present)
  const pkHex   = privateKey.startsWith("0x") ? privateKey.slice(2) : privateKey;
  const password = Buffer.from(pkHex, "hex");

  return crypto.scryptSync(password, salt, KEY_LEN, { N: SCRYPT_N, r: SCRYPT_R, p: SCRYPT_P });
}

/**
 * Encrypt plaintext with AES-256-GCM.
 *
 * Output layout: [IV (12 bytes)] [authTag (16 bytes)] [ciphertext (N bytes)]
 *
 * @param {Buffer|string} plaintext  Data to encrypt
 * @param {Buffer}        key        32-byte AES key (from deriveKey)
 * @returns {Buffer}
 */
function encrypt(plaintext, key) {
  const iv      = crypto.randomBytes(IV_LEN);
  const cipher  = crypto.createCipheriv("aes-256-gcm", key, iv);
  const input   = Buffer.isBuffer(plaintext) ? plaintext : Buffer.from(plaintext);
  const enc1    = cipher.update(input);
  const enc2    = cipher.final();
  const authTag = cipher.getAuthTag(); // 16 bytes GCM tag

  return Buffer.concat([iv, authTag, enc1, enc2]);
}

/**
 * Decrypt a buffer produced by encrypt().
 *
 * @param {Buffer} buf  Encrypted buffer
 * @param {Buffer} key  32-byte AES key
 * @returns {Buffer} Decrypted plaintext
 * @throws If auth tag verification fails (tampering detected)
 */
function decrypt(buf, key) {
  if (buf.length < IV_LEN + TAG_LEN) {
    throw new Error("crypto: buffer too short to contain IV + authTag");
  }
  const iv       = buf.slice(0, IV_LEN);
  const authTag  = buf.slice(IV_LEN, IV_LEN + TAG_LEN);
  const ciphertext = buf.slice(IV_LEN + TAG_LEN);

  const decipher = crypto.createDecipheriv("aes-256-gcm", key, iv);
  // SECURITY: setAuthTag must be called before .update/.final for GCM verification
  decipher.setAuthTag(authTag);

  const dec1 = decipher.update(ciphertext);
  const dec2 = decipher.final(); // throws if authTag mismatch
  return Buffer.concat([dec1, dec2]);
}

module.exports = { deriveKey, encrypt, decrypt };
