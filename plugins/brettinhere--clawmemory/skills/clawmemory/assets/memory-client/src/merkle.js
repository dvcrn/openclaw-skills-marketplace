"use strict";
/**
 * merkle.js — Keccak-256 Merkle tree for memory chunks
 *
 * ⚠️ CRITICAL SECURITY NOTES:
 *  1. Uses ethers.keccak256 (Keccak-256), NOT Node.js crypto SHA-256.
 *     The on-chain contract uses keccak256() — these MUST match or PoW
 *     submissions will fail Merkle proof verification.
 *
 *  2. sortPairs: true — required to align with OpenZeppelin MerkleProof.sol
 *     which sorts sibling pairs before hashing. Without this flag the computed
 *     root will differ from what OZ verifies on-chain.
 *
 *  3. Leaf encoding: keccak256(abi.encodePacked(uint256 index, bytes chunkData))
 *     Must mirror exactly: ethers.solidityPacked(['uint256','bytes'], [i, data])
 *     then ethers.keccak256(...). Any change breaks on-chain verification.
 */

const { MerkleTree } = require("merkletreejs");
const { ethers }     = require("ethers");

/// @notice Each chunk is exactly 256 KB
const CHUNK_SIZE = 256 * 1024;

/**
 * Compute the Keccak-256 leaf hash for a chunk.
 * Mirrors: keccak256(abi.encodePacked(uint256 chunkIndex, bytes chunkData))
 *
 * @param {number|bigint} index   Chunk index (0-based)
 * @param {Buffer|Uint8Array} data Chunk bytes
 * @returns {Buffer} 32-byte leaf hash
 */
function leafHash(index, data) {
  // ⚠️ solidityPacked encodes uint256 as 32-byte big-endian, bytes as raw bytes
  const encoded = ethers.solidityPacked(["uint256", "bytes"], [index, data]);
  // ⚠️ Use ethers.keccak256 (Keccak-256), not crypto.createHash('sha256')
  const hash    = ethers.keccak256(encoded);
  return Buffer.from(hash.slice(2), "hex");
}

/**
 * The hash function used by MerkleTree for internal nodes.
 * Must also be Keccak-256 to stay consistent.
 *
 * @param {Buffer} data
 * @returns {Buffer}
 */
function keccakBuffer(data) {
  const hash = ethers.keccak256(data);
  return Buffer.from(hash.slice(2), "hex");
}

/**
 * Split a Buffer into CHUNK_SIZE (256KB) chunks.
 *
 * @param {Buffer} data Full payload
 * @returns {Buffer[]} Array of chunk Buffers
 */
function splitChunks(data) {
  const chunks = [];
  for (let offset = 0; offset < data.length; offset += CHUNK_SIZE) {
    chunks.push(data.slice(offset, offset + CHUNK_SIZE));
  }
  return chunks;
}

/**
 * Build a Merkle tree from a payload Buffer.
 *
 * @param {Buffer} payload Full plaintext/encrypted payload
 * @returns {{ tree: MerkleTree, chunks: Buffer[], root: string }}
 *   - tree:   MerkleTree instance (for proof generation)
 *   - chunks: Array of 256KB chunk Buffers
 *   - root:   Hex string Merkle root (0x-prefixed)
 */
function buildTree(payload) {
  const chunks = splitChunks(payload);
  if (chunks.length === 0) throw new Error("merkle: empty payload");

  const leaves = chunks.map((chunk, i) => leafHash(i, chunk));

  // ⚠️ sortPairs: true — mandatory for OZ MerkleProof.sol compatibility
  const tree = new MerkleTree(leaves, keccakBuffer, { sortPairs: true });

  return {
    tree,
    chunks,
    root:     tree.getHexRoot(),
    sizeKB:   Math.ceil(payload.length / 1024),
    numChunks: chunks.length,
  };
}

/**
 * Generate a Merkle proof for a specific chunk index.
 *
 * @param {MerkleTree} tree   The tree from buildTree()
 * @param {Buffer[]}   chunks Chunks array from buildTree()
 * @param {number}     index  Chunk index to prove
 * @returns {string[]}  Array of 0x-prefixed sibling hashes
 */
function getProof(tree, chunks, index) {
  const leaf  = leafHash(index, chunks[index]);
  const proof = tree.getProof(leaf);
  return proof.map((p) => "0x" + p.data.toString("hex"));
}

/**
 * Verify a Merkle proof off-chain (useful for debugging).
 *
 * @param {string}   root      Hex Merkle root
 * @param {number}   index     Chunk index
 * @param {Buffer}   chunkData Chunk bytes
 * @param {string[]} proof     Array of proof hashes
 * @returns {boolean}
 */
function verifyProof(root, index, chunkData, proof) {
  const rootBuf = Buffer.from(root.slice(2), "hex");
  const leaf    = leafHash(index, chunkData);
  const proofBufs = proof.map((p) => Buffer.from(p.slice(2), "hex"));
  return MerkleTree.verify(proofBufs, leaf, rootBuf, keccakBuffer, { sortPairs: true });
}

module.exports = {
  CHUNK_SIZE,
  leafHash,
  splitChunks,
  buildTree,
  getProof,
  verifyProof,
};
