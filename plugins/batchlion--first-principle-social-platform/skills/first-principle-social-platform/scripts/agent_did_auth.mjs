#!/usr/bin/env node
// SECURITY MANIFEST:
//   Environment variables accessed: SKILLS_ROOT_DIR, OPENCLAW_STATE_DIR
//   External endpoints called: <base-url>/agent/auth/did/register/challenge, <base-url>/agent/auth/did/register, <base-url>/agent/auth/didwba/verify
//   Local files read: explicit private key files, OpenClaw gateway device identity file, existing key files in output dir
//   Local files written: manual bootstrap key files, optional session file, optional credential index file

import { createHash, createPrivateKey, createPublicKey, generateKeyPairSync, randomBytes, sign } from "node:crypto";
import { chmodSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { canonicalizeJson } from "./lib/rfc8785_jcs.mjs";

const DID_WBA_USER_PATTERN = /^did:wba:([a-z0-9.-]+):user:([A-Za-z0-9._~-]{1,128})$/;
const DEFAULT_REGISTER_DID_DOMAINS = ["first-principle.com.cn"];
const DEFAULT_LOGIN_DID_DOMAINS = ["first-principle.com.cn"];
const SCRIPT_FILE = fileURLToPath(import.meta.url);
const SCRIPT_DIR = path.dirname(SCRIPT_FILE);
const SKILLS_ROOT_DIR = resolveSkillsRootDir();
const DEFAULT_STATE_DIR = path.join(SKILLS_ROOT_DIR, ".first-principle-social-platform");

function usage() {
  console.log(`OpenClaw DID helper

Usage:
  node scripts/agent_did_auth.mjs generate-keys --out-dir <dir> --name <name>
  node scripts/agent_did_auth.mjs sign --private-jwk <file> --challenge <text>
  node scripts/agent_did_auth.mjs login --base-url <api> [--did <did> --private-jwk <file> | --private-pem <file>] [--device-identity <file>] [--key-id <id>] [--display-name <name>] [--save-session <file>] [--save-credential <file>] [--no-bootstrap] [--allow-bootstrap-after-explicit]
  node scripts/agent_did_auth.mjs bootstrap --base-url <api> [--device-identity <file> | --did <did> --name <name> [--out-dir <dir>]] [--key-id <id>] [--display-name <name>] [--save-session <file>] [--save-credential <file>]

Notes:
  - local credential discovery/scanning is disabled
  - login with explicit DID+key uses only user-provided key path
  - login without explicit DID+key uses OpenClaw gateway device identity (device.json)
  - default gateway device path: ${path.join(resolveOpenClawStateDir(), "identity", "device.json")}
  - default local state dir: ${DEFAULT_STATE_DIR}
  - optional env SKILLS_ROOT_DIR overrides manual key/session defaults
  - optional env OPENCLAW_STATE_DIR overrides OpenClaw device identity location
  - script-side DID domain defaults: login first-principle.com.cn; bootstrap first-principle.com.cn
  - backend still enforces domain allowlists server-side
`);
}

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) {
      continue;
    }
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      args[key] = "true";
      continue;
    }
    args[key] = next;
    i += 1;
  }
  return args;
}

function hasFlag(args, key) {
  const value = String(args[key] || "").trim().toLowerCase();
  return value === "true" || value === "1" || value === "yes";
}

function requireArg(args, key) {
  const value = args[key];
  if (!value) {
    throw new Error(`Missing required argument --${key}`);
  }
  return String(value);
}

function expandHome(inputPath) {
  if (!inputPath) {
    return "";
  }
  if (inputPath === "~") {
    return homedir();
  }
  if (inputPath.startsWith("~/")) {
    return path.join(homedir(), inputPath.slice(2));
  }
  return inputPath;
}

function resolveSkillsRootDir() {
  const fromEnv = String(process.env.SKILLS_ROOT_DIR || "").trim();
  if (fromEnv) {
    return path.resolve(expandHome(fromEnv));
  }
  return path.resolve(SCRIPT_DIR, "../..");
}

