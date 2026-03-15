#!/usr/bin/env node
/**
 * Max Auth Server
 * - Master password (hash + salt + PBKDF2)
 * - Biometric passkeys via WebAuthn
 * - 2h session tokens
 * - Rate limiting (5 attempts / 15min)
 * - Audit trail
 * - i18n: pt-BR / en (browser-detected)
 */

const http = require('http');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const os = require('os');

const {
  generateRegistrationOptions,
  verifyRegistrationResponse,
  generateAuthenticationOptions,
  verifyAuthenticationResponse,
} = require('@simplewebauthn/server');

const PORT = process.env.AUTH_PORT || 8456;
const SESSION_DURATION_MS = 2 * 60 * 60 * 1000;
const RATE_LIMIT_WINDOW_MS = 15 * 60 * 1000;
const RATE_LIMIT_MAX_ATTEMPTS = 5;

const CONFIG_DIR = path.join(os.homedir(), '.max-auth');
const PASSWORD_FILE = path.join(CONFIG_DIR, '.password');
const SESSION_FILE = path.join(CONFIG_DIR, '.session');
const AUDIT_FILE = path.join(CONFIG_DIR, 'audit.log');
const RATE_LIMIT_FILE = path.join(CONFIG_DIR, '.rate-limit');
const PASSKEYS_FILE = path.join(CONFIG_DIR, '.passkeys');
const WEBAUTHN_CHALLENGE_FILE = path.join(CONFIG_DIR, '.webauthn-challenge');

const RP_NAME = 'Max Auth';

function getRpID() {
  try {
    const { execSync } = require('child_process');
    const ts = JSON.parse(execSync('tailscale status --json 2>/dev/null', { encoding: 'utf8' }));
    const dns = ts.Self?.DNSName?.replace(/\.$/, '');
    if (dns) return dns;
  } catch {}
  return os.hostname();
}
const RP_ID = process.env.RP_ID || getRpID();
const RP_ORIGIN = process.env.RP_ORIGIN || `https://${RP_ID}`;

// ========== i18n ==========

const STRINGS = {
  en: {
    title: 'Max Auth',
    authenticated: (min) => `✅ Authenticated — session expires in ${min} min`,
    auth_required: '🔒 Authentication required',
    session_section: 'Session',
    logout: 'Log out',
    passkeys_section: (n) => `Registered passkeys (${n})`,
    no_passkeys: 'No passkeys yet.',
    add_passkey: '+ Register new passkey',
    passkey_name_placeholder: 'Passkey name (e.g. iPhone, MacBook)',
    confirm_register: 'Confirm & register',
    cancel: 'Cancel',
    confirm_pwd_for_reg: 'Confirm master password to register passkey',
    pwd_placeholder: 'Master password',
    login_btn: 'Sign in with password',
    login_with_passkey: '🔑 Sign in with passkey / biometrics',
    or: '— or —',
    blocked: (min) => `Too many attempts. Try again in ${min} min.`,
    verifying: 'Verifying...',
    waiting_bio: 'Waiting for biometrics...',
    authenticated_ok: '✅ Authenticated!',
    error_prefix: 'Error: ',
    wrong_pwd: 'Wrong password',
    not_authenticated: 'Not authenticated',
    challenge_expired: 'Challenge expired, refresh and try again',
    passkey_not_found: 'Passkey not found',
    verify_failed: 'Verification failed',
    bio_failed: 'Biometric verification failed',
    reg_ok: '✅ Passkey registered!',
    remove_passkey_confirm: 'Remove this passkey?',
    setup_first: 'Set master password first via CLI:',
    delete_ok: 'Deleted',
    password_section: 'Master password',
  },
  pt: {
    title: 'Max Auth',
    authenticated: (min) => `✅ Autenticado — sessão expira em ${min} min`,
    auth_required: '🔒 Autenticação necessária',
    session_section: 'Sessão',
    logout: 'Encerrar sessão',
    passkeys_section: (n) => `Passkeys cadastradas (${n})`,
    no_passkeys: 'Nenhuma passkey ainda.',
    add_passkey: '+ Cadastrar nova passkey',
    passkey_name_placeholder: 'Nome da passkey (ex: iPhone, MacBook)',
    confirm_register: 'Confirmar e cadastrar',
    cancel: 'Cancelar',
    confirm_pwd_for_reg: 'Confirme a senha mestra para cadastrar passkey',
    pwd_placeholder: 'Senha mestra',
    login_btn: 'Entrar com senha',
    login_with_passkey: '🔑 Entrar com passkey / biometria',
    or: '— ou —',
    blocked: (min) => `Bloqueado. Tente novamente em ${min} min.`,
    verifying: 'Verificando...',
    waiting_bio: 'Aguardando biometria...',
    authenticated_ok: '✅ Autenticado!',
    error_prefix: 'Erro: ',
    wrong_pwd: 'Senha incorreta',
    not_authenticated: 'Não autenticado',
    challenge_expired: 'Challenge expirado, atualize a página',
    passkey_not_found: 'Passkey não encontrada',
    verify_failed: 'Falha na verificação',
    bio_failed: 'Verificação biométrica falhou',
    reg_ok: '✅ Passkey cadastrada!',
    remove_passkey_confirm: 'Remover esta passkey?',
    setup_first: 'Defina a senha mestra primeiro via CLI:',
    delete_ok: 'Removida',
    password_section: 'Senha mestra',
  }
};

