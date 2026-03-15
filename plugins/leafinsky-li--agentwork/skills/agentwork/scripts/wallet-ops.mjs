#!/usr/bin/env node
// wallet-ops.mjs — Hot wallet operations for AgentWork agents.
// All commands output JSON to stdout, errors to stderr, non-zero exit on failure.
// Called by the AI agent via bash tool calls — never by humans directly.
//
// Commands:
//   generate          Create new encrypted keystore
//   register-sign     Build registration message + sign in one step (recommended)
//   register-message  Build registration message with expiration
//   sign              Sign a message (EIP-191 personal_sign)
//   verify-wallet     Fetch challenge + sign + submit (escrow upgrade, one step)
//   address           Read wallet address from keystore
//   balance           Check ETH and ERC-20 token balance
//   transfer          Transfer ERC-20 tokens
//   deposit           Approve + deposit to escrow contract
//   audit             Report credential storage state (no secrets exposed)
//
// Security guarantees:
// - No key-export, key-dump, or private-key-display command exists
// - Private keys are decrypted only during signing, then GC'd
// - All network calls are explicit (user-specified --rpc, --escrow, and --base-url only)
// - No telemetry, no remote reporting, no opaque fetches

import { readFileSync, writeFileSync, mkdirSync, existsSync, chmodSync, statSync } from 'node:fs';
import { dirname } from 'node:path';
import { execSync } from 'node:child_process';
import { randomBytes } from 'node:crypto';

// Dynamic import of ethers (installed as skill dependency)
let ethers;
try {
  ethers = await import('ethers');
} catch {
  error('MISSING_DEPENDENCY', 'ethers is not installed. Run: npm install ethers');
}

// ─── Helpers ───

function error(code, message, details = {}) {
  process.stderr.write(JSON.stringify({ error: code, message, details }) + '\n');
  process.exit(1);
}

function output(data) {
  process.stdout.write(JSON.stringify(data) + '\n');
}

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    }
  }
  return args;
}

function requireArg(args, name) {
  if (!args[name]) {
    error('MISSING_ARG', `--${name} is required`);
  }
  return args[name];
}

// ─── Passphrase Management ───

function resolvePassphraseDir(keystorePath) {
  return dirname(keystorePath);
}

function storePassphrase(passphrase, credDir) {
  // Try macOS Keychain first
  if (process.platform === 'darwin') {
    try {
      execSync(
        `security add-generic-password -a agentwork-hot-wallet -s agentwork-hot-wallet -w "${passphrase}" -U`,
        { stdio: 'pipe' }
      );
      return 'keychain';
    } catch {
      // Fall through to file
    }
  }

  // Try Linux secret-tool
  if (process.platform === 'linux') {
    try {
      execSync(
        `echo -n "${passphrase}" | secret-tool store --label "agentwork-hot-wallet" service agentwork-hot-wallet account hot-wallet`,
        { stdio: 'pipe' }
      );
      return 'secret-tool';
    } catch {
      // Fall through to file
    }
  }

  // Fallback: file
  const passFile = `${credDir}/.passphrase`;
  writeFileSync(passFile, passphrase, { mode: 0o600 });
  return 'file';
}

function readPassphrase(credDir) {
  // Try macOS Keychain first
  if (process.platform === 'darwin') {
    try {
      const result = execSync(
        'security find-generic-password -a agentwork-hot-wallet -s agentwork-hot-wallet -w',
        { stdio: ['pipe', 'pipe', 'pipe'], encoding: 'utf8' }
      );
      return result.trim();
    } catch {
      // Fall through to file
    }
  }

  // Try Linux secret-tool
  if (process.platform === 'linux') {
    try {
      const result = execSync(
        'secret-tool lookup service agentwork-hot-wallet account hot-wallet',
        { stdio: ['pipe', 'pipe', 'pipe'], encoding: 'utf8' }
      );
      return result.trim();
    } catch {
      // Fall through to file
    }
  }

  // Fallback: file
  const passFile = `${credDir}/.passphrase`;
  if (!existsSync(passFile)) {
    error('PASSPHRASE_NOT_FOUND', 'No passphrase in keychain or file');
  }
  return readFileSync(passFile, 'utf8').trim();
}

