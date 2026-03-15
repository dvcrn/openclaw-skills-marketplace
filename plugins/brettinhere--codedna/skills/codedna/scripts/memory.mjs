#!/usr/bin/env node
/**
 * CodeDNA Memory System v2 — Learning & Strategy Adaptation
 * 
 * Three layers:
 *   1. Action Log    — Raw history of every action + result (ring buffer 200)
 *   2. Plot Knowledge — Visited plots with actual yield data (persistent map)
 *   3. Strategy Weights — Adaptive scoring parameters that evolve over time
 * 
 * Storage: ~/.codedna/memory_{tokenId}.json
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "fs";
import { join } from "path";
import { homedir } from "os";

const DATA_DIR = join(homedir(), ".codedna");
const MAX_ACTION_LOG = 200;
const MAX_PLOT_ENTRIES = 500;

function memoryPath(tokenId) {
  return join(DATA_DIR, `memory_${tokenId}.json`);
}

// ========== Default Memory Structure ==========

function defaultMemory() {
  return {
    version: 2,
    actionLog: [],        // [{block, action, target, success, reward, energyBefore, energyAfter, goldBefore, goldAfter, plotKey, note, timestamp}]
    plotKnowledge: {},     // { "500,499": {plotType, multiplier, visits, totalYield, avgYield, lastVisit, agentsSeen} }
    strategyWeights: {
      // These evolve based on outcomes
      gatherWeight: 1.0,       // How much to prioritize gather
      moveWeight: 1.0,         // How aggressively to seek better plots
      eatThreshold: 0.5,       // Energy ratio below which to eat (0.5 = 50%)
      raidAggression: 0.5,     // 0=never raid, 1=raid whenever possible
      exploreVsExploit: 0.3,   // 0=always exploit known, 1=always explore new
      emergencyThreshold: 20,  // Energy level considered critical
      moveThresholdMult: 1.3,  // Target must be Nx better than current to move
    },
    stats: {
      totalGathers: 0,
      totalGoldEarned: 0,
      totalMoves: 0,
      totalEats: 0,
      totalRaids: 0,
      raidWins: 0,
      raidLosses: 0,
      totalReproductions: 0,
      totalDeaths: 0,          // Times entered DYING
      gasWasted: 0,            // Failed transactions
      cyclesSinceAdapt: 0,     // Cycles since last strategy adaptation
      bestPlotKey: null,       // Highest yield plot discovered
      bestPlotYield: 0,
    },
    navTarget: null,           // Persistent navigation: {x, y, plotType, multiplier, reason}
  };
}

// ========== Load / Save ==========

export function loadMemory(tokenId) {
  const fp = memoryPath(tokenId);
  if (!existsSync(fp)) return defaultMemory();
  try {
    const raw = readFileSync(fp, "utf-8");
    const data = JSON.parse(raw);
    // Migrate v1 → v2
    if (!data.version || data.version < 2) {
      const mem = defaultMemory();
      // Import old action log if it was an array
      if (Array.isArray(data)) {
        mem.actionLog = data.slice(-MAX_ACTION_LOG);
      }
      return mem;
    }
    return data;
  } catch {
    return defaultMemory();
  }
}

function persist(tokenId, memory) {
  if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });
  // Trim action log
  if (memory.actionLog.length > MAX_ACTION_LOG) {
    memory.actionLog = memory.actionLog.slice(-MAX_ACTION_LOG);
  }
  // Trim plot knowledge (keep most recently visited)
  const plotKeys = Object.keys(memory.plotKnowledge);
  if (plotKeys.length > MAX_PLOT_ENTRIES) {
    const sorted = plotKeys.sort((a, b) => 
      (memory.plotKnowledge[b].lastVisit || 0) - (memory.plotKnowledge[a].lastVisit || 0)
    );
    const toRemove = sorted.slice(MAX_PLOT_ENTRIES);
    for (const k of toRemove) delete memory.plotKnowledge[k];
  }
  writeFileSync(memoryPath(tokenId), JSON.stringify(memory, null, 2));
}

// ========== Action Recording ==========

/**
 * Record an action result and update all memory layers
 */
