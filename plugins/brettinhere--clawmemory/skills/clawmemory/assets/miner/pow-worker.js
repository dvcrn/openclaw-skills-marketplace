"use strict";
/**
 * pow-worker.js — PoW mining worker thread
 *
 * Runs in a Worker thread and searches for a valid nonce in batches of 10,000.
 *
 * ⚠️ CRITICAL: Hash computation MUST exactly match the Solidity contract:
 *   keccak256(abi.encodePacked(nonce, msg.sender, targetRoot, epochSeed))
 *
 *   Solidity abi.encodePacked encoding:
 *     - uint256 nonce  → 32 bytes big-endian
 *     - address sender → 20 bytes
 *     - bytes32 root   → 32 bytes
 *     - bytes32 seed   → 32 bytes
 *
 *   We use ethers.solidityPacked(['uint256','address','bytes32','bytes32'], [...])
 *   which produces exactly this encoding. Do NOT use ABI.encode (padded) or
 *   manual Buffer concatenation without verifying byte layout.
 *
 * Worker receives a message: { targetRoot, epochSeed, target, minerAddr, startNonce }
 * Worker sends back:         { found: true, nonce } | { found: false, hashrate }
 */

const { workerData, parentPort } = require("worker_threads");
const { ethers } = require("ethers");

/// @notice Batch size — 10,000 hashes per iteration before reporting back
const BATCH_SIZE = 10_000;

function mine() {
  const { targetRoot, epochSeed, target, minerAddr, startNonce } = workerData;

  const targetBig = BigInt(target);

  let nonce    = BigInt(startNonce);
  const start  = Date.now();

  while (true) {
    // Process BATCH_SIZE nonces before yielding
    for (let i = 0; i < BATCH_SIZE; i++) {
      // ⚠️ SECURITY: solidityPacked exactly mirrors abi.encodePacked in Solidity.
      // Types and order must match: uint256, address, bytes32, bytes32
      const packed = ethers.solidityPacked(
        ["uint256", "address", "bytes32", "bytes32"],
        [nonce, minerAddr, targetRoot, epochSeed]
      );

      const hashHex = ethers.keccak256(packed);
      const hashBig = BigInt(hashHex);

      if (hashBig < targetBig) {
        // Found a valid nonce!
        parentPort.postMessage({ found: true, nonce: nonce.toString() });
        return;
      }

      nonce++;
    }

    // Report hashrate and current progress after each batch
    const elapsed = (Date.now() - start) / 1000; // seconds
    const hashrate = elapsed > 0 ? Math.round((Number(nonce - BigInt(startNonce))) / elapsed) : 0;
    parentPort.postMessage({ found: false, hashrate, nonce: nonce.toString() });
  }
}

mine();
