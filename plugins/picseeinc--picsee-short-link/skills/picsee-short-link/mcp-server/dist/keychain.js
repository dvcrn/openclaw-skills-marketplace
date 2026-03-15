/**
 * Cross-platform secure token storage using AES-256-CBC encryption.
 * Compatible with the existing OpenClaw skill's keychain.mjs.
 */
import { readFileSync, writeFileSync, unlinkSync, existsSync, mkdirSync, } from "fs";
import { createCipheriv, createDecipheriv, randomBytes, createHash, } from "crypto";
import { homedir } from "os";
import { join, dirname } from "path";
import os from "os";
const TOKEN_FILE = join(homedir(), ".openclaw", ".picsee_token");
/** Generate machine-specific encryption key (hostname + username → SHA-256). */
function getMachineKey() {
    const identifier = `${os.hostname()}-${os.userInfo().username}`;
    return createHash("sha256").update(identifier).digest();
}
function encryptToken(token) {
    const key = getMachineKey();
    const iv = randomBytes(16);
    const cipher = createCipheriv("aes-256-cbc", key, iv);
    let encrypted = cipher.update(token, "utf8", "hex");
    encrypted += cipher.final("hex");
    return iv.toString("hex") + ":" + encrypted;
}
function decryptToken(encrypted) {
    const key = getMachineKey();
    const parts = encrypted.split(":");
    if (parts.length !== 2)
        throw new Error("Invalid encrypted token format");
    const iv = Buffer.from(parts[0], "hex");
    const decipher = createDecipheriv("aes-256-cbc", key, iv);
    let decrypted = decipher.update(parts[1], "hex", "utf8");
    decrypted += decipher.final("utf8");
    return decrypted;
}
export function setToken(token) {
    if (!token || typeof token !== "string")
        throw new Error("Invalid token");
    const dir = dirname(TOKEN_FILE);
    if (!existsSync(dir))
        mkdirSync(dir, { recursive: true });
    const encrypted = encryptToken(token);
    writeFileSync(TOKEN_FILE, encrypted, { mode: 0o600 });
    return true;
}
export function getToken() {
    try {
        if (!existsSync(TOKEN_FILE))
            return null;
        const encrypted = readFileSync(TOKEN_FILE, "utf8").trim();
        return decryptToken(encrypted) || null;
    }
    catch {
        return null;
    }
}
export function deleteToken() {
    try {
        if (existsSync(TOKEN_FILE))
            unlinkSync(TOKEN_FILE);
        return true;
    }
    catch {
        return false;
    }
}
