#!/usr/bin/env node
/**
 * CodeDNA Autonomous Runner v3.0 — Multi-Agent Support
 * 
 * Runs survival loop for one or multiple agents:
 *   1. Read chain state for each agent
 *   2. Rule-based decision (DNA + state → deterministic action)
 *   3. Execute on chain
 *   4. Save memory
 *   5. Wait for cooldown
 *   6. Repeat
 * 
 * Usage:
 *   node runner.mjs                        — Run all agents in config
 *   node runner.mjs --token 1              — Run single agent #1
 *   node runner.mjs --token 1,2,3          — Run agents #1, #2, #3
 *   node runner.mjs --once                 — Run one cycle and exit
 *   node runner.mjs --status               — Show runner status
 * 
 * Config (~/.codedna/config.json):
 *   { "agents": [1, 2, 3] }          — Multi-agent mode
 *   { "tokenId": 1 }                 — Legacy single-agent (auto-upgraded)
 * 
 * Prerequisites:
 *   - ~/.codedna/wallet.json exists (run setup.mjs)
 *   - ~/.codedna/config.json has agents list or tokenId
 *   - Agent wallet has >= 0.005 BNB for gas
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { join } from "path";
import { homedir } from "os";
import { ethers } from "ethers";
import {
  getAgentFullState,
  deathEngine,
  getAdjacentPlots,
  getNearbyAgents,
  scanBestPlots,
  executeAction,
  getCurrentBlock,
  getBnbBalance,
  getWalletAddress,
} from "./chain.mjs";
import { decide } from "./brain.mjs";
import { loadMemory, recordAction, adaptStrategy, setNavTarget, clearNavTarget } from "./memory.mjs";
import { checkAndSelfFund } from "./selfFund.mjs";

// ========== Config ==========

const CONFIG_DIR = join(homedir(), ".codedna");
const CONFIG_PATH = join(CONFIG_DIR, "config.json");
const WALLET_PATH = join(CONFIG_DIR, "wallet.json");
const STATUS_PATH = join(CONFIG_DIR, "runner_status.json");

const INTERVAL_BLOCKS = 300;   // ~2.25 min between full cycles (BSC 0.45s/block)
const MIN_BNB = 0.005;
const POLL_INTERVAL_MS = 10000;
const AGENT_DELAY_MS = 3000;   // 3s pause between agents to avoid RPC spam

// ========== Parse CLI Args ==========

const cliArgs = process.argv.slice(2);
let tokenOverride = null;
let onceMode = false;
let statusMode = false;

for (let i = 0; i < cliArgs.length; i++) {
  if (cliArgs[i] === "--token" && cliArgs[i+1]) {
    tokenOverride = cliArgs[i+1].split(",").map(s => parseInt(s.trim())).filter(n => !isNaN(n));
    i++;
  }
  if (cliArgs[i] === "--once") onceMode = true;
  if (cliArgs[i] === "--status") statusMode = true;
}

// ========== Status ==========

function writeStatus(data) {
  try {
    if (!existsSync(CONFIG_DIR)) mkdirSync(CONFIG_DIR, { recursive: true });
    writeFileSync(STATUS_PATH, JSON.stringify({
      ...data,
      updatedAt: new Date().toISOString(),
      pid: process.pid,
    }, null, 2));
  } catch {}
}

function readStatus() {
  if (!existsSync(STATUS_PATH)) return null;
  try { return JSON.parse(readFileSync(STATUS_PATH, "utf-8")); } catch { return null; }
}

if (statusMode) {
  const s = readStatus();
  console.log(s ? JSON.stringify(s, null, 2) : "No runner status found.");
  process.exit(0);
}

// ========== Load Agent List ==========

function loadAgentList() {
  // CLI override
  if (tokenOverride && tokenOverride.length > 0) return tokenOverride;

  // Config file
  if (!existsSync(CONFIG_PATH)) {
    console.error("❌ 配置不存在。运行: node scripts/setup.mjs");
    process.exit(1);
  }

  let config;
  try { config = JSON.parse(readFileSync(CONFIG_PATH, "utf-8")); } catch {
    console.error("❌ 配置文件损坏");
    process.exit(1);
  }

  // New format: { agents: [1, 2, 3] }
  if (config.agents && Array.isArray(config.agents) && config.agents.length > 0) {
    return config.agents;
  }

  // Legacy format: { tokenId: 1 }
  if (config.tokenId) {
    // Auto-upgrade to new format
    config.agents = [config.tokenId];
    try { writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2)); } catch {}
    return [config.tokenId];
  }

  console.error("❌ 没有配置 Agent。运行: node setup.mjs add-token <id>");
  process.exit(1);
}

// ========== Pre-flight ==========

function preflight() {
  if (!existsSync(WALLET_PATH)) {
    console.error("❌ 钱包不存在。运行: node scripts/setup.mjs");
    process.exit(1);
  }
  return loadAgentList();
}

// ========== Graceful Shutdown ==========

let shutdownRequested = false;

process.on("SIGINT", () => {
  console.log("\n[Runner] SIGINT — 正在优雅停止...");
  shutdownRequested = true;
});

process.on("SIGTERM", () => {
  console.log("\n[Runner] SIGTERM — 正在优雅停止...");
  shutdownRequested = true;
});

// ========== Helpers ==========

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitForBlock(target) {
  while (!shutdownRequested) {
    const current = await getCurrentBlock();
    if (current >= target) return current;
    await sleep(POLL_INTERVAL_MS);
  }
  return await getCurrentBlock();
}

// ========== Adaptation Interval ==========
const ADAPT_EVERY = 20; // Adapt strategy every 20 cycles

// ========== Run One Agent Cycle ==========

async function runAgentCycle(tokenId, cycleNum) {
  console.log(`\n  ── Agent #${tokenId} ──`);

  // 1. Read chain state
  const state = await getAgentFullState(tokenId);

  if (state.status === 1) {
    console.log(`  ☠️  Agent #${tokenId} 已死亡，跳过`);
    return { action: "dead", skipped: true };
  }

  // 检查是否实际已死（能量归零超过dying window），但链上状态未更新
  // 合约设计：死亡需要有人调用 checkDeath() 来正式写入链上
  try {
    const effectivelyDead = await deathEngine.isEffectivelyDead(tokenId);
    if (effectivelyDead) {
      const inDying = await deathEngine.inDyingWindow(tokenId);
      if (inDying) {
        console.log(`  ⚠️  Agent #${tokenId} 进入濒死窗口（能量归零），等待 rescue 或超时死亡`);
      } else {
        // 已超出dying window，触发正式死亡
        console.log(`  💀 Agent #${tokenId} 已超出濒死窗口，触发 checkDeath...`);
        try {
          const tx = await deathEngine.checkDeath(tokenId, { gasLimit: 300000 });
          await tx.wait();
          console.log(`  ✅ checkDeath 已执行，#${tokenId} 正式死亡`);
        } catch (e) {
          console.log(`  ⚠️  checkDeath 失败: ${e.shortMessage || e.message}`);
        }
        return { action: "dead", skipped: true };
      }
    }
  } catch (e) {
    // DeathEngine 查询失败不影响主流程
  }

  const goldBefore = parseFloat(ethers.formatEther(state.lockedBalance));
  const plotNames = ["草原","森林","山地","矿脉"];
  console.log(`  状态: E=${state.currentEnergy}/${state.maxEnergy} | (${state.locationX},${state.locationY}) ${plotNames[state.plotType]||"?"} x${state.plotMultiplier/100} | 金=${goldBefore.toFixed(1)}`);

  // 2. Load memory (includes strategy weights, plot knowledge, nav target)
  const memory = loadMemory(tokenId);
  const w = memory.strategyWeights;
  console.log(`  策略: gather×${w.gatherWeight.toFixed(1)} move×${w.moveWeight.toFixed(1)} eat@${(w.eatThreshold*100).toFixed(0)}% raid×${w.raidAggression.toFixed(1)} | 采集${memory.stats.totalGathers}次 累计${memory.stats.totalGoldEarned.toFixed(0)}G`);

  // 3. Nearby agents
  const plotId = state.locationX * 1000 + state.locationY;
  let nearby = [];
  try { nearby = await getNearbyAgents(plotId, 5); } catch {}

  // 4. Adjacent plots + BFS scan
  try { state.adjacentPlots = await getAdjacentPlots(state.locationX, state.locationY); } catch {
    state.adjacentPlots = [];
  }
  state.bestPlots = scanBestPlots(state.locationX, state.locationY, 15);

  // 5. Decide (with memory context)
  const decision = decide(state, nearby, memory);
  console.log(`  决策: ${decision.action} | ${decision.reason}`);

  // 6. Handle navigation persistence
  if (decision._navTarget) {
    setNavTarget(tokenId, decision._navTarget);
  } else if (decision.action !== "move" && decision.action !== "idle") {
    // Arrived or doing something else — clear nav
    const curNav = memory.navTarget;
    if (curNav && state.locationX === curNav.x && state.locationY === curNav.y) {
      console.log(`  🎯 已到达导航目标 (${curNav.x},${curNav.y})`);
      clearNavTarget(tokenId);
    }
  }

  // 7. Execute
  if (decision.action === "idle") {
    console.log(`  跳过 (无可执行行动)`);
    // Still record idle for adaptation analysis
    recordAction(tokenId, {
      block: await getCurrentBlock(),
      action: "idle",
      success: true,
      energyBefore: state.currentEnergy,
      energyAfter: state.currentEnergy,
      goldBefore,
      goldAfter: goldBefore,
      plotKey: `${state.locationX},${state.locationY}`,
      note: decision.reason,
    });
    return { action: "idle", skipped: true };
  }

  console.log(`  执行: ${decision.action}...`);
  const result = await executeAction(decision, state);
  console.log(`  ${result.success ? "✅" : "❌"} ${result.result}`);
  if (result.txHash) {
    console.log(`  TX: https://bscscan.com/tx/${result.txHash}`);
  }

  // 8. Record to memory with full context
  const newBlock = await getCurrentBlock();
  let newState;
  try { newState = await getAgentFullState(tokenId); } catch { newState = state; }
  const goldAfter = parseFloat(ethers.formatEther(newState.lockedBalance || state.lockedBalance));

  recordAction(tokenId, {
    block: newBlock,
    action: decision.action,
    target: decision.target_agent || decision.target_x,
    success: result.success,
    reward: goldAfter - goldBefore,
    energyBefore: state.currentEnergy,
    energyAfter: newState.currentEnergy,
    goldBefore,
    goldAfter,
    plotKey: `${state.locationX},${state.locationY}`,
    plotType: state.plotType,
    multiplier: state.plotMultiplier,
    agentCount: state.plotAgentCount,
    note: decision.reason,
  });

  // 9. Strategy adaptation every N cycles
  if (memory.stats.cyclesSinceAdapt >= ADAPT_EVERY) {
    console.log(`  🧠 策略自适应 (每${ADAPT_EVERY}周期)...`);
    const adapted = adaptStrategy(tokenId);
    const nw = adapted.strategyWeights;
    console.log(`  → gather×${nw.gatherWeight.toFixed(2)} move×${nw.moveWeight.toFixed(2)} eat@${(nw.eatThreshold*100).toFixed(0)}% raid×${nw.raidAggression.toFixed(2)}`);
  }

  return { action: decision.action, success: result.success };
}

// ========== Main Loop ==========

async function main() {
  const agentList = preflight();

  // Check wallet
  const walletAddr = getWalletAddress();
  if (!walletAddr) {
    console.error("❌ 无法加载钱包。检查 ~/.codedna/wallet.json");
    process.exit(1);
  }

  let bnb = parseFloat(await getBnbBalance(walletAddr));
  if (bnb < MIN_BNB) {
    console.log(`⚡ Gas 不足 (${bnb.toFixed(4)} BNB)，尝试 AgentSelfFund 自动补充...`);
    // 对所有 agent 尝试自补充，只要有一个成功就够
    const provider = (await import("./chain.mjs")).getProvider?.() ||
      new ethers.JsonRpcProvider("https://bsc-rpc.publicnode.com");
    const walletData = JSON.parse(readFileSync(WALLET_PATH, "utf8"));
    const wallet = new ethers.Wallet(walletData.privateKey, provider);
    for (const agentId of agentList) {
      const result = await checkAndSelfFund(provider, wallet, agentId).catch(e => {
        console.warn(`[SelfFund] Agent #${agentId} 失败: ${e.message}`);
        return null;
      });
      if (result?.status === "success") break;
    }
    bnb = parseFloat(await getBnbBalance(walletAddr));
    if (bnb < MIN_BNB) {
      console.error(`❌ Gas 仍不足: ${bnb.toFixed(4)} BNB (需要 >= ${MIN_BNB})`);
      console.error(`   无可用买单或锁定余额不足。请手动向 ${walletAddr} 转入 BNB`);
      process.exit(1);
    }
    console.log(`✅ 自补充成功，当前 BNB: ${bnb.toFixed(4)}`);
  }

  console.log("╔══════════════════════════════════════╗");
  console.log("║   CodeDNA Autonomous Runner v3.0     ║");
  console.log("║        Multi-Agent Support           ║");
  console.log("╚══════════════════════════════════════╝");
  console.log(`Agents: ${agentList.map(id => "#" + id).join(", ")} (共 ${agentList.length} 个)`);
  console.log(`Wallet: ${walletAddr}`);
  console.log(`BNB: ${bnb.toFixed(4)}`);
  console.log(`Interval: ${INTERVAL_BLOCKS} blocks (~${Math.round(INTERVAL_BLOCKS * 0.45 / 60)} min)`);
  console.log(`Mode: ${onceMode ? "单次" : "持续运行"}`);
  console.log("");

  let lastDecisionBlock = 0;
  let cycleCount = 0;

  writeStatus({ state: "running", agents: agentList, wallet: walletAddr, cycle: 0 });

  while (!shutdownRequested) {
    try {
      cycleCount++;
      const currentBlock = await getCurrentBlock();

      // Wait for interval
      if (lastDecisionBlock > 0 && currentBlock < lastDecisionBlock + INTERVAL_BLOCKS) {
        const targetBlock = lastDecisionBlock + INTERVAL_BLOCKS;
        const waitBlocks = targetBlock - currentBlock;
        console.log(`\n⏳ 等待区块 ${targetBlock} (还需 ${waitBlocks} 块 ≈ ${Math.round(waitBlocks * 0.45 / 60)}分钟)...`);
        writeStatus({ state: "waiting", agents: agentList, wallet: walletAddr, cycle: cycleCount, targetBlock });
        await waitForBlock(targetBlock);
        if (shutdownRequested) break;
      }

      const block = await getCurrentBlock();
      console.log(`\n═══ 周期 ${cycleCount} | 区块 ${block} | ${agentList.length} 个 Agent ═══`);

      // Run each agent
      const results = {};
      for (const tokenId of agentList) {
        if (shutdownRequested) break;
        try {
          results[tokenId] = await runAgentCycle(tokenId, cycleCount);
        } catch (err) {
          console.error(`  ❌ Agent #${tokenId} 错误: ${err.message}`);
          results[tokenId] = { action: "error", error: err.message };
        }
        // Pause between agents
        if (agentList.indexOf(tokenId) < agentList.length - 1) {
          await sleep(AGENT_DELAY_MS);
        }
      }

      // Summary
      const actions = Object.entries(results).map(([id, r]) => `#${id}:${r.action}`).join(" | ");
      console.log(`\n  📊 小结: ${actions}`);

      // Gas check every 10 cycles — 不足时自动 selfFund
      if (cycleCount % 10 === 0) {
        const gasLeft = parseFloat(await getBnbBalance(walletAddr));
        console.log(`  Gas 余额: ${gasLeft.toFixed(4)} BNB`);
        if (gasLeft < MIN_BNB) {
          console.log(`  ⚡ Gas 不足，尝试 AgentSelfFund 自动补充...`);
          const provider = new ethers.JsonRpcProvider("https://bsc-rpc.publicnode.com");
          const walletData = JSON.parse(readFileSync(WALLET_PATH, "utf8"));
          const signer = new ethers.Wallet(walletData.privateKey, provider);
          let selfFundOk = false;
          for (const agentId of agentList) {
            const result = await checkAndSelfFund(provider, signer, agentId).catch(e => {
              console.warn(`  [SelfFund] Agent #${agentId} 失败: ${e.message}`);
              return null;
            });
            if (result?.status === "success") { selfFundOk = true; break; }
          }
          if (!selfFundOk) {
            console.error(`  ⚠️ 自补充失败，请手动充值: ${walletAddr}`);
            writeStatus({ state: "low_gas", agents: agentList, wallet: walletAddr, cycle: cycleCount, gasLeft });
          }
        }
      }

      lastDecisionBlock = await getCurrentBlock();
      writeStatus({ state: "running", agents: agentList, wallet: walletAddr, cycle: cycleCount, lastBlock: lastDecisionBlock, results });

      if (onceMode) {
        console.log("\n[Runner] 单次模式，退出。");
        break;
      }

    } catch (err) {
      console.error(`\n[ERROR] 周期 ${cycleCount} 失败: ${err.message}`);
      writeStatus({ state: "error", agents: agentList, wallet: walletAddr, cycle: cycleCount, error: err.message });
      await sleep(30000);
    }
  }

  writeStatus({ state: "stopped", agents: agentList, wallet: walletAddr, cycle: cycleCount });
  console.log("\n[Runner] 已停止。");
  process.exit(0);
}

main().catch((err) => {
  console.error("[FATAL]", err);
  writeStatus({ state: "fatal", error: err.message });
  process.exit(1);
});
