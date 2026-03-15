#!/usr/bin/env node
import { readFileSync, writeFileSync, existsSync, mkdirSync, copyFileSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import { homedir } from "os";
import { generatePrivateKey, privateKeyToAccount } from "viem/accounts";

const __dirname = dirname(fileURLToPath(import.meta.url));
const stateDir = join(__dirname, "..", "state");
const walletFile = join(stateDir, "wallet.json");

// Persistent dir survives skill updates
const persistDir = process.env.RMB_PERSIST_DIR || join(homedir(), ".rent-my-browser");
const persistWalletFile = join(persistDir, "wallet.json");

mkdirSync(stateDir, { recursive: true });
mkdirSync(persistDir, { recursive: true });

// Check local first, then persistent backup
if (existsSync(walletFile)) {
  const existing = JSON.parse(readFileSync(walletFile, "utf-8"));
  process.stdout.write(existing.address);
  process.exit(0);
}

if (existsSync(persistWalletFile)) {
  copyFileSync(persistWalletFile, walletFile);
  const existing = JSON.parse(readFileSync(walletFile, "utf-8"));
  process.stdout.write(existing.address);
  process.exit(0);
}

const privateKey = generatePrivateKey();
const account = privateKeyToAccount(privateKey);

const walletData = JSON.stringify(
  { privateKey, address: account.address, createdAt: new Date().toISOString() },
  null,
  2
);

// Save to both local and persistent
writeFileSync(walletFile, walletData, { mode: 0o600 });
writeFileSync(persistWalletFile, walletData, { mode: 0o600 });

process.stdout.write(account.address);
