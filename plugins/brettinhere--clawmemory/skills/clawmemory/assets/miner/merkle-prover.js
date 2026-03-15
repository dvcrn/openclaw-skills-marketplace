"use strict";
/**
 * merkle-prover.js — Construct Merkle proofs for PoW submission
 *
 * The miner retrieves chunk data from Hypercore and constructs Merkle proofs
 * to prove possession of the challenged chunk to the MemoryProtocol contract.
 *
 * ⚠️ Uses merkletreejs with:
 *   - Keccak-256 hash function (ethers.keccak256)
 *   - sortPairs: true (required for OZ MerkleProof.sol alignment)
 *   - Leaf: keccak256(abi.encodePacked(uint256 index, bytes chunkData))
 */

const { MerkleTree } = require("merkletreejs");
const { ethers }     = require("ethers");

/**
 * Compute a leaf hash for a chunk.
 * Mirrors contracts/MemoryProtocol.sol:
 *   leaf = keccak256(abi.encodePacked(chunkIndex, chunkData))
 */
function leafHash(index, data) {
  const encoded = ethers.solidityPacked(["uint256", "bytes"], [index, data]);
  return Buffer.from(ethers.keccak256(encoded).slice(2), "hex");
}

/**
 * Keccak-256 hash function for MerkleTree internal nodes.
 */
function keccakBuffer(data) {
  return Buffer.from(ethers.keccak256(data).slice(2), "hex");
}

/**
 * Rebuild the Merkle tree from all chunks and generate a proof for one chunk.
 *
 * @param {Buffer[]} chunks     All chunks for this tree (in order)
 * @param {number}   proveIndex Index of the chunk to prove
 * @returns {{ proof: string[], root: string, leaf: string }}
 */
function buildProof(chunks, proveIndex) {
  if (chunks.length === 0) throw new Error("prover: no chunks provided");
  if (proveIndex >= chunks.length) {
    throw new Error(`prover: index ${proveIndex} out of range (${chunks.length} chunks)`);
  }

  const leaves = chunks.map((chunk, i) => leafHash(i, chunk));

  // ⚠️ sortPairs: true — must match merkle.js and the on-chain OZ verifier
  const tree = new MerkleTree(leaves, keccakBuffer, { sortPairs: true });

  const targetLeaf = leaves[proveIndex];
  const proofData  = tree.getProof(targetLeaf);
  const proof      = proofData.map((p) => "0x" + p.data.toString("hex"));
  const root       = tree.getHexRoot();

  return {
    proof,
    root,
    leaf:      "0x" + targetLeaf.toString("hex"),
    chunkData: chunks[proveIndex],
    chunkIndex: proveIndex,
  };
}

/**
 * Verify a proof off-chain (debug utility).
 *
 * @param {string}   root
 * @param {number}   index
 * @param {Buffer}   chunkData
 * @param {string[]} proof
 * @returns {boolean}
 */
function verifyProof(root, index, chunkData, proof) {
  const rootBuf    = Buffer.from(root.replace("0x", ""), "hex");
  const leaf       = leafHash(index, chunkData);
  const proofBufs  = proof.map((p) => Buffer.from(p.replace("0x", ""), "hex"));
  return MerkleTree.verify(proofBufs, leaf, rootBuf, keccakBuffer, { sortPairs: true });
}

module.exports = { buildProof, verifyProof, leafHash };
