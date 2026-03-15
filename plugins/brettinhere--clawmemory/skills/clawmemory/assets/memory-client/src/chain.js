"use strict";
/**
 * chain.js — MemoryProtocol on-chain interaction layer
 *
 * Wraps all contract calls into a clean async API.
 * Handles both direct approval flow and EIP-2612 permit flow.
 */

const { ethers }                  = require("ethers");
const { generatePermitSignature } = require("./permit");

// Minimal ABI — only functions we call
const PROTOCOL_ABI = [
  // Write
  "function storeMemory(bytes32 merkleRoot, uint256 totalSizeKB, uint256 totalChunks, uint256 rentBlocks) external",
  "function storeNamedSlot(string calldata slotName, bytes32 merkleRoot, uint256 totalSizeKB, uint256 totalChunks) external",
  "function getNamedSlot(address owner, string calldata slotName) view returns (bytes32)",
  "function getSlotCount(address owner) view returns (uint256)",
  "function FREE_SLOTS_PER_ADDRESS() view returns (uint256)",
  "function storeMemoryWithPermit(bytes32 merkleRoot, uint256 totalSizeKB, uint256 totalChunks, uint256 rentBlocks, uint256 permitDeadline, uint8 v, bytes32 r, bytes32 s) external",
  "function renewMemory(bytes32 merkleRoot, uint256 rentBlocks) external",
  "function renewMemoryWithPermit(bytes32 merkleRoot, uint256 rentBlocks, uint256 permitDeadline, uint8 v, bytes32 r, bytes32 s) external",
  "function grantAccess(bytes32 merkleRoot, address accessor) external",
  "function revokeAccess(bytes32 merkleRoot, address accessor) external",
  // Read
  "function getUserTree(bytes32 merkleRoot) view returns (address owner, uint256 totalSizeKB, uint256 totalChunks, uint256 storedAt, uint256 expiresAt, bool isFree)",
  "function getPoWParams() view returns (bytes32 targetRoot, bytes32 epochSeed, uint256 target, uint256 epochStart, uint256 totalSubs)",
  "function getActiveRootsCount() view returns (uint256)",
  "function getDiscountActive() view returns (bool)",
  "function estimateCost(uint256 sizeKB, uint256 rentBlocks) view returns (uint256)",
  "function getBlocksUntilExpiry(bytes32 merkleRoot) view returns (uint256)",
  "function activeRoots(uint256 index) view returns (bytes32)",
  // Events
  "event MemoryStored(address indexed owner, bytes32 indexed merkleRoot, uint256 sizeKB, uint256 expiresAt)",
];

const MMP_ABI = [
  "function approve(address spender, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
  "function balanceOf(address account) view returns (uint256)",
  "function nonces(address owner) view returns (uint256)",
];

/**
 * Create a chain client.
 *
 * @param {object} config
 * @param {ethers.Wallet}  config.wallet        Signer wallet
 * @param {string}         config.protocolAddr  MemoryProtocol address
 * @param {string}         config.mmpAddr       MMPToken address
 * @returns {object} Chain client API
 */
