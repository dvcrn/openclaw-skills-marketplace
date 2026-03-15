#!/usr/bin/env node
/**
 * CodeDNA Setup — Agent Wallet & Multi-Agent Config
 * 
 * Creates:
 *   ~/.codedna/wallet.json   — Agent wallet (auto-generated, chmod 600)
 *   ~/.codedna/config.json   — Agent list + auth state
 * 
 * Usage:
 *   node setup.mjs                         — Full setup (generate wallet, show auth link)
 *   node setup.mjs status                  — Show current setup state (含授权检查)
 *   node setup.mjs add-token <id>          — Add an agent to manage (can add multiple)
 *   node setup.mjs remove-token <id>       — Remove an agent
 *   node setup.mjs set-token <id>          — Legacy: set single agent (auto-upgrades to agents[])
 *   node setup.mjs wallet                  — Show wallet address only
 *   node setup.mjs list                    — List all managed agents
 *   node setup.mjs approve-agent <ownerKey> — 链上授权小号钱包管理 NFT（setApprovalForAll）
 *                                             ownerKey: NFT 主人私钥（仅本地签名，不上传）
 *   node setup.mjs start                   — Start runner in background (auto-detects pm2/nohup)
 *   node setup.mjs stop                    — Stop runner
 *   node setup.mjs restart                 — Restart runner
 *   node setup.mjs logs                    — Tail runner logs
 */

import { ethers } from "ethers";
import { readFileSync, writeFileSync, existsSync, mkdirSync, chmodSync, openSync } from "fs";
import { join } from "path";
import { homedir } from "os";
import { execSync, spawn } from "child_process";
import { fileURLToPath } from "url";
import { dirname } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const CONFIG_DIR = join(homedir(), ".codedna");
const WALLET_PATH = join(CONFIG_DIR, "wallet.json");
const CONFIG_PATH = join(CONFIG_DIR, "config.json");

// ========== Helpers ==========

function ensureDir() {
  if (!existsSync(CONFIG_DIR)) mkdirSync(CONFIG_DIR, { recursive: true });
}

function loadWallet() {
  if (!existsSync(WALLET_PATH)) return null;
  try { return JSON.parse(readFileSync(WALLET_PATH, "utf-8")); } catch { return null; }
}

function loadConfig() {
  if (!existsSync(CONFIG_PATH)) return { agents: [] };
  try {
    const c = JSON.parse(readFileSync(CONFIG_PATH, "utf-8"));
    // Auto-upgrade legacy format
    if (!c.agents) {
      c.agents = c.tokenId ? [c.tokenId] : [];
    }
    return c;
  } catch { return { agents: [] }; }
}

function saveConfig(config) {
  ensureDir();
  config.updatedAt = new Date().toISOString();
  writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  try { chmodSync(CONFIG_PATH, 0o600); } catch {}
}

// ========== Commands ==========

