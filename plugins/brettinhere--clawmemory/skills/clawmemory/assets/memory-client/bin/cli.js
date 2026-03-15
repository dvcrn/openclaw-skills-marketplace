#!/usr/bin/env node
"use strict";
/**
 * cli.js — OpenClaw Memory Protocol CLI
 *
 * Commands:
 *   init    — Create a new wallet
 *   save    — Encrypt → Merkle → storeMemoryWithPermit → P2P confirm
 *   load    — Retrieve and decrypt a memory tree
 *   grant   — Grant read access to an address
 *   renew   — Extend expiry of a memory tree
 *   status  — Show tree info and expiry
 *   sync    — Re-upload chunks to P2P network
 *   topup   — Check balance and display top-up instructions
 */

require("dotenv").config();
const { program } = require("commander");
const { ethers }  = require("ethers");
const fs          = require("fs");
const path        = require("path");

const { createWallet, loadWallet }  = require("../src/wallet");
const { deriveKey, encrypt, decrypt } = require("../src/crypto");
const { buildTree, getProof }       = require("../src/merkle");
const { writeAndConfirm }           = require("../src/hypercore");
const { createChainClient }         = require("../src/chain");
const { buildIndexFile, parseIndexFile } = require("../src/index-file");

const VERSION = "1.0.0";

function getProvider() {
  const rpc = process.env.RPC_URL || process.env.BSC_RPC || "https://bsc-dataseed.binance.org/";
  return new ethers.JsonRpcProvider(rpc);
}

function getAddresses() {
  const protocolAddr = process.env.PROTOCOL_ADDRESS;
  const mmpAddr      = process.env.MMP_TOKEN_ADDRESS;
  if (!protocolAddr || !mmpAddr) {
    console.error("Error: PROTOCOL_ADDRESS and MMP_TOKEN_ADDRESS must be set in .env");
    process.exit(1);
  }
  return { protocolAddr, mmpAddr };
}

// ─── init ──────────────────────────────────────────────────────────────────
program
  .command("init")
  .description("Create a new encrypted wallet")
  .action(async () => {
    try {
      await createWallet();
    } catch (err) {
      console.error("init error:", err.message);
      process.exit(1);
    }
  });