function resolveOpenClawStateDir() {
  const fromEnv = String(process.env.OPENCLAW_STATE_DIR || "").trim();
  if (fromEnv) {
    return path.resolve(expandHome(fromEnv));
  }
  return path.join(homedir(), ".openclaw");
}

function normalizePathForRead(filePath, sourceFile = "") {
  const expanded = expandHome(filePath);
  if (path.isAbsolute(expanded)) {
    return expanded;
  }
  if (sourceFile) {
    return path.resolve(path.dirname(sourceFile), expanded);
  }
  return path.resolve(expanded);
}

function parseDidDescriptor(did) {
  const match = String(did).match(DID_WBA_USER_PATTERN);
  if (!match) {
    throw new Error("Invalid DID format");
  }
  return {
    domain: match[1].toLowerCase(),
    userId: match[2],
  };
}

function ensureDidFormat(did) {
  parseDidDescriptor(did);
}

function parseRegisterAllowedDomains() {
  return new Set(DEFAULT_REGISTER_DID_DOMAINS);
}

function parseLoginAllowedDomains() {
  return new Set(DEFAULT_LOGIN_DID_DOMAINS);
}

function isDidDomainAllowed(domain, allowedDomains) {
  if (allowedDomains.has("*")) {
    return true;
  }
  return allowedDomains.has(String(domain || "").toLowerCase());
}

function readPrivateJwk(filePath) {
  const raw = readFileSync(filePath, "utf8");
  const jwk = JSON.parse(raw);
  if (!jwk || typeof jwk !== "object") {
    throw new Error("Invalid private JWK file");
  }
  if (!("d" in jwk)) {
    throw new Error("JWK is not a private key");
  }
  return jwk;
}

function pickString(obj, keys) {
  for (const key of keys) {
    if (typeof obj[key] === "string" && obj[key].trim()) {
      return obj[key].trim();
    }
  }
  return "";
}

function readPrivatePem(filePath) {
  const raw = readFileSync(filePath, "utf8").trim();
  if (raw.includes("BEGIN") && raw.includes("PRIVATE KEY")) {
    return raw;
  }
  try {
    const parsed = JSON.parse(raw);
    const privatePem = pickString(parsed, ["private_key_pem", "privatePem", "private_pem", "privateKeyPem"]);
    if (privatePem && privatePem.includes("BEGIN") && privatePem.includes("PRIVATE KEY")) {
      return privatePem.trim();
    }
  } catch {
    // fallthrough
  }
  throw new Error("Invalid private PEM file");
}

function parsePrivateKeyFromCredential(params) {
  if (params.privateJwk) {
    return createPrivateKey({ key: params.privateJwk, format: "jwk" });
  }
  if (params.privateJwkPath) {
    const jwk = readPrivateJwk(params.privateJwkPath);
    return createPrivateKey({ key: jwk, format: "jwk" });
  }
  if (params.privatePem) {
    return createPrivateKey(params.privatePem);
  }
  if (params.privatePemPath) {
    const pem = readPrivatePem(params.privatePemPath);
    return createPrivateKey(pem);
  }
  throw new Error("Missing private key material");
}

function b64u(input) {
  return Buffer.from(input).toString("base64url");
}

function resolveOptionalPath(rawPath) {
  const value = String(rawPath || "").trim();
  if (!value) {
    return "";
  }
  return normalizePathForRead(value);
}

function resolveGatewayDeviceIdentityPath(args) {
  const fromArgs = String(args["device-identity"] || "").trim();
  if (fromArgs) {
    return normalizePathForRead(fromArgs);
  }
  return path.join(resolveOpenClawStateDir(), "identity", "device.json");
}

function resolveOutputDir(rawPath) {
  const value = String(rawPath || "").trim();
  if (!value) {
    return path.join(DEFAULT_STATE_DIR, "keys");
  }
  return normalizePathForRead(value);
}

function enforcePrivateFileMode(filePath) {
  if (!filePath) {
    return;
  }
  try {
    chmodSync(filePath, 0o600);
  } catch {
    // Ignore chmod failures and preserve original write error handling behavior.
  }
}