function createChainClient({ wallet, protocolAddr, mmpAddr }) {
  const protocol = new ethers.Contract(protocolAddr, PROTOCOL_ABI, wallet);
  const mmp      = new ethers.Contract(mmpAddr, MMP_ABI, wallet);

  return {
    /**
     * Store a memory tree using approve + storeMemory
     */
    async storeNamedSlot({ slotName, merkleRoot, sizeKB, numChunks }) {
      const protocol = new ethers.Contract(this.protocolAddress, ABI, this.wallet);
      const tx = await protocol.storeNamedSlot(slotName, merkleRoot, sizeKB, numChunks);
      const receipt = await tx.wait();
      return receipt;
    },

    async getNamedSlot({ slotName }) {
      const protocol = new ethers.Contract(this.protocolAddress, ABI, this.wallet);
      return await protocol.getNamedSlot(this.wallet.address, slotName);
    },

    async storeMemory({ merkleRoot, sizeKB, numChunks, rentBlocks }) {
      const cost = await protocol.estimateCost(sizeKB, rentBlocks);
      if (cost > 0n) {
        const allowance = await mmp.allowance(wallet.address, protocolAddr);
        if (allowance < cost) {
          const approveTx = await mmp.approve(protocolAddr, cost);
          await approveTx.wait();
        }
      }
      const tx = await protocol.storeMemory(merkleRoot, sizeKB, numChunks, rentBlocks);
      return tx.wait();
    },

    /**
     * Store using EIP-2612 permit (single tx, gas efficient)
     */
    async storeMemoryWithPermit({ merkleRoot, sizeKB, numChunks, rentBlocks }) {
      const cost     = await protocol.estimateCost(sizeKB, rentBlocks);
      const deadline = Math.floor(Date.now() / 1000) + 3600; // 1 hour

      let v = 0, r = ethers.ZeroHash, s = ethers.ZeroHash;
      if (cost > 0n) {
        const sig = await generatePermitSignature(wallet, mmpAddr, protocolAddr, cost, deadline);
        v = sig.v; r = sig.r; s = sig.s;
      }

      const tx = await protocol.storeMemoryWithPermit(
        merkleRoot, sizeKB, numChunks, rentBlocks, deadline, v, r, s
      );
      return tx.wait();
    },

    /**
     * Renew a memory tree using approve + renewMemory
     */
    async renewMemory({ merkleRoot, rentBlocks }) {
      const tree = await protocol.getUserTree(merkleRoot);
      const cost = await protocol.estimateCost(tree.totalSizeKB, rentBlocks);
      if (cost > 0n) {
        const approveTx = await mmp.approve(protocolAddr, cost);
        await approveTx.wait();
      }
      const tx = await protocol.renewMemory(merkleRoot, rentBlocks);
      return tx.wait();
    },

    /**
     * Renew using EIP-2612 permit
     */
    async renewMemoryWithPermit({ merkleRoot, rentBlocks }) {
      const tree     = await protocol.getUserTree(merkleRoot);
      const cost     = await protocol.estimateCost(tree.totalSizeKB, rentBlocks);
      const deadline = Math.floor(Date.now() / 1000) + 3600;

      let v = 0, r = ethers.ZeroHash, s = ethers.ZeroHash;
      if (cost > 0n) {
        const sig = await generatePermitSignature(wallet, mmpAddr, protocolAddr, cost, deadline);
        v = sig.v; r = sig.r; s = sig.s;
      }
      const tx = await protocol.renewMemoryWithPermit(merkleRoot, rentBlocks, deadline, v, r, s);
      return tx.wait();
    },

    /** Retrieve user's tree metadata */
    async getUserTree(merkleRoot) {
      const t = await protocol.getUserTree(merkleRoot);
      return {
        owner:      t.owner,
        sizeKB:     t.totalSizeKB,
        numChunks:  t.totalChunks,
        storedAt:   t.storedAt,
        expiresAt:  t.expiresAt,
        isFree:     t.isFree,
      };
    },

    /** Get current PoW mining parameters */
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

    /** Get total number of active roots */
    async getActiveRootsCount() {
      return protocol.getActiveRootsCount();
    },

    /** Check if early-bird discount is active */
    async getDiscountActive() {
      return protocol.getDiscountActive();
    },

    /** Estimate storage cost */
    async estimateCost(sizeKB, rentBlocks) {
      return protocol.estimateCost(sizeKB, rentBlocks);
    },

    /** MMP balance of wallet */
    async getBalance() {
      return mmp.balanceOf(wallet.address);
    },

    /** Grant access to a tree */
    async grantAccess(merkleRoot, accessor) {
      const tx = await protocol.grantAccess(merkleRoot, accessor);
      return tx.wait();
    },

    /** Revoke access to a tree */
    async revokeAccess(merkleRoot, accessor) {
      const tx = await protocol.revokeAccess(merkleRoot, accessor);
      return tx.wait();
    },

    // Raw contract instances for advanced use
    protocol,
    mmp,
    wallet,
  };
}

module.exports = { createChainClient };
