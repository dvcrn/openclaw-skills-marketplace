"use strict";
/**
 * Wallet Connect — Unified wallet management for UTXO agents
 *
 * Single entry point for all wallet operations:
 *
 * - **Auto-detect**: No wallet? → provisions one. Has wallet? → connects it.
 * - **Provision**: Server generates a BIP39 mnemonic, encrypts via ECDH, agent saves locally.
 * - **Connect**: Agent encrypts existing mnemonic, sends to server, receives session.
 * - **Disconnect**: Destroys server session + removes local session file.
 *
 * Run from repo root:
 *   node agent-workspace/skills/utxo_wallet/scripts/wallet-connect.js
 *
 * Options:
 *   --wallet <path>   Path to .wallet.json (default: auto-detected)
 *   --base-url <url>  UTXO API base URL (default: http://localhost:3000)
 *   --disconnect      Disconnect the current session and exit
 *   --force           Force reconnect even if session appears valid
 *   --provision        Create a new wallet (required for first-time setup)
 *   --force --provision  Destroy existing wallet and create a new one
 *
 * Zero external dependencies beyond Node.js built-in `crypto`.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const crypto = __importStar(require("crypto"));
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const HKDF_INFO = 'utxo-wallet-connect-v1';
const AES_KEY_LENGTH = 32;
const GCM_IV_LENGTH = 12;
/** Fetch with timeout — prevents hanging forever if server is unresponsive */
async function fetchWithTimeout(url, opts = {}, timeoutMs = 30_000) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
        return await fetch(url, { ...opts, signal: controller.signal });
    }
    catch (err) {
        if (err.name === 'AbortError') {
            throw new Error(`Request timed out after ${timeoutMs / 1000}s: ${url}`);
        }
        throw err;
    }
    finally {
        clearTimeout(timer);
    }
}
function parseArgs() {
    const args = process.argv.slice(2);
    // Try multiple default locations for wallet file
    const candidates = [
        path.join(process.cwd(), '.wallet.json'), // CWD is agent-workspace/
        path.join(process.cwd(), 'agent-workspace', '.wallet.json'), // CWD is project root
    ];
    let walletPath = candidates.find(p => fs.existsSync(p)) || candidates[0];
    let baseUrl = process.env.UTXO_API_BASE_URL || 'http://localhost:3000';
    let disconnect = false;
    let force = false;
    let provision = false;
    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--wallet' && args[i + 1]) {
            walletPath = path.resolve(args[++i]);
        }
        else if (args[i] === '--base-url' && args[i + 1]) {
            baseUrl = args[++i];
        }
        else if (args[i] === '--disconnect') {
            disconnect = true;
        }
        else if (args[i] === '--force') {
            force = true;
        }
        else if (args[i] === '--provision') {
            provision = true;
        }
    }
    // Validate base URL to prevent connecting to malicious servers
    if (!isAllowedBaseUrl(baseUrl)) {
        console.error(`ERROR: Base URL not allowed: ${baseUrl}`);
        console.error('Allowed: localhost, 127.0.0.1, utxo.fun, *.utxo.fun');
        console.error('Set UTXO_ALLOW_CUSTOM_BASE_URL=1 to override.');
        process.exit(1);
    }
    // Session file lives next to wallet file
    const sessionPath = path.join(path.dirname(walletPath), '.session.json');
    return { walletPath, baseUrl, disconnect, force, provision, sessionPath };
}
// ---------------------------------------------------------------------------
// Base URL validation
// ---------------------------------------------------------------------------
const ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'utxo.fun'];
function isAllowedBaseUrl(url) {
    if (process.env.UTXO_ALLOW_CUSTOM_BASE_URL === '1')
        return true;
    try {
        const parsed = new URL(url);
        const host = parsed.hostname;
        if (ALLOWED_HOSTS.includes(host))
            return true;
        if (host.endsWith('.utxo.fun'))
            return true;
        return false;
    }
    catch {
        return false;
    }
}
function generateEphemeralKeypair() {
    const { publicKey, privateKey } = crypto.generateKeyPairSync('x25519');
    const rawPub = publicKey.export({ type: 'spki', format: 'der' });
    const pubBytes = rawPub.subarray(rawPub.length - 32);
    return { publicKey: pubBytes, privateKey };
}
function deriveSharedKey(ourPrivateKey, theirRawPublicKeyHex, nonce) {
    // Wrap raw 32-byte public key into X25519 SPKI DER
    const spkiHeader = Buffer.from('302a300506032b656e032100', 'hex');
    const theirRawBuf = Buffer.from(theirRawPublicKeyHex, 'hex');
    const spkiDer = Buffer.concat([spkiHeader, theirRawBuf]);
    const theirKeyObj = crypto.createPublicKey({
        key: spkiDer,
        type: 'spki',
        format: 'der',
    });
    const sharedSecret = crypto.diffieHellman({
        privateKey: ourPrivateKey,
        publicKey: theirKeyObj,
    });
    const aesKey = crypto.hkdfSync('sha256', sharedSecret, Buffer.from(nonce, 'hex'), HKDF_INFO, AES_KEY_LENGTH);
    return Buffer.from(aesKey);
}
function encrypt(plaintext, key) {
    const iv = crypto.randomBytes(GCM_IV_LENGTH);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    const encrypted = Buffer.concat([
        cipher.update(plaintext, 'utf8'),
        cipher.final(),
    ]);
    return {
        ciphertext: encrypted.toString('hex'),
        iv: iv.toString('hex'),
        tag: cipher.getAuthTag().toString('hex'),
    };
}
function decrypt(payload, key) {
    const decipher = crypto.createDecipheriv('aes-256-gcm', key, Buffer.from(payload.iv, 'hex'));
    decipher.setAuthTag(Buffer.from(payload.tag, 'hex'));
    const decrypted = Buffer.concat([
        decipher.update(Buffer.from(payload.ciphertext, 'hex')),
        decipher.final(),
    ]);
    return decrypted.toString('utf8');
}
// ---------------------------------------------------------------------------
// At-rest encryption for wallet mnemonic
// ---------------------------------------------------------------------------
const WALLET_KEY_FILENAME = '.wallet.key';
function getWalletKeyPath(walletPath) {
    return path.join(path.dirname(walletPath), WALLET_KEY_FILENAME);
}
function writeFileRestricted(filePath, data) {
    fs.writeFileSync(filePath, data, { mode: 0o600 });
    // On platforms that support chmod, enforce owner-only access
    try {
        fs.chmodSync(filePath, 0o600);
    }
    catch { /* Windows — ok */ }
}
function encryptMnemonicAtRest(mnemonic, walletKeyPath) {
    const key = crypto.randomBytes(32);
    writeFileRestricted(walletKeyPath, key.toString('hex'));
    return encrypt(mnemonic, key);
}
function decryptMnemonicAtRest(payload, walletKeyPath) {
    if (!fs.existsSync(walletKeyPath)) {
        console.error(`ERROR: Wallet key file not found: ${walletKeyPath}`);
        console.error('Cannot decrypt mnemonic without the .wallet.key file.');
        process.exit(1);
    }
    const keyHex = fs.readFileSync(walletKeyPath, 'utf-8').trim();
    if (keyHex.length !== 64) {
        console.error('ERROR: Wallet key file is corrupted (expected 64 hex chars).');
        process.exit(1);
    }
    const key = Buffer.from(keyHex, 'hex');
    return decrypt(payload, key);
}
// ---------------------------------------------------------------------------
// Shared: Handshake + keypair
// ---------------------------------------------------------------------------
async function performHandshake(baseUrl) {
    const hsRes = await fetchWithTimeout(`${baseUrl}/api/agent/wallet/handshake`, {}, 30_000);
    if (!hsRes.ok) {
        const text = await hsRes.text();
        console.error(`Handshake failed (${hsRes.status}): ${text}`);
        process.exit(1);
    }
    const handshake = await hsRes.json();
    const { server_pubkey, nonce } = handshake;
    const agentKeypair = generateEphemeralKeypair();
    const sharedKey = deriveSharedKey(agentKeypair.privateKey, server_pubkey, nonce);
    return { agentKeypair, sharedKey, nonce };
}
// ---------------------------------------------------------------------------
// Disconnect
// ---------------------------------------------------------------------------
async function doDisconnect(baseUrl, sessionPath) {
    if (!fs.existsSync(sessionPath)) {
        console.log('No active session found.');
        return;
    }
    const sessionData = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
    const token = sessionData.session_token;
    if (!token) {
        console.log('Session file has no token. Removing stale file.');
        fs.unlinkSync(sessionPath);
        return;
    }
    console.log(`Disconnecting session for ${sessionData.spark_address || 'unknown'}...`);
    try {
        const res = await fetchWithTimeout(`${baseUrl}/api/agent/wallet/disconnect`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        }, 30_000);
        const data = await res.json();
        if (data.ok) {
            console.log('Disconnected successfully.');
        }
        else {
            console.log(`Server said: ${data.error || 'unknown error'} (may already be expired)`);
        }
    }
    catch (err) {
        console.log(`Disconnect request failed: ${err.message} (server may be down)`);
    }
    // Always remove local session file
    fs.unlinkSync(sessionPath);
    console.log('Session file removed.');
}
// ---------------------------------------------------------------------------
// Provision (no wallet exists — server generates one)
// ---------------------------------------------------------------------------
async function doProvision(walletPath, baseUrl, sessionPath) {
    console.log('No wallet found. Requesting a new one from UTXO server...');
    console.log('');
    // --- Step 1–2: Handshake + keypair ---
    console.log(`  [1/4] Requesting handshake from ${baseUrl}...`);
    const { agentKeypair, sharedKey, nonce } = await performHandshake(baseUrl);
    console.log(`  [1/4] Handshake received. Nonce: ${nonce.slice(0, 16)}...`);
    console.log('  [2/4] Ephemeral keypair + shared key derived.');
    // --- Step 3: Request wallet provision ---
    console.log('  [3/4] Requesting new wallet from server...');
    const provisionRes = await fetchWithTimeout(`${baseUrl}/api/agent/wallet/provision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            agent_pubkey: agentKeypair.publicKey.toString('hex'),
            nonce,
        }),
    }, 30_000);
    if (!provisionRes.ok) {
        const errData = await provisionRes.json().catch(() => ({ error: 'Unknown' }));
        console.error(`Provision failed (${provisionRes.status}): ${errData.error || JSON.stringify(errData)}`);
        process.exit(1);
    }
    const data = await provisionRes.json();
    if (!data.ok || !data.encrypted_mnemonic || !data.encrypted_session_token) {
        console.error('Provision response missing required fields:', data);
        process.exit(1);
    }
    // --- Step 4: Decrypt mnemonic + session token ---
    console.log('  [4/4] Decrypting mnemonic + session token...');
    const mnemonic = decrypt(data.encrypted_mnemonic, sharedKey);
    const sessionToken = decrypt(data.encrypted_session_token, sharedKey);
    // Validate mnemonic looks real
    const wordCount = mnemonic.trim().split(/\s+/).length;
    if (wordCount !== 12 && wordCount !== 24) {
        console.error(`ERROR: Decrypted mnemonic has ${wordCount} words (expected 12 or 24). Something went wrong.`);
        process.exit(1);
    }
    // --- Save wallet file (mnemonic encrypted at rest) ---
    fs.mkdirSync(path.dirname(walletPath), { recursive: true });
    const walletKeyPath = getWalletKeyPath(walletPath);
    const encryptedMnemonicAtRest = encryptMnemonicAtRest(mnemonic, walletKeyPath);
    const walletFile = {
        agent: 'utxo-agent',
        network: data.network,
        encrypted_mnemonic: encryptedMnemonicAtRest,
        identityPublicKey: data.identity_public_key,
        sparkAddress: data.spark_address,
        createdAt: new Date().toISOString(),
        provisionedBy: 'utxo-server',
    };
    writeFileRestricted(walletPath, JSON.stringify(walletFile, null, 2));
    // --- Save session file ---
    const sessionFile = {
        session_token: sessionToken,
        spark_address: data.spark_address,
        network: data.network,
        connected_at: new Date().toISOString(),
        idle_timeout_minutes: data.session_info?.idle_timeout_minutes || 15,
        base_url: baseUrl,
    };
    writeFileRestricted(sessionPath, JSON.stringify(sessionFile, null, 2));
    console.log('');
    console.log('=== WALLET PROVISIONED ===');
    console.log(`  Address:  ${data.spark_address}`);
    console.log(`  Network:  ${data.network}`);
    console.log(`  Wallet:   ${walletPath}`);
    console.log(`  Key:      ${walletKeyPath}`);
    console.log(`  Session:  ${sessionPath}`);
    console.log(`  Timeout:  ${sessionFile.idle_timeout_minutes} min idle`);
    console.log('');
    console.log('IMPORTANT: Your mnemonic is encrypted in .wallet.json.');
    console.log('           The decryption key is in .wallet.key.');
    console.log('           Back up BOTH files. The server does NOT have a copy.');
    console.log('');
    console.log('Use this in API calls:');
    console.log(`  Authorization: Bearer ${sessionToken.slice(0, 16)}...`);
    console.log('');
}
// ---------------------------------------------------------------------------
// Connect (wallet exists — reconnect session)
// ---------------------------------------------------------------------------
async function doConnect(walletPath, baseUrl, sessionPath) {
    // --- Load mnemonic ---
    if (!fs.existsSync(walletPath)) {
        console.error(`ERROR: Wallet file not found: ${walletPath}`);
        process.exit(1);
    }
    const walletData = JSON.parse(fs.readFileSync(walletPath, 'utf-8'));
    // Decrypt mnemonic from at-rest encryption
    let mnemonic;
    if (walletData.encrypted_mnemonic && typeof walletData.encrypted_mnemonic === 'object') {
        const walletKeyPath = getWalletKeyPath(walletPath);
        mnemonic = decryptMnemonicAtRest(walletData.encrypted_mnemonic, walletKeyPath);
    }
    else if (walletData.mnemonic) {
        // Legacy plaintext wallet — still works but warn
        console.warn('WARNING: Wallet has plaintext mnemonic. Re-provision to upgrade to encrypted storage.');
        mnemonic = walletData.mnemonic;
    }
    else {
        console.error('ERROR: Wallet file has no mnemonic (encrypted or plaintext).');
        process.exit(1);
    }
    console.log('Wallet loaded. Starting encrypted handshake...');
    // --- Step 1–2: Handshake + keypair ---
    console.log(`  [1/4] Requesting handshake from ${baseUrl}...`);
    const { agentKeypair, sharedKey, nonce } = await performHandshake(baseUrl);
    console.log(`  [1/4] Handshake received. Nonce: ${nonce.slice(0, 16)}...`);
    console.log('  [2/4] Ephemeral keypair + shared key derived.');
    // --- Step 3: Encrypt mnemonic + send ---
    console.log('  [3/4] Encrypting mnemonic + sending connect request...');
    const encryptedMnemonic = encrypt(mnemonic, sharedKey);
    const connectRes = await fetchWithTimeout(`${baseUrl}/api/agent/wallet/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            agent_pubkey: agentKeypair.publicKey.toString('hex'),
            encrypted_mnemonic: encryptedMnemonic,
            nonce,
        }),
    }, 30_000);
    if (!connectRes.ok) {
        const errData = await connectRes.json().catch(() => ({ error: 'Unknown' }));
        console.error(`Connect failed (${connectRes.status}): ${errData.error || JSON.stringify(errData)}`);
        process.exit(1);
    }
    const connectData = await connectRes.json();
    if (!connectData.ok || !connectData.encrypted_session_token) {
        console.error('Connect response missing encrypted_session_token:', connectData);
        process.exit(1);
    }
    // --- Step 4: Decrypt session token ---
    console.log('  [4/4] Decrypting session token...');
    const sessionToken = decrypt(connectData.encrypted_session_token, sharedKey);
    // --- Save session ---
    const sessionFile = {
        session_token: sessionToken,
        spark_address: connectData.spark_address,
        network: connectData.network,
        connected_at: new Date().toISOString(),
        idle_timeout_minutes: connectData.session_info?.idle_timeout_minutes || 15,
        base_url: baseUrl,
    };
    writeFileRestricted(sessionPath, JSON.stringify(sessionFile, null, 2));
    console.log('');
    console.log('=== WALLET CONNECTED ===');
    console.log(`  Address:  ${connectData.spark_address}`);
    console.log(`  Network:  ${connectData.network}`);
    console.log(`  Session:  ${sessionPath}`);
    console.log(`  Timeout:  ${sessionFile.idle_timeout_minutes} min idle`);
    console.log('');
    console.log('Use this in API calls:');
    console.log(`  Authorization: Bearer ${sessionToken.slice(0, 16)}...`);
    console.log('');
}
// ---------------------------------------------------------------------------
// Main — auto-detects provision vs connect
// ---------------------------------------------------------------------------
async function main() {
    const { walletPath, baseUrl, disconnect, force, provision, sessionPath } = parseArgs();
    if (disconnect) {
        await doDisconnect(baseUrl, sessionPath);
        return;
    }
    const walletExists = fs.existsSync(walletPath);
    if (!walletExists) {
        if (!provision) {
            // Safety: refuse to auto-provision without explicit --provision flag
            console.error('ERROR: No wallet found at ' + walletPath);
            console.error('');
            console.error('  To CREATE a new wallet, run with --provision:');
            console.error('    node skills/utxo_wallet/scripts/wallet-connect.js --provision');
            console.error('');
            console.error('  If you already have a wallet, specify its path:');
            console.error('    node skills/utxo_wallet/scripts/wallet-connect.js --wallet /path/to/.wallet.json');
            console.error('');
            process.exit(1);
        }
        // Disconnect any stale session first
        if (fs.existsSync(sessionPath)) {
            console.log('Existing session found. Disconnecting first...');
            await doDisconnect(baseUrl, sessionPath);
            console.log('');
        }
        await doProvision(walletPath, baseUrl, sessionPath);
    }
    else if (force && provision) {
        // --force --provision: explicitly destroy and reprovision wallet
        console.log(`--force --provision: overwriting existing wallet at ${walletPath}`);
        if (fs.existsSync(sessionPath)) {
            console.log('Existing session found. Disconnecting first...');
            await doDisconnect(baseUrl, sessionPath);
            console.log('');
        }
        await doProvision(walletPath, baseUrl, sessionPath);
    }
    else if (force) {
        // --force (without --provision): force reconnect even if session looks valid
        console.log(`--force: forcing reconnect for wallet ${walletPath}`);
        if (fs.existsSync(sessionPath)) {
            console.log('Existing session found. Disconnecting first...');
            await doDisconnect(baseUrl, sessionPath);
            console.log('');
        }
        await doConnect(walletPath, baseUrl, sessionPath);
    }
    else {
        // Wallet exists → reconnect with it
        if (fs.existsSync(sessionPath)) {
            console.log('Existing session found. Disconnecting first...');
            await doDisconnect(baseUrl, sessionPath);
            console.log('');
        }
        await doConnect(walletPath, baseUrl, sessionPath);
    }
}
main().catch((err) => {
    console.error('FATAL:', err);
    process.exit(1);
});