function readGatewayDeviceIdentity(filePath) {
  const raw = readFileSync(filePath, "utf8");
  const parsed = JSON.parse(raw);
  if (!parsed || typeof parsed !== "object") {
    throw new Error("Invalid OpenClaw device identity JSON");
  }

  const publicKeyPem = pickString(parsed, ["publicKeyPem", "public_key_pem", "public_pem"]);
  const privateKeyPem = pickString(parsed, ["privateKeyPem", "private_key_pem", "private_pem"]);
  if (!publicKeyPem.includes("BEGIN") || !publicKeyPem.includes("PUBLIC KEY")) {
    throw new Error("OpenClaw device identity missing valid publicKeyPem");
  }
  if (!privateKeyPem.includes("BEGIN") || !privateKeyPem.includes("PRIVATE KEY")) {
    throw new Error("OpenClaw device identity missing valid privateKeyPem");
  }

  const privateKey = createPrivateKey(privateKeyPem);
  const publicJwk = createPublicKey(publicKeyPem).export({ format: "jwk" });
  const privateDerivedPublicJwk = createPublicKey(privateKey).export({ format: "jwk" });
  validatePublicJwk(publicJwk);
  validatePublicJwk(privateDerivedPublicJwk);
  if (String(publicJwk.crv || "") !== "Ed25519" || typeof publicJwk.x !== "string") {
    throw new Error("OpenClaw gateway device key must be Ed25519");
  }
  if (publicJwk.x !== privateDerivedPublicJwk.x) {
    throw new Error("OpenClaw device identity public/private key mismatch");
  }

  const deviceId = createHash("sha256").update(Buffer.from(publicJwk.x, "base64url")).digest("hex");
  return {
    filePath,
    deviceId,
    publicJwk,
    privateKey,
  };
}

function buildGatewayDidMaterial(args, registerAllowedDomains) {
  const deviceIdentityPath = resolveGatewayDeviceIdentityPath(args);
  if (!existsSync(deviceIdentityPath)) {
    throw new Error(`OpenClaw gateway device identity not found: ${deviceIdentityPath}`);
  }
  const identity = readGatewayDeviceIdentity(deviceIdentityPath);
  const domain = Array.from(registerAllowedDomains)[0];
  if (!domain) {
    throw new Error("No register-allowed DID domains configured for gateway-device flow.");
  }
  const did = `did:wba:${domain}:user:${identity.deviceId}`;
  const keyId = `${did}#key-1`;
  return {
    did,
    keyId,
    deviceId: identity.deviceId,
    deviceIdentityPath,
    privateKey: identity.privateKey,
    publicJwk: identity.publicJwk,
    didDocument: buildDidDocument(did, keyId, identity.publicJwk),
  };
}

function createKeyFiles(outDir, name) {
  mkdirSync(outDir, { recursive: true });
  const { publicKey, privateKey } = generateKeyPairSync("ed25519");
  const publicJwk = publicKey.export({ format: "jwk" });
  const privateJwk = privateKey.export({ format: "jwk" });

  const publicPath = path.join(outDir, `${name}-public.jwk`);
  const privatePath = path.join(outDir, `${name}-private.jwk`);
  writeFileSync(publicPath, JSON.stringify(publicJwk, null, 2));
  writeFileSync(privatePath, JSON.stringify(privateJwk, null, 2), { mode: 0o600 });
  enforcePrivateFileMode(privatePath);

  return {
    publicPath,
    privatePath,
    publicJwk,
    privateJwk,
    keySource: "generated",
  };
}

function validatePublicJwk(jwk) {
  if (!jwk || typeof jwk !== "object") {
    throw new Error("Invalid public JWK file");
  }
  if (typeof jwk.kty !== "string" || typeof jwk.crv !== "string" || typeof jwk.x !== "string") {
    throw new Error("Public JWK missing required fields (kty/crv/x)");
  }
}

function validatePrivateJwk(jwk) {
  if (!jwk || typeof jwk !== "object") {
    throw new Error("Invalid private JWK file");
  }
  if (typeof jwk.d !== "string") {
    throw new Error("Private JWK missing required field (d)");
  }
}

