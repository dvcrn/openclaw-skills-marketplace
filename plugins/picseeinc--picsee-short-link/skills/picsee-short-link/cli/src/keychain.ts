/**
 * Cross-platform secure token storage using AES-256-CBC encryption.
 * Key derivation: SHA-256(random-salt + hostname + username).
 * The random salt is generated once and stored alongside the token,
 * making the key unpredictable even if hostname/username are known.
 */

import {
  readFileSync,
  writeFileSync,
  unlinkSync,
  existsSync,
  mkdirSync,
} from "fs";
import {
  createCipheriv,
  createDecipheriv,
  randomBytes,
  createHash,
} from "crypto";
import { homedir } from "os";
import { join, dirname } from "path";
import os from "os";

const TOKEN_DIR = join(homedir(), ".openclaw");
const TOKEN_FILE = join(TOKEN_DIR, ".picsee_token");
const SALT_FILE = join(TOKEN_DIR, ".picsee_salt");

/** Get or create a random salt for key derivation. */
function getSalt(): Buffer {
  if (existsSync(SALT_FILE)) {
    return Buffer.from(readFileSync(SALT_FILE, "utf8").trim(), "hex");
  }
  const salt = randomBytes(32);
  if (!existsSync(TOKEN_DIR)) mkdirSync(TOKEN_DIR, { recursive: true });
  writeFileSync(SALT_FILE, salt.toString("hex"), { mode: 0o600 });
  return salt;
}

/** Generate encryption key: SHA-256(salt + hostname + username). */
function getMachineKey(): Buffer {
  const salt = getSalt();
  const identifier = `${os.hostname()}-${os.userInfo().username}`;
  return createHash("sha256").update(Buffer.concat([salt, Buffer.from(identifier)])).digest();
}

function encryptToken(token: string): string {
  const key = getMachineKey();
  const iv = randomBytes(16);
  const cipher = createCipheriv("aes-256-cbc", key, iv);
  let encrypted = cipher.update(token, "utf8", "hex");
  encrypted += cipher.final("hex");
  return iv.toString("hex") + ":" + encrypted;
}

function decryptToken(encrypted: string): string {
  const key = getMachineKey();
  const parts = encrypted.split(":");
  if (parts.length !== 2) throw new Error("Invalid encrypted token format");
  const iv = Buffer.from(parts[0], "hex");
  const decipher = createDecipheriv("aes-256-cbc", key, iv);
  let decrypted = decipher.update(parts[1], "hex", "utf8");
  decrypted += decipher.final("utf8");
  return decrypted;
}

export function setToken(token: string): boolean {
  if (!token || typeof token !== "string") throw new Error("Invalid token");
  const dir = dirname(TOKEN_FILE);
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
  const encrypted = encryptToken(token);
  writeFileSync(TOKEN_FILE, encrypted, { mode: 0o600 });
  return true;
}

export function getToken(): string | null {
  try {
    if (!existsSync(TOKEN_FILE)) return null;
    const encrypted = readFileSync(TOKEN_FILE, "utf8").trim();
    return decryptToken(encrypted) || null;
  } catch {
    return null;
  }
}

export function deleteToken(): boolean {
  try {
    if (existsSync(TOKEN_FILE)) unlinkSync(TOKEN_FILE);
    if (existsSync(SALT_FILE)) unlinkSync(SALT_FILE);
    return true;
  } catch {
    return false;
  }
}