// ─── save ──────────────────────────────────────────────────────────────────
program
  .command("save <file>")
  .description("Save a file to the memory protocol")
  .option("-r, --rent-blocks <n>", "Rent duration in blocks (0 = free if ≤10KB)", "201600")
  .option("--free", "Force free tier (must be ≤10KB)")
  .option("--slot <name>", "Named free slot (V3: up to 10 slots, ≤10KB each, permanent)")
  .action(async (filePath, opts) => {
    try {
      const provider = getProvider();
      const { protocolAddr, mmpAddr } = getAddresses();

      // 1. Load wallet
      const wallet    = (await loadWallet()).connect(provider);
      const chain     = createChainClient({ wallet, protocolAddr, mmpAddr });

      // 2. Read file
      if (!fs.existsSync(filePath)) {
        console.error(`File not found: ${filePath}`);
        process.exit(1);
      }
      const fileData = fs.readFileSync(filePath);
      const fileName = path.basename(filePath);
      const sizeBytes = fileData.length;

      // 3. Encrypt
      const timestamp = Math.floor(Date.now() / 1000);
      const key       = deriveKey(wallet.privateKey, wallet.address, timestamp);
      const encrypted = encrypt(fileData, key);
      console.log(`Encrypted: ${encrypted.length} bytes`);

      // 4. Build index file and encrypt it with the same key
      //    FIX H-04: index file is encrypted and PREPENDED to the Merkle Tree.
      //    FIX N-M-01: use 4-byte big-endian length prefix before encIndex so that
      //    load command can find the exact split point without brute-force search.
      //    Format: [4 bytes: encIndex.length BE] [encIndex bytes] [encrypted file bytes]
      const indexEntry = {
        name:         fileName,
        mimeType:     "application/octet-stream",
        sizeBytes,
        keyTimestamp: timestamp,
      };
      const indexBuf  = Buffer.from(buildIndexFile([indexEntry]));
      const encIndex  = encrypt(indexBuf, key);

      // Write 4-byte big-endian length prefix so load can find split point precisely
      const lenBuf = Buffer.allocUnsafe(4);
      lenBuf.writeUInt32BE(encIndex.length, 0);

      // Concatenate: [4B length | encIndex | encryptedFile] → single Merkle Tree
      const combined  = Buffer.concat([lenBuf, encIndex, encrypted]);

      // FIX CLI-M-01: sizeKB must be based on combined.length (not original fileData.length)
      // so that files at exact N×256KB boundaries don't produce numChunks mismatch vs sizeKB.
      const sizeKB    = Math.ceil(combined.length / 1024);

      const { tree, chunks, root, numChunks } = buildTree(combined);
      console.log(`Saving: ${fileName} (${sizeKB} KB combined)`);
      console.log(`Merkle root: ${root}`);
      console.log(`Chunks: ${numChunks} (4B+${encIndex.length}B index + ${encrypted.length}B file)`);

      // 6. store on-chain (named slot or paid/free)
      let receipt;
      if (opts.slot) {
        // V3: storeNamedSlot — free, permanent, up to 10 slots, <=10KB each
        if (sizeKB > 10) {
          console.error("Slot size " + sizeKB + "KB exceeds 10KB free limit for named slots.");
          process.exit(1);
        }
        const slotName = opts.slot.toLowerCase().replace(/\s+/g, "-").slice(0, 32);
        console.log("Storing in named slot \"" + slotName + "\" (free, permanent)...");
        receipt = await chain.storeNamedSlot({
          slotName,
          merkleRoot: root,
          sizeKB:     BigInt(sizeKB),
          numChunks:  BigInt(numChunks),
        });
      } else {
        const rentBlocks = opts.free ? 0n : BigInt(opts.rentBlocks);
        console.log("Storing on-chain (rentBlocks=" + rentBlocks + ")...");
        receipt = await chain.storeMemoryWithPermit({
          merkleRoot: root,
          sizeKB:     BigInt(sizeKB),
          numChunks:  BigInt(numChunks),
          rentBlocks,
        });
      }
      console.log("Stored! Tx: " + receipt.hash);

      // 7. P2P confirmation
      console.log("Waiting for P2P confirmations...");
      try {
        const p2p = await writeAndConfirm(chunks, root);
        console.log(`P2P confirmed: ${p2p.confirmations} peers, feedKey=${p2p.feedKey.slice(0, 16)}...`);
      } catch (p2pErr) {
        console.warn(`P2P warning (data stored on-chain): ${p2pErr.message}`);
      }

      // FIX CLI-M-02: print timestamp so user can use --timestamp=<n> with load command
      console.log(`Key timestamp: ${timestamp}  ← load 时需要：--timestamp=${timestamp}`);

      // Persist root metadata locally so timestamp is never lost
      const os = require("os");
      const metaDir = path.join(os.homedir(), ".omp", "roots");
      fs.mkdirSync(metaDir, { recursive: true });
      fs.writeFileSync(
        path.join(metaDir, root.replace("0x", "").slice(0, 16) + ".json"),
        JSON.stringify({ root, timestamp, fileName, sizeKB }, null, 2)
      );

      // FIX CLI-H-01: cache combined buffer so sync command can rebuild identical Merkle tree
      const cacheDir = path.join(os.homedir(), ".omp", "cache", root.replace("0x", "").slice(0, 16));
      fs.mkdirSync(cacheDir, { recursive: true });
      fs.writeFileSync(path.join(cacheDir, "combined.bin"), combined);

      console.log(`\n✓ Save complete. Root: ${root}`);
    } catch (err) {
      console.error("save error:", err.message);
      process.exit(1);
    }
  });