// ========== Utils ==========

function log(msg) { console.log(`[${new Date().toISOString()}] ${msg}`); }

function ensureConfigDir() {
  if (!fs.existsSync(CONFIG_DIR)) fs.mkdirSync(CONFIG_DIR, { recursive: true, mode: 0o700 });
}

function hashPassword(password, salt = null) {
  salt = salt || crypto.randomBytes(32).toString('hex');
  const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
  return { hash, salt };
}

function verifyPassword(password, storedHash, salt) {
  const { hash } = hashPassword(password, salt);
  return crypto.timingSafeEqual(Buffer.from(hash), Buffer.from(storedHash));
}

function generateToken() { return crypto.randomBytes(32).toString('hex'); }

// ========== Rate Limiting ==========

function getRateLimitData() {
  try { if (fs.existsSync(RATE_LIMIT_FILE)) return JSON.parse(fs.readFileSync(RATE_LIMIT_FILE, 'utf8')); } catch {}
  return { attempts: [], blocked: false, blockedUntil: null };
}
function saveRateLimitData(d) { fs.writeFileSync(RATE_LIMIT_FILE, JSON.stringify(d), { mode: 0o600 }); }

function checkRateLimit(ip) {
  const data = getRateLimitData();
  const now = Date.now();
  data.attempts = data.attempts.filter(t => now - t.time < RATE_LIMIT_WINDOW_MS);
  if (data.blocked && data.blockedUntil && now < data.blockedUntil) {
    return { allowed: false, remaining: Math.ceil((data.blockedUntil - now) / 60000) };
  }
  const ipAttempts = data.attempts.filter(t => t.ip === ip);
  return { allowed: true, attemptsRemaining: RATE_LIMIT_MAX_ATTEMPTS - ipAttempts.length };
}

function recordAttempt(ip, success) {
  const data = getRateLimitData();
  const now = Date.now();
  if (!success) {
    data.attempts.push({ ip, time: now });
    const failures = data.attempts.filter(t => t.ip === ip && now - t.time < RATE_LIMIT_WINDOW_MS);
    if (failures.length >= RATE_LIMIT_MAX_ATTEMPTS) {
      data.blocked = true; data.blockedUntil = now + RATE_LIMIT_WINDOW_MS;
      log(`⚠️ IP rate-limited: ${ip}`);
    }
  } else {
    data.attempts = data.attempts.filter(t => t.ip !== ip);
  }
  saveRateLimitData(data);
}

// ========== Password ==========

function setPassword(password) {
  ensureConfigDir();
  const { hash, salt } = hashPassword(password);
  fs.writeFileSync(PASSWORD_FILE, JSON.stringify({ hash, salt, createdAt: new Date().toISOString() }), { mode: 0o600 });
  log('✓ Master password set');
}
function getPasswordData() {
  try { if (fs.existsSync(PASSWORD_FILE)) return JSON.parse(fs.readFileSync(PASSWORD_FILE, 'utf8')); } catch {}
  return null;
}
function hasPassword() { return getPasswordData() !== null; }

// ========== Session ==========

