#!/usr/bin/env node
"use strict";
/**
 * index.js — OMP Miner main process
 *
 * Fixes applied (audit 2026-03-09):
 *  C-01: hcServer passed as parameter to submitSolution (was global.__hcServer, never set)
 *  C-02: wallet.address passed to spawnWorker (was currentChallenge.minerAddr, always "")
 *  H-01: wallet passed as parameter to submitSolution (was re-created every call)
 *  M-05: subscribe MemoryStored event → immediately host new files (was 5-min polling only)
 */

require("dotenv").config();
const { ethers }       = require("ethers");
const { Worker }       = require("worker_threads");
const os               = require("os");
const path             = require("path");

const { loadWallet, createWallet }    = require("./wallet");
const { createMinerChain }            = require("./chain");
const { createHypercoreServer }       = require("./hypercore-server");
const { buildProof }                  = require("./merkle-prover");

const NUM_WORKERS = Math.max(1, os.cpus().length - 1);
const WORKER_FILE = path.join(__dirname, "pow-worker.js");

// ─── State ──────────────────────────────────────────────────────────────────
let currentChallenge  = null;   // { targetRoot, epochSeed, target }
let activeWorkers     = [];
let todaySubmissions  = 0;
let totalHashrate     = 0;
let mining            = false;
let submitting        = false;  // prevent concurrent PoW submissions

// ─── Main ────────────────────────────────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2);

  if (args.includes("--init")) {
    await createWallet();
    process.exit(0);
  }

  const rpc      = process.env.RPC_URL || process.env.BSC_RPC || "https://bsc-dataseed.binance.org/";
  const provider = new ethers.JsonRpcProvider(rpc);

  let wallet;
  try {
    wallet = (await loadWallet()).connect(provider);
  } catch (err) {
    console.error("Error loading wallet:", err.message);
    console.error("Run with --init to create a wallet first.");
    process.exit(1);
  }

  const { protocolAddr, mmpAddr } = getAddresses();
  const chain = createMinerChain({ wallet, protocolAddr, mmpAddr });

  console.log("═══════════════════════════════════════════════════");
  console.log("  OMP Miner v1.0.1");
  console.log(`  Miner address: ${wallet.address}`);
  console.log(`  Protocol:      ${protocolAddr}`);
  console.log(`  Workers:       ${NUM_WORKERS}`);
  console.log("═══════════════════════════════════════════════════");

  // ── Start Hypercore server ─────────────────────────────────────────────
  // FIX C-01: hcServer is a named local variable, passed explicitly to
  //           submitSolution() — never assigned to global to avoid pollution.
  const hcServer = createHypercoreServer({
    listActiveRoots: () => chain.listActiveRoots(),
  });

  hcServer.on("hosting",     ({ root }) => console.log(`[P2P] Hosting: ${root.slice(0, 18)}...`));
  hcServer.on("replicating", ({ root }) => console.log(`[P2P] Replicating: ${root.slice(0, 18)}...`));
  hcServer.on("error",       (err)      => console.warn("[P2P] Error:", err));

  await hcServer.start();

  // ── Fetch initial PoW params ──────────────────────────────────────────
  try {
    const params = await chain.getPoWParams();
    if (params.targetRoot !== ethers.ZeroHash) {
      currentChallenge = {
        targetRoot: params.targetRoot,
        epochSeed:  params.epochSeed,
        target:     params.target,
      };
      startMining(wallet, chain, hcServer);
    } else {
      console.log("[miner] No challenge yet — waiting for first MemoryStored event...");
    }
  } catch (err) {
    console.warn("[miner] Could not fetch PoW params:", err.message);
  }

  // ── Subscribe to ChallengeUpdated events (event-driven) ──────────────
  chain.subscribeChallenge(({ targetRoot, epochSeed, epochStart }) => {
    console.log(`\n[miner] New challenge: ${targetRoot.slice(0, 18)}... epoch@${epochStart}`);
    currentChallenge = { targetRoot, epochSeed, target: currentChallenge?.target };
    chain.getPoWParams().then((p) => {
      currentChallenge.target = p.target;
      restartWorkers(wallet, chain, hcServer);
    }).catch(() => restartWorkers(wallet, chain, hcServer));
  });

  // ── FIX M-05: Subscribe to MemoryStored event ────────────────────────
  // When a new file is stored, immediately add it to the Hypercore server
  // instead of waiting up to 5 minutes for the next scheduled refresh.
  chain.subscribeMemoryStored(({ owner, merkleRoot }) => {
    console.log(`[miner] New file stored by ${owner.slice(0, 10)}..., adding to P2P hosting`);
    hcServer.addRoot(merkleRoot).catch((err) =>
      console.warn("[miner] Could not add new root to P2P:", err.message)
    );
  });

  // ── Status printer every 10 seconds ──────────────────────────────────
  setInterval(async () => {
    const balance = await chain.getBalance().catch(() => 0n);
    const hosted  = hcServer.count;
    console.log(
      `[status] hashrate=${formatHashrate(totalHashrate)} | ` +
      `today=${todaySubmissions} submissions | ` +
      `balance=${ethers.formatEther(balance)} MMP | ` +
      `hosting=${hosted} roots`
    );
  }, 10_000);

  // ── Refresh hosted roots every 5 minutes (fallback) ──────────────────
  setInterval(() => hcServer.refresh().catch(() => {}), 5 * 60_000);

  process.on("SIGINT", async () => {
    console.log("\n[miner] Shutting down...");
    stopWorkers();
    await hcServer.destroy();
    process.exit(0);
  });
}