function loadOrCreateKeyFiles(outDir, name) {
  mkdirSync(outDir, { recursive: true });
  const publicPath = path.join(outDir, `${name}-public.jwk`);
  const privatePath = path.join(outDir, `${name}-private.jwk`);
  const hasPublic = existsSync(publicPath);
  const hasPrivate = existsSync(privatePath);

  if (hasPublic && hasPrivate) {
    const publicJwk = JSON.parse(readFileSync(publicPath, "utf8"));
    const privateJwk = JSON.parse(readFileSync(privatePath, "utf8"));
    validatePublicJwk(publicJwk);
    validatePrivateJwk(privateJwk);
    enforcePrivateFileMode(privatePath);
    return {
      publicPath,
      privatePath,
      publicJwk,
      privateJwk,
      keySource: "existing",
    };
  }

  if (hasPublic || hasPrivate) {
    throw new Error(
      `Partial key files detected in ${outDir}. Expected both ${name}-public.jwk and ${name}-private.jwk.`,
    );
  }

  return createKeyFiles(outDir, name);
}

function buildDidDocument(did, keyId, publicJwk) {
  return {
    id: did,
    verificationMethod: [
      {
        id: keyId,
        type: "JsonWebKey2020",
        controller: did,
        publicKeyJwk: {
          kty: publicJwk.kty,
          crv: publicJwk.crv,
          x: publicJwk.x,
        },
      },
    ],
    authentication: [keyId],
  };
}

function resolveServiceDomainFromBaseUrl(baseUrl) {
  const url = new URL(baseUrl);
  return url.hostname.toLowerCase();
}

function resolveVerificationMethodFragment(did, keyId) {
  const trimmed = String(keyId || "").trim();
  if (!trimmed) {
    return "key-1";
  }
  if (trimmed.includes("#")) {
    const [prefix, fragment] = trimmed.split("#");
    if (prefix && prefix !== did) {
      throw new Error(`key_id DID mismatch: ${trimmed}`);
    }
    if (!fragment) {
      throw new Error(`Invalid key_id: ${trimmed}`);
    }
    return fragment;
  }
  return trimmed;
}

function signDidWbaContentHash(privateKey, contentHash) {
  if (!privateKey || typeof privateKey !== "object") {
    throw new Error("Invalid private key");
  }
  const keyType = privateKey.asymmetricKeyType;
  if (keyType === "ed25519" || keyType === "ed448") {
    return sign(null, contentHash, privateKey);
  }
  if (keyType === "ec") {
    return sign("sha256", contentHash, { key: privateKey, dsaEncoding: "ieee-p1363" });
  }
  return sign("sha256", contentHash, privateKey);
}

function buildDidWbaAuthorization(params) {
  const payload = {
    nonce: randomBytes(16).toString("hex"),
    timestamp: new Date().toISOString().replace(/\.\d{3}Z$/, "Z"),
    did: params.did,
    aud: params.serviceDomain,
  };

  const canonical = canonicalizeJson(payload);
  const contentHash = createHash("sha256").update(canonical).digest();
  const signature = signDidWbaContentHash(params.privateKey, contentHash).toString("base64url");
  const verificationMethodFragment = resolveVerificationMethodFragment(params.did, params.keyId);
  return `DIDWba did="${params.did}", nonce="${payload.nonce}", timestamp="${payload.timestamp}", verification_method="${verificationMethodFragment}", signature="${signature}"`;
}

async function postJson(url, payload, extraHeaders = {}) {
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...extraHeaders,
    },
    body: JSON.stringify(payload),
  });
  const text = await res.text();
  let json;
  try {
    json = text ? JSON.parse(text) : {};
  } catch {
    json = { raw: text };
  }
  if (!res.ok) {
    const msg = json?.error ? String(json.error) : `HTTP ${res.status}`;
    throw new Error(`${url} -> ${msg}`);
  }
  return json;
}