// ─── load ──────────────────────────────────────────────────────────────────
// FIX H-05: full P2P download + decrypt implementation.
// Flow:
//  1. Fetch tree metadata from chain (numChunks)
//  2. Connect to Hyperswarm, download all chunks
//  3. Decrypt first chunk(s) → parse index file → get keyTimestamp
//  4. Derive key, decrypt payload chunks → write to outFile
program
  .command("load <merkleRoot> <outFile>")
  .description("Download and decrypt a memory tree")
  .action(async (merkleRoot, outFile) => {
    try {
      const Hypercore  = require("hypercore");
      const Hyperswarm = require("hyperswarm");
      const provider   = getProvider();
      const { protocolAddr, mmpAddr } = getAddresses();
      const wallet     = (await loadWallet()).connect(provider);
      const chain      = createChainClient({ wallet, protocolAddr, mmpAddr });

      // Step 1: get tree metadata from chain
      const treeInfo = await chain.getUserTree(merkleRoot);
      if (treeInfo.owner === ethers.ZeroAddress) {
        console.error("Tree not found on-chain");
        process.exit(1);
      }
      const numChunks = Number(treeInfo.numChunks);
      console.log(`Tree: ${numChunks} chunks, expires block ${treeInfo.expiresAt}`);

      // Step 2: download all chunks from P2P
      // FIX N-L-02: use Hypercore v10 API (core.replicate(peerStream)) matching
      //             hypercore-server.js, not v9's .pipe() pattern.
      console.log("Connecting to P2P network...");
      const storageDir = path.join(
        process.env.HOME || process.env.USERPROFILE || ".",
        ".omp", "cache", merkleRoot.slice(0, 16)
      );
      const core  = new Hypercore(storageDir);
      await core.ready();

      const swarm = new Hyperswarm();
      const topic = Buffer.from(merkleRoot.replace(/^0x/, ""), "hex");
      swarm.join(topic, { server: false, client: true });

      await new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
          swarm.destroy();
          reject(new Error("P2P download timeout (60s) — no peers found"));
        }, 60_000);

        swarm.on("connection", (peerStream) => {
          // FIX N-L-02: Hypercore v10 replicate API — pass stream directly
          const clone = core.replicate(peerStream);
          clone.on("error", () => {});
          // FIX CLI-L-02: Hypercore v10 fires "sync" when all blocks are downloaded,
          // not "close". "close" fires when the stream is torn down (too late / wrong event).
          clone.on("sync", async () => {
            if (core.length >= numChunks) {
              clearTimeout(timer);
              await swarm.destroy();
              resolve();
            }
          });
        });
      });

      console.log(`Downloaded ${core.length} chunks`);

      // Step 3: read all chunks
      const allChunks = [];
      for (let i = 0; i < numChunks; i++) {
        allChunks.push(await core.get(i));
      }
      const combined = Buffer.concat(allChunks);

      // Step 4: parse index using 4-byte length prefix (FIX N-M-01)
      // Format written by save: [4B: encIndex.length BE] [encIndex] [encFile]
      // This eliminates brute-force search — we know exact split point immediately.
      // Bootstrap key: use --timestamp flag OR OMP_KEY_TIMESTAMP env to get initial key,
      // then read keyTimestamp from decrypted index for self-contained operation.
      const timestampEnv = process.env.OMP_KEY_TIMESTAMP;
      const tsArg        = process.argv.find(a => a.startsWith("--timestamp="))
                            ?.replace("--timestamp=", "");
      const timestampStr = tsArg || timestampEnv;
      if (!timestampStr) {
        console.error("Error: key timestamp required. Set --timestamp=<unix> or OMP_KEY_TIMESTAMP env.");
        console.error("(Timestamp was printed during 'save' — check your save log)");
        process.exit(1);
      }
      const timestamp = parseInt(timestampStr, 10);
      const key = deriveKey(wallet.privateKey, wallet.address, timestamp);

      // FIX N-M-01: read 4-byte length prefix to find exact split point
      const indexLen    = combined.readUInt32BE(0);
      const encIdx      = combined.slice(4, 4 + indexLen);
      const encFile     = combined.slice(4 + indexLen);

      // Decrypt index → extract keyTimestamp for file decryption
      const idxPlain    = decrypt(encIdx, key);
      const idxData     = parseIndexFile(idxPlain.toString("utf8"));
      const entry       = idxData.entries?.[0] || idxData[0] || {};
      const fileTs      = entry.keyTimestamp || timestamp;
      const fileKey     = deriveKey(wallet.privateKey, wallet.address, fileTs);

      // Step 5: decrypt file payload
      let fileContent;
      try {
        fileContent = decrypt(encFile, fileKey);
      } catch {
        throw new Error("Decryption failed — wrong timestamp or corrupted data");
      }

      // Step 6: write to output file
      fs.writeFileSync(outFile, fileContent);
      console.log(`\n✓ Loaded: ${outFile} (${Buffer.byteLength(fileContent)} bytes)`);

    } catch (err) {
      console.error("load error:", err.message);
      process.exit(1);
    }
  });

