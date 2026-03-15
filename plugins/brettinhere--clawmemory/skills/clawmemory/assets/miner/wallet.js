"use strict";
/**
 * wallet.js — Miner wallet management
 *
 * Mirrors memory-client/src/wallet.js but stored at ~/.omp/miner-wallet.enc
 * Private key shown ONCE on creation.
 */

const crypto   = require("crypto");
const fs       = require("fs");
const path     = require("path");
const os       = require("os");
const readline = require("readline");
const { ethers } = require("ethers");

const WALLET_DIR   = path.join(os.homedir(), ".omp");
const WALLET_FILE  = path.join(WALLET_DIR, "miner-wallet.enc");
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

function deriveEncKey(password, salt) {
  return crypto.scryptSync(Buffer.from(password), salt, KEY_LEN, {
    N: SCRYPT_N, r: SCRYPT_R, p: SCRYPT_P,
  });
}

function encryptWallet(plaintext, password) {
  const salt    = crypto.randomBytes(SALT_LEN);
  const key     = deriveEncKey(password, salt);
  const iv      = crypto.randomBytes(IV_LEN);
  const cipher  = crypto.createCipheriv("aes-256-gcm", key, iv);
  const enc     = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const authTag = cipher.getAuthTag();
  return Buffer.concat([salt, iv, authTag, enc]);
}

function decryptWallet(buf, password) {
  const salt    = buf.slice(0, SALT_LEN);
  const iv      = buf.slice(SALT_LEN, SALT_LEN + IV_LEN);
  const authTag = buf.slice(SALT_LEN + IV_LEN, SALT_LEN + IV_LEN + TAG_LEN);
  const ctxt    = buf.slice(SALT_LEN + IV_LEN + TAG_LEN);
  const key     = deriveEncKey(password, salt);
  const dec     = crypto.createDecipheriv("aes-256-gcm", key, iv);
  dec.setAuthTag(authTag);
  return Buffer.concat([dec.update(ctxt), dec.final()]);
}

async function promptPassword(prompt) {
  if (process.env.MINER_WALLET_PASSWORD) {
    // FIX L-01: delete after read to reduce /proc/[pid]/environ exposure window
    const pw = process.env.MINER_WALLET_PASSWORD;
    delete process.env.MINER_WALLET_PASSWORD;
    return pw;
  }
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    process.stdout.write(prompt);
    let pwd = "";
    process.stdin.setRawMode?.(true);
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
 * Load the miner wallet from encrypted local file.
 * @returns {Promise<ethers.Wallet>}
 */
async function loadWallet() {
  if (!fs.existsSync(WALLET_FILE)) {
    throw new Error(`No miner wallet at ${WALLET_FILE}. Run with --init to create one.`);
  }
  const password = await promptPassword("Miner wallet password: ");
  const buf      = fs.readFileSync(WALLET_FILE);
  let plain;
  try {
    plain = decryptWallet(buf, password);
  } catch {
    throw new Error("wallet: wrong password or corrupted keystore");
  }
  const { privateKey } = JSON.parse(plain.toString("utf8"));
  return new ethers.Wallet(privateKey);
}

/**
 * Create a new miner wallet.
 * @returns {Promise<ethers.Wallet>}
 */
async function createWallet() {
  if (fs.existsSync(WALLET_FILE)) {
    throw new Error(`Miner wallet already exists at ${WALLET_FILE}`);
  }
  ensureDir();

  const wallet   = ethers.Wallet.createRandom();
  const password = await promptPassword("Set miner wallet password: ");
  const confirm  = await promptPassword("Confirm password: ");
  if (password !== confirm) throw new Error("Passwords do not match");

  const data = JSON.stringify({ privateKey: wallet.privateKey, address: wallet.address });
  fs.writeFileSync(WALLET_FILE, encryptWallet(Buffer.from(data), password), { mode: 0o600 });

  console.log("\n═══════════════════════════════════════════════════");
  console.log("  Miner wallet created!");
  console.log("  Address:     ", wallet.address);
  console.log("  Private key: ", wallet.privateKey);
  console.log("  ⚠️  Save your private key NOW — it will not be shown again!");
  console.log("═══════════════════════════════════════════════════\n");

  return wallet;
}

module.exports = { loadWallet, createWallet };