async function runDidWbaLogin(params) {
  const serviceDomain = resolveServiceDomainFromBaseUrl(params.baseUrl);
  const authorization = buildDidWbaAuthorization({
    did: params.did,
    keyId: params.keyId,
    privateKey: params.privateKey,
    serviceDomain,
  });

  const verifyRes = await postJson(`${params.baseUrl}/agent/auth/didwba/verify`, params.displayName ? {
    display_name: params.displayName,
  } : {}, {
    Authorization: authorization,
  });

  if (params.saveSession) {
    mkdirSync(path.dirname(params.saveSession), { recursive: true });
    writeFileSync(params.saveSession, JSON.stringify(verifyRes, null, 2), { mode: 0o600 });
    enforcePrivateFileMode(params.saveSession);
  }

  const accessToken = verifyRes?.session?.access_token ? String(verifyRes.session.access_token) : "";
  const refreshToken = verifyRes?.session?.refresh_token ? String(verifyRes.session.refresh_token) : "";

  return {
    verifyRes,
    summary: {
      ok: true,
      user: verifyRes.user || null,
      profile: verifyRes.profile || null,
      access_token_preview: accessToken ? `${accessToken.slice(0, 12)}...` : "",
      refresh_token_preview: refreshToken ? `${refreshToken.slice(0, 12)}...` : "",
      session_saved_to: params.saveSession || null,
      session_file_mode: params.saveSession ? "0600" : null,
    },
  };
}

async function registerDidAndLogin(params) {
  const registerChallengeRes = await postJson(`${params.baseUrl}/agent/auth/did/register/challenge`, { did: params.did });
  const registerChallengeText = String(registerChallengeRes.challenge || "");
  const registerChallengeId = String(registerChallengeRes.challenge_id || "");
  if (!registerChallengeText || !registerChallengeId) {
    throw new Error("Register challenge response missing fields");
  }

  const registerSignature = sign(null, Buffer.from(registerChallengeText, "utf8"), params.privateKey).toString("base64url");
  const registerBody = {
    did: params.did,
    did_document: params.didDocument,
    challenge_id: registerChallengeId,
    signature: registerSignature,
    key_id: params.keyId,
  };
  if (params.displayName) {
    registerBody.display_name = params.displayName;
  }

  const registerRes = await postJson(`${params.baseUrl}/agent/auth/did/register`, registerBody);
  const loginRes = await runDidWbaLogin({
    baseUrl: params.baseUrl,
    did: params.did,
    privateKey: params.privateKey,
    keyId: params.keyId,
    saveSession: params.saveSession,
    displayName: params.displayName,
  });
  return { registerRes, loginRes };
}

function saveDidCredential(filePath, payload) {
  const resolvedPath = normalizePathForRead(filePath);
  mkdirSync(path.dirname(resolvedPath), { recursive: true });
  const body = {
    did: payload.did,
    key_id: payload.keyId || null,
    private_jwk_path: payload.privateJwkPath || null,
    private_pem_path: payload.privatePemPath || null,
    saved_at: new Date().toISOString(),
  };
  writeFileSync(resolvedPath, JSON.stringify(body, null, 2), { mode: 0o600 });
  enforcePrivateFileMode(resolvedPath);
  return resolvedPath;
}

function generateKeys(args) {
  const outDir = requireArg(args, "out-dir");
  const name = requireArg(args, "name");
  const generated = createKeyFiles(outDir, name);

  console.log(JSON.stringify({
    ok: true,
    public_jwk_path: generated.publicPath,
    private_jwk_path: generated.privatePath,
    did_public_x: generated.publicJwk.x,
    key_type: generated.publicJwk.kty,
    curve: generated.publicJwk.crv,
  }, null, 2));
}

function signChallenge(args) {
  const privateJwkPath = requireArg(args, "private-jwk");
  const challenge = requireArg(args, "challenge");
  const privateJwk = readPrivateJwk(privateJwkPath);
  const privateKey = createPrivateKey({ key: privateJwk, format: "jwk" });
  const signature = sign(null, Buffer.from(challenge, "utf8"), privateKey);
  console.log(JSON.stringify({ signature: b64u(signature) }, null, 2));
}

