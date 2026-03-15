#!/usr/bin/env node
// activate.js — One-command GuavaSuite activation CLI
// Why: Users shouldn't need to curl multiple endpoints manually.
// This script wraps the entire challenge→sign→verify→activate flow.

import http from "node:http";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { exec } from "node:child_process";
import { homedir } from "node:os";
import { createInterface } from "node:readline";
import { LicenseService } from "./licenseService.js";
import { SuiteGate } from "./suiteGate.js";
import { SuiteBridge } from "./suiteBridge.js";
import { DOMAIN, TYPES } from "./signatureVerifier.js";

// ── Config ──

const SUITE_DIR = join(homedir(), ".openclaw", "guava-suite");
const TOKEN_FILE = join(SUITE_DIR, "token.jwt");
const CONFIG_FILE = join(homedir(), ".openclaw", "openclaw.json");
const PORT = parseInt(process.env.LICENSE_PORT || "3100", 10);
const JWT_SECRET = process.env.JWT_SECRET || "guava-suite-secret-" + homedir();

// ── Helpers ──

function ensureDir(dir) {
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
}

function readConfig() {
    try {
        return JSON.parse(readFileSync(CONFIG_FILE, "utf8"));
    } catch {
        return {};
    }
}

function writeConfig(config) {
    writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2) + "\n");
}

function ask(question) {
    const rl = createInterface({ input: process.stdin, output: process.stdout });
    return new Promise((resolve) => {
        rl.question(question, (answer) => {
            rl.close();
            resolve(answer.trim());
        });
    });
}

// ── EIP-712 message display ──

function displaySigningMessage(nonce, address) {
    console.log("\n┌──────────────────────────────────────────┐");
    console.log("│  🍈 EIP-712 Signing Required             │");
    console.log("├──────────────────────────────────────────┤");
    console.log("│                                          │");
    console.log("│  Sign this message in your wallet:       │");
    console.log("│                                          │");
    console.log(`│  Domain: ${DOMAIN.name} v${DOMAIN.version} (Chain ${DOMAIN.chainId})  │`);
    console.log("│  Type: LicenseChallenge                  │");
    console.log(`│  nonce: ${nonce.slice(0, 20)}...       │`);
    console.log(`│  address: ${address.slice(0, 14)}...${address.slice(-4)}       │`);
    console.log("│  action: activate-guava-suite            │");
    console.log("│                                          │");
    console.log("└──────────────────────────────────────────┘");
    console.log("\n💡 Use MetaMask or any EIP-712 compatible wallet.");
    console.log("   Or use the signing helper at: https://eip712.guava.dev (coming soon)\n");
}

// ── Status check ──

async function checkStatus() {
    console.log("\n🍈 GuavaSuite Status Check\n");

    // Check saved token
    if (existsSync(TOKEN_FILE)) {
        const token = readFileSync(TOKEN_FILE, "utf8").trim();
        const gate = new SuiteGate({ jwtSecret: JWT_SECRET });
        const status = gate.activate(token);

        if (status.suiteEnabled) {
            const bridge = new SuiteBridge({ gate });
            const fullStatus = bridge.getStatus();
            console.log("  ✅ Suite: ACTIVE");
            console.log(`  🛡️ Guard Mode: ${fullStatus.guardMode}`);
            console.log(`  📅 Expires: ${status.expiresAt ? new Date(status.expiresAt).toISOString() : "N/A"}`);
            console.log("\n  Features:");
            for (const [feat, enabled] of Object.entries(fullStatus.features)) {
                console.log(`    ${enabled ? "✅" : "❌"} ${feat}`);
            }
            return;
        }

        console.log("  ⚠️  Token found but expired or invalid");
        console.log("  → Run: node activate.js --wallet 0x...");
        return;
    }

    console.log("  ❌ Suite: NOT ACTIVATED");
    console.log("  → Run: node activate.js --wallet 0x...");
    console.log("  → Need: 1,000,000+ $GUAVA on Polygon Mainnet");
}

// ── Activation flow ──