function createSession(ip) {
  ensureConfigDir();
  const token = generateToken();
  const session = { token, createdAt: Date.now(), expiresAt: Date.now() + SESSION_DURATION_MS, ip };
  fs.writeFileSync(SESSION_FILE, JSON.stringify(session), { mode: 0o600 });
  log(`✓ Session created for IP: ${ip}`);
  return token;
}
function getSession() {
  try {
    if (fs.existsSync(SESSION_FILE)) {
      const s = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf8'));
      if (Date.now() < s.expiresAt) return s;
    }
  } catch {}
  return null;
}
function isValidSession(token) { const s = getSession(); return s && s.token === token; }
function clearSession() { if (fs.existsSync(SESSION_FILE)) { fs.unlinkSync(SESSION_FILE); log('✓ Session cleared'); } }

// ========== Audit ==========

function auditLog(action, ip, success, details = {}) {
  ensureConfigDir();
  fs.appendFileSync(AUDIT_FILE, JSON.stringify({ timestamp: new Date().toISOString(), action, ip, success, ...details }) + '\n', { mode: 0o600 });
}

// ========== Passkeys ==========

function getPasskeys() {
  try { if (fs.existsSync(PASSKEYS_FILE)) return JSON.parse(fs.readFileSync(PASSKEYS_FILE, 'utf8')); } catch {}
  return [];
}
function savePasskeys(p) { fs.writeFileSync(PASSKEYS_FILE, JSON.stringify(p, null, 2), { mode: 0o600 }); }
function saveChallenge(c) { fs.writeFileSync(WEBAUTHN_CHALLENGE_FILE, JSON.stringify({ challenge: c, ts: Date.now() }), { mode: 0o600 }); }
function getChallenge() {
  try {
    if (fs.existsSync(WEBAUTHN_CHALLENGE_FILE)) {
      const { challenge, ts } = JSON.parse(fs.readFileSync(WEBAUTHN_CHALLENGE_FILE, 'utf8'));
      if (Date.now() - ts < 5 * 60 * 1000) return challenge;
    }
  } catch {}
  return null;
}
function clearChallenge() { if (fs.existsSync(WEBAUTHN_CHALLENGE_FILE)) fs.unlinkSync(WEBAUTHN_CHALLENGE_FILE); }

// ========== HTTP Server ==========

function sendJSON(res, status, data) { res.writeHead(status, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(data)); }
function sendHTML(res, status, html) { res.writeHead(status, { 'Content-Type': 'text/html; charset=utf-8' }); res.end(html); }

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => { try { resolve(JSON.parse(body)); } catch(e) { reject(e); } });
    req.on('error', reject);
  });
}