async function bootstrapDidWithManualKeys(args) {
  const baseUrl = requireArg(args, "base-url").replace(/\/$/, "");
  const did = requireArg(args, "did");
  ensureDidFormat(did);

  const descriptor = parseDidDescriptor(did);
  const registerAllowedDomains = parseRegisterAllowedDomains();
  if (!registerAllowedDomains.has(descriptor.domain)) {
    throw new Error(
      `Bootstrap is not allowed for DID domain "${descriptor.domain}". Allowed bootstrap domains: ${Array.from(registerAllowedDomains).join(", ")}.`,
    );
  }

  const outDir = resolveOutputDir(args["out-dir"]);
  const name = requireArg(args, "name");
  const keyId = args["key-id"] ? String(args["key-id"]) : `${did}#key-1`;
  const displayName = args["display-name"] ? String(args["display-name"]).trim() : "";
  const saveSession = resolveOptionalPath(args["save-session"]);
  const saveCredentialPath = resolveOptionalPath(args["save-credential"]);

  const generated = loadOrCreateKeyFiles(outDir, name);
  const didDocument = buildDidDocument(did, keyId, generated.publicJwk);
  const privateKey = createPrivateKey({ key: generated.privateJwk, format: "jwk" });
  let registerRes = null;
  let registerSkipped = false;
  let loginRes = null;

  if (generated.keySource === "existing") {
    try {
      loginRes = await runDidWbaLogin({
        baseUrl,
        did,
        privateKey,
        keyId,
        saveSession,
        displayName,
      });
      registerSkipped = true;
    } catch {
      // Fall through to register flow.
    }
  }

  if (!loginRes) {
    const registered = await registerDidAndLogin({
      baseUrl,
      did,
      keyId,
      didDocument,
      privateKey,
      saveSession,
      displayName,
    });
    registerRes = registered.registerRes;
    loginRes = registered.loginRes;
  }

  let credentialSavedTo = null;
  if (saveCredentialPath) {
    credentialSavedTo = saveDidCredential(saveCredentialPath, {
      did,
      keyId,
      privateJwkPath: generated.privatePath,
    });
  }

  console.log(JSON.stringify({
    ok: true,
    bootstrap: {
      did,
      key_id: keyId,
      public_jwk_path: generated.publicPath,
      private_jwk_path: generated.privatePath,
      private_jwk_mode: generated.privatePath ? "0600" : null,
      key_source: generated.keySource,
      register_skipped: registerSkipped,
      did_document_url: registerRes?.did_document_url || null,
      register_ok: registerRes ? Boolean(registerRes?.ok) : null,
      credential_saved_to: credentialSavedTo,
    },
    login: loginRes.summary,
  }, null, 2));
}

async function bootstrapDidWithGatewayDevice(args) {
  const baseUrl = requireArg(args, "base-url").replace(/\/$/, "");
  const registerAllowedDomains = parseRegisterAllowedDomains();
  const displayName = args["display-name"] ? String(args["display-name"]).trim() : "";
  const saveSession = resolveOptionalPath(args["save-session"]);
  const saveCredentialPath = resolveOptionalPath(args["save-credential"]);
  const gateway = buildGatewayDidMaterial(args, registerAllowedDomains);

  let registerRes = null;
  let registerSkipped = false;
  let loginRes = null;

  try {
    loginRes = await runDidWbaLogin({
      baseUrl,
      did: gateway.did,
      privateKey: gateway.privateKey,
      keyId: gateway.keyId,
      saveSession,
      displayName,
    });
    registerSkipped = true;
  } catch {
    const registered = await registerDidAndLogin({
      baseUrl,
      did: gateway.did,
      keyId: gateway.keyId,
      didDocument: gateway.didDocument,
      privateKey: gateway.privateKey,
      saveSession,
      displayName,
    });
    registerRes = registered.registerRes;
    loginRes = registered.loginRes;
  }

  let credentialSavedTo = null;
  if (saveCredentialPath) {
    credentialSavedTo = saveDidCredential(saveCredentialPath, {
      did: gateway.did,
      keyId: gateway.keyId,
      privatePemPath: gateway.deviceIdentityPath,
    });
  }

  console.log(JSON.stringify({
    ok: true,
    bootstrap: {
      did: gateway.did,
      key_id: gateway.keyId,
      gateway_device_id: gateway.deviceId,
      device_identity_path: gateway.deviceIdentityPath,
      key_source: "gateway-device",
      register_skipped: registerSkipped,
      did_document_url: registerRes?.did_document_url || `https://${parseDidDescriptor(gateway.did).domain}/user/${gateway.deviceId}/did.json`,
      register_ok: registerRes ? Boolean(registerRes?.ok) : null,
      credential_saved_to: credentialSavedTo,
    },
    login: loginRes.summary,
  }, null, 2));
}