async function activate(walletAddress) {
    console.log("\n🍈 GuavaSuite Activation\n");
    console.log(`  Wallet: ${walletAddress}`);

    // 1. Create service and get challenge
    const service = new LicenseService({ jwtSecret: JWT_SECRET });

    console.log("\n  [1/4] Requesting challenge...");
    const { nonce, expiresAt } = service.issueChallenge(walletAddress);
    console.log(`  ✅ Challenge issued (expires: ${new Date(expiresAt).toLocaleTimeString()})`);

    // 2. Display signing message
    displaySigningMessage(nonce, walletAddress);

    // 3. Auto-open sign-helper.html with nonce pre-filled
    const __dirname = dirname(fileURLToPath(import.meta.url));
    const helperPath = join(__dirname, "sign-helper.html");
    if (existsSync(helperPath)) {
        const helperUrl = `file://${helperPath}?nonce=${encodeURIComponent(nonce)}`;
        console.log("  🌐 Opening signing helper in browser...");
        // macOS: open, Linux: xdg-open, Windows: start
        const cmd = process.platform === "darwin" ? "open" : process.platform === "win32" ? "start" : "xdg-open";
        exec(`${cmd} "${helperUrl}"`, (err) => {
            if (err) console.log("  ⚠️  Could not auto-open browser. Open sign-helper.html manually.");
        });
    } else {
        console.log("  ⚠️  sign-helper.html not found. Sign manually with your wallet.");
    }

    // 4. Get signature from user
    const signature = await ask("  Paste your signature (0x...): ");

    if (!signature || !signature.startsWith("0x")) {
        console.error("\n  ❌ Invalid signature format. Must start with 0x.");
        process.exit(1);
    }

    // 4. Verify and get JWT
    console.log("\n  [2/4] Verifying signature & checking $GUAVA balance...");
    const result = await service.verify({
        address: walletAddress,
        nonce,
        signature,
    });

    if (!result.ok) {
        console.error(`\n  ❌ Verification failed: ${result.code}`);
        if (result.code === "INSUFFICIENT_BALANCE") {
            console.error(`     Current: ${result.balance?.current || "?"} $GUAVA`);
            console.error(`     Required: ${result.balance?.required || "1,000,000"} $GUAVA`);
            console.error("     → Buy $GUAVA: https://quickswap.exchange/#/swap");
        }
        process.exit(1);
    }

    // 5. Save JWT
    console.log("  [3/4] Saving license token...");
    ensureDir(SUITE_DIR);
    writeFileSync(TOKEN_FILE, result.token);
    console.log(`  ✅ Token saved to ${TOKEN_FILE}`);

    // 6. Update openclaw.json
    console.log("  [4/4] Activating strict mode...");
    const config = readConfig();
    if (!config.plugins) config.plugins = {};
    if (!config.plugins["guard-scanner"]) config.plugins["guard-scanner"] = {};
    config.plugins["guard-scanner"].mode = "strict";
    config.plugins["guard-scanner"].suiteEnabled = true;
    writeConfig(config);
    console.log("  ✅ guard-scanner mode set to: strict");

    // 7. Verify activation
    const gate = new SuiteGate({ jwtSecret: JWT_SECRET });
    const status = gate.activate(result.token);
    const bridge = new SuiteBridge({ gate });

    console.log("\n┌──────────────────────────────────────────┐");
    console.log("│  🍈 GuavaSuite Activated!                │");
    console.log("├──────────────────────────────────────────┤");
    console.log(`│  Mode: ${bridge.getMode().padEnd(33)}│`);
    console.log(`│  Suite: ${status.suiteEnabled ? "ACTIVE ✅" : "INACTIVE ❌"}                       │`);
    if (result.balance) {
        console.log(`│  Balance: ${result.balance.current} $GUAVA              │`);
    }
    console.log("│  Token expires in: 24h                   │");
    console.log("│                                          │");
    console.log("│  Re-activate daily or set up auto-renew  │");
    console.log("└──────────────────────────────────────────┘");
}

// ── Deactivate ──

async function deactivate() {
    console.log("\n🍈 Deactivating GuavaSuite...\n");

    // Remove token
    if (existsSync(TOKEN_FILE)) {
        const { unlinkSync } = await import("node:fs");
        unlinkSync(TOKEN_FILE);
        console.log("  ✅ Token removed");
    }

    // Reset config
    const config = readConfig();
    if (config.plugins?.["guard-scanner"]) {
        config.plugins["guard-scanner"].mode = "enforce";
        config.plugins["guard-scanner"].suiteEnabled = false;
        writeConfig(config);
        console.log("  ✅ guard-scanner mode reset to: enforce");
    }

    console.log("\n  Suite deactivated. OSS guard remains active.");
}

// ── CLI ──

const args = process.argv.slice(2);

if (args.includes("--help") || args.includes("-h")) {
    console.log(`
🍈 GuavaSuite CLI

Usage:
  node activate.js --wallet 0x...    Activate with wallet
  node activate.js --status          Check activation status
  node activate.js --deactivate      Deactivate suite
  node activate.js --help            Show this help

Environment:
  JWT_SECRET       Secret for JWT signing (default: auto-generated)
  LICENSE_PORT     API port (default: 3100)
`);
    process.exit(0);
}

if (args.includes("--status")) {
    await checkStatus();
    process.exit(0);
}

if (args.includes("--deactivate")) {
    await deactivate();
    process.exit(0);
}

const walletIdx = args.indexOf("--wallet");
if (walletIdx === -1 || !args[walletIdx + 1]) {
    console.error("❌ Wallet address required. Usage: node activate.js --wallet 0x...");
    process.exit(1);
}

const wallet = args[walletIdx + 1];
if (!wallet.startsWith("0x") || wallet.length !== 42) {
    console.error("❌ Invalid wallet address. Must be 42-char hex starting with 0x.");
    process.exit(1);
}

await activate(wallet);