export function recordAction(tokenId, entry) {
  const mem = loadMemory(tokenId);
  
  // 1. Append to action log
  mem.actionLog.push({
    block: entry.block || 0,
    action: entry.action,
    target: entry.target || null,
    success: entry.success !== false,
    reward: entry.reward || 0,         // GOLD earned (float)
    energyBefore: entry.energyBefore || 0,
    energyAfter: entry.energyAfter || 0,
    goldBefore: entry.goldBefore || 0,
    goldAfter: entry.goldAfter || 0,
    plotKey: entry.plotKey || null,
    note: entry.note || "",
    timestamp: Date.now(),
  });

  // 2. Update stats
  if (entry.success !== false) {
    switch (entry.action) {
      case "gather":
        mem.stats.totalGathers++;
        const goldGained = (entry.goldAfter || 0) - (entry.goldBefore || 0);
        if (goldGained > 0) mem.stats.totalGoldEarned += goldGained;
        break;
      case "move":
        mem.stats.totalMoves++;
        break;
      case "eat":
        mem.stats.totalEats++;
        break;
      case "raid":
        mem.stats.totalRaids++;
        if (entry.reward > 0) mem.stats.raidWins++;
        else mem.stats.raidLosses++;
        break;
      case "reproduce":
        mem.stats.totalReproductions++;
        break;
    }
  } else {
    mem.stats.gasWasted++;
  }

  // 3. Update plot knowledge if gathering
  if (entry.action === "gather" && entry.plotKey && entry.success !== false) {
    const pk = entry.plotKey;
    if (!mem.plotKnowledge[pk]) {
      mem.plotKnowledge[pk] = {
        plotType: entry.plotType || 0,
        multiplier: entry.multiplier || 1000,
        visits: 0,
        totalYield: 0,
        avgYield: 0,
        lastVisit: 0,
        maxAgentsSeen: 1,
      };
    }
    const plot = mem.plotKnowledge[pk];
    const goldGained = Math.max(0, (entry.goldAfter || 0) - (entry.goldBefore || 0));
    plot.visits++;
    plot.totalYield += goldGained;
    plot.avgYield = plot.totalYield / plot.visits;
    plot.lastVisit = entry.block || Date.now();
    plot.maxAgentsSeen = Math.max(plot.maxAgentsSeen, entry.agentCount || 1);

    // Track best plot
    if (plot.avgYield > mem.stats.bestPlotYield) {
      mem.stats.bestPlotYield = plot.avgYield;
      mem.stats.bestPlotKey = pk;
    }
  }

  // 4. Increment adaptation counter
  mem.stats.cyclesSinceAdapt++;

  persist(tokenId, mem);
  return mem;
}

// ========== Strategy Adaptation ==========

/**
 * Analyze recent performance and adjust strategy weights.
 * Called every N cycles (recommended: 20).
 */
export function adaptStrategy(tokenId) {
  const mem = loadMemory(tokenId);
  const w = mem.strategyWeights;
  const recent = mem.actionLog.slice(-50); // Last 50 actions
  if (recent.length < 10) return mem; // Not enough data

  // --- Gather effectiveness ---
  const gathers = recent.filter(a => a.action === "gather" && a.success);
  if (gathers.length > 0) {
    const avgReward = gathers.reduce((s, a) => s + (a.reward || 0), 0) / gathers.length;
    // If average gather reward is declining, boost move weight (seek better plots)
    const oldGathers = mem.actionLog.slice(-100, -50).filter(a => a.action === "gather" && a.success);
    if (oldGathers.length > 3) {
      const oldAvg = oldGathers.reduce((s, a) => s + (a.reward || 0), 0) / oldGathers.length;
      if (avgReward < oldAvg * 0.8) {
        // Yield dropped >20% → move more aggressively
        w.moveWeight = Math.min(2.0, w.moveWeight + 0.1);
        w.moveThresholdMult = Math.max(1.1, w.moveThresholdMult - 0.05);
      } else if (avgReward > oldAvg * 1.2) {
        // Yield improved >20% → settle in, move less
        w.moveWeight = Math.max(0.5, w.moveWeight - 0.1);
        w.moveThresholdMult = Math.min(2.0, w.moveThresholdMult + 0.05);
      }
    }
  }

  // --- Energy management ---
  const lowEnergyCount = recent.filter(a => a.energyAfter < 30).length;
  const lowEnergyRate = lowEnergyCount / recent.length;
  if (lowEnergyRate > 0.3) {
    // Too often in low energy → eat earlier
    w.eatThreshold = Math.min(0.7, w.eatThreshold + 0.05);
    w.emergencyThreshold = Math.min(30, w.emergencyThreshold + 2);
  } else if (lowEnergyRate < 0.05) {
    // Rarely low energy → can eat later, be more aggressive
    w.eatThreshold = Math.max(0.3, w.eatThreshold - 0.02);
    w.emergencyThreshold = Math.max(15, w.emergencyThreshold - 1);
  }

  // --- Raid effectiveness ---
  const raids = recent.filter(a => a.action === "raid");
  if (raids.length >= 3) {
    const winRate = raids.filter(a => a.success && a.reward > 0).length / raids.length;
    if (winRate > 0.6) {
      w.raidAggression = Math.min(1.0, w.raidAggression + 0.1);
    } else if (winRate < 0.3) {
      w.raidAggression = Math.max(0.0, w.raidAggression - 0.15);
    }
  }

  // --- Gas waste ---
  const failures = recent.filter(a => !a.success).length;
  const failRate = failures / recent.length;
  if (failRate > 0.2) {
    // Too many failed txns → be more conservative
    w.exploreVsExploit = Math.max(0.1, w.exploreVsExploit - 0.05);
  }

  // --- Explore vs exploit ---
  const uniquePlots = new Set(recent.filter(a => a.plotKey).map(a => a.plotKey));
  if (uniquePlots.size <= 2 && recent.length > 20) {
    // Stuck in same spot — explore more
    w.exploreVsExploit = Math.min(0.8, w.exploreVsExploit + 0.05);
  }

  mem.stats.cyclesSinceAdapt = 0;
  persist(tokenId, mem);
  return mem;
}

