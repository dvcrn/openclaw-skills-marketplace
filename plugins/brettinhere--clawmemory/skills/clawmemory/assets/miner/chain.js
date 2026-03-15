"use strict";
/**
 * chain.js — Miner on-chain interaction layer
 *
 * Provides:
 *  - getPoWParams(): fetch current PoW challenge + target
 *  - listActiveRoots(): enumerate all active Merkle roots (for Hypercore hosting)
 *  - submitPoW(): submit PoW solution with Merkle proof
 */

const { ethers } = require("ethers");

const PROTOCOL_ABI = [
  "function getPoWParams() view returns (bytes32 targetRoot, bytes32 epochSeed, uint256 target, uint256 epochStart, uint256 totalSubs)",
  "function getActiveRootsCount() view returns (uint256)",
  "function activeRoots(uint256 index) view returns (bytes32)",
  "function submitPoW(uint256 nonce, uint256 chunkIndex, bytes calldata chunkData, bytes32[] calldata proof) external",
  "function getUserTree(bytes32 root) view returns (address owner, uint256 totalSizeKB, uint256 totalChunks, uint256 storedAt, uint256 expiresAt, bool isFree)",
  // Events
  "event ChallengeUpdated(bytes32 indexed targetRoot, bytes32 epochSeed, uint256 epochStart)",
  "event PoWSubmitted(address indexed miner, bytes32 indexed merkleRoot, uint256 reward, uint256 newTarget)",
  "event MemoryStored(address indexed owner, bytes32 indexed merkleRoot, uint256 sizeKB, uint256 expiresAt)",
];

const MMP_ABI = [
  "function balanceOf(address account) view returns (uint256)",
];

/**
 * Create a miner chain client.
 *
 * @param {object} config
 * @param {ethers.Wallet}  config.wallet
 * @param {string}         config.protocolAddr
 * @param {string}         config.mmpAddr
 */
function createMinerChain({ wallet, protocolAddr, mmpAddr }) {
  const protocol = new ethers.Contract(protocolAddr, PROTOCOL_ABI, wallet);
  const mmp      = new ethers.Contract(mmpAddr, MMP_ABI, wallet.provider);

  return {
    /**
     * Get current PoW parameters for mining.
     */
    async getPoWParams() {
      const p = await protocol.getPoWParams();
      return {
        targetRoot: p.targetRoot,
        epochSeed:  p.epochSeed,
        target:     p.target,
        epochStart: p.epochStart,
        totalSubs:  p.totalSubs,
      };
    },

    /**
     * Enumerate all active Merkle roots on-chain.
     * FIX H-06: Use Promise.all for parallel RPC calls instead of serial for-loop.
     *           Serial: N × ~100ms latency; Parallel: ~100ms regardless of N.
     *
     * @returns {Promise<string[]>} Array of hex Merkle roots
     */
    async listActiveRoots() {
      const count = await protocol.getActiveRootsCount();
      if (count === 0n) return [];
      // Parallel fetch — all requests in-flight simultaneously
      return Promise.all(
        Array.from({ length: Number(count) }, (_, i) => protocol.activeRoots(i))
      );
    },

    /**
     * Submit a PoW solution with a Merkle proof.
     *
     * @param {bigint}   nonce       Found nonce
     * @param {number}   chunkIndex  Proved chunk index
     * @param {Buffer}   chunkData   Chunk bytes
     * @param {string[]} proof       Merkle proof (0x-prefixed hashes)
     */
    async submitPoW(nonce, chunkIndex, chunkData, proof) {
      const tx = await protocol.submitPoW(nonce, chunkIndex, chunkData, proof);
      return tx.wait();
    },

    /**
     * Get tree metadata for a given root.
     */
    async getTreeInfo(root) {
      const t = await protocol.getUserTree(root);
      return {
        owner:     t.owner,
        sizeKB:    t.totalSizeKB,
        numChunks: t.totalChunks,
        storedAt:  t.storedAt,
        expiresAt: t.expiresAt,
        isFree:    t.isFree,
      };
    },

    /**
     * Get MMP balance of the miner.
     */
    async getBalance() {
      return mmp.balanceOf(wallet.address);
    },

    /**
     * Subscribe to ChallengeUpdated events (event-driven, not polling).
     * Calls onChallenge({ targetRoot, epochSeed, epochStart }) on each new challenge.
     *
     * @param {function} onChallenge  Callback
     */
    subscribeChallenge(onChallenge) {
      protocol.on("ChallengeUpdated", (targetRoot, epochSeed, epochStart) => {
        onChallenge({ targetRoot, epochSeed, epochStart: epochStart.toString() });
      });
    },

    /**
     * FIX M-05: Subscribe to MemoryStored events so newly stored files are
     * immediately added to the Hypercore server, not waiting up to 5 minutes.
     *
     * @param {function} onStored  Callback({ owner, merkleRoot })
     */
    subscribeMemoryStored(onStored) {
      protocol.on("MemoryStored", (owner, merkleRoot) => {
        onStored({ owner, merkleRoot });
      });
    },

    /**
     * Unsubscribe from all events.
     */
    removeAllListeners() {
      protocol.removeAllListeners();
    },

    protocol,
    wallet,
  };
}

module.exports = { createMinerChain };
