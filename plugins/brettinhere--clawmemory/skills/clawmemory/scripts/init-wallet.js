#!/usr/bin/env node
/**
 * ClawMemory — headless wallet initializer
 * Creates wallet using WALLET_PASSWORD env var (no TTY required)
 * Usage: WALLET_PASSWORD=<pw> node init-wallet.js
 */
"use strict";

const crypto  = require("crypto");
const fs      = require("fs");
const path    = require("path");
const os      = require("os");
const { ethers } = require("ethers");

const WALLET_DIR  = path.join(os.homedir(), ".omp");
const WALLET_FILE = path.join(WALLET_DIR, "wallet.enc");

// Encryption params (must match wallet.js)
const SCRYPT_N = 2 ** 13;
const SCRYPT_R = 8;
const SCRYPT_P = 1;
const KEY_LEN  = 32;
const IV_LEN   = 12;
const TAG_LEN  = 16;
const SALT_LEN = 32;

function encryptWallet(data, password) {
  const salt       = crypto.randomBytes(SALT_LEN);
  const key        = crypto.scryptSync(Buffer.from(password), salt, KEY_LEN, { N: SCRYPT_N, r: SCRYPT_R, p: SCRYPT_P });
  const iv         = crypto.randomBytes(IV_LEN);
  const cipher     = crypto.createCipheriv("aes-256-gcm", key, iv);
  const encrypted  = Buffer.concat([cipher.update(data), cipher.final()]);
  const tag        = cipher.getAuthTag();
  return Buffer.concat([salt, iv, tag, encrypted]);
}

async function main() {
  const password = process.env.WALLET_PASSWORD;
  if (!password || password.length < 8) {
    console.error("ERROR: WALLET_PASSWORD env var required (min 8 chars)");
    process.exit(1);
  }

  if (fs.existsSync(WALLET_FILE)) {
    // Already exists — just load and print address
    const encrypted = fs.readFileSync(WALLET_FILE);
    const salt      = encrypted.slice(0, SALT_LEN);
    const iv        = encrypted.slice(SALT_LEN, SALT_LEN + IV_LEN);
    const tag       = encrypted.slice(SALT_LEN + IV_LEN, SALT_LEN + IV_LEN + TAG_LEN);
    const data      = encrypted.slice(SALT_LEN + IV_LEN + TAG_LEN);
    const key       = crypto.scryptSync(Buffer.from(password), salt, KEY_LEN, { N: SCRYPT_N, r: SCRYPT_R, p: SCRYPT_P });
    const decipher  = crypto.createDecipheriv("aes-256-gcm", key, iv);
    decipher.setAuthTag(tag);
    const decrypted = Buffer.concat([decipher.update(data), decipher.final()]);
    const { address } = JSON.parse(decrypted.toString("utf8"));
    console.log(JSON.stringify({ status: "exists", address }));
    return;
  }

  // Create wallet
  if (!fs.existsSync(WALLET_DIR)) fs.mkdirSync(WALLET_DIR, { recursive: true, mode: 0o700 });

  const wallet        = ethers.Wallet.createRandom();
  const keystoreData  = JSON.stringify({ privateKey: wallet.privateKey, address: wallet.address });
  const encrypted     = encryptWallet(Buffer.from(keystoreData, "utf8"), password);
  fs.writeFileSync(WALLET_FILE, encrypted, { mode: 0o600 });

  console.log(JSON.stringify({
    status:      "created",
    address:     wallet.address,
    privateKey:  wallet.privateKey,
    walletFile:  WALLET_FILE,
    warning:     "Save your private key — it will not be shown again"
  }));
}

main().catch(e => {
  console.error(JSON.stringify({ status: "error", message: e.message }));
  process.exit(1);
});
