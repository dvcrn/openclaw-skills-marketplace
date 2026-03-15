"use strict";
/**
 * hypercore.js — Hypercore/Hyperswarm P2P write + confirmation
 *
 * Writes encrypted chunks to a local Hypercore feed, then swarms
 * until at least MIN_PEER_CONFIRMATIONS non-local peers have replicated
 * the data. Times out after CONFIRM_TIMEOUT_MS.
 *
 * SECURITY: Local addresses (127.x, ::1) are filtered from confirmation
 * count to prevent self-confirmation loops.
 */

const Hypercore  = require("hypercore");
const Hyperswarm = require("hyperswarm");
const path       = require("path");
const os         = require("os");

const MIN_PEER_CONFIRMATIONS = 1;
const CONFIRM_TIMEOUT_MS     = 30_000;

/// @notice Default storage directory for hypercores
const DEFAULT_STORAGE = path.join(os.homedir(), ".omp", "cores");

/**
 * Check if a remote address string is a local loopback address.
 * Filters: 127.x.x.x, ::1, localhost
 *
 * @param {string} addr Remote address
 * @returns {boolean}
 */
function isLocalAddress(addr) {
  if (!addr) return true;
  return addr.startsWith("127.") || addr === "::1" || addr === "localhost";
}

/**
 * Write chunks to a Hypercore feed and wait for P2P replication confirmations.
 *
 * @param {Buffer[]}  chunks      Array of chunk Buffers to append
 * @param {string}    merkleRoot  Hex Merkle root (used as topic key for swarm)
 * @param {object}    [opts]
 * @param {string}    [opts.storage]  Path for Hypercore storage
 * @param {number}    [opts.minPeers] Override MIN_PEER_CONFIRMATIONS
 * @param {number}    [opts.timeout]  Override CONFIRM_TIMEOUT_MS
 * @returns {Promise<{feedKey: string, length: number, confirmations: number}>}
 */
async function writeAndConfirm(chunks, merkleRoot, opts = {}) {
  const storageDir = opts.storage || path.join(DEFAULT_STORAGE, merkleRoot.slice(2, 18));
  const minPeers   = opts.minPeers || MIN_PEER_CONFIRMATIONS;
  const timeout    = opts.timeout  || CONFIRM_TIMEOUT_MS;

  const feed   = new Hypercore(storageDir, { sparse: false });
  const swarm  = new Hyperswarm();

  await feed.ready();

  // Append all chunks to the feed
  for (const chunk of chunks) {
    await feed.append(chunk);
  }

  const feedKey = feed.key.toString("hex");

  // Derive swarm topic from Merkle root (deterministic, so miners can find it)
  const topicBuf = Buffer.from(merkleRoot.replace("0x", ""), "hex");
  swarm.join(topicBuf, { server: true, client: true });

  let confirmations    = 0;
  const confirmedPeers = new Set();

  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      cleanup().then(() => {
        if (confirmations >= minPeers) {
          resolve({ feedKey, length: feed.length, confirmations });
        } else {
          reject(
            new Error(
              `P2P confirmation timeout: got ${confirmations}/${minPeers} confirmations`
            )
          );
        }
      });
    }, timeout);

    swarm.on("connection", (stream, info) => {
      const remoteAddr = info.remotePublicKey
        ? info.remotePublicKey.toString("hex").slice(0, 16)
        : null;

      // SECURITY: filter local/loopback peers — only count remote confirmations
      const rawAddr = info.host || "";
      if (isLocalAddress(rawAddr)) return;

      const peerKey = info.remotePublicKey
        ? info.remotePublicKey.toString("hex")
        : remoteAddr;

      if (confirmedPeers.has(peerKey)) return;

      const clone = feed.replicate(stream);
      clone.on("error", () => {}); // ignore replication errors

      // FIX M-04: use 'sync' event instead of stream 'close'.
      // 'close' fires on ANY disconnect (partial transfer, timeout, network drop).
      // 'sync' fires only when the remote feed is fully up-to-date with ours,
      // meaning the peer has confirmed receipt of all appended chunks.
      clone.on("sync", () => {
        if (!confirmedPeers.has(peerKey)) {
          confirmedPeers.add(peerKey);
          confirmations++;

          if (confirmations >= minPeers) {
            clearTimeout(timer);
            cleanup().then(() =>
              resolve({ feedKey, length: feed.length, confirmations })
            );
          }
        }
      });
    });

    swarm.on("error", (err) => {
      clearTimeout(timer);
      cleanup().then(() => reject(err));
    });
  });

  async function cleanup() {
    try {
      await swarm.destroy();
      await feed.close();
    } catch (_) {}
  }
}

module.exports = { writeAndConfirm, MIN_PEER_CONFIRMATIONS, CONFIRM_TIMEOUT_MS };