// ─── Wallet Loading ───

function loadWallet(keystorePath, credDir) {
  if (!existsSync(keystorePath)) {
    error('KEYSTORE_NOT_FOUND', `No keystore at ${keystorePath}`);
  }
  const keystore = readFileSync(keystorePath, 'utf8');
  const passphrase = readPassphrase(credDir);
  try {
    return ethers.Wallet.fromEncryptedJsonSync(keystore, passphrase);
  } catch (e) {
    error('KEYSTORE_DECRYPT_FAILED', `Failed to decrypt keystore: ${e.message}`);
  }
}

// ─── Commands ───

async function cmdGenerate(args) {
  const keystorePath = requireArg(args, 'keystore');
  const credDir = dirname(keystorePath);

  if (existsSync(keystorePath)) {
    error('KEYSTORE_EXISTS', `Keystore already exists at ${keystorePath}`);
  }

  // Create directory
  mkdirSync(credDir, { recursive: true });
  try { chmodSync(credDir, 0o700); } catch { /* best effort */ }

  // Generate wallet
  const wallet = ethers.Wallet.createRandom();
  const passphrase = randomBytes(32).toString('hex');

  // Encrypt to keystore v3
  const keystore = await wallet.encrypt(passphrase);

  // Write keystore file
  writeFileSync(keystorePath, keystore, { mode: 0o600 });

  // Store passphrase
  const storage = storePassphrase(passphrase, credDir);

  output({
    address: wallet.address,
    keystore_path: keystorePath,
    passphrase_storage: storage,
  });
}

function cmdRegisterMessage(args) {
  const name = requireArg(args, 'name');
  const address = requireArg(args, 'address');
  const ttlMinutes = parseInt(args['ttl-minutes'] ?? '5', 10);

  const expiresAt = new Date(Date.now() + ttlMinutes * 60 * 1000);
  const message = [
    'agentwork:register',
    `name:${name}`,
    `address:${address}`,
    `Expiration Time:${expiresAt.toISOString()}`,
  ].join('\n');

  output({ message });
}

async function cmdSign(args) {
  const keystorePath = requireArg(args, 'keystore');
  const message = requireArg(args, 'message');
  const credDir = dirname(keystorePath);

  const wallet = loadWallet(keystorePath, credDir);
  const signature = await wallet.signMessage(message);

  output({ signature });
}

async function cmdRegisterSign(args) {
  const keystorePath = requireArg(args, 'keystore');
  const name = requireArg(args, 'name');
  const ttlMinutes = parseInt(args['ttl-minutes'] ?? '5', 10);
  const credDir = dirname(keystorePath);

  // Idempotent: generate wallet if missing, read if exists
  let address;
  if (!existsSync(keystorePath)) {
    mkdirSync(credDir, { recursive: true });
    try { chmodSync(credDir, 0o700); } catch { /* best effort */ }
    const wallet = ethers.Wallet.createRandom();
    const passphrase = randomBytes(32).toString('hex');
    const keystore = await wallet.encrypt(passphrase);
    writeFileSync(keystorePath, keystore, { mode: 0o600 });
    storePassphrase(passphrase, credDir);
    address = wallet.address;
  } else {
    const ks = JSON.parse(readFileSync(keystorePath, 'utf8'));
    address = ethers.getAddress(`0x${ks.address}`);
  }

  // Build registration message
  const expiresAt = new Date(Date.now() + ttlMinutes * 60 * 1000);
  const message = [
    'agentwork:register',
    `name:${name}`,
    `address:${address}`,
    `Expiration Time:${expiresAt.toISOString()}`,
  ].join('\n');

  // Sign
  const wallet = loadWallet(keystorePath, credDir);
  const signature = await wallet.signMessage(message);

  output({ address, message, signature });
}

function cmdAddress(args) {
  const keystorePath = requireArg(args, 'keystore');

  if (!existsSync(keystorePath)) {
    error('KEYSTORE_NOT_FOUND', `No keystore at ${keystorePath}`);
  }
  const keystore = JSON.parse(readFileSync(keystorePath, 'utf8'));
  // ethers v3 keystore stores address in the 'address' field (without 0x prefix)
  const address = keystore.address
    ? ethers.getAddress(`0x${keystore.address}`)
    : error('KEYSTORE_INVALID', 'No address field in keystore');

  output({ address });
}