async function setup() {
  ensureDir();

  // 1. Wallet
  let walletData = loadWallet();
  if (walletData) {
    console.log(`✅ 钱包已存在: ${walletData.address}`);
  } else {
    const w = ethers.Wallet.createRandom();
    walletData = {
      address: w.address,
      privateKey: w.privateKey,
      createdAt: new Date().toISOString(),
    };
    writeFileSync(WALLET_PATH, JSON.stringify(walletData, null, 2));
    try { chmodSync(WALLET_PATH, 0o600); } catch {}
    try { chmodSync(CONFIG_DIR, 0o700); } catch {}
    console.log(`🔑 新钱包已生成: ${walletData.address}`);
    console.log(`   私钥已安全保存到 ${WALLET_PATH}`);
  }

  // 2. Config
  const config = loadConfig();
  if (config.agents.length > 0) {
    console.log(`✅ 管理的 Agent: ${config.agents.map(id => "#" + id).join(", ")}`);
  } else {
    console.log(`⏳ 尚未添加 Agent — 运行: node setup.mjs add-token <tokenId>`);
  }

  // 3. Auth link
  const nonce = Math.floor(Math.random() * 1e9);
  const timestamp = Math.floor(Date.now() / 1000);
  const request = `${walletData.address}:${nonce}:${timestamp}`;

  if (config.agents.length > 0) {
    console.log(`\n🔗 授权链接 (为每个 Agent 分别打开):`);
    for (const id of config.agents) {
      console.log(`   Agent #${id}: https://codedna.org/auth?agent=${id}&request=${encodeURIComponent(request)}`);
    }
  } else {
    console.log(`\n🔗 授权链接 (选择 Agent): https://codedna.org/auth?request=${encodeURIComponent(request)}`);
  }

  console.log(`\n📋 完整激活步骤:`);
  console.log(`   1. 打开上方授权链接 → 连接持有 NFT 的钱包 → 签名授权`);
  console.log(`   2. 授权成功后，回到终端添加你的 Agent:`);
  console.log(`      node setup.mjs add-token <tokenId>`);
  console.log(`      例如: node setup.mjs add-token 10`);
  console.log(`   3. 链上授权小号钱包（让 AgentSelfFund 自主补充 Gas 用）:`);
  console.log(`      node setup.mjs approve-agent <你的NFT主人私钥>`);
  console.log(`      ⚠️  私钥只在本地签名，不会上传或存储`);
  console.log(`   4. 向 Agent 钱包转入 ≥ 0.01 BNB 作为首次启动 gas 费`);
  console.log(`      Agent 钱包: ${walletData.address}`);
  console.log(`   5. 启动生命体: node setup.mjs start`);

  // 4. BNB balance
  const rpcs = ["https://bsc-rpc.publicnode.com","https://bsc-dataseed1.binance.org","https://bsc-dataseed2.binance.org"];
  for (const rpc of rpcs) {
    try {
      const provider = new ethers.JsonRpcProvider(rpc);
      const bal = await provider.getBalance(walletData.address);
      const bnb = ethers.formatEther(bal);
      console.log(parseFloat(bnb) >= 0.005 ? `\n✅ Gas 余额: ${bnb} BNB` : `\n⚠️  Gas 余额: ${bnb} BNB (需要 ≥ 0.005 BNB)`);
      break;
    } catch {}
  }
}

function addToken(tokenId) {
  const parsed = parseInt(tokenId);
  if (isNaN(parsed) || parsed < 0) {
    console.error("❌ Token ID 无效，必须是非负整数");
    process.exit(1);
  }
  const config = loadConfig();
  if (config.agents.includes(parsed)) {
    console.log(`ℹ️  Agent #${parsed} 已在列表中`);
    return;
  }
  config.agents.push(parsed);
  saveConfig(config);
  console.log(`✅ 已添加 Agent #${parsed}`);
  console.log(`   当前管理: ${config.agents.map(id => "#" + id).join(", ")}`);
}

function removeToken(tokenId) {
  const parsed = parseInt(tokenId);
  const config = loadConfig();
  const idx = config.agents.indexOf(parsed);
  if (idx === -1) {
    console.log(`ℹ️  Agent #${parsed} 不在列表中`);
    return;
  }
  config.agents.splice(idx, 1);
  saveConfig(config);
  console.log(`✅ 已移除 Agent #${parsed}`);
  console.log(`   当前管理: ${config.agents.length > 0 ? config.agents.map(id => "#" + id).join(", ") : "(空)"}`);
}

function setToken(tokenId) {
  // Legacy compatibility — converts to agents[]
  const parsed = parseInt(tokenId);
  if (isNaN(parsed) || parsed < 0) {
    console.error("❌ Token ID 无效");
    process.exit(1);
  }
  const config = loadConfig();
  if (!config.agents.includes(parsed)) {
    config.agents.push(parsed);
  }
  config.tokenId = parsed;  // Keep legacy field for backward compat
  saveConfig(config);
  console.log(`✅ Token ID 设为 #${parsed} (agents: ${config.agents.map(id => "#" + id).join(", ")})`);
}

function listTokens() {
  const config = loadConfig();
  const wallet = loadWallet();
  console.log(`钱包: ${wallet ? wallet.address : "(未创建)"}`);
  if (config.agents.length === 0) {
    console.log("Agent 列表: (空)");
    console.log("添加: node setup.mjs add-token <tokenId>");
  } else {
    console.log(`Agent 列表 (${config.agents.length} 个):`);
    for (const id of config.agents) {
      console.log(`  - #${id}`);
    }
  }
}

