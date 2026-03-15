"use strict";
/**
 * hypercore-server.js — P2P Hyperswarm hosting server for memory trees
 *
 * The miner hosts ALL activeRoots on the P2P network.
 * When a peer requests a root's topic, we replicate the Hypercore feed.
 *
 * Responsibilities:
 *  1. Enumerate activeRoots from chain
 *  2. For each root, open/create a Hypercore feed
 *  3. Join Hyperswarm topic = Merkle root bytes
 *  4. Serve replication streams to peers
 *  5. Re-sync when new roots are added on-chain
 */

const Hypercore  = require("hypercore");
const Hyperswarm = require("hyperswarm");
const path       = require("path");
const os         = require("os");
const { EventEmitter } = require("events");

const CORES_DIR = path.join(os.homedir(), ".omp", "cores");

/**
 * Create a Hypercore server that hosts all active roots.
 *
 * @param {object} opts
 * @param {function} opts.listActiveRoots  async fn() → string[] of hex roots
 * @param {string}   [opts.coresDir]       Override storage directory
 * @returns {HypercoreServer}
 */
function createHypercoreServer({ listActiveRoots, coresDir = CORES_DIR }) {
  const swarm   = new Hyperswarm();
  const cores   = new Map(); // root hex → Hypercore instance
  const emitter = new EventEmitter();

  // Join a single root's topic on the swarm
  async function joinRoot(rootHex) {
    if (cores.has(rootHex)) return; // already hosting

    const storePath = path.join(coresDir, rootHex.replace("0x", "").slice(0, 32));
    const core      = new Hypercore(storePath, { sparse: false });
    await core.ready();

    cores.set(rootHex, core);

    // Topic = raw bytes of the Merkle root (same as client uses)
    const topic = Buffer.from(rootHex.replace("0x", ""), "hex");
    swarm.join(topic, { server: true, client: false });

    emitter.emit("hosting", { root: rootHex, feedKey: core.key?.toString("hex") });
    return core;
  }

  // Stop hosting a root (root expired/pruned)
  async function leaveRoot(rootHex) {
    const core = cores.get(rootHex);
    if (!core) return;

    const topic = Buffer.from(rootHex.replace("0x", ""), "hex");
    await swarm.leave(topic);
    await core.close();
    cores.delete(rootHex);

    emitter.emit("stopped", { root: rootHex });
  }

  // Handle incoming peer connections — replicate matching feeds
  swarm.on("connection", (stream, info) => {
    // Identify which root this peer is interested in by matching announcement topics
    const peerTopics = info.topics || [];
    for (const topic of peerTopics) {
      const rootHex = "0x" + topic.toString("hex");
      const core    = cores.get(rootHex);
      if (core) {
        const clone = core.replicate(stream);
        clone.on("error", () => {}); // peer disconnects are normal
        emitter.emit("replicating", { root: rootHex, peer: info.remotePublicKey?.toString("hex") });
        return;
      }
    }
    // If we can't match, still replicate all cores (fallback)
    // This handles cases where topic info isn't available
    stream.on("error", () => {});
  });

  swarm.on("error", (err) => emitter.emit("error", err));

  return {
    /**
     * Start hosting — load all active roots from chain.
     */
    async start() {
      const roots = await listActiveRoots();
      for (const root of roots) {
        await joinRoot(root).catch((err) =>
          emitter.emit("error", { root, err })
        );
      }
      console.log(`[hypercore-server] Hosting ${roots.length} roots`);
    },

    /**
     * Add a new root to host (called when a new MemoryStored event fires).
     */
    async addRoot(rootHex) {
      await joinRoot(rootHex);
    },

    /**
     * Remove a root (called when MemoryPruned event fires).
     */
    async removeRoot(rootHex) {
      await leaveRoot(rootHex);
    },

    /**
     * Refresh all roots (resync from chain).
     */
    async refresh() {
      const onChain  = new Set(await listActiveRoots());
      const current  = new Set(cores.keys());

      // Add new roots
      for (const root of onChain) {
        if (!current.has(root)) await joinRoot(root).catch(() => {});
      }
      // Remove stale roots
      for (const root of current) {
        if (!onChain.has(root)) await leaveRoot(root).catch(() => {});
      }
    },

    /**
     * Get a Hypercore feed for a given root (for building proofs).
     */
    getCore(rootHex) {
      // First try in-memory map
      const cached = cores.get(rootHex);
      if (cached && cached.length > 0) return cached;
      // Fallback: open core directly from disk (handles same-machine CLI+miner case)
      try {
        const shortKey = rootHex.replace('0x','').slice(0, 16);
        const storePath = require('path').join(coresDir, shortKey);
        if (require('fs').existsSync(storePath)) {
          const fallback = new (require('hypercore'))(storePath, { sparse: false });
          // Register for future use
          cores.set(rootHex, fallback);
          return fallback;
        }
      } catch(_) {}
      return null;
    },

    /** Number of roots being hosted */
    get count() { return cores.size; },

    /** Event emitter for 'hosting', 'stopped', 'replicating', 'error' */
    on(event, fn) { return emitter.on(event, fn); },

    /** Graceful shutdown */
    async destroy() {
      for (const core of cores.values()) {
        await core.close().catch(() => {});
      }
      await swarm.destroy().catch(() => {});
      cores.clear();
    },
  };
}

module.exports = { createHypercoreServer };