async function cmdBalance(args) {
  const keystorePath = requireArg(args, 'keystore');
  const rpcUrl = requireArg(args, 'rpc');
  const tokenAddress = requireArg(args, 'token');

  if (!existsSync(keystorePath)) {
    error('KEYSTORE_NOT_FOUND', `No keystore at ${keystorePath}`);
  }
  const keystore = JSON.parse(readFileSync(keystorePath, 'utf8'));
  const address = ethers.getAddress(`0x${keystore.address}`);

  const provider = new ethers.JsonRpcProvider(rpcUrl);

  try {
    // ETH balance
    const ethBalance = await provider.getBalance(address);

    // ERC-20 balance
    const erc20 = new ethers.Contract(
      tokenAddress,
      [
        'function balanceOf(address) view returns (uint256)',
        'function symbol() view returns (string)',
        'function decimals() view returns (uint8)',
      ],
      provider
    );

    const [tokenBalance, symbol, decimals] = await Promise.all([
      erc20.balanceOf(address),
      erc20.symbol().catch(() => 'UNKNOWN'),
      erc20.decimals().catch(() => 6),
    ]);

    output({
      token_balance: tokenBalance.toString(),
      eth_balance: ethBalance.toString(),
      token_symbol: symbol,
      token_decimals: Number(decimals),
    });
  } catch (e) {
    error('RPC_FAILURE', `RPC call failed: ${e.message}`, { rpc_url: rpcUrl });
  }
}

async function cmdTransfer(args) {
  const keystorePath = requireArg(args, 'keystore');
  const rpcUrl = requireArg(args, 'rpc');
  const tokenAddress = requireArg(args, 'token');
  const to = requireArg(args, 'to');
  const amount = requireArg(args, 'amount');
  const credDir = dirname(keystorePath);

  const wallet = loadWallet(keystorePath, credDir);
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const signer = wallet.connect(provider);

  const erc20 = new ethers.Contract(
    tokenAddress,
    ['function transfer(address to, uint256 amount) returns (bool)'],
    signer
  );

  try {
    const tx = await erc20.transfer(to, amount);
    const receipt = await tx.wait();
    output({ tx_hash: receipt.hash, amount });
  } catch (e) {
    if (e.message?.includes('insufficient')) {
      error('INSUFFICIENT_BALANCE', e.message);
    }
    error('TX_FAILED', `Transfer failed: ${e.message}`);
  }
}

async function cmdDeposit(args) {
  const keystorePath = requireArg(args, 'keystore');
  const rpcUrl = requireArg(args, 'rpc');
  const escrowAddress = requireArg(args, 'escrow');
  const tokenAddress = requireArg(args, 'token');
  const orderId = requireArg(args, 'order-id');
  const termsHash = requireArg(args, 'terms-hash');
  const amount = requireArg(args, 'amount');
  const seller = requireArg(args, 'seller');
  const jurors = JSON.parse(requireArg(args, 'jurors'));
  const threshold = parseInt(requireArg(args, 'threshold'), 10);
  const credDir = dirname(keystorePath);

  const wallet = loadWallet(keystorePath, credDir);
  const provider = new ethers.JsonRpcProvider(rpcUrl);
  const signer = wallet.connect(provider);

  // Step 1: Approve ERC-20 spend
  const erc20 = new ethers.Contract(
    tokenAddress,
    ['function approve(address spender, uint256 amount) returns (bool)'],
    signer
  );

  try {
    const approveTx = await erc20.approve(escrowAddress, amount);
    await approveTx.wait();
  } catch (e) {
    error('APPROVE_FAILED', `Token approval failed: ${e.message}`);
  }

  // Step 2: Call deposit on escrow contract
  const escrow = new ethers.Contract(
    escrowAddress,
    ['function deposit(bytes32 orderId, address token, uint256 amount, bytes32 termsHash, address seller, address[] jurors, uint8 threshold) external'],
    signer
  );

  try {
    const tx = await escrow.deposit(orderId, tokenAddress, amount, termsHash, seller, jurors, threshold);
    const receipt = await tx.wait();
    output({ tx_hash: receipt.hash });
  } catch (e) {
    if (e.receipt?.hash) {
      error('TX_REVERTED', `Transaction reverted: ${e.message}`, { tx_hash: e.receipt.hash });
    }
    error('DEPOSIT_FAILED', `Deposit failed: ${e.message}`);
  }
}