// ─── grant ─────────────────────────────────────────────────────────────────
program
  .command("grant <merkleRoot> <address>")
  .description("Grant read access to an address")
  .action(async (merkleRoot, address, _opts) => {
    try {
      const provider = getProvider();
      const { protocolAddr, mmpAddr } = getAddresses();
      const wallet   = (await loadWallet()).connect(provider);
      const chain    = createChainClient({ wallet, protocolAddr, mmpAddr });

      const receipt = await chain.grantAccess(merkleRoot, address);
      console.log(`Access granted to ${address}. Tx: ${receipt.hash}`);
    } catch (err) {
      console.error("grant error:", err.message);
      process.exit(1);
    }
  });

// ─── revoke ────────────────────────────────────────────────────────────────
// FIX CLI-L-01: revoke command was missing entirely — revokeAccess was exposed
// in chain.js but had no CLI entry point, making it unreachable from the terminal.
program
  .command("revoke <merkleRoot> <address>")
  .description("Revoke read access from an address")
  .action(async (merkleRoot, address, _opts) => {
    try {
      const provider = getProvider();
      const { protocolAddr, mmpAddr } = getAddresses();
      const wallet   = (await loadWallet()).connect(provider);
      const chain    = createChainClient({ wallet, protocolAddr, mmpAddr });

      const receipt = await chain.revokeAccess(merkleRoot, address);
      console.log(`Access revoked from ${address}. Tx: ${receipt.hash}`);
    } catch (err) {
      console.error("revoke error:", err.message);
      process.exit(1);
    }
  });

// ─── renew ─────────────────────────────────────────────────────────────────
program
  .command("renew <merkleRoot>")
  .description("Renew a memory tree's rent")
  .option("-r, --rent-blocks <n>", "Additional rent blocks", "201600")
  .action(async (merkleRoot, opts) => {
    try {
      const provider = getProvider();
      const { protocolAddr, mmpAddr } = getAddresses();
      const wallet   = (await loadWallet()).connect(provider);
      const chain    = createChainClient({ wallet, protocolAddr, mmpAddr });

      const rentBlocks = BigInt(opts.rentBlocks);
      // FIX L-02: fetch actual tree size before estimating cost (was using 0n → always 0)
      const treeInfo = await chain.getUserTree(merkleRoot);
      if (treeInfo.owner === ethers.ZeroAddress) {
        console.error("Tree not found on-chain");
        process.exit(1);
      }
      const cost = await chain.estimateCost(treeInfo.sizeKB, rentBlocks);
      console.log(`Renewing ${treeInfo.sizeKB} KB for ${rentBlocks} blocks — cost: ${ethers.formatEther(cost)} MMP`);
      console.log(`Renewing for ${rentBlocks} blocks...`);

      const receipt = await chain.renewMemoryWithPermit({ merkleRoot, rentBlocks });
      console.log(`Renewed! Tx: ${receipt.hash}`);
    } catch (err) {
      console.error("renew error:", err.message);
      process.exit(1);
    }
  });