async function bootstrapDid(args) {
  if (String(args.did || "").trim()) {
    await bootstrapDidWithManualKeys(args);
    return;
  }
  await bootstrapDidWithGatewayDevice(args);
}

async function tryExplicitLogin(args, params) {
  const explicitDid = args.did ? String(args.did).trim() : "";
  const explicitPrivateJwkPath = resolveOptionalPath(args["private-jwk"]);
  const explicitPrivatePemPath = resolveOptionalPath(args["private-pem"]);
  const explicitKeyId = args["key-id"] ? String(args["key-id"]) : undefined;

  const explicitProvided = Boolean(explicitDid || explicitPrivateJwkPath || explicitPrivatePemPath || explicitKeyId);
  if (!explicitProvided) {
    return false;
  }

  if (explicitPrivateJwkPath && explicitPrivatePemPath) {
    throw new Error("Use only one explicit private key input: --private-jwk or --private-pem.");
  }
  if (!explicitDid || (!explicitPrivateJwkPath && !explicitPrivatePemPath)) {
    throw new Error("Explicit login requires --did and either --private-jwk or --private-pem.");
  }

  ensureDidFormat(explicitDid);
  const descriptor = parseDidDescriptor(explicitDid);
  if (!isDidDomainAllowed(descriptor.domain, params.allowedLoginDomains)) {
    throw new Error(`DID domain "${descriptor.domain}" is not in script-side login allowed domains.`);
  }

  const keyIdAttempts = explicitKeyId ? [explicitKeyId] : [undefined];
  const errors = [];

  for (const keyIdAttempt of keyIdAttempts) {
    try {
      const privateKey = explicitPrivateJwkPath
        ? parsePrivateKeyFromCredential({ privateJwkPath: explicitPrivateJwkPath })
        : parsePrivateKeyFromCredential({ privatePemPath: explicitPrivatePemPath });

      const loginRes = await runDidWbaLogin({
        baseUrl: params.baseUrl,
        did: explicitDid,
        privateKey,
        keyId: keyIdAttempt,
        saveSession: params.saveSession,
        displayName: params.displayName,
      });

      let credentialSavedTo = null;
      if (params.saveCredentialPath) {
        credentialSavedTo = saveDidCredential(params.saveCredentialPath, {
          did: explicitDid,
          keyId: keyIdAttempt || explicitKeyId,
          privateJwkPath: explicitPrivateJwkPath,
          privatePemPath: explicitPrivatePemPath,
        });
      }

      console.log(JSON.stringify({
        ...loginRes.summary,
        did: explicitDid,
        key_id: keyIdAttempt || explicitKeyId || null,
        credential_saved_to: credentialSavedTo,
        login_mode: "explicit",
      }, null, 2));
      return true;
    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error);
      const keyLabel = keyIdAttempt ? ` (key_id=${keyIdAttempt})` : " (key_id=<auto>)";
      errors.push(`Explicit login failed${keyLabel}: ${msg}`);
    }
  }

  throw new Error(errors.join(" | "));
}