async function cmdAudit(args) {
  const keystorePath = requireArg(args, 'keystore');
  const credDir = dirname(keystorePath);

  if (!existsSync(keystorePath)) {
    error('KEYSTORE_NOT_FOUND', `No keystore at ${keystorePath}`);
  }

  const keystore = JSON.parse(readFileSync(keystorePath, 'utf8'));
  const address = keystore.address
    ? ethers.getAddress(`0x${keystore.address}`)
    : 'unknown';

  // Check passphrase storage method
  let passphraseStorage = 'unknown';
  if (process.platform === 'darwin') {
    try {
      execSync('security find-generic-password -a agentwork-hot-wallet -s agentwork-hot-wallet', { stdio: 'pipe' });
      passphraseStorage = 'keychain';
    } catch {
      passphraseStorage = existsSync(`${credDir}/.passphrase`) ? 'file' : 'none';
    }
  } else if (process.platform === 'linux') {
    try {
      execSync('secret-tool lookup service agentwork-hot-wallet account hot-wallet', { stdio: ['pipe', 'pipe', 'pipe'] });
      passphraseStorage = 'secret-tool';
    } catch {
      passphraseStorage = existsSync(`${credDir}/.passphrase`) ? 'file' : 'none';
    }
  } else {
    passphraseStorage = existsSync(`${credDir}/.passphrase`) ? 'file' : 'none';
  }

  // Check file permissions
  let keystorePermissions = 'unknown';
  let dirPermissions = 'unknown';
  try {
    keystorePermissions = '0' + (statSync(keystorePath).mode & 0o777).toString(8);
  } catch { /* best effort */ }
  try {
    dirPermissions = '0' + (statSync(credDir).mode & 0o777).toString(8);
  } catch { /* best effort */ }

  output({
    address,
    passphrase_storage: passphraseStorage,
    keystore_permissions: keystorePermissions,
    dir_permissions: dirPermissions,
  });
}