// ─── status ────────────────────────────────────────────────────────────────
program
  .command("status [merkleRoot]")
  .description("Show tree status or network overview")
  .action(async (merkleRoot, _opts) => {
    try {
      const provider = getProvider();
      const { protocolAddr, mmpAddr } = getAddresses();
      const wallet   = (await loadWallet()).connect(provider);
      const chain    = createChainClient({ wallet, protocolAddr, mmpAddr });

      const balance  = await chain.getBalance();
      const count    = await chain.getActiveRootsCount();
      const pow      = await chain.getPoWParams();
      const discount = await chain.getDiscountActive();

      console.log("═══════════════════════════════════════");
      console.log("  OMP Network Status");
      console.log("═══════════════════════════════════════");
      console.log(`  Address:       ${wallet.address}`);
      console.log(`  MMP Balance:   ${ethers.formatEther(balance)} MMP`);
      console.log(`  Active Roots:  ${count}`);
      console.log(`  Discount:      ${discount ? "✓ Active" : "✗ Expired"}`);
      console.log(`  PoW Target:    ${pow.target.toString(16).slice(0, 16)}...`);
      console.log(`  Challenge:     ${pow.targetRoot.slice(0, 18)}...`);
      console.log("═══════════════════════════════════════");

      if (merkleRoot) {
        const tree = await chain.getUserTree(merkleRoot);
        console.log("\n  Tree Details:");
        console.log(`    Root:     ${merkleRoot}`);
        console.log(`    Owner:    ${tree.owner}`);
        console.log(`    Size:     ${tree.sizeKB} KB`);
        console.log(`    Chunks:   ${tree.numChunks}`);
        console.log(`    Expires:  block ${tree.expiresAt} ${tree.isFree ? "(permanent)" : ""}`);
      }
    } catch (err) {
      console.error("status error:", err.message);
      process.exit(1);
    }
  });

// ─── sync ──────────────────────────────────────────────────────────────────
program
  .command("sync <merkleRoot>")
  .description("Re-seed a tree to the P2P network")
  .option("--data <path>", "Path to original combined.bin cache (optional if auto-cache exists)")
  .action(async (merkleRoot, opts) => {
    try {
      const os = require("os");

      // FIX CLI-H-01: sync must use the same `combined` buffer that save used to build
      // the Merkle tree. Rebuilding from the raw original file produces a different root.
      // Strategy: read from local cache written by save, or fall back to --data if provided.
      const autoCacheFile = path.join(
        os.homedir(), ".omp", "cache", merkleRoot.replace("0x", "").slice(0, 16), "combined.bin"
      );

      let combined;
      if (fs.existsSync(autoCacheFile)) {
        combined = fs.readFileSync(autoCacheFile);
        console.log(`Using cached combined buffer: ${autoCacheFile}`);
      } else if (opts.data) {
        combined = fs.readFileSync(opts.data);
        console.log(`Using provided --data file: ${opts.data}`);
      } else {
        console.error(
          "Error: no local cache found for this merkleRoot.\n" +
          "Re-run 'save' to regenerate cache, or provide the original combined.bin via --data <path>."
        );
        process.exit(1);
      }

      const { chunks } = buildTree(combined);
      console.log(`Syncing ${chunks.length} chunks for root ${merkleRoot.slice(0, 18)}...`);
      const result = await writeAndConfirm(chunks, merkleRoot);
      console.log(`Synced: ${result.confirmations} peers confirmed`);
    } catch (err) {
      console.error("sync error:", err.message);
      process.exit(1);
    }
  });

// ─── topup ─────────────────────────────────────────────────────────────────
program
  .command("topup")
  .description("Check MMP balance and show top-up info")
  .action(async () => {
    try {
      const provider = getProvider();
      const { protocolAddr, mmpAddr } = getAddresses();
      const wallet   = (await loadWallet()).connect(provider);
      const chain    = createChainClient({ wallet, protocolAddr, mmpAddr });

      const balance  = await chain.getBalance();
      console.log("═══════════════════════════════════════");
      console.log("  MMP Balance");
      console.log("═══════════════════════════════════════");
      console.log(`  Address:  ${wallet.address}`);
      console.log(`  Balance:  ${ethers.formatEther(balance)} MMP`);
      console.log("\n  To acquire MMP:");
      console.log(`  - Mine blocks by running: packages/miner/`);
      console.log(`  - Or swap on PancakeSwap: ${mmpAddr}`);
      console.log("═══════════════════════════════════════");
    } catch (err) {
      console.error("topup error:", err.message);
      process.exit(1);
    }
  });

program
  .name("omp")
  .description("OpenClaw Memory Protocol CLI")
  .version(VERSION);

program.parse(process.argv);