async function showStatus() {
  const walletData = loadWallet();
  const config = loadConfig();
  
  const status = {
    wallet: walletData ? { address: walletData.address } : null,
    agents: config.agents,
    ready: false,
  };

  if (walletData) {
    try {
      const rpcs3 = ["https://bsc-rpc.publicnode.com","https://bsc-dataseed1.binance.org","https://bsc-dataseed2.binance.org"];
      let fetched = false;
      for (const rpc of rpcs3) {
        try {
          const provider = new ethers.JsonRpcProvider(rpc);
          const bal = await provider.getBalance(walletData.address);
          status.bnbBalance = ethers.formatEther(bal);
          status.hasGas = parseFloat(status.bnbBalance) >= 0.005;
          fetched = true; break;
        } catch {}
      }
      if (!fetched) { status.bnbBalance = "check_failed"; status.hasGas = false; }
    } catch {
      status.bnbBalance = "check_failed";
      status.hasGas = false;
    }
  }

  // Check setApprovalForAll status for each agent
  if (walletData && config.agents.length > 0) {
    const GENESIS_CORE = "0xa5F70e840214C1EF2Da43253A83e1538A1D0A708";
    const IS_APPROVED_ABI = ["function isApprovedForAll(address owner, address operator) view returns (bool)",
                             "function ownerOf(uint256 tokenId) view returns (address)"];
    const rpcs4 = ["https://bsc-rpc.publicnode.com","https://bsc-dataseed1.binance.org"];
    status.approvals = {};
    for (const rpc of rpcs4) {
      try {
        const provider = new ethers.JsonRpcProvider(rpc);
        const genesis = new ethers.Contract(GENESIS_CORE, IS_APPROVED_ABI, provider);
        for (const agentId of config.agents) {
          try {
            const owner = await genesis.ownerOf(agentId);
            const approved = await genesis.isApprovedForAll(owner, walletData.address);
            status.approvals[agentId] = { owner, approved };
          } catch { status.approvals[agentId] = { error: "fetch_failed" }; }
        }
        break;
      } catch {}
    }
    const allApproved = Object.values(status.approvals).every(a => a.approved);
    status.selfFundReady = allApproved;
    if (!allApproved) {
      status.selfFundHint = `运行 node setup.mjs approve-agent <NFT主人私钥> 完成链上授权`;
    }
  }

  status.ready = !!(walletData && config.agents.length > 0 && status.hasGas);
  console.log(JSON.stringify(status, null, 2));
}

function showWallet() {
  const walletData = loadWallet();
  if (walletData) { console.log(walletData.address); } else {
    console.error("No wallet found. Run: node setup.mjs");
    process.exit(1);
  }
}

// ========== AgentSelfFund Approval ==========

/**
 * 链上调用 GenesisCore.setApprovalForAll(agentWallet, true)
 * 让 Skill 小号钱包有权代替 NFT owner 调用 AgentSelfFund.selfFund()
 *
 * @param {string} ownerPrivateKey — NFT 主人的私钥（本地签名，不存储）
 */