function handleRequest(req, res) {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const ip = req.headers['x-forwarded-for']?.split(',')[0]?.trim() || req.socket.remoteAddress;

  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }

  const p = url.pathname;

  // ---- Status ----
  if (p === '/auth/status' || p === '/status') {
    const session = getSession();
    sendJSON(res, 200, { hasPassword: hasPassword(), hasSession: !!session, sessionExpiresAt: session?.expiresAt || null });
    return;
  }

  // ---- Dashboard ----
  if (p === '/auth' || p === '/auth/' || p === '/' || p === '') {
    const session = getSession();
    const hasPwd = hasPassword();
    const passkeys = getPasskeys();
    const rateLimit = checkRateLimit(ip);

    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Max Auth</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { box-sizing: border-box; }
    body { font-family: system-ui, sans-serif; max-width: 420px; margin: 50px auto; padding: 20px; background: #0f0f0f; color: #fff; }
    h1 { font-size: 1.5em; margin-bottom: 0.3em; }
    .card { background: #1a1a1a; border-radius: 12px; padding: 24px; }
    input { width: 100%; padding: 12px; border: 1px solid #333; border-radius: 8px; background: #0f0f0f; color: #fff; font-size: 16px; margin-top: 8px; }
    button { width: 100%; padding: 12px; border: none; border-radius: 8px; color: #fff; font-size: 16px; cursor: pointer; margin-top: 10px; }
    .btn-bio    { background: #2563eb; } .btn-bio:hover    { background: #1d4ed8; }
    .btn-pwd    { background: #374151; } .btn-pwd:hover    { background: #4b5563; }
    .btn-reg    { background: #7c3aed; } .btn-reg:hover    { background: #6d28d9; }
    .btn-danger { background: #dc2626; } .btn-danger:hover { background: #b91c1c; }
    button:disabled { background: #555; cursor: not-allowed; }
    .msg     { margin-top: 10px; font-size: 14px; display: none; }
    .error   { color: #f87171; }
    .success { color: #4ade80; }
    .info    { color: #9ca3af; }
    .status  { font-size: 13px; color: #9ca3af; margin-bottom: 16px; }
    .divider { text-align: center; color: #4b5563; margin: 16px 0; font-size: 13px; }
    .section-title { font-size: 12px; font-weight: 600; color: #6b7280; margin-top: 20px; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.06em; }
    .passkey-item { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #2a2a2a; font-size: 13px; }
    .passkey-date { color: #4b5563; font-size: 11px; }
    .del-btn { background: none; border: none; color: #f87171; cursor: pointer; padding: 0 4px; width: auto; margin: 0; font-size: 14px; }
  </style>
</head>
<body>
  <div class="card">
    <h1 id="title">🎯 Max Auth</h1>
    <div class="status" id="statusLine"></div>
    <div id="msg" class="msg"></div>

    <div id="app">
      ${!hasPwd ? `
        <div id="noPwdMsg"></div>
        <code id="cliExample" style="background:#333;padding:8px;display:block;border-radius:4px;word-break:break-all;font-size:12px;margin-top:8px">
          node auth-server.js set-password 'your_password'
        </code>
      ` : session ? `
        <div class="section-title" id="sec_session"></div>
        <button class="btn-danger" id="btnLogout" onclick="doLogout()"></button>

        <div class="section-title" id="sec_passkeys"></div>
        <div id="passkeyList">
          ${passkeys.length === 0
            ? `<p id="noPasskeys" style="font-size:13px;color:#6b7280"></p>`
            : passkeys.map(pk => `
              <div class="passkey-item">
                <span>🔑 ${pk.name || 'Passkey'} <span class="passkey-date">${new Date(pk.createdAt).toLocaleDateString()}</span></span>
                <button class="del-btn" onclick="deletePasskey('${pk.id}')">✕</button>
              </div>`).join('')}
        </div>
        <div id="regForm" style="display:none;margin-top:12px;border:1px solid #333;border-radius:8px;padding:12px">
          <div class="section-title" id="sec_confirm_pwd"></div>
          <input type="password" id="regPassword" placeholder="">
          <input type="text" id="passkeyName" placeholder="" style="margin-top:8px">
          <button class="btn-reg" id="btnConfirmReg" onclick="confirmRegisterPasskey()"></button>
          <button class="btn-pwd" id="btnCancelReg" onclick="cancelReg()"></button>
        </div>
        <button class="btn-reg" id="btnShowReg" onclick="showRegForm()"></button>
      ` : `
        ${passkeys.length > 0 ? `<button class="btn-bio" id="btnPasskeyLogin" onclick="doPasskeyLogin()"></button><div class="divider" id="divOr"></div>` : ''}
        <div class="section-title" id="sec_pwd_section"></div>
        <input type="password" id="password" placeholder="" ${rateLimit.allowed ? '' : 'disabled'}>
        <button class="btn-pwd" id="btnLogin" onclick="doPasswordLogin()" ${rateLimit.allowed ? '' : 'disabled'}></button>
        ${!rateLimit.allowed ? `<p class="error" id="blockedMsg"></p>` : ''}
      `}
    </div>
  </div>

  <script>
    // ---- i18n ----
    const lang = navigator.language?.startsWith('pt') ? 'pt' : 'en';
    const T = {
      en: {
        status_auth: (min) => \`✅ Authenticated — expires in \${min} min\`,
        status_req: '🔒 Authentication required',
        sec_session: 'Session', logout: 'Log out',
        sec_passkeys: (n) => \`Registered passkeys (\${n})\`,
        no_passkeys: 'No passkeys yet.',
        add_passkey: '+ Register new passkey',
        pk_name_ph: 'Passkey name (e.g. iPhone, MacBook)',
        confirm_reg: 'Confirm & register', cancel: 'Cancel',
        sec_confirm_pwd: 'Confirm master password',
        pwd_ph: 'Master password', login_btn: 'Sign in with password',
        passkey_btn: '🔑 Sign in with passkey / biometrics',
        divOr: '— or —',
        blocked: (min) => \`Too many attempts. Try again in \${min} min.\`,
        sec_pwd: 'Master password', noPwd: 'Set master password first via CLI:',
        verifying: 'Verifying…', waiting_bio: 'Waiting for biometrics…',
        ok_auth: '✅ Authenticated!', ok_reg: '✅ Passkey registered!',
        remove_confirm: 'Remove this passkey?',
      },
      pt: {
        status_auth: (min) => \`✅ Autenticado — expira em \${min} min\`,
        status_req: '🔒 Autenticação necessária',
        sec_session: 'Sessão', logout: 'Encerrar sessão',
        sec_passkeys: (n) => \`Passkeys cadastradas (\${n})\`,
        no_passkeys: 'Nenhuma passkey ainda.',
        add_passkey: '+ Cadastrar nova passkey',
        pk_name_ph: 'Nome da passkey (ex: iPhone, MacBook)',
        confirm_reg: 'Confirmar e cadastrar', cancel: 'Cancelar',
        sec_confirm_pwd: 'Confirme a senha mestra',
        pwd_ph: 'Senha mestra', login_btn: 'Entrar com senha',
        passkey_btn: '🔑 Entrar com passkey / biometria',
        divOr: '— ou —',
        blocked: (min) => \`Bloqueado. Tente em \${min} min.\`,
        sec_pwd: 'Senha mestra', noPwd: 'Defina a senha mestra primeiro via CLI:',
        verifying: 'Verificando…', waiting_bio: 'Aguardando biometria…',
        ok_auth: '✅ Autenticado!', ok_reg: '✅ Passkey cadastrada!',
        remove_confirm: 'Remover esta passkey?',
      }
    }[lang];

    // Apply i18n
    const $ = id => document.getElementById(id);
    function applyStrings() {
      const statusSession = ${session ? `${Math.round((session.expiresAt - Date.now()) / 60000)}` : 'null'};
      if ($('statusLine')) $('statusLine').textContent = statusSession !== null ? T.status_auth(statusSession) : T.status_req;
      if ($('sec_session'))  $('sec_session').textContent  = T.sec_session;
      if ($('btnLogout'))    $('btnLogout').textContent    = T.logout;
      if ($('sec_passkeys')) $('sec_passkeys').textContent = T.sec_passkeys(${passkeys.length});
      if ($('noPasskeys'))   $('noPasskeys').textContent   = T.no_passkeys;
      if ($('btnShowReg'))   $('btnShowReg').textContent   = T.add_passkey;
      if ($('passkeyName'))  $('passkeyName').placeholder  = T.pk_name_ph;
      if ($('btnConfirmReg')) $('btnConfirmReg').textContent = T.confirm_reg;
      if ($('btnCancelReg')) $('btnCancelReg').textContent = T.cancel;
      if ($('sec_confirm_pwd')) $('sec_confirm_pwd').textContent = T.sec_confirm_pwd;
      if ($('regPassword'))  $('regPassword').placeholder  = T.pwd_ph;
      if ($('sec_pwd_section')) $('sec_pwd_section').textContent = T.sec_pwd;
      if ($('password'))     $('password').placeholder     = T.pwd_ph;
      if ($('btnLogin'))     $('btnLogin').textContent     = T.login_btn;
      if ($('btnPasskeyLogin')) $('btnPasskeyLogin').textContent = T.passkey_btn;
      if ($('divOr'))        $('divOr').textContent        = T.divOr;
      if ($('blockedMsg'))   $('blockedMsg').textContent   = T.blocked(${rateLimit.remaining || 0});
      if ($('noPwdMsg'))     $('noPwdMsg').textContent     = T.noPwd;
    }
    applyStrings();

    const base = window.location.pathname.replace(/\\/$/, '').replace(/\\/auth$/, '') + '/auth';

    function showMsg(text, type = 'error') {
      const el = $('msg');
      el.textContent = text; el.className = 'msg ' + type; el.style.display = 'block';
    }

    // ---- Login ----
    async function doPasswordLogin() {
      const pwd = $('password')?.value;
      showMsg(T.verifying, 'info');
      try {
        const r = await fetch(base + '/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password: pwd }) });
        const d = await r.json();
        if (d.success) { showMsg(T.ok_auth, 'success'); setTimeout(() => location.reload(), 700); }
        else showMsg(d.error || '');
      } catch(e) { showMsg(e.message); }
    }
    $('password')?.addEventListener('keydown', e => { if (e.key === 'Enter') doPasswordLogin(); });

    // ---- Logout ----
    async function doLogout() {
      await fetch(base + '/logout', { method: 'POST' });
      location.reload();
    }

    // ---- Passkey Login ----
    async function doPasskeyLogin() {
      showMsg(T.waiting_bio, 'info');
      try {
        const options = await (await fetch(base + '/passkey/auth-options')).json();
        if (options.error) { showMsg(options.error); return; }
        options.challenge = b64ToBuffer(options.challenge);
        options.allowCredentials = (options.allowCredentials || []).map(c => ({ ...c, id: b64ToBuffer(c.id) }));
        const assertion = await navigator.credentials.get({ publicKey: options });
        const r = await fetch(base + '/passkey/auth-verify', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            id: assertion.id, rawId: bufToB64(assertion.rawId), type: assertion.type,
            response: {
              authenticatorData: bufToB64(assertion.response.authenticatorData),
              clientDataJSON: bufToB64(assertion.response.clientDataJSON),
              signature: bufToB64(assertion.response.signature),
              userHandle: assertion.response.userHandle ? bufToB64(assertion.response.userHandle) : null,
            }
          })
        });
        const d = await r.json();
        if (d.success) { showMsg(T.ok_auth, 'success'); setTimeout(() => location.reload(), 700); }
        else showMsg(d.error || '');
      } catch(e) { showMsg(e.message); }
    }

    // ---- Passkey Register ----
    function showRegForm() {
      $('regForm').style.display = 'block';
      $('btnShowReg').style.display = 'none';
      $('regPassword').focus();
    }
    function cancelReg() {
      $('regForm').style.display = 'none';
      $('btnShowReg').style.display = 'block';
      $('regPassword').value = '';
      $('passkeyName').value = '';
    }
    async function confirmRegisterPasskey() {
      const name = $('passkeyName')?.value?.trim() || 'Passkey';
      const password = $('regPassword')?.value || '';
      showMsg(T.waiting_bio, 'info');
      try {
        const options = await (await fetch(base + '/passkey/reg-options', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ password })
        })).json();
        if (options.error) { showMsg(options.error); return; }
        options.challenge = b64ToBuffer(options.challenge);
        options.user.id = b64ToBuffer(options.user.id);
        if (options.excludeCredentials)
          options.excludeCredentials = options.excludeCredentials.map(c => ({ ...c, id: b64ToBuffer(c.id) }));
        const cred = await navigator.credentials.create({ publicKey: options });
        const r = await fetch(base + '/passkey/reg-verify', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name,
            id: cred.id, rawId: bufToB64(cred.rawId), type: cred.type,
            response: {
              attestationObject: bufToB64(cred.response.attestationObject),
              clientDataJSON: bufToB64(cred.response.clientDataJSON),
            }
          })
        });
        const d = await r.json();
        if (d.success) { showMsg(T.ok_reg, 'success'); setTimeout(() => location.reload(), 900); }
        else showMsg(d.error || '');
      } catch(e) { showMsg(e.message); }
    }

    // ---- Delete Passkey ----
    async function deletePasskey(id) {
      if (!confirm(T.remove_confirm)) return;
      const r = await fetch(base + '/passkey/delete', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id }) });
      const d = await r.json();
      if (d.success) location.reload(); else showMsg(d.error || '');
    }

    // ---- Base64url helpers ----
    function b64ToBuffer(b64) {
      const b = b64.replace(/-/g,'+').replace(/_/g,'/');
      return Uint8Array.from(atob(b), c => c.charCodeAt(0)).buffer;
    }
    function bufToB64(buf) {
      return btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=/g,'');
    }
  </script>
</body>
</html>`;
    sendHTML(res, 200, html);
    return;
  }

  // ---- Password Login ----
  if ((p === '/auth/login' || p === '/login') && req.method === 'POST') {
    readBody(req).then(({ password }) => {
      const rl = checkRateLimit(ip);
      if (!rl.allowed) { auditLog('login', ip, false, { reason: 'rate_limited' }); sendJSON(res, 429, { error: `Rate limited (${rl.remaining}min)` }); return; }
      if (!hasPassword()) { sendJSON(res, 400, { error: 'No password set' }); return; }
      const pwd = getPasswordData();
      const valid = verifyPassword(password, pwd.hash, pwd.salt);
      recordAttempt(ip, valid);
      if (valid) {
        const token = createSession(ip);
        auditLog('login', ip, true);
        sendJSON(res, 200, { success: true, token, expiresAt: Date.now() + SESSION_DURATION_MS });
      } else {
        auditLog('login', ip, false, { reason: 'wrong_password' });
        sendJSON(res, 401, { error: STRINGS.pt.wrong_pwd });
      }
    }).catch(() => sendJSON(res, 400, { error: 'Invalid request' }));
    return;
  }

  // ---- Logout ----
  if ((p === '/auth/logout' || p === '/logout') && req.method === 'POST') {
    clearSession(); auditLog('logout', ip, true); sendJSON(res, 200, { success: true });
    return;
  }

  // ---- Verify token (for external use) ----
  if (p === '/auth/verify' || p === '/verify') {
    const token = (req.headers.authorization || '').replace('Bearer ', '');
    sendJSON(res, isValidSession(token) ? 200 : 401, { valid: isValidSession(token) });
    return;
  }

  // ---- Passkey: Registration Options (requires session + password) ----
  if ((p === '/auth/passkey/reg-options' || p === '/passkey/reg-options') && req.method === 'POST') {
    const session = getSession();
    if (!session) { sendJSON(res, 401, { error: 'Not authenticated' }); return; }

    readBody(req).then(async ({ password }) => {
      // Require master password confirmation even when session is active
      if (!hasPassword()) { sendJSON(res, 400, { error: 'No password set' }); return; }
      const pwd = getPasswordData();
      if (!verifyPassword(password || '', pwd.hash, pwd.salt)) {
        recordAttempt(ip, false);
        auditLog('passkey-reg-attempt', ip, false, { reason: 'wrong_password' });
        sendJSON(res, 401, { error: STRINGS.pt.wrong_pwd }); return;
      }
      try {
        const passkeys = getPasskeys();
        const options = await generateRegistrationOptions({
          rpName: RP_NAME, rpID: RP_ID,
          userID: new TextEncoder().encode('max-user'),
          userName: 'max', userDisplayName: 'Max Auth',
          attestationType: 'none',
          excludeCredentials: passkeys.map(pk => ({ id: pk.credentialID, type: 'public-key' })),
          authenticatorSelection: { userVerification: 'required', residentKey: 'preferred' },
        });
        saveChallenge(options.challenge);
        sendJSON(res, 200, options);
      } catch(e) { sendJSON(res, 500, { error: e.message }); }
    }).catch(() => sendJSON(res, 400, { error: 'Invalid request' }));
    return;
  }

  // ---- Passkey: Registration Verify ----
  if ((p === '/auth/passkey/reg-verify' || p === '/passkey/reg-verify') && req.method === 'POST') {
    if (!getSession()) { sendJSON(res, 401, { error: 'Not authenticated' }); return; }
    readBody(req).then(async ({ name, ...credentialJSON }) => {
      const expectedChallenge = getChallenge();
      if (!expectedChallenge) { sendJSON(res, 400, { error: 'Challenge expired' }); return; }
      try {
        const verification = await verifyRegistrationResponse({
          response: credentialJSON, expectedChallenge, expectedOrigin: RP_ORIGIN, expectedRPID: RP_ID, requireUserVerification: true,
        });
        clearChallenge();
        if (verification.verified && verification.registrationInfo) {
          const { credential } = verification.registrationInfo;
          const passkeys = getPasskeys();
          passkeys.push({
            id: credential.id, credentialID: credential.id,
            credentialPublicKey: Buffer.from(credential.publicKey).toString('base64'),
            counter: credential.counter, name: name || 'Passkey',
            createdAt: new Date().toISOString(), ip,
          });
          savePasskeys(passkeys);
          auditLog('passkey-register', ip, true, { name });
          log(`✓ Passkey registered: ${name}`);
          sendJSON(res, 200, { success: true });
        } else { sendJSON(res, 400, { error: 'Verification failed' }); }
      } catch(e) { log(`Passkey reg error: ${e.message}`); sendJSON(res, 500, { error: e.message }); }
    }).catch(() => sendJSON(res, 400, { error: 'Invalid request' }));
    return;
  }

  // ---- Passkey: Authentication Options ----
  if (p === '/auth/passkey/auth-options' || p === '/passkey/auth-options') {
    (async () => {
      try {
        const passkeys = getPasskeys();
        const options = await generateAuthenticationOptions({
          rpID: RP_ID,
          allowCredentials: passkeys.map(pk => ({ id: pk.credentialID, type: 'public-key' })),
          userVerification: 'required',
        });
        saveChallenge(options.challenge);
        sendJSON(res, 200, options);
      } catch(e) { sendJSON(res, 500, { error: e.message }); }
    })();
    return;
  }

  // ---- Passkey: Authentication Verify ----
  if ((p === '/auth/passkey/auth-verify' || p === '/passkey/auth-verify') && req.method === 'POST') {
    readBody(req).then(async (credentialJSON) => {
      const expectedChallenge = getChallenge();
      if (!expectedChallenge) { sendJSON(res, 400, { error: 'Challenge expired' }); return; }
      const passkeys = getPasskeys();
      const passkey = passkeys.find(pk => pk.id === credentialJSON.id || pk.credentialID === credentialJSON.id);
      if (!passkey) { sendJSON(res, 400, { error: 'Passkey not found' }); return; }
      try {
        const verification = await verifyAuthenticationResponse({
          response: credentialJSON, expectedChallenge, expectedOrigin: RP_ORIGIN, expectedRPID: RP_ID, requireUserVerification: true,
          credential: { id: passkey.credentialID, publicKey: Buffer.from(passkey.credentialPublicKey, 'base64'), counter: passkey.counter },
        });
        clearChallenge();
        if (verification.verified) {
          passkey.counter = verification.authenticationInfo.newCounter;
          savePasskeys(passkeys);
          const token = createSession(ip);
          auditLog('passkey-login', ip, true);
          log(`✓ Passkey login: ${passkey.name}`);
          sendJSON(res, 200, { success: true, token, expiresAt: Date.now() + SESSION_DURATION_MS });
        } else {
          auditLog('passkey-login', ip, false);
          sendJSON(res, 401, { error: 'Biometric verification failed' });
        }
      } catch(e) { log(`Passkey auth error: ${e.message}`); sendJSON(res, 500, { error: e.message }); }
    }).catch(() => sendJSON(res, 400, { error: 'Invalid request' }));
    return;
  }

  // ---- Passkey: Delete ----
  if ((p === '/auth/passkey/delete' || p === '/passkey/delete') && req.method === 'POST') {
    if (!getSession()) { sendJSON(res, 401, { error: 'Not authenticated' }); return; }
    readBody(req).then(({ id }) => {
      let passkeys = getPasskeys().filter(pk => pk.id !== id && pk.credentialID !== id);
      savePasskeys(passkeys);
      auditLog('passkey-delete', ip, true, { id });
      sendJSON(res, 200, { success: true });
    }).catch(() => sendJSON(res, 400, { error: 'Invalid request' }));
    return;
  }

  sendJSON(res, 404, { error: 'Not found' });
}

// ========== CLI ==========

function cliSetPassword(password) {
  if (!password || password.length < 8) { console.error('❌ Password must be at least 8 characters'); process.exit(1); }
  setPassword(password);
  console.log('✅ Master password set');
}

function cliStatus() {
  const hasPwd = hasPassword();
  const session = getSession();
  console.log('\n🎯 Max Auth Status\n==================');
  console.log(`Password set:   ${hasPwd ? '✅ Yes' : '❌ No'}`);
  console.log(`Session active: ${session ? `✅ Yes (expires in ${Math.round((session.expiresAt - Date.now()) / 60000)}min)` : '❌ No'}`);
  console.log(`Passkeys:       ${getPasskeys().length}`);
  console.log(`Port:           ${PORT}\n`);
}

// ========== Main ==========

const server = http.createServer(handleRequest);

if (require.main === module) {
  const args = process.argv.slice(2);
  if (args[0] === 'set-password') {
    if (!args[1]) { console.error('Usage: node auth-server.js set-password <password>'); process.exit(1); }
    cliSetPassword(args[1]); process.exit(0);
  }
  if (args[0] === 'status') { cliStatus(); process.exit(0); }
  ensureConfigDir();
  server.listen(PORT, '127.0.0.1', () => {
    log(`Max Auth running on http://127.0.0.1:${PORT}`);
    log(`Tailscale: https://${RP_ID}/auth`);
  });
}

module.exports = { server, checkAuthStatus: () => getSession() !== null, getSession, isValidSession };