// ─── Worker Management ──────────────────────────────────────────────────────

function startMining(wallet, chain, hcServer) {
  if (mining || !currentChallenge) return;
  mining = true;
  console.log(`[miner] Starting ${NUM_WORKERS} PoW workers...`);
  for (let i = 0; i < NUM_WORKERS; i++) {
    spawnWorker(i, wallet, chain, hcServer);
  }
}

function stopWorkers() {
  mining = false;
  for (const w of activeWorkers) {
    w.terminate().catch(() => {});
  }
  activeWorkers = [];
}

function restartWorkers(wallet, chain, hcServer) {
  stopWorkers();
  mining = false;
  if (currentChallenge) {
    startMining(wallet, chain, hcServer);
  }
}

function spawnWorker(workerIndex, wallet, chain, hcServer) {
  if (!currentChallenge) return;

  const { targetRoot, epochSeed, target } = currentChallenge;

  // Stagger nonces across workers to avoid redundant work
  const startNonce = BigInt(workerIndex) * BigInt(Number.MAX_SAFE_INTEGER);

  const worker = new Worker(WORKER_FILE, {
    workerData: {
      targetRoot,
      epochSeed,
      target:     target.toString(),
      // FIX C-02: use wallet.address (real miner address) instead of
      //           currentChallenge.minerAddr which was never set (always "").
      //           The contract verifies keccak256(nonce, msg.sender, root, seed),
      //           so the address used here MUST match the submitting wallet.
      minerAddr:  wallet.address,
      startNonce: startNonce.toString(),
    },
  });

  activeWorkers.push(worker);

  worker.on("message", async (msg) => {
    if (!msg.found) {
      totalHashrate = (totalHashrate + (msg.hashrate || 0)) / 2;
      return;
    }

    const nonce = BigInt(msg.nonce);
    console.log(`\n[miner] Worker ${workerIndex} found nonce: ${nonce}`);

    if (submitting) {
      console.log('[miner] Already submitting, discarding duplicate nonce');
      return;
    }
    submitting = true;
    stopWorkers();

    try {
      // FIX C-01 + H-01: pass wallet, chain, hcServer as parameters
      // Use the challenge snapshot from when this worker was started, not the
      // current global challenge which may have been refreshed in the meantime.
      // Use the challenge snapshot (targetRoot/epochSeed/target) captured when
      // this worker was spawned — NOT currentChallenge which may have refreshed.
      const workerChallenge = { targetRoot, epochSeed, target };
      await submitSolution(nonce, workerChallenge, wallet, chain, hcServer);
    } catch (err) {
      console.error("[miner] Submit failed:", err.message);
    } finally {
      submitting = false;
    }

    setTimeout(() => {
      mining = false;
      startMining(wallet, chain, hcServer);
    }, 2000);
  });

  worker.on("error", (err) => {
    console.error(`[worker ${workerIndex}] Error:`, err.message);
  });

  worker.on("exit", (code) => {
    activeWorkers = activeWorkers.filter((w) => w !== worker);
    if (mining && code !== 0) {
      setTimeout(() => spawnWorker(workerIndex, wallet, chain, hcServer), 1000);
    }
  });
}