async function cmdVerifyWallet(args) {
  if (typeof globalThis.fetch !== 'function') {
    error('MISSING_RUNTIME', 'Node 18+ is required for verify-wallet (built-in fetch)');
  }

  const keystorePath = requireArg(args, 'keystore');
  const baseUrl = requireArg(args, 'base-url');
  const chain = args.chain ?? 'base';
  const credDir = dirname(keystorePath);

  // Resolve API key: --api-key-file > env AGENTWORK_API_KEY > --api-key (legacy)
  let apiKey = args['api-key'];
  if (args['api-key-file']) {
    try {
      apiKey = readFileSync(args['api-key-file'], 'utf8').trim();
    } catch (e) {
      error('FILE_READ_FAILED', `Cannot read --api-key-file: ${e.message}`);
    }
  } else if (!apiKey && process.env.AGENTWORK_API_KEY) {
    apiKey = process.env.AGENTWORK_API_KEY;
  }
  if (!apiKey) {
    error('MISSING_ARG', '--api-key-file, AGENTWORK_API_KEY env, or --api-key is required');
  }

  // Resolve recovery code: --recovery-code-file > env AGENTWORK_RECOVERY_CODE > --recovery-code (legacy)
  let recoveryCode = args['recovery-code'];
  if (args['recovery-code-file']) {
    try {
      recoveryCode = readFileSync(args['recovery-code-file'], 'utf8').trim();
    } catch (e) {
      error('FILE_READ_FAILED', `Cannot read --recovery-code-file: ${e.message}`);
    }
  } else if (!recoveryCode && process.env.AGENTWORK_RECOVERY_CODE) {
    recoveryCode = process.env.AGENTWORK_RECOVERY_CODE;
  }

  // Read address from keystore without decrypting
  if (!existsSync(keystorePath)) {
    error('KEYSTORE_NOT_FOUND', `No keystore at ${keystorePath}`);
  }
  let ks;
  try {
    ks = JSON.parse(readFileSync(keystorePath, 'utf8'));
  } catch (e) {
    error('KEYSTORE_INVALID', `Cannot parse keystore JSON: ${e.message}`);
  }
  const address = ks.address
    ? ethers.getAddress(`0x${ks.address}`)
    : error('KEYSTORE_INVALID', 'No address field in keystore');

  // Step 1: Fetch challenge
  const challengeUrl = `${baseUrl}/agent/v1/profile/wallet-challenge?address=${encodeURIComponent(address)}&chain=${encodeURIComponent(chain)}`;
  let challengeRes;
  try {
    challengeRes = await fetch(challengeUrl, {
      headers: { 'Authorization': `Bearer ${apiKey}` },
    });
  } catch (e) {
    error('CHALLENGE_FETCH_FAILED', `GET wallet-challenge network error: ${e.message}`);
  }
  if (!challengeRes.ok) {
    const body = await challengeRes.text().catch(() => '');
    error('CHALLENGE_FETCH_FAILED', `GET wallet-challenge returned ${challengeRes.status}`, { body });
  }
  let challengeData;
  try {
    challengeData = await challengeRes.json();
  } catch (e) {
    error('CHALLENGE_PARSE_FAILED', `Failed to parse challenge response JSON: ${e.message}`);
  }
  const challenge = challengeData.data?.challenge;
  if (!challenge) {
    error('CHALLENGE_PARSE_FAILED', 'Response missing data.challenge', { body: challengeData });
  }

  // Extract nonce from challenge for idempotency key
  const nonceMatch = challenge.match(/\nnonce:([a-fA-F0-9]+)/);
  const nonce = nonceMatch ? nonceMatch[1] : '';

  // Step 2: Sign the exact challenge string
  const wallet = loadWallet(keystorePath, credDir);
  const signature = await wallet.signMessage(challenge);

  // Step 3: Submit verification
  const verifyBody = {
    address,
    chain,
    challenge,
    signature,
    idempotency_key: `verify-wallet:${address.toLowerCase()}:${chain}:${nonce}`,
  };
  if (recoveryCode) {
    verifyBody.recovery_code = recoveryCode;
  }

  let verifyRes;
  try {
    verifyRes = await fetch(`${baseUrl}/agent/v1/profile/verify-wallet`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(verifyBody),
    });
  } catch (e) {
    error('VERIFY_FAILED', `POST verify-wallet network error: ${e.message}`);
  }
  if (!verifyRes.ok) {
    const body = await verifyRes.text().catch(() => '');
    error('VERIFY_FAILED', `POST verify-wallet returned ${verifyRes.status}`, { body });
  }
  let verifyData;
  try {
    verifyData = await verifyRes.json();
  } catch (e) {
    error('VERIFY_FAILED', `Failed to parse verify response JSON: ${e.message}`);
  }
  output(verifyData.data);
}

// ─── Main ───

const command = process.argv[2];
const args = parseArgs(process.argv.slice(3));

switch (command) {
  case 'generate':
    await cmdGenerate(args);
    break;
  case 'register-message':
    cmdRegisterMessage(args);
    break;
  case 'sign':
    await cmdSign(args);
    break;
  case 'register-sign':
    await cmdRegisterSign(args);
    break;
  case 'address':
    cmdAddress(args);
    break;
  case 'balance':
    await cmdBalance(args);
    break;
  case 'transfer':
    await cmdTransfer(args);
    break;
  case 'deposit':
    await cmdDeposit(args);
    break;
  case 'verify-wallet':
    await cmdVerifyWallet(args);
    break;
  case 'audit':
    await cmdAudit(args);
    break;
  default:
    error('UNKNOWN_COMMAND', `Unknown command: ${command}. Valid: generate, register-sign, register-message, sign, verify-wallet, address, balance, transfer, deposit, audit`);
}