async function loginWithGatewayDevice(args, params) {
  const registerAllowedDomains = parseRegisterAllowedDomains();
  const gateway = buildGatewayDidMaterial(args, registerAllowedDomains);
  const descriptor = parseDidDescriptor(gateway.did);
  if (!isDidDomainAllowed(descriptor.domain, params.allowedLoginDomains)) {
    throw new Error(`DID domain "${descriptor.domain}" is not in script-side login allowed domains.`);
  }

  try {
    const loginRes = await runDidWbaLogin({
      baseUrl: params.baseUrl,
      did: gateway.did,
      privateKey: gateway.privateKey,
      keyId: gateway.keyId,
      saveSession: params.saveSession,
      displayName: params.displayName,
    });

    let credentialSavedTo = null;
    if (params.saveCredentialPath) {
      credentialSavedTo = saveDidCredential(params.saveCredentialPath, {
        did: gateway.did,
        keyId: gateway.keyId,
        privatePemPath: gateway.deviceIdentityPath,
      });
    }

    console.log(JSON.stringify({
      ...loginRes.summary,
      did: gateway.did,
      key_id: gateway.keyId,
      gateway_device_id: gateway.deviceId,
      device_identity_path: gateway.deviceIdentityPath,
      credential_saved_to: credentialSavedTo,
      login_mode: "gateway-device-existing",
    }, null, 2));
    return;
  } catch (loginError) {
    if (params.noBootstrap) {
      const message = loginError instanceof Error ? loginError.message : String(loginError);
      throw new Error(`Gateway device DID login failed and bootstrap is disabled: ${message}`);
    }
  }

  const registered = await registerDidAndLogin({
    baseUrl: params.baseUrl,
    did: gateway.did,
    keyId: gateway.keyId,
    didDocument: gateway.didDocument,
    privateKey: gateway.privateKey,
    saveSession: params.saveSession,
    displayName: params.displayName,
  });

  let credentialSavedTo = null;
  if (params.saveCredentialPath) {
    credentialSavedTo = saveDidCredential(params.saveCredentialPath, {
      did: gateway.did,
      keyId: gateway.keyId,
      privatePemPath: gateway.deviceIdentityPath,
    });
  }

  console.log(JSON.stringify({
    ok: true,
    bootstrap: {
      did: gateway.did,
      key_id: gateway.keyId,
      gateway_device_id: gateway.deviceId,
      device_identity_path: gateway.deviceIdentityPath,
      key_source: "gateway-device",
      register_skipped: false,
      did_document_url: registered.registerRes?.did_document_url || null,
      register_ok: Boolean(registered.registerRes?.ok),
      credential_saved_to: credentialSavedTo,
    },
    login: {
      ...registered.loginRes.summary,
      login_mode: "gateway-device-bootstrap",
    },
  }, null, 2));
}

async function loginWithDid(args) {
  const baseUrl = requireArg(args, "base-url").replace(/\/$/, "");
  const saveSession = resolveOptionalPath(args["save-session"]);
  const saveCredentialPath = resolveOptionalPath(args["save-credential"]);
  const displayName = args["display-name"] ? String(args["display-name"]).trim() : "";
  const noBootstrap = hasFlag(args, "no-bootstrap");
  const allowBootstrapAfterExplicit = hasFlag(args, "allow-bootstrap-after-explicit");

  const allowedLoginDomains = parseLoginAllowedDomains();

  try {
    const explicitLoggedIn = await tryExplicitLogin(args, {
      baseUrl,
      saveSession,
      saveCredentialPath,
      displayName,
      allowedLoginDomains,
    });
    if (explicitLoggedIn) {
      return;
    }
  } catch (error) {
    if (!allowBootstrapAfterExplicit) {
      throw error;
    }
    if (noBootstrap) {
      throw error;
    }
  }

  await loginWithGatewayDevice(args, {
    baseUrl,
    saveSession,
    saveCredentialPath,
    displayName,
    noBootstrap,
    allowedLoginDomains,
  });
}

async function main() {
  const [, , command = "", ...rest] = process.argv;
  if (!command || command === "--help" || command === "-h") {
    usage();
    process.exit(0);
  }

  const args = parseArgs(rest);

  try {
    if (command === "generate-keys") {
      generateKeys(args);
      return;
    }
    if (command === "sign") {
      signChallenge(args);
      return;
    }
    if (command === "login") {
      await loginWithDid(args);
      return;
    }
    if (command === "bootstrap") {
      await bootstrapDid(args);
      return;
    }
    usage();
    process.exit(1);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    console.error(JSON.stringify({ ok: false, error: message }));
    process.exit(1);
  }
}

await main();
