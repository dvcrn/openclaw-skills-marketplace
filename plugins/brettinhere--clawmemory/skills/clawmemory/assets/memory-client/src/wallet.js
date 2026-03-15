"use strict";
/**
 * wallet.js — Encrypted local wallet management for memory-client
 *
 * Wallets are stored as AES-256-GCM encrypted JSON keystores in ~/.omp/wallet.enc
 *
 * SECURITY:
 *  - Private key is only shown ONCE on creation, never again
 *  - Keystore file uses AES-256-GCM authenticated encryption
 *  - Password is read from env or interactive prompt — never logged
 *
 * AUDIT NOTE (L-01): WALLET_PASSWORD / MINER_WALLET_PASSWORD environment
 * variables are convenient for automation but are visible to other processes
 * on the same machine via /proc/[pid]/environ (Linux). For production servers:
 *  1. Prefer interactive password input (omit the env var)
 *  2. Or clear the env var immediately after reading:
 *       const pw = process.env.WALLET_PASSWORD; delete process.env.WALLET_PASSWORD;
 *  3. For high-security deployments, use a KMS or HSM instead of file-based keystore.
 */

const crypto = require("crypto");
const fs     = require("fs");
const path   = require("path");
const os     = require("os");
const readline = require("readline");
const { ethers } = require("ethers");

const WALLET_DIR   = path.join(os.homedir(), ".omp");
const WALLET_FILE  = path.join(WALLET_DIR, "wallet.enc");
const SCRYPT_N     = 2 ** 13;
const SCRYPT_R     = 8;
const SCRYPT_P     = 1;
const KEY_LEN      = 32;
const IV_LEN       = 12;
const TAG_LEN      = 16;
const SALT_LEN     = 32;

function ensureDir() {
  if (!fs.existsSync(WALLET_DIR)) {
    fs.mkdirSync(WALLET_DIR, { recursive: true, mode: 0o700 });
  }
}

/**
 * Derive encryption key from password + random salt (scrypt).
 */
function deriveEncKey(password, salt) {
  return crypto.scryptSync(Buffer.from(password), salt, KEY_LEN, {
    N: SCRYPT_N, r: SCRYPT_R, p: SCRYPT_P,
  });
}

/**
 * Encrypt a plaintext Buffer with AES-256-GCM.
 * Output: [salt(32)] [iv(12)] [authTag(16)] [ciphertext]
 */
function encryptWallet(plaintext, password) {
  const salt    = crypto.randomBytes(SALT_LEN);
  const key     = deriveEncKey(password, salt);
  const iv      = crypto.randomBytes(IV_LEN);
  const cipher  = crypto.createCipheriv("aes-256-gcm", key, iv);
  const enc     = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const authTag = cipher.getAuthTag();
  return Buffer.concat([salt, iv, authTag, enc]);
}

/**
 * Decrypt a buffer produced by encryptWallet().
 */
function decryptWallet(buf, password) {
  if (buf.length < SALT_LEN + IV_LEN + TAG_LEN) {
    throw new Error("wallet: encrypted file too short");
  }
  const salt     = buf.slice(0, SALT_LEN);
  const iv       = buf.slice(SALT_LEN, SALT_LEN + IV_LEN);
  const authTag  = buf.slice(SALT_LEN + IV_LEN, SALT_LEN + IV_LEN + TAG_LEN);
  const ctxt     = buf.slice(SALT_LEN + IV_LEN + TAG_LEN);
  const key      = deriveEncKey(password, salt);
  const decipher = crypto.createDecipheriv("aes-256-gcm", key, iv);
  decipher.setAuthTag(authTag);
  return Buffer.concat([decipher.update(ctxt), decipher.final()]);
}

/**
 * Prompt user for password (hidden input).
 */
async function promptPassword(prompt) {
  // Use env variable first for non-interactive / scripted usage
  if (process.env.WALLET_PASSWORD) {
    // FIX L-01: read password then immediately delete from env to minimize
    // exposure window via /proc/[pid]/environ on Linux systems.
    const pw = process.env.WALLET_PASSWORD;
    delete process.env.WALLET_PASSWORD;
    return pw;
  }

  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    process.stdout.write(prompt);
    process.stdin.setRawMode?.(true);
    let pwd = "";
    process.stdin.on("data", (char) => {
      char = char.toString();
      if (char === "\n" || char === "\r") {
        process.stdin.setRawMode?.(false);
        process.stdout.write("\n");
        rl.close();
        resolve(pwd);
      } else if (char === "\u0003") {
        process.exit();
      } else {
        pwd += char;
        process.stdout.write("*");
      }
    });
  });
}

/**
 * Load an existing wallet from the encrypted local file.
 *
 * @returns {Promise<ethers.Wallet>} Wallet with no provider (attach separately)
 */
async function loadWallet() {
  if (!fs.existsSync(WALLET_FILE)) {
    throw new Error(`No wallet found at ${WALLET_FILE}. Run 'omp init' to create one.`);
  }
  const password = await promptPassword("Wallet password: ");
  const encrypted = fs.readFileSync(WALLET_FILE);
  let plaintext;
  try {
    plaintext = decryptWallet(encrypted, password);
  } catch {
    throw new Error("wallet: wrong password or corrupted keystore");
  }
  const { privateKey } = JSON.parse(plaintext.toString("utf8"));
  return new ethers.Wallet(privateKey);
}

/**
 * Create a new wallet, encrypt it, and save to disk.
 * Private key is printed ONCE — user must save it manually.
 *
 * @returns {Promise<ethers.Wallet>}
 */
async function createWallet() {
  if (fs.existsSync(WALLET_FILE)) {
    throw new Error(`Wallet already exists at ${WALLET_FILE}. Delete it first to create a new one.`);
  }
  ensureDir();

  const wallet   = ethers.Wallet.createRandom();
  const password = await promptPassword("Set wallet password: ");
  const confirm  = await promptPassword("Confirm password: ");

  if (password !== confirm) throw new Error("Passwords do not match");
  if (password.length < 8)  throw new Error("Password must be at least 8 characters");

  const keystoreData = JSON.stringify({ privateKey: wallet.privateKey, address: wallet.address });
  const encrypted    = encryptWallet(Buffer.from(keystoreData, "utf8"), password);
  fs.writeFileSync(WALLET_FILE, encrypted, { mode: 0o600 });

  // ⚠️ Private key shown ONCE — user responsibility to back it up
  console.log("\n═══════════════════════════════════════════════════");
  console.log("  Wallet created successfully!");
  console.log("  Address:     ", wallet.address);
  console.log("  Private key: ", wallet.privateKey);
  console.log("  ⚠️  Save your private key NOW — it will not be shown again!");
  console.log("═══════════════════════════════════════════════════\n");

  return wallet;
}

module.exports = { loadWallet, createWallet };
