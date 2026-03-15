"use strict";
/**
 * index-file.js — Memory index file serialization
 *
 * An "index file" is a JSON manifest stored as the first chunk of a memory tree.
 * It describes all entries in the tree (file names, types, sizes, encryption params).
 *
 * Format:
 * {
 *   version: 1,
 *   createdAt: <unix timestamp>,
 *   entries: [
 *     {
 *       name:       string,       // Human-readable name
 *       mimeType:   string,       // MIME type
 *       sizeBytes:  number,       // Original size in bytes
 *       chunkStart: number,       // First chunk index for this entry
 *       chunkCount: number,       // Number of chunks
 *       keyTimestamp: number,     // Timestamp used in deriveKey (for decryption)
 *       iv:         string,       // Base64 IV (if separately tracked)
 *       extra:      object,       // Arbitrary metadata
 *     }
 *   ]
 * }
 */

const INDEX_VERSION = 1;

/**
 * Build a serialized index file Buffer from an array of entry descriptors.
 *
 * @param {object[]} entries  Array of entry objects (see format above)
 * @returns {Buffer} UTF-8 JSON buffer
 */
function buildIndexFile(entries) {
  if (!Array.isArray(entries)) throw new TypeError("entries must be an array");

  const index = {
    version:   INDEX_VERSION,
    createdAt: Math.floor(Date.now() / 1000),
    entries:   entries.map((e) => ({
      name:         e.name         || "",
      mimeType:     e.mimeType     || "application/octet-stream",
      sizeBytes:    Number(e.sizeBytes  || 0),
      chunkStart:   Number(e.chunkStart || 0),
      chunkCount:   Number(e.chunkCount || 1),
      keyTimestamp: Number(e.keyTimestamp || 0),
      iv:           e.iv           || null,
      extra:        e.extra        || {},
    })),
  };

  return Buffer.from(JSON.stringify(index, null, 2), "utf8");
}

/**
 * Parse an index file Buffer back into a structured object.
 *
 * @param {Buffer|string} data  Raw index file bytes or string
 * @returns {{ version: number, createdAt: number, entries: object[] }}
 * @throws If data is malformed or version is unknown
 */
function parseIndexFile(data) {
  const str = Buffer.isBuffer(data) ? data.toString("utf8") : String(data);

  let parsed;
  try {
    parsed = JSON.parse(str);
  } catch (err) {
    throw new Error(`index-file: invalid JSON — ${err.message}`);
  }

  if (!parsed.version || !Array.isArray(parsed.entries)) {
    throw new Error("index-file: missing version or entries field");
  }
  if (parsed.version !== INDEX_VERSION) {
    throw new Error(`index-file: unsupported version ${parsed.version}`);
  }

  return parsed;
}

module.exports = { buildIndexFile, parseIndexFile, INDEX_VERSION };