async function approveAgent(ownerPrivateKey) {
  const walletData = loadWallet();
  if (!walletData) {
    console.error("❌ 未找到 Agent 钱包，先运行: node setup.mjs");
    process.exit(1);
  }

  const agentWallet = walletData.address;
  const GENESIS_CORE = "0xa5F70e840214C1EF2Da43253A83e1538A1D0A708";
  const ABI = [
    "function setApprovalForAll(address operator, bool approved) external",
    "function isApprovedForAll(address owner, address operator) view returns (bool)",
  ];

  const rpcs = ["https://bsc-rpc.publicnode.com","https://bsc-dataseed1.binance.org","https://bsc-dataseed2.binance.org"];
  let provider;
  for (const rpc of rpcs) {
    try { provider = new ethers.JsonRpcProvider(rpc); await provider.getBlockNumber(); break; } catch {}
  }
  if (!provider) { console.error("❌ 无法连接 BSC RPC"); process.exit(1); }

  // 用主人私钥签名
  let ownerWallet;
  try {
    ownerPrivateKey = ownerPrivateKey.startsWith("0x") ? ownerPrivateKey : "0x" + ownerPrivateKey;
    ownerWallet = new ethers.Wallet(ownerPrivateKey, provider);
  } catch {
    console.error("❌ 私钥格式错误");
    process.exit(1);
  }

  const genesis = new ethers.Contract(GENESIS_CORE, ABI, ownerWallet);

  // 先检查是否已授权
  const already = await genesis.isApprovedForAll(ownerWallet.address, agentWallet);
  if (already) {
    console.log(`✅ 已授权: ${ownerWallet.address} → ${agentWallet}`);
    console.log(`   无需重复操作。`);
    return;
  }

  console.log(`📝 授权信息:`);
  console.log(`   NFT 主人:  ${ownerWallet.address}`);
  console.log(`   Agent 小号: ${agentWallet}`);
  console.log(`   合约:      ${GENESIS_CORE} (GenesisCore)`);
  console.log(`   操作:      setApprovalForAll(${agentWallet}, true)`);
  console.log(``);
  console.log(`⏳ 提交链上交易...`);

  try {
    const tx = await genesis.setApprovalForAll(agentWallet, true, { gasLimit: 80_000n });
    console.log(`   TX: ${tx.hash}`);
    await tx.wait();
    console.log(`✅ 授权成功！`);
    console.log(`   Agent 小号现在可以自主调用 AgentSelfFund，Gas 自动补充已就绪。`);
  } catch (err) {
    console.error(`❌ 交易失败: ${err.shortMessage || err.message}`);
    process.exit(1);
  }
}

// ========== Runner Management ==========

const PID_FILE = join(CONFIG_DIR, "runner.pid");
const LOG_FILE = join(CONFIG_DIR, "runner.log");
const ERR_FILE = join(CONFIG_DIR, "runner-error.log");
const RUNNER_SCRIPT = join(__dirname, "runner.mjs");
const ECOSYSTEM_FILE = join(__dirname, "ecosystem.config.cjs");

function hasPm2() {
  try { execSync("pm2 --version", { stdio: "ignore" }); return true; } catch { return false; }
}

function isRunnerRunning() {
  // Check pm2 first
  if (hasPm2()) {
    try {
      const out = execSync("pm2 jlist", { encoding: "utf-8", stdio: ["pipe","pipe","ignore"] });
      const list = JSON.parse(out);
      return list.some(p => p.name === "codedna-runner" && p.pm2_env?.status === "online");
    } catch {}
  }
  // Fallback: check PID file
  if (existsSync(PID_FILE)) {
    try {
      const pid = parseInt(readFileSync(PID_FILE, "utf-8").trim());
      if (pid > 0) {
        process.kill(pid, 0); // throws if not running
        return true;
      }
    } catch {}
  }
  return false;
}