// ─── PoW Submission ─────────────────────────────────────────────────────────

/**
 * FIX C-01: hcServer passed as parameter (was global.__hcServer, never assigned).
 * FIX H-01: wallet + chain passed as parameters (was re-created every call,
 *           which re-invoked loadWallet() and prompted for password each time).
 */
async function submitSolution(nonce, challenge, wallet, chain, hcServer) {
  // Always fetch live challenge from chain — epochSeed may have changed since worker started
  const livePow = await chain.getPoWParams();
  const targetRoot = livePow.targetRoot;
  const epochSeed  = livePow.epochSeed;
  const liveTarget = livePow.target;

  // Verify nonce is still valid against the live challenge before submitting
  const { ethers: _ethers } = require('ethers');
  const _packed = _ethers.solidityPacked(
    ['uint256','address','bytes32','bytes32'],
    [nonce, wallet.address, targetRoot, epochSeed]
  );
  const _powHash = _ethers.keccak256(_packed);
  if (BigInt(_powHash) >= liveTarget) {
    console.log('[miner] Nonce stale (challenge refreshed mid-mining) — skipping, workers will restart');
    return;
  }

  // Get tree info
  const treeInfo  = await chain.getTreeInfo(targetRoot);
  const numChunks = Number(treeInfo.numChunks);

  // Determine which chunk to prove (must match contract's expected index)
  const proveIndex = Number(BigInt(epochSeed) % BigInt(numChunks));

  // Retrieve chunk data from Hypercore server
  const core = hcServer.getCore(targetRoot);

  let chunkData;
  if (core && proveIndex < core.length) {
    chunkData = await core.get(proveIndex);
  } else {
    console.warn("[miner] Chunk data not available for proof — skipping submission");
    return;
  }

  // FIX Miner-L-01: do NOT silently fallback to zero-filled buffers for missing chunks.
  // A zero-filled chunk builds an invalid Merkle proof → submitPoW reverts → gas wasted.
  // Instead, abort the submission and warn so the miner waits for full sync.
  const allChunks = [];
  for (let i = 0; i < numChunks; i++) {
    let chunk;
    try { chunk = await core.get(i); } catch { /* not available */ }
    if (!chunk) {
      console.warn(`[miner] Chunk ${i}/${numChunks} not available — aborting submission to avoid gas waste`);
      return;
    }
    allChunks.push(chunk);
  }
  const { proof } = buildProof(allChunks, proveIndex);

  const receipt = await chain.submitPoW(nonce, proveIndex, chunkData, proof);
  todaySubmissions++;
  console.log(`[miner] PoW submitted! Tx: ${receipt.hash} | Today: ${todaySubmissions}`);
}

// ─── Helpers ────────────────────────────────────────────────────────────────

function getAddresses() {
  const protocolAddr = process.env.PROTOCOL_ADDRESS;
  const mmpAddr      = process.env.MMP_TOKEN_ADDRESS;
  if (!protocolAddr || !mmpAddr) {
    console.error("Error: PROTOCOL_ADDRESS and MMP_TOKEN_ADDRESS must be in .env");
    process.exit(1);
  }
  return { protocolAddr, mmpAddr };
}

function formatHashrate(hps) {
  if (hps > 1e9) return `${(hps / 1e9).toFixed(2)} GH/s`;
  if (hps > 1e6) return `${(hps / 1e6).toFixed(2)} MH/s`;
  if (hps > 1e3) return `${(hps / 1e3).toFixed(2)} KH/s`;
  return `${Math.round(hps)} H/s`;
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
