#!/usr/bin/env node
/**
 * agentline-crypto.mjs — Standalone crypto helper (zero npm dependencies).
 *
 * Subcommands:
 *   keygen                                    Generate Ed25519 keypair
 *   sign-challenge <priv_b64> <challenge_b64> Sign a challenge
 *   payload-hash                              Compute payload hash (stdin JSON)
 *   sign-envelope                             Sign an envelope (stdin JSON)
 */

import {
  createHash,
  createPrivateKey,
  generateKeyPairSync,
  sign,
} from "node:crypto";

// ── JCS (RFC 8785) canonicalization ─────────────────────────────
function jcsCanonicalize(value) {
  if (value === null || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (Object.is(value, -0)) return "0";
    return JSON.stringify(value);
  }
  if (typeof value === "string") return JSON.stringify(value);
  if (Array.isArray(value))
    return "[" + value.map((v) => jcsCanonicalize(v)).join(",") + "]";
  if (typeof value === "object") {
    const keys = Object.keys(value).sort();
    const parts = [];
    for (const k of keys) {
      if (value[k] === undefined) continue;
      parts.push(JSON.stringify(k) + ":" + jcsCanonicalize(value[k]));
    }
    return "{" + parts.join(",") + "}";
  }
  return undefined;
}

// ── Build Node.js KeyObject from raw 32-byte seed ───────────────
function privateKeyFromSeed(seed32) {
  // Ed25519 PKCS8 DER = fixed 16-byte prefix + 32-byte seed
  const prefix = Buffer.from("302e020100300506032b657004220420", "hex");
  return createPrivateKey({
    key: Buffer.concat([prefix, seed32]),
    format: "der",
    type: "pkcs8",
  });
}

// ── Helpers ─────────────────────────────────────────────────────
function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", reject);
  });
}

function out(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

// ── Commands ────────────────────────────────────────────────────
function cmdKeygen() {
  const { publicKey, privateKey } = generateKeyPairSync("ed25519");

  // Ed25519 PKCS8 DER: last 32 bytes = seed
  const privDer = privateKey.export({ type: "pkcs8", format: "der" });
  const privB64 = Buffer.from(privDer.slice(-32)).toString("base64");

  // Ed25519 SPKI DER: last 32 bytes = public key
  const pubDer = publicKey.export({ type: "spki", format: "der" });
  const pubB64 = Buffer.from(pubDer.slice(-32)).toString("base64");

  out({
    private_key: privB64,
    public_key: pubB64,
    pubkey_formatted: `ed25519:${pubB64}`,
  });
}

function cmdSignChallenge(privB64, challengeB64) {
  const pk = privateKeyFromSeed(Buffer.from(privB64, "base64"));
  const sig = sign(null, Buffer.from(challengeB64, "base64"), pk);
  out({ sig: sig.toString("base64") });
}

async function cmdPayloadHash() {
  const payload = JSON.parse(await readStdin());
  const canonical = jcsCanonicalize(payload);
  const digest = createHash("sha256").update(canonical).digest("hex");
  out({ payload_hash: `sha256:${digest}` });
}

async function cmdSignEnvelope() {
  const data = JSON.parse(await readStdin());
  const pk = privateKeyFromSeed(Buffer.from(data.private_key, "base64"));

  const parts = [
    data.v,
    data.msg_id,
    String(data.ts),
    data.from,
    data.to,
    String(data.type),
    data.reply_to || "",
    String(data.ttl_sec),
    data.payload_hash,
  ];

  const sig = sign(null, Buffer.from(parts.join("\n")), pk);
  out({ alg: "ed25519", key_id: data.key_id, value: sig.toString("base64") });
}

// ── Main ────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const cmd = args[0];

if (!cmd) {
  process.stderr.write(
    "Usage: agentline-crypto.mjs <keygen|sign-challenge|payload-hash|sign-envelope>\n"
  );
  process.exit(1);
}

switch (cmd) {
  case "keygen":
    cmdKeygen();
    break;
  case "sign-challenge":
    if (args.length !== 3) {
      process.stderr.write("Usage: sign-challenge <priv_b64> <challenge_b64>\n");
      process.exit(1);
    }
    cmdSignChallenge(args[1], args[2]);
    break;
  case "payload-hash":
    await cmdPayloadHash();
    break;
  case "sign-envelope":
    await cmdSignEnvelope();
    break;
  default:
    process.stderr.write(`Unknown command: ${cmd}\n`);
    process.exit(1);
}