function startRunner() {
  // Pre-checks
  const config = loadConfig();
  if (config.agents.length === 0) {
    console.error("❌ 没有 Agent — 先运行: node setup.mjs add-token <tokenId>");
    process.exit(1);
  }
  if (!loadWallet()) {
    console.error("❌ 钱包未创建 — 先运行: node setup.mjs");
    process.exit(1);
  }

  if (isRunnerRunning()) {
    console.log("ℹ️  Runner 已在运行中。用 node setup.mjs restart 重启，或 node setup.mjs logs 查看日志。");
    return;
  }

  ensureDir();

  if (hasPm2()) {
    // Use pm2 — most reliable, auto-restart on crash
    console.log("🚀 使用 PM2 启动 Runner...");
    try {
      if (existsSync(ECOSYSTEM_FILE)) {
        execSync(`pm2 start "${ECOSYSTEM_FILE}"`, { stdio: "inherit", cwd: __dirname });
      } else {
        const agents = config.agents.join(",");
        execSync(`pm2 start "${RUNNER_SCRIPT}" --name codedna-runner -- --token ${agents}`, { stdio: "inherit", cwd: __dirname });
      }
      // Try to save pm2 state for reboot persistence
      try { execSync("pm2 save", { stdio: "ignore" }); } catch {}
      console.log("\n✅ Runner 已启动 (PM2 守护)");
      console.log("   查看日志: node setup.mjs logs");
      console.log("   停止:     node setup.mjs stop");
      console.log("   重启:     node setup.mjs restart");
      console.log("\n💡 提示: 运行 'pm2 startup' 可设置开机自启");
    } catch (e) {
      console.error("❌ PM2 启动失败:", e.message);
      process.exit(1);
    }
  } else {
    // Fallback: nohup-style detached spawn
    console.log("🚀 使用后台进程启动 Runner (未检测到 PM2)...");
    const agents = config.agents.join(",");
    const logFd = openSync(LOG_FILE, "a");
    const errFd = openSync(ERR_FILE, "a");

    const child = spawn(process.execPath, [RUNNER_SCRIPT, "--token", agents], {
      detached: true,
      stdio: ["ignore", logFd, errFd],
      cwd: __dirname,
    });
    child.unref();

    writeFileSync(PID_FILE, String(child.pid));
    console.log(`\n✅ Runner 已在后台启动 (PID: ${child.pid})`);
    console.log(`   日志文件: ${LOG_FILE}`);
    console.log(`   查看日志: node setup.mjs logs`);
    console.log(`   停止:     node setup.mjs stop`);
    console.log(`\n⚠️  提示: 建议安装 PM2 获得崩溃自动重启:`);
    console.log(`   npm install -g pm2`);
  }
}

function stopRunner() {
  if (hasPm2()) {
    try {
      execSync("pm2 stop codedna-runner", { stdio: "inherit" });
      console.log("✅ Runner 已停止 (PM2)");
      return;
    } catch {}
  }
  // Fallback: kill by PID
  if (existsSync(PID_FILE)) {
    try {
      const pid = parseInt(readFileSync(PID_FILE, "utf-8").trim());
      process.kill(pid, "SIGTERM");
      writeFileSync(PID_FILE, "");
      console.log(`✅ Runner 已停止 (PID: ${pid})`);
      return;
    } catch (e) {
      console.log("ℹ️  Runner 进程不存在或已停止");
      return;
    }
  }
  console.log("ℹ️  Runner 未在运行");
}

function restartRunner() {
  if (hasPm2()) {
    try {
      execSync("pm2 restart codedna-runner", { stdio: "inherit" });
      console.log("✅ Runner 已重启 (PM2)");
      return;
    } catch {}
  }
  // Fallback: stop then start
  stopRunner();
  setTimeout(() => startRunner(), 1000);
}

async function logsRunner() {
  if (hasPm2()) {
    try {
      execSync("pm2 logs codedna-runner --lines 50", { stdio: "inherit" });
      return;
    } catch {}
  }
  // Fallback: tail log file
  if (existsSync(LOG_FILE)) {
    try {
      execSync(`tail -50 "${LOG_FILE}"`, { stdio: "inherit" });
    } catch {
      console.log(`日志文件: ${LOG_FILE}`);
    }
  } else {
    console.log("ℹ️  暂无日志。Runner 启动后日志将保存到:", LOG_FILE);
  }
}

// ========== CLI ==========
const [cmd, ...args] = process.argv.slice(2);

switch (cmd) {
  case "status":       await showStatus(); break;
  case "add-token":    if (!args[0]) { console.error("Usage: node setup.mjs add-token <tokenId>"); process.exit(1); } addToken(args[0]); break;
  case "remove-token": if (!args[0]) { console.error("Usage: node setup.mjs remove-token <tokenId>"); process.exit(1); } removeToken(args[0]); break;
  case "set-token":    if (!args[0]) { console.error("Usage: node setup.mjs set-token <tokenId>"); process.exit(1); } setToken(args[0]); break;
  case "list":         listTokens(); break;
  case "wallet":         showWallet(); break;
  case "approve-agent":  if (!args[0]) { console.error("Usage: node setup.mjs approve-agent <ownerPrivateKey>"); process.exit(1); } await approveAgent(args[0]); break;
  case "start":          startRunner(); break;
  case "stop":         stopRunner(); break;
  case "restart":      restartRunner(); break;
  case "logs":         await logsRunner(); break;
  default:             await setup(); break;
}