// ========== Navigation Memory ==========

export function setNavTarget(tokenId, target) {
  const mem = loadMemory(tokenId);
  mem.navTarget = target; // {x, y, plotType, multiplier, reason} or null
  persist(tokenId, mem);
}

export function getNavTarget(tokenId) {
  const mem = loadMemory(tokenId);
  return mem.navTarget;
}

export function clearNavTarget(tokenId) {
  const mem = loadMemory(tokenId);
  mem.navTarget = null;
  persist(tokenId, mem);
}

// ========== Query Helpers ==========

export function getRecentMemory(tokenId, count = 20) {
  const mem = loadMemory(tokenId);
  return mem.actionLog.slice(-count);
}

export function getPlotKnowledge(tokenId, plotKey) {
  const mem = loadMemory(tokenId);
  return mem.plotKnowledge[plotKey] || null;
}

export function getBestKnownPlots(tokenId, limit = 10) {
  const mem = loadMemory(tokenId);
  return Object.entries(mem.plotKnowledge)
    .sort(([, a], [, b]) => b.avgYield - a.avgYield)
    .slice(0, limit)
    .map(([key, data]) => ({ plotKey: key, ...data }));
}

export function getStrategyWeights(tokenId) {
  const mem = loadMemory(tokenId);
  return mem.strategyWeights;
}

export function getStats(tokenId) {
  const mem = loadMemory(tokenId);
  return mem.stats;
}

// ========== Legacy compat ==========
export function saveMemory(tokenId, entry) {
  // Bridge old calls to new recordAction
  recordAction(tokenId, entry);
}

// ========== CLI ==========
if (process.argv[1] && process.argv[1].endsWith("memory.mjs")) {
  const [cmd, ...args] = process.argv.slice(2);
  switch (cmd) {
    case "show": {
      const tokenId = parseInt(args[0]);
      if (!tokenId) { console.error("Usage: node memory.mjs show <tokenId> [count]"); process.exit(1); }
      const count = parseInt(args[1]) || 20;
      const entries = getRecentMemory(tokenId, count);
      if (entries.length === 0) {
        console.log(`No memories for agent #${tokenId}`);
      } else {
        for (const e of entries) {
          console.log(`[Block ${e.block}] ${e.action}${e.target ? ` → ${e.target}` : ""} | ${e.success ? "✅" : "❌"} | E:${e.energyBefore}→${e.energyAfter} | G:${e.goldBefore?.toFixed?.(1) || "?"}→${e.goldAfter?.toFixed?.(1) || "?"} | ${e.note}`);
        }
      }
      break;
    }
    case "stats": {
      const tokenId = parseInt(args[0]);
      if (!tokenId) { console.error("Usage: node memory.mjs stats <tokenId>"); process.exit(1); }
      const stats = getStats(tokenId);
      const weights = getStrategyWeights(tokenId);
      console.log("\n=== Agent #" + tokenId + " Stats ===");
      console.log(JSON.stringify(stats, null, 2));
      console.log("\n=== Strategy Weights ===");
      console.log(JSON.stringify(weights, null, 2));
      break;
    }
    case "plots": {
      const tokenId = parseInt(args[0]);
      if (!tokenId) { console.error("Usage: node memory.mjs plots <tokenId>"); process.exit(1); }
      const best = getBestKnownPlots(tokenId, 10);
      const names = ["草原","森林","山地","矿脉"];
      console.log("\n=== Best Known Plots for Agent #" + tokenId + " ===");
      for (const p of best) {
        console.log(`  ${p.plotKey} | ${names[p.plotType]} x${p.multiplier/100} | 采集${p.visits}次 | 平均${p.avgYield.toFixed(1)} GOLD | 最多${p.maxAgentsSeen}人`);
      }
      break;
    }
    case "clear": {
      const tokenId = parseInt(args[0]);
      if (!tokenId) { console.error("Usage: node memory.mjs clear <tokenId>"); process.exit(1); }
      const fp = memoryPath(tokenId);
      if (existsSync(fp)) {
        writeFileSync(fp, JSON.stringify(defaultMemory(), null, 2));
        console.log(`Memory reset for agent #${tokenId}`);
      }
      break;
    }
    default:
      console.error("Usage: node memory.mjs <show|stats|plots|clear> <tokenId> [args...]");
      process.exit(1);
  }
}
